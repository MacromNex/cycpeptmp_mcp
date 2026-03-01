"""
Shared molecular manipulation functions for cyclic peptide MCP scripts.

These are extracted and simplified from repo code to minimize dependencies.
"""
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors
    from rdkit import DataStructs
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


def canonicalize_smiles(smiles: str) -> Optional[str]:
    """
    Canonicalize SMILES string using RDKit.
    Extracted from repo/cycpeptmp/utils/utils_function.py
    """
    if not RDKIT_AVAILABLE:
        raise ImportError("RDKit is required for SMILES canonicalization")

    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol)
    except Exception:
        return None


def validate_smiles_basic(smiles: str) -> bool:
    """Basic SMILES validation using RDKit."""
    if not RDKIT_AVAILABLE:
        return False

    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None
    except Exception:
        return False


def calculate_molecular_properties(mol: Chem.Mol) -> Dict[str, Any]:
    """
    Calculate comprehensive molecular properties.
    Extracted and simplified from use case scripts.
    """
    if not RDKIT_AVAILABLE:
        raise ImportError("RDKit is required for molecular property calculation")

    try:
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
            'aromatic_rings': Descriptors.NumAromaticRings(mol),
            'formal_charge': Chem.rdmolops.GetFormalCharge(mol),
            'fraction_csp3': Descriptors.FractionCsp3(mol)
        }
    except Exception as e:
        raise ValueError(f"Error calculating molecular properties: {e}")


def generate_molecular_fingerprint(mol: Chem.Mol, radius: int = 2, n_bits: int = 1024):
    """
    Generate Morgan fingerprint for a molecule.
    Used for similarity calculations.
    """
    if not RDKIT_AVAILABLE:
        raise ImportError("RDKit is required for fingerprint generation")

    try:
        return rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
    except Exception as e:
        raise ValueError(f"Error generating fingerprint: {e}")


def calculate_tanimoto_similarity(mol1: Chem.Mol, mol2: Chem.Mol, radius: int = 2, n_bits: int = 1024) -> float:
    """Calculate Tanimoto similarity between two molecules."""
    if not RDKIT_AVAILABLE:
        raise ImportError("RDKit is required for similarity calculation")

    try:
        fp1 = generate_molecular_fingerprint(mol1, radius, n_bits)
        fp2 = generate_molecular_fingerprint(mol2, radius, n_bits)
        return DataStructs.TanimotoSimilarity(fp1, fp2)
    except Exception as e:
        raise ValueError(f"Error calculating similarity: {e}")


def is_cyclic_peptide(mol: Chem.Mol) -> bool:
    """
    Check if molecule is a cyclic peptide.
    Basic heuristic checks.
    """
    if not RDKIT_AVAILABLE:
        return False

    try:
        # Check for ring structure
        ring_info = mol.GetRingInfo()
        if ring_info.NumRings() == 0:
            return False

        # Check for peptide-like elements (N, O, C should be present)
        atom_counts = {}
        for atom in mol.GetAtoms():
            symbol = atom.GetSymbol()
            atom_counts[symbol] = atom_counts.get(symbol, 0) + 1

        # Basic requirements for peptides
        has_nitrogen = 'N' in atom_counts and atom_counts['N'] >= 2
        has_oxygen = 'O' in atom_counts and atom_counts['O'] >= 2
        has_carbon = 'C' in atom_counts

        return has_nitrogen and has_oxygen and has_carbon

    except Exception:
        return False


def smiles_to_mol(smiles: str) -> Optional[Chem.Mol]:
    """Convert SMILES string to RDKit molecule object."""
    if not RDKIT_AVAILABLE:
        raise ImportError("RDKit is required for SMILES parsing")

    try:
        return Chem.MolFromSmiles(smiles)
    except Exception:
        return None


def mol_to_smiles(mol: Chem.Mol, canonical: bool = True) -> str:
    """Convert RDKit molecule to SMILES string."""
    if not RDKIT_AVAILABLE:
        raise ImportError("RDKit is required for SMILES generation")

    try:
        if canonical:
            return Chem.MolToSmiles(mol)
        else:
            return Chem.MolToSmiles(mol, canonical=False)
    except Exception as e:
        raise ValueError(f"Error converting molecule to SMILES: {e}")


def check_rdkit_available() -> bool:
    """Check if RDKit is available for import."""
    return RDKIT_AVAILABLE


def get_atom_counts(mol: Chem.Mol) -> Dict[str, int]:
    """Get count of each atom type in the molecule."""
    if not RDKIT_AVAILABLE:
        raise ImportError("RDKit is required for atom counting")

    atom_counts = {}
    for atom in mol.GetAtoms():
        symbol = atom.GetSymbol()
        atom_counts[symbol] = atom_counts.get(symbol, 0) + 1

    return atom_counts