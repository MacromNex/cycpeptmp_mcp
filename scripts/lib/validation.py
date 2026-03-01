"""
Shared validation functions for cyclic peptide MCP scripts.

Input validation and data checking utilities.
"""
from pathlib import Path
from typing import Union, List, Optional, Dict, Any
import pandas as pd

from .molecules import validate_smiles_basic


def validate_input_dataframe(df: pd.DataFrame, required_columns: List[str],
                           min_rows: int = 1) -> Dict[str, Any]:
    """
    Validate input DataFrame structure and content.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        min_rows: Minimum number of rows required

    Returns:
        Dictionary with validation results
    """
    validation = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'row_count': len(df),
        'column_count': len(df.columns)
    }

    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        validation['valid'] = False
        validation['errors'].append(f"Missing required columns: {missing_columns}")

    # Check minimum rows
    if len(df) < min_rows:
        validation['valid'] = False
        validation['errors'].append(f"DataFrame has {len(df)} rows, minimum {min_rows} required")

    # Check for empty DataFrame
    if df.empty:
        validation['valid'] = False
        validation['errors'].append("DataFrame is empty")

    # Check for duplicate columns
    duplicate_columns = df.columns[df.columns.duplicated()].tolist()
    if duplicate_columns:
        validation['warnings'].append(f"Duplicate column names: {duplicate_columns}")

    return validation


def validate_smiles_column(df: pd.DataFrame, smiles_column: str = 'SMILES',
                          min_valid_ratio: float = 0.8) -> Dict[str, Any]:
    """
    Validate SMILES column in DataFrame.

    Args:
        df: DataFrame containing SMILES
        smiles_column: Name of SMILES column
        min_valid_ratio: Minimum ratio of valid SMILES required

    Returns:
        Dictionary with validation results
    """
    validation = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'total_smiles': 0,
        'valid_smiles': 0,
        'invalid_smiles': 0,
        'valid_ratio': 0.0,
        'invalid_indices': []
    }

    if smiles_column not in df.columns:
        validation['valid'] = False
        validation['errors'].append(f"SMILES column '{smiles_column}' not found")
        return validation

    smiles_series = df[smiles_column].dropna()
    validation['total_smiles'] = len(smiles_series)

    if validation['total_smiles'] == 0:
        validation['valid'] = False
        validation['errors'].append(f"No SMILES found in column '{smiles_column}'")
        return validation

    # Validate each SMILES
    valid_count = 0
    invalid_indices = []

    for idx, smiles in smiles_series.items():
        if isinstance(smiles, str) and validate_smiles_basic(smiles):
            valid_count += 1
        else:
            invalid_indices.append(idx)

    validation['valid_smiles'] = valid_count
    validation['invalid_smiles'] = len(invalid_indices)
    validation['invalid_indices'] = invalid_indices
    validation['valid_ratio'] = valid_count / validation['total_smiles']

    # Check minimum valid ratio
    if validation['valid_ratio'] < min_valid_ratio:
        validation['valid'] = False
        validation['errors'].append(
            f"Only {validation['valid_ratio']:.1%} of SMILES are valid "
            f"(minimum {min_valid_ratio:.1%} required)"
        )

    # Warnings for invalid SMILES
    if validation['invalid_smiles'] > 0:
        validation['warnings'].append(
            f"{validation['invalid_smiles']} invalid SMILES found "
            f"(rows: {invalid_indices[:5]}{'...' if len(invalid_indices) > 5 else ''})"
        )

    return validation


def check_file_exists(file_path: Union[str, Path], file_type: str = "file") -> Dict[str, Any]:
    """
    Check if file exists and is accessible.

    Args:
        file_path: Path to check
        file_type: Type description for error messages

    Returns:
        Dictionary with check results
    """
    validation = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'path': str(file_path),
        'exists': False,
        'readable': False,
        'size_bytes': 0
    }

    file_path = Path(file_path)
    validation['exists'] = file_path.exists()

    if not validation['exists']:
        validation['valid'] = False
        validation['errors'].append(f"{file_type.capitalize()} not found: {file_path}")
        return validation

    # Check readability
    try:
        validation['readable'] = file_path.is_file() and os.access(file_path, os.R_OK)
    except Exception:
        validation['readable'] = False

    if not validation['readable']:
        validation['valid'] = False
        validation['errors'].append(f"{file_type.capitalize()} is not readable: {file_path}")

    # Get file size
    try:
        validation['size_bytes'] = file_path.stat().st_size
        if validation['size_bytes'] == 0:
            validation['warnings'].append(f"{file_type.capitalize()} is empty")
    except Exception:
        validation['warnings'].append(f"Could not determine {file_type} size")

    return validation


def validate_output_path(output_path: Union[str, Path], create_dirs: bool = True) -> Dict[str, Any]:
    """
    Validate output path and create directories if needed.

    Args:
        output_path: Path for output file
        create_dirs: Whether to create parent directories

    Returns:
        Dictionary with validation results
    """
    validation = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'path': str(output_path),
        'parent_exists': False,
        'parent_writable': False,
        'created_dirs': False
    }

    output_path = Path(output_path)
    parent_dir = output_path.parent

    validation['parent_exists'] = parent_dir.exists()

    if not validation['parent_exists'] and create_dirs:
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
            validation['parent_exists'] = True
            validation['created_dirs'] = True
        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f"Could not create output directory {parent_dir}: {e}")
            return validation

    if validation['parent_exists']:
        try:
            import os
            validation['parent_writable'] = os.access(parent_dir, os.W_OK)
        except Exception:
            validation['parent_writable'] = False

        if not validation['parent_writable']:
            validation['valid'] = False
            validation['errors'].append(f"Output directory is not writable: {parent_dir}")

    # Check if file already exists
    if output_path.exists():
        validation['warnings'].append(f"Output file already exists and will be overwritten: {output_path}")

    return validation


def validate_config_dict(config: Dict[str, Any], required_keys: List[str],
                        optional_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate configuration dictionary.

    Args:
        config: Configuration dictionary to validate
        required_keys: List of required keys
        optional_keys: List of optional keys (for completeness checking)

    Returns:
        Dictionary with validation results
    """
    validation = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'missing_required': [],
        'extra_keys': [],
        'total_keys': len(config)
    }

    # Check required keys
    missing_required = [key for key in required_keys if key not in config]
    if missing_required:
        validation['valid'] = False
        validation['missing_required'] = missing_required
        validation['errors'].append(f"Missing required config keys: {missing_required}")

    # Check for extra keys (if optional_keys provided)
    if optional_keys is not None:
        allowed_keys = set(required_keys + optional_keys)
        extra_keys = [key for key in config.keys() if key not in allowed_keys]
        if extra_keys:
            validation['extra_keys'] = extra_keys
            validation['warnings'].append(f"Unknown config keys: {extra_keys}")

    # Check for None values in required keys
    none_values = [key for key in required_keys if config.get(key) is None]
    if none_values:
        validation['warnings'].append(f"Required config keys with None values: {none_values}")

    return validation


def summarize_validation_results(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Summarize multiple validation results.

    Args:
        validations: List of validation result dictionaries

    Returns:
        Summary dictionary
    """
    summary = {
        'total_validations': len(validations),
        'all_valid': True,
        'total_errors': 0,
        'total_warnings': 0,
        'error_summary': [],
        'warning_summary': []
    }

    all_errors = []
    all_warnings = []

    for validation in validations:
        if not validation.get('valid', True):
            summary['all_valid'] = False

        errors = validation.get('errors', [])
        warnings = validation.get('warnings', [])

        all_errors.extend(errors)
        all_warnings.extend(warnings)

    summary['total_errors'] = len(all_errors)
    summary['total_warnings'] = len(all_warnings)

    # Summarize unique errors and warnings
    from collections import Counter
    error_counts = Counter(all_errors)
    warning_counts = Counter(all_warnings)

    summary['error_summary'] = [
        {'message': error, 'count': count}
        for error, count in error_counts.most_common()
    ]

    summary['warning_summary'] = [
        {'message': warning, 'count': count}
        for warning, count in warning_counts.most_common()
    ]

    return summary


# Import os for file permission checks
import os