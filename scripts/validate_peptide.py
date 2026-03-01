#!/usr/bin/env python3
"""
Script: validate_peptide.py
Description: Validate cyclic peptide SMILES and calculate molecular properties

Original Use Case: examples/use_case_2_validate_cyclic_peptide.py
Dependencies Removed: repo/cycpeptmp/utils/utils_function (canonicalize_smiles, get_unique_monomer inlined)

Usage:
    python scripts/validate_peptide.py --input <input_file> --output <output_file>
    python scripts/validate_peptide.py --smiles "SMILES_STRING"

Example:
    python scripts/validate_peptide.py --input examples/data/sequences/new_data.csv --output results/validation.csv
    python scripts/validate_peptide.py --smiles "NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O"
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
import json
import sys

# Essential scientific packages
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski
from collections import Counter

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "molecular_weight": {
        "min_warning": 500,
        "max_warning": 2000
    },
    "validation": {
        "check_cyclicity": True,
        "check_peptide_elements": True,
        "check_hbd": True
    }
}

# ==============================================================================
# Inlined Utility Functions (simplified from repo)
# ==============================================================================
def canonicalize_smiles(smiles: str) -> Optional[str]:
    """
    Canonicalize SMILES string using RDKit.
    Inlined from repo/cycpeptmp/utils/utils_function.py
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol)
    except Exception:
        return None

def validate_cyclic_peptide_structure(mol: Chem.Mol) -> bool:
    """Validate that molecule is a cyclic peptide."""
    # Check for ring structure
    ring_info = mol.GetRingInfo()
    if ring_info.NumRings() == 0:
        return False

    # Check for peptide-like elements (N, O, C should be present)
    atom_counts = {}
    for atom in mol.GetAtoms():
        symbol = atom.GetSymbol()
        atom_counts[symbol] = atom_counts.get(symbol, 0) + 1

    # Basic peptide requirements
    return 'N' in atom_counts and 'O' in atom_counts and 'C' in atom_counts

def calculate_molecular_properties(mol: Chem.Mol) -> Dict[str, Any]:
    """Calculate comprehensive molecular properties."""
    return {
        'molecular_weight': round(Descriptors.MolWt(mol), 2),
        'num_atoms': mol.GetNumAtoms(),
        'num_bonds': mol.GetNumBonds(),
        'num_rings': mol.GetRingInfo().NumRings(),
        'logp': round(Crippen.MolLogP(mol), 2),
        'tpsa': round(Descriptors.TPSA(mol), 2),
        'hbd': Lipinski.NumHDonors(mol),
        'hba': Lipinski.NumHAcceptors(mol),
        'rotatable_bonds': Descriptors.NumRotatableBonds(mol),
        'aromatic_rings': Descriptors.NumAromaticRings(mol)
    }

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def validate_smiles(smiles_string: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validate a SMILES string and extract molecular properties.

    Args:
        smiles_string: SMILES representation of the molecule
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)

    Returns:
        Dict containing validation results and molecular properties
    """
    config = {**DEFAULT_CONFIG, **(config or {})}

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
        'hbd': None,
        'hba': None,
        'rotatable_bonds': None,
        'aromatic_rings': None,
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
        result['canonical_smiles'] = canonicalize_smiles(smiles_string)

        # Calculate molecular properties
        properties = calculate_molecular_properties(mol)
        result.update(properties)

        # Ring and cyclicity information
        result['is_cyclic'] = result['num_rings'] > 0

        # Validation checks based on config
        if config['validation']['check_cyclicity'] and not result['is_cyclic']:
            result['errors'].append("Warning: Molecule does not appear to be cyclic")

        # Molecular weight warnings
        mw_config = config['molecular_weight']
        if result['molecular_weight'] < mw_config['min_warning']:
            result['errors'].append("Warning: Low molecular weight for a cyclic peptide")
        elif result['molecular_weight'] > mw_config['max_warning']:
            result['errors'].append("Warning: High molecular weight for a typical cyclic peptide")

        # Hydrogen bond donor check
        if config['validation']['check_hbd'] and result['hbd'] == 0:
            result['errors'].append("Warning: No hydrogen bond donors found")

        # Check for common peptide elements
        if config['validation']['check_peptide_elements']:
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

def run_validate_peptide(
    input_file: Optional[Union[str, Path]] = None,
    smiles: Optional[str] = None,
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for cyclic peptide validation.

    Args:
        input_file: Path to input CSV file with SMILES column (optional if smiles provided)
        smiles: Single SMILES string to validate (optional if input_file provided)
        output_file: Path to save output CSV (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Validation results (single dict or DataFrame)
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata

    Example:
        >>> result = run_validate_peptide(smiles="CC1CCCCC1")
        >>> print(result['result']['valid'])

        >>> result = run_validate_peptide("input.csv", "output.csv")
        >>> print(result['output_file'])
    """
    # Setup
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    if not input_file and not smiles:
        raise ValueError("Either input_file or smiles must be provided")

    if smiles:
        # Validate single SMILES
        validation_result = validate_smiles(smiles, config)
        result = validation_result

        # Save single result if output requested
        output_path = None
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame([validation_result])
            df.to_csv(output_path, index=False)

    else:
        # Validate file
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        input_df = pd.read_csv(input_path)
        if 'SMILES' not in input_df.columns:
            raise ValueError("Input file must contain a 'SMILES' column")

        # Validate all SMILES
        results = []
        for idx, row in input_df.iterrows():
            smiles_str = row.get('SMILES', '')
            peptide_id = row.get('ID_org', f'peptide_{idx}')

            validation_result = validate_smiles(smiles_str, config)
            validation_result['ID_org'] = peptide_id
            validation_result['original_id'] = row.get('ID', idx)
            results.append(validation_result)

        result = pd.DataFrame(results)

        # Save results if requested
        output_path = None
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            result.to_csv(output_path, index=False)

    return {
        "result": result,
        "output_file": str(output_path) if output_path else None,
        "metadata": {
            "input_file": str(input_file) if input_file else None,
            "smiles": smiles,
            "config": config
        }
    }

def print_validation_summary(results_df: pd.DataFrame) -> None:
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
        print(f"\nMolecular Weight Range: {valid_results['molecular_weight'].min():.1f} - {valid_results['molecular_weight'].max():.1f} Da")
        print(f"Average LogP: {valid_results['logp'].mean():.2f}")
        print(f"Average TPSA: {valid_results['tpsa'].mean():.1f} Ų")
        print(f"Cyclic peptides: {valid_results['is_cyclic'].sum()}/{valid}")
        print(f"Average aromatic rings: {valid_results['aromatic_rings'].mean():.1f}")

    # Show most common issues
    all_errors = []
    for errors in results_df['errors']:
        if isinstance(errors, list):
            all_errors.extend(errors)

    if all_errors:
        print(f"\nCommon Issues:")
        error_counts = Counter(all_errors)
        for error, count in error_counts.most_common(5):
            print(f"  - {error}: {count} times")

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', help='Input CSV file with SMILES column')
    parser.add_argument('--smiles', '-s', help='Single SMILES string to validate')
    parser.add_argument('--output', '-o', help='Output CSV file path')
    parser.add_argument('--config', '-c', help='Config file (JSON)')

    args = parser.parse_args()

    if not args.input and not args.smiles:
        parser.error("Either --input or --smiles must be provided")

    # Load config if provided
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Run validation
    result = run_validate_peptide(
        input_file=args.input,
        smiles=args.smiles,
        output_file=args.output,
        config=config
    )

    # Print results
    if args.smiles:
        # Single SMILES result
        validation_result = result['result']
        print(f"\nValidation Result for: {args.smiles}")
        print(f"  Valid: {validation_result['valid']}")
        print(f"  Canonical SMILES: {validation_result['canonical_smiles']}")
        print(f"  Molecular Weight: {validation_result['molecular_weight']} Da")
        print(f"  Atoms: {validation_result['num_atoms']}")
        print(f"  Rings: {validation_result['num_rings']}")
        print(f"  Cyclic: {validation_result['is_cyclic']}")
        print(f"  LogP: {validation_result['logp']}")
        print(f"  TPSA: {validation_result['tpsa']} Ų")
        print(f"  H-bond donors: {validation_result['hbd']}")
        print(f"  H-bond acceptors: {validation_result['hba']}")
        print(f"  Rotatable bonds: {validation_result['rotatable_bonds']}")

        if validation_result['errors']:
            print(f"  Issues:")
            for error in validation_result['errors']:
                print(f"    - {error}")
    else:
        # Multiple SMILES results
        results_df = result['result']
        print_validation_summary(results_df)

    if result['output_file']:
        print(f"\nResults saved to: {result['output_file']}")

    return result

if __name__ == '__main__':
    main()