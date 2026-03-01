#!/usr/bin/env python3
"""
CycPeptMP Use Case 3: Batch Analysis of Cyclic Peptides

This script performs comprehensive batch analysis of multiple cyclic peptides,
including validation, permeability prediction, and comparative analysis.

Usage:
    python use_case_3_batch_analysis.py --input examples/data/sequences/new_data.csv --output analysis_report.csv
    python use_case_3_batch_analysis.py --input examples/data/sequences/new_data.csv --compare-with-database

Requirements:
    - Python 3.9+ environment with all CycPeptMP dependencies
"""

import argparse
import json
import sys
import time
import pandas as pd
import numpy as np
from pathlib import Path

# Add the repo path to sys.path to import CycPeptMP modules
repo_path = Path(__file__).parent.parent / "repo" / "cycpeptmp"
sys.path.insert(0, str(repo_path))

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen
    from utils import utils_function
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure you have RDKit installed.")
    sys.exit(1)

def load_database_peptides(database_path="repo/cycpeptmp/data/CycPeptMPDB_Peptide_All.csv"):
    """Load the CycPeptMPDB database for comparison."""
    try:
        db_df = pd.read_csv(database_path, low_memory=False)
        print(f"Loaded CycPeptMPDB database with {len(db_df)} peptides")
        return db_df
    except FileNotFoundError:
        print(f"Database file not found: {database_path}")
        return None

def calculate_basic_properties(smiles_list):
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

def find_similar_peptides(query_smiles, database_df, similarity_threshold=0.8):
    """Find similar peptides in the database using Tanimoto similarity."""
    try:
        from rdkit import DataStructs
        from rdkit.Chem import rdMolDescriptors

        query_mol = Chem.MolFromSmiles(query_smiles)
        if not query_mol:
            return []

        query_fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(query_mol, 2, nBits=1024)

        similarities = []
        for idx, row in database_df.iterrows():
            try:
                db_mol = Chem.MolFromSmiles(row['SMILES'])
                if db_mol:
                    db_fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(db_mol, 2, nBits=1024)
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

    except ImportError:
        print("Warning: RDKit fingerprint modules not available for similarity search")
        return []

def analyze_diversity(smiles_list):
    """Analyze the chemical diversity of the peptide set."""
    try:
        from rdkit import DataStructs
        from rdkit.Chem import rdMolDescriptors

        fingerprints = []
        valid_smiles = []

        for smiles in smiles_list:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol:
                    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)
                    fingerprints.append(fp)
                    valid_smiles.append(smiles)
            except Exception:
                continue

        if len(fingerprints) < 2:
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

def generate_summary_statistics(results_df):
    """Generate summary statistics for the analysis."""
    summary = {}

    # Basic counts
    summary['total_peptides'] = len(results_df)
    summary['valid_smiles'] = results_df['valid'].sum() if 'valid' in results_df else 0

    if summary['valid_smiles'] > 0:
        valid_df = results_df[results_df['valid'] == True] if 'valid' in results_df else results_df

        # Molecular weight statistics
        if 'mw' in valid_df:
            summary['mw_mean'] = valid_df['mw'].mean()
            summary['mw_std'] = valid_df['mw'].std()
            summary['mw_min'] = valid_df['mw'].min()
            summary['mw_max'] = valid_df['mw'].max()

        # LogP statistics
        if 'logp' in valid_df:
            summary['logp_mean'] = valid_df['logp'].mean()
            summary['logp_std'] = valid_df['logp'].std()
            summary['logp_min'] = valid_df['logp'].min()
            summary['logp_max'] = valid_df['logp'].max()

        # TPSA statistics
        if 'tpsa' in valid_df:
            summary['tpsa_mean'] = valid_df['tpsa'].mean()
            summary['tpsa_std'] = valid_df['tpsa'].std()

        # Drug-likeness assessment
        if all(col in valid_df for col in ['mw', 'logp', 'hbd', 'hba']):
            # Lipinski's Rule of Five
            lipinski_violations = 0
            lipinski_violations += (valid_df['mw'] > 500).sum()
            lipinski_violations += (valid_df['logp'] > 5).sum()
            lipinski_violations += (valid_df['hbd'] > 5).sum()
            lipinski_violations += (valid_df['hba'] > 10).sum()

            summary['lipinski_compliant'] = len(valid_df) - lipinski_violations / 4
            summary['lipinski_compliance_rate'] = summary['lipinski_compliant'] / len(valid_df)

    return summary

def run_comprehensive_analysis(input_df, database_df=None, output_prefix="analysis"):
    """Run comprehensive analysis of the peptide dataset."""
    print("Starting comprehensive analysis...")
    start_time = time.time()

    results = {}

    # 1. Basic validation and properties
    print("1. Calculating molecular properties...")
    properties_df = calculate_basic_properties(input_df['SMILES'].tolist())

    # Merge with input data
    analysis_df = pd.concat([input_df.reset_index(drop=True), properties_df], axis=1)

    # 2. Summary statistics
    print("2. Generating summary statistics...")
    results['summary'] = generate_summary_statistics(analysis_df)

    # 3. Diversity analysis
    print("3. Analyzing chemical diversity...")
    diversity = analyze_diversity(input_df['SMILES'].tolist())
    results['diversity'] = diversity

    # 4. Database comparison (if available)
    if database_df is not None:
        print("4. Comparing with CycPeptMPDB database...")
        similar_peptides = []

        for idx, row in input_df.iterrows():
            smiles = row['SMILES']
            peptide_id = row.get('ID_org', f'peptide_{idx}')

            print(f"   Searching similarities for {peptide_id}...", end='')

            similarities = find_similar_peptides(smiles, database_df, similarity_threshold=0.7)

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
            results['similar_peptides'] = pd.DataFrame(similar_peptides)

    # 5. Save results
    print("5. Saving analysis results...")

    # Main analysis results
    analysis_df.to_csv(f"{output_prefix}_properties.csv", index=False)
    print(f"   Molecular properties saved to {output_prefix}_properties.csv")

    # Summary report
    with open(f"{output_prefix}_summary.json", 'w') as f:
        json.dump(results['summary'], f, indent=2, default=str)
    print(f"   Summary statistics saved to {output_prefix}_summary.json")

    # Similar peptides (if any)
    if 'similar_peptides' in results:
        results['similar_peptides'].to_csv(f"{output_prefix}_similarities.csv", index=False)
        print(f"   Similar peptides saved to {output_prefix}_similarities.csv")

    # Diversity report
    with open(f"{output_prefix}_diversity.json", 'w') as f:
        json.dump(diversity, f, indent=2, default=str)
    print(f"   Diversity analysis saved to {output_prefix}_diversity.json")

    elapsed = time.time() - start_time
    print(f"\nAnalysis completed in {elapsed:.1f} seconds")

    return results, analysis_df

def print_analysis_report(results, analysis_df):
    """Print a comprehensive analysis report."""
    print("\n" + "="*60)
    print("COMPREHENSIVE ANALYSIS REPORT")
    print("="*60)

    summary = results.get('summary', {})

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
    diversity = results.get('diversity', {})
    if 'diversity_score' in diversity:
        print(f"\nChemical Diversity:")
        print(f"  Diversity score: {diversity['diversity_score']:.3f} (0=identical, 1=completely diverse)")
        print(f"  Mean similarity: {diversity['mean_similarity']:.3f}")
        print(f"  Similarity range: {diversity['min_similarity']:.3f} - {diversity['max_similarity']:.3f}")

    # Similar peptides
    if 'similar_peptides' in results:
        similar_df = results['similar_peptides']
        print(f"\nDatabase Comparison:")
        print(f"  Found {len(similar_df)} similar peptides in CycPeptMPDB")

        # Show peptides with known permeability
        known_perm = similar_df.dropna(subset=['known_permeability'])
        if len(known_perm) > 0:
            print(f"  {len(known_perm)} have experimental permeability data")
            print(f"  Mean experimental LogP: {known_perm['known_permeability'].mean():.2f}")

def main():
    parser = argparse.ArgumentParser(description='Comprehensive batch analysis of cyclic peptides')
    parser.add_argument('--input', type=str, required=True,
                       help='Input CSV file with SMILES')
    parser.add_argument('--output', type=str, default='batch_analysis',
                       help='Output prefix for result files')
    parser.add_argument('--compare-with-database', action='store_true',
                       help='Compare with CycPeptMPDB database')
    parser.add_argument('--database-path', type=str,
                       default='repo/cycpeptmp/data/CycPeptMPDB_Peptide_All.csv',
                       help='Path to CycPeptMPDB database file')

    args = parser.parse_args()

    # Load input data
    print(f"Loading input data from {args.input}...")
    if not Path(args.input).exists():
        print(f"Error: Input file {args.input} not found")
        sys.exit(1)

    input_df = pd.read_csv(args.input)

    if 'SMILES' not in input_df.columns:
        print("Error: Input file must contain a 'SMILES' column")
        sys.exit(1)

    print(f"Loaded {len(input_df)} peptides for analysis")

    # Load database if requested
    database_df = None
    if args.compare_with_database:
        print("Loading CycPeptMPDB database...")
        database_df = load_database_peptides(args.database_path)

    # Run comprehensive analysis
    results, analysis_df = run_comprehensive_analysis(
        input_df, database_df, args.output
    )

    # Print report
    print_analysis_report(results, analysis_df)

    print(f"\nAll analysis results saved with prefix: {args.output}")

if __name__ == "__main__":
    main()