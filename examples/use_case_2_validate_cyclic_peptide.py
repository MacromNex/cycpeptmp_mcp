#!/usr/bin/env python3
"""
CycPeptMP Use Case 2: Validate Cyclic Peptide SMILES

This script validates cyclic peptide SMILES strings and extracts basic properties
like monomer composition, molecular weight, and structural features.

Usage:
    python use_case_2_validate_cyclic_peptide.py --smiles "NCCCC[C@@H]1NC(=O)..."
    python use_case_2_validate_cyclic_peptide.py --input examples/data/sequences/new_data.csv --output validation_results.csv

Requirements:
    - Python 3.9+ environment with rdkit
"""

import argparse
import sys
import pandas as pd
from pathlib import Path

# Add the repo path to sys.path to import CycPeptMP modules
repo_path = Path(__file__).parent.parent / "repo" / "cycpeptmp"
sys.path.insert(0, str(repo_path))

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski
    from utils import utils_function
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure you have RDKit installed.")
    sys.exit(1)

def validate_smiles(smiles_string):
    """
    Validate a SMILES string and extract basic molecular properties.

    Args:
        smiles_string (str): SMILES representation of the molecule

    Returns:
        dict: Validation results and molecular properties
    """
    result = {
        'smiles': smiles_string,
        'valid': False,
        'canonical_smiles': None,
        'molecular_weight': None,
        'num_atoms': None,
        'num_bonds': None,
        'num_rings': None,
        'is_cyclic': False,
        'logp': None,
        'tpsa': None,
        'hbd': None,  # Hydrogen bond donors
        'hba': None,  # Hydrogen bond acceptors
        'rotatable_bonds': None,
        'aromatic_rings': None,
        'monomer_count': None,
        'errors': []
    }

    try:
        # Parse SMILES
        mol = Chem.MolFromSmiles(smiles_string)

        if mol is None:
            result['errors'].append("Invalid SMILES string")
            return result

        result['valid'] = True

        # Get canonical SMILES
        result['canonical_smiles'] = utils_function.canonicalize_smiles(smiles_string)

        # Basic molecular properties
        result['molecular_weight'] = round(Descriptors.MolWt(mol), 2)
        result['num_atoms'] = mol.GetNumAtoms()
        result['num_bonds'] = mol.GetNumBonds()

        # Ring information
        ring_info = mol.GetRingInfo()
        result['num_rings'] = ring_info.NumRings()
        result['is_cyclic'] = result['num_rings'] > 0

        # Drug-like properties
        result['logp'] = round(Crippen.MolLogP(mol), 2)
        result['tpsa'] = round(Descriptors.TPSA(mol), 2)
        result['hbd'] = Lipinski.NumHDonors(mol)
        result['hba'] = Lipinski.NumHAcceptors(mol)
        result['rotatable_bonds'] = Descriptors.NumRotatableBonds(mol)
        result['aromatic_rings'] = Descriptors.NumAromaticRings(mol)

        # Check if peptide-like
        if result['molecular_weight'] < 500:
            result['errors'].append("Warning: Low molecular weight for a cyclic peptide")
        elif result['molecular_weight'] > 2000:
            result['errors'].append("Warning: High molecular weight for a typical cyclic peptide")

        if not result['is_cyclic']:
            result['errors'].append("Warning: Molecule does not appear to be cyclic")

        # Try to extract monomers (simplified)
        try:
            # Create temporary DataFrame for monomer extraction
            temp_df = pd.DataFrame({
                'ID': [1],
                'SMILES': [smiles_string],
                'ID_org': ['temp']
            })

            # This will attempt to split the peptide into monomers
            unique_monomers_path = "temp_monomers.csv"
            utils_function.get_unique_monomer(temp_df, unique_monomers_path)

            # Count monomers if file was created
            if Path(unique_monomers_path).exists():
                monomer_df = pd.read_csv(unique_monomers_path)
                result['monomer_count'] = len(monomer_df)
                # Clean up temp file
                Path(unique_monomers_path).unlink()

        except Exception as e:
            result['errors'].append(f"Could not extract monomers: {str(e)}")

        # Additional cyclic peptide checks
        if result['hbd'] == 0:
            result['errors'].append("Warning: No hydrogen bond donors found")

        # Check for common peptide elements
        atom_counts = {}
        for atom in mol.GetAtoms():
            symbol = atom.GetSymbol()
            atom_counts[symbol] = atom_counts.get(symbol, 0) + 1

        if 'N' not in atom_counts:
            result['errors'].append("Warning: No nitrogen atoms found (unusual for peptides)")
        if 'O' not in atom_counts:
            result['errors'].append("Warning: No oxygen atoms found (unusual for peptides)")

    except Exception as e:
        result['errors'].append(f"Error during validation: {str(e)}")

    return result

def validate_dataframe(input_df):
    """
    Validate all SMILES in a DataFrame.

    Args:
        input_df (pd.DataFrame): DataFrame with SMILES column

    Returns:
        pd.DataFrame: DataFrame with validation results
    """
    results = []

    print(f"Validating {len(input_df)} SMILES strings...")

    for idx, row in input_df.iterrows():
        smiles = row.get('SMILES', '')
        peptide_id = row.get('ID_org', f'peptide_{idx}')

        print(f"Processing {peptide_id}... ", end='', flush=True)

        result = validate_smiles(smiles)
        result['ID_org'] = peptide_id
        result['original_id'] = row.get('ID', idx)

        if result['valid']:
            print("✓ Valid")
        else:
            print("✗ Invalid")

        if result['errors']:
            for error in result['errors']:
                print(f"  - {error}")

        results.append(result)

    return pd.DataFrame(results)

def print_summary(results_df):
    """Print a summary of validation results."""
    total = len(results_df)
    valid = results_df['valid'].sum()
    invalid = total - valid

    print(f"\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)
    print(f"Total SMILES processed: {total}")
    print(f"Valid SMILES: {valid}")
    print(f"Invalid SMILES: {invalid}")
    print(f"Success rate: {valid/total*100:.1f}%")

    if valid > 0:
        valid_results = results_df[results_df['valid']]
        print(f"\nMolecular Weight Range: {valid_results['molecular_weight'].min():.1f} - {valid_results['molecular_weight'].max():.1f}")
        print(f"Average LogP: {valid_results['logp'].mean():.2f}")
        print(f"Average TPSA: {valid_results['tpsa'].mean():.1f}")
        print(f"Cyclic peptides: {valid_results['is_cyclic'].sum()}/{valid}")

        if 'monomer_count' in valid_results.columns:
            monomer_counts = valid_results['monomer_count'].dropna()
            if len(monomer_counts) > 0:
                print(f"Average monomer count: {monomer_counts.mean():.1f}")

    # Show most common issues
    all_errors = []
    for errors in results_df['errors']:
        if isinstance(errors, list):
            all_errors.extend(errors)

    if all_errors:
        print(f"\nCommon Issues:")
        from collections import Counter
        error_counts = Counter(all_errors)
        for error, count in error_counts.most_common(5):
            print(f"  - {error}: {count} times")

def main():
    parser = argparse.ArgumentParser(description='Validate cyclic peptide SMILES strings')
    parser.add_argument('--input', type=str, help='Input CSV file with SMILES')
    parser.add_argument('--smiles', type=str, help='Single SMILES string to validate')
    parser.add_argument('--output', type=str, default='validation_results.csv',
                       help='Output CSV file for results')

    args = parser.parse_args()

    if not args.input and not args.smiles:
        parser.error("Either --input or --smiles must be provided")

    if args.smiles:
        # Validate single SMILES
        print(f"Validating SMILES: {args.smiles}")
        result = validate_smiles(args.smiles)

        print(f"\nValidation Result:")
        print(f"  Valid: {result['valid']}")
        print(f"  Canonical SMILES: {result['canonical_smiles']}")
        print(f"  Molecular Weight: {result['molecular_weight']}")
        print(f"  Atoms: {result['num_atoms']}")
        print(f"  Rings: {result['num_rings']}")
        print(f"  Cyclic: {result['is_cyclic']}")
        print(f"  LogP: {result['logp']}")
        print(f"  TPSA: {result['tpsa']}")
        print(f"  H-bond donors: {result['hbd']}")
        print(f"  H-bond acceptors: {result['hba']}")
        print(f"  Rotatable bonds: {result['rotatable_bonds']}")

        if result['monomer_count']:
            print(f"  Monomer count: {result['monomer_count']}")

        if result['errors']:
            print(f"  Issues:")
            for error in result['errors']:
                print(f"    - {error}")

    else:
        # Validate file
        print(f"Loading SMILES from {args.input}...")
        if not Path(args.input).exists():
            print(f"Error: Input file {args.input} not found")
            sys.exit(1)

        input_df = pd.read_csv(args.input)

        if 'SMILES' not in input_df.columns:
            print("Error: Input file must contain a 'SMILES' column")
            sys.exit(1)

        # Validate all SMILES
        results_df = validate_dataframe(input_df)

        # Save results
        results_df.to_csv(args.output, index=False)
        print(f"\nResults saved to {args.output}")

        # Print summary
        print_summary(results_df)

if __name__ == "__main__":
    main()