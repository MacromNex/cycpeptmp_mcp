"""
Shared library for cyclic peptide MCP scripts.

This library contains common functions extracted and simplified from repo code
to minimize dependencies while maintaining functionality.
"""

__version__ = "1.0.0"
__author__ = "CycPeptMCP Step 5 Extraction"

from .molecules import (
    canonicalize_smiles,
    validate_smiles_basic,
    calculate_molecular_properties,
    generate_molecular_fingerprint
)

from .io import (
    load_csv_with_validation,
    save_results_csv,
    load_json_config
)

from .validation import (
    validate_input_dataframe,
    validate_smiles_column,
    check_file_exists
)

__all__ = [
    # Molecules
    'canonicalize_smiles',
    'validate_smiles_basic',
    'calculate_molecular_properties',
    'generate_molecular_fingerprint',

    # I/O
    'load_csv_with_validation',
    'save_results_csv',
    'load_json_config',

    # Validation
    'validate_input_dataframe',
    'validate_smiles_column',
    'check_file_exists'
]