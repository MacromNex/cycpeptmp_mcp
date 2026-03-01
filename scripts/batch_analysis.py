#!/usr/bin/env python3
"""
Script: batch_analysis.py
Description: Comprehensive batch analysis of cyclic peptides including properties, diversity, and similarity

Original Use Case: examples/use_case_3_batch_analysis.py
Dependencies Removed: repo/cycpeptmp/utils/utils_function (canonicalize_smiles inlined)

Usage:
    python scripts/batch_analysis.py --input <input_file> --output <output_prefix>

Example:
    python scripts/batch_analysis.py --input examples/data/sequences/new_data.csv --output results/batch_analysis
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
import json
import time

# Essential scientific packages
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors
from rdkit import DataStructs

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "similarity": {
        "threshold": 0.7,
        "fingerprint": {
            "type": "morgan",
            "radius": 2,
            "n_bits": 1024
        }
    },
    "diversity": {
        "min_molecules": 2
    },
    "database": {
        "default_path": "repo/cycpeptmp/data/CycPeptMPDB_Peptide_All.csv"
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

def calculate_molecular_fingerprint(mol: Chem.Mol, radius: int = 2, n_bits: int = 1024):
    """Calculate Morgan fingerprint for a molecule."""
    return rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)

# ==============================================================================
# Core Functions (main logic extracted from use case)
# ==============================================================================
def calculate_basic_properties(smiles_list: List[str]) -> pd.DataFrame:
    """Calculate basic molecular properties for a list of SMILES."""
    properties = []

    for smiles in smiles_list:
        prop = {
            'smiles': smiles,
            'valid': False,
            'mw': None,
            'logp': None,
            'tpsa': None,
            'hbd': None,
            'hba': None,
            'rotatable_bonds': None,
            'rings': None,
            'aromatic_rings': None
        }

        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                prop['valid'] = True
                prop['mw'] = Descriptors.MolWt(mol)
                prop['logp'] = Crippen.MolLogP(mol)
                prop['tpsa'] = Descriptors.TPSA(mol)
                prop['hbd'] = Descriptors.NumHDonors(mol)
                prop['hba'] = Descriptors.NumHAcceptors(mol)
                prop['rotatable_bonds'] = Descriptors.NumRotatableBonds(mol)
                prop['rings'] = Descriptors.RingCount(mol)
                prop['aromatic_rings'] = Descriptors.NumAromaticRings(mol)

        except Exception as e:
            print(f"Error calculating properties for {smiles}: {e}")

        properties.append(prop)

    return pd.DataFrame(properties)

def analyze_diversity(smiles_list: List[str], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Analyze the chemical diversity of the peptide set."""
    config = {**DEFAULT_CONFIG, **(config or {})}
    fp_config = config.get('similarity', {}).get('fingerprint', DEFAULT_CONFIG['similarity']['fingerprint'])

    try:
        fingerprints = []
        valid_smiles = []

        for smiles in smiles_list:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol:
                    fp = calculate_molecular_fingerprint(mol, fp_config['radius'], fp_config['n_bits'])
                    fingerprints.append(fp)
                    valid_smiles.append(smiles)
            except Exception:
                continue

        if len(fingerprints) < config['diversity']['min_molecules']:
            return {"error": "Not enough valid molecules for diversity analysis"}

        # Calculate pairwise similarities
        similarities = []
        for i in range(len(fingerprints)):
            for j in range(i+1, len(fingerprints)):
                sim = DataStructs.TanimotoSimilarity(fingerprints[i], fingerprints[j])
                similarities.append(sim)

        return {
            'num_valid': len(fingerprints),
            'mean_similarity': np.mean(similarities),
            'min_similarity': np.min(similarities),
            'max_similarity': np.max(similarities),
            'std_similarity': np.std(similarities),
            'diversity_score': 1 - np.mean(similarities)  # Higher = more diverse
        }

    except ImportError:
        return {"error": "RDKit fingerprint modules not available"}
    except Exception as e:
        return {"error": f"Error in diversity analysis: {str(e)}"}

def find_similar_peptides(query_smiles: str, database_df: pd.DataFrame,
                         similarity_threshold: float = 0.8,
                         config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Find similar peptides in the database using Tanimoto similarity."""
    config = {**DEFAULT_CONFIG, **(config or {})}
    fp_config = config.get('similarity', {}).get('fingerprint', DEFAULT_CONFIG['similarity']['fingerprint'])

    try:
        query_mol = Chem.MolFromSmiles(query_smiles)
        if not query_mol:
            return []

        query_fp = calculate_molecular_fingerprint(query_mol, fp_config['radius'], fp_config['n_bits'])

        similarities = []
        for idx, row in database_df.iterrows():
            try:
                db_mol = Chem.MolFromSmiles(row['SMILES'])
                if db_mol:
                    db_fp = calculate_molecular_fingerprint(db_mol, fp_config['radius'], fp_config['n_bits'])
                    similarity = DataStructs.TanimotoSimilarity(query_fp, db_fp)

                    if similarity >= similarity_threshold:
                        similarities.append({
                            'db_id': row.get('ID', idx),
                            'db_name': row.get('Name', 'Unknown'),
                            'similarity': similarity,
                            'db_permeability': row.get('LogPexp', None),
                            'db_smiles': row['SMILES']
                        })

            except Exception:
                continue

        return sorted(similarities, key=lambda x: x['similarity'], reverse=True)

    except Exception as e:
        print(f"Error in similarity search: {e}")
        return []

def generate_summary_statistics(results_df: pd.DataFrame) -> Dict[str, Any]:
    """Generate summary statistics for the analysis."""
    summary = {}

    # Basic counts
    summary['total_peptides'] = len(results_df)
    summary['valid_smiles'] = results_df['valid'].sum() if 'valid' in results_df else 0

    if summary['valid_smiles'] > 0:
        valid_df = results_df[results_df['valid'] == True] if 'valid' in results_df else results_df

        # Molecular weight statistics
        if 'mw' in valid_df:
            summary['mw_mean'] = float(valid_df['mw'].mean())
            summary['mw_std'] = float(valid_df['mw'].std())
            summary['mw_min'] = float(valid_df['mw'].min())
            summary['mw_max'] = float(valid_df['mw'].max())

        # LogP statistics
        if 'logp' in valid_df:
            summary['logp_mean'] = float(valid_df['logp'].mean())
            summary['logp_std'] = float(valid_df['logp'].std())
            summary['logp_min'] = float(valid_df['logp'].min())
            summary['logp_max'] = float(valid_df['logp'].max())

        # TPSA statistics
        if 'tpsa' in valid_df:
            summary['tpsa_mean'] = float(valid_df['tpsa'].mean())
            summary['tpsa_std'] = float(valid_df['tpsa'].std())

        # Drug-likeness assessment (Lipinski's Rule of Five)
        if all(col in valid_df for col in ['mw', 'logp', 'hbd', 'hba']):
            lipinski_violations = 0
            lipinski_violations += (valid_df['mw'] > 500).sum()
            lipinski_violations += (valid_df['logp'] > 5).sum()
            lipinski_violations += (valid_df['hbd'] > 5).sum()
            lipinski_violations += (valid_df['hba'] > 10).sum()

            # Calculate compliance correctly
            total_rules = len(valid_df) * 4  # 4 rules per molecule
            compliance_rate = 1 - (lipinski_violations / total_rules)
            summary['lipinski_compliance_rate'] = float(compliance_rate)

    return summary

def load_database_peptides(database_path: Union[str, Path]) -> Optional[pd.DataFrame]:
    """Load the CycPeptMPDB database for comparison."""
    try:
        database_path = Path(database_path)
        if not database_path.exists():
            print(f"Database file not found: {database_path}")
            return None

        db_df = pd.read_csv(database_path, low_memory=False)
        print(f"Loaded CycPeptMPDB database with {len(db_df)} peptides")
        return db_df
    except Exception as e:
        print(f"Error loading database: {e}")
        return None

def run_batch_analysis(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    database_path: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for batch analysis of cyclic peptides.

    Args:
        input_file: Path to input CSV file with SMILES column
        output_file: Path prefix for output files (optional)
        database_path: Path to database file for similarity comparison (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - analysis_df: DataFrame with molecular properties
            - summary: Summary statistics
            - diversity: Diversity analysis results
            - similar_peptides: Similar peptides (if database provided)
            - output_files: List of generated output files
            - metadata: Execution metadata

    Example:
        >>> result = run_batch_analysis("input.csv", "output_prefix")
        >>> print(result['summary']['total_peptides'])
    """
    # Setup
    input_file = Path(input_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Load input data
    print(f"Loading input data from {input_file}...")
    input_df = pd.read_csv(input_file)

    if 'SMILES' not in input_df.columns:
        raise ValueError("Input file must contain a 'SMILES' column")

    print(f"Loaded {len(input_df)} peptides for analysis")
    start_time = time.time()

    results = {}
    output_files = []

    # 1. Basic validation and properties
    print("1. Calculating molecular properties...")
    properties_df = calculate_basic_properties(input_df['SMILES'].tolist())

    # Merge with input data
    analysis_df = pd.concat([input_df.reset_index(drop=True), properties_df], axis=1)

    # 2. Summary statistics
    print("2. Generating summary statistics...")
    summary = generate_summary_statistics(analysis_df)

    # 3. Diversity analysis
    print("3. Analyzing chemical diversity...")
    diversity = analyze_diversity(input_df['SMILES'].tolist(), config)

    # 4. Database comparison (if available)
    similar_peptides_df = None
    if database_path:
        print("4. Comparing with CycPeptMPDB database...")
        database_df = load_database_peptides(database_path)

        if database_df is not None:
            similar_peptides = []
            similarity_threshold = config['similarity']['threshold']

            for idx, row in input_df.iterrows():
                smiles = row['SMILES']
                peptide_id = row.get('ID_org', f'peptide_{idx}')

                print(f"   Searching similarities for {peptide_id}...", end='')

                similarities = find_similar_peptides(
                    smiles, database_df, similarity_threshold, config
                )

                if similarities:
                    print(f" Found {len(similarities)} similar peptides")
                    for sim in similarities[:3]:  # Top 3 similar
                        similar_peptides.append({
                            'query_id': peptide_id,
                            'query_smiles': smiles,
                            'similar_id': sim['db_id'],
                            'similar_name': sim['db_name'],
                            'similarity': sim['similarity'],
                            'known_permeability': sim['db_permeability']
                        })
                else:
                    print(" No similar peptides found")

            if similar_peptides:
                similar_peptides_df = pd.DataFrame(similar_peptides)

    # 5. Save results
    output_prefix = output_file or "batch_analysis"
    print("5. Saving analysis results...")

    # Main analysis results
    properties_file = f"{output_prefix}_properties.csv"
    analysis_df.to_csv(properties_file, index=False)
    output_files.append(properties_file)
    print(f"   Molecular properties saved to {properties_file}")

    # Summary report
    summary_file = f"{output_prefix}_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    output_files.append(summary_file)
    print(f"   Summary statistics saved to {summary_file}")

    # Similar peptides (if any)
    if similar_peptides_df is not None:
        similarities_file = f"{output_prefix}_similarities.csv"
        similar_peptides_df.to_csv(similarities_file, index=False)
        output_files.append(similarities_file)
        print(f"   Similar peptides saved to {similarities_file}")

    # Diversity report
    diversity_file = f"{output_prefix}_diversity.json"
    with open(diversity_file, 'w') as f:
        json.dump(diversity, f, indent=2, default=str)
    output_files.append(diversity_file)
    print(f"   Diversity analysis saved to {diversity_file}")

    elapsed = time.time() - start_time
    print(f"\nAnalysis completed in {elapsed:.1f} seconds")

    return {
        "analysis_df": analysis_df,
        "summary": summary,
        "diversity": diversity,
        "similar_peptides": similar_peptides_df,
        "output_files": output_files,
        "metadata": {
            "input_file": str(input_file),
            "database_path": str(database_path) if database_path else None,
            "config": config,
            "execution_time": elapsed
        }
    }

def print_analysis_report(summary: Dict[str, Any], diversity: Dict[str, Any],
                         similar_peptides_df: Optional[pd.DataFrame] = None) -> None:
    """Print a comprehensive analysis report."""
    print("\n" + "="*60)
    print("COMPREHENSIVE ANALYSIS REPORT")
    print("="*60)

    # Basic statistics
    print(f"\nDataset Overview:")
    print(f"  Total peptides: {summary.get('total_peptides', 0)}")
    print(f"  Valid SMILES: {summary.get('valid_smiles', 0)}")

    if summary.get('valid_smiles', 0) > 0:
        print(f"\nMolecular Weight:")
        print(f"  Mean: {summary.get('mw_mean', 0):.1f} Da")
        print(f"  Range: {summary.get('mw_min', 0):.1f} - {summary.get('mw_max', 0):.1f} Da")

        print(f"\nLipophilicity (LogP):")
        print(f"  Mean: {summary.get('logp_mean', 0):.2f}")
        print(f"  Range: {summary.get('logp_min', 0):.2f} - {summary.get('logp_max', 0):.2f}")

        print(f"\nPolar Surface Area (TPSA):")
        print(f"  Mean: {summary.get('tpsa_mean', 0):.1f} Ų")

        if 'lipinski_compliance_rate' in summary:
            print(f"\nDrug-likeness (Lipinski's Rule):")
            print(f"  Compliance rate: {summary.get('lipinski_compliance_rate', 0)*100:.1f}%")

    # Diversity analysis
    if 'diversity_score' in diversity and 'error' not in diversity:
        print(f"\nChemical Diversity:")
        print(f"  Diversity score: {diversity['diversity_score']:.3f} (0=identical, 1=completely diverse)")
        print(f"  Mean Tanimoto similarity: {diversity['mean_similarity']:.3f}")
        print(f"  Similarity range: {diversity['min_similarity']:.3f} - {diversity['max_similarity']:.3f}")

    # Similar peptides
    if similar_peptides_df is not None:
        print(f"\nDatabase Comparison:")
        print(f"  Found {len(similar_peptides_df)} similar peptides in CycPeptMPDB")

        # Show peptides with known permeability
        known_perm = similar_peptides_df.dropna(subset=['known_permeability'])
        if len(known_perm) > 0:
            print(f"  {len(known_perm)} have experimental permeability data")
            print(f"  Mean experimental LogP: {known_perm['known_permeability'].mean():.2f}")

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', required=True, help='Input CSV file with SMILES')
    parser.add_argument('--output', '-o', default='batch_analysis', help='Output prefix for result files')
    parser.add_argument('--database', '-d', help='Path to CycPeptMPDB database file for similarity comparison')
    parser.add_argument('--config', '-c', help='Config file (JSON)')
    parser.add_argument('--similarity-threshold', type=float, default=0.7,
                       help='Similarity threshold for database comparison')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Override similarity threshold if provided
    if config is None:
        config = {}
    if 'similarity' not in config:
        config['similarity'] = {}
    config['similarity']['threshold'] = args.similarity_threshold

    # Run comprehensive analysis
    result = run_batch_analysis(
        input_file=args.input,
        output_file=args.output,
        database_path=args.database,
        config=config
    )

    # Print report
    print_analysis_report(
        result['summary'],
        result['diversity'],
        result['similar_peptides']
    )

    print(f"\nAll analysis results saved with prefix: {args.output}")
    print("Output files:")
    for output_file in result['output_files']:
        print(f"  - {output_file}")

    return result

if __name__ == "__main__":
    main()