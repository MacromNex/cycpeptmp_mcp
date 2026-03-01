"""
Shared I/O functions for cyclic peptide MCP scripts.

File loading, saving, and validation utilities.
"""
import json
from pathlib import Path
from typing import Union, Dict, Any, List, Optional
import pandas as pd


def load_csv_with_validation(file_path: Union[str, Path], required_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Load CSV file with validation.

    Args:
        file_path: Path to CSV file
        required_columns: List of required column names (optional)

    Returns:
        DataFrame with validated data

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV file {file_path}: {e}")

    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

    return df


def save_results_csv(data: Union[pd.DataFrame, List[Dict[str, Any]]], file_path: Union[str, Path],
                    create_dirs: bool = True, index: bool = False) -> None:
    """
    Save results to CSV file.

    Args:
        data: DataFrame or list of dictionaries to save
        file_path: Output file path
        create_dirs: Whether to create parent directories
        index: Whether to include index in CSV
    """
    file_path = Path(file_path)

    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data

    try:
        df.to_csv(file_path, index=index)
    except Exception as e:
        raise ValueError(f"Error saving CSV to {file_path}: {e}")


def load_json_config(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON configuration file.

    Args:
        file_path: Path to JSON config file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file {file_path}: {e}")
    except Exception as e:
        raise ValueError(f"Error reading config file {file_path}: {e}")


def save_json_config(config: Dict[str, Any], file_path: Union[str, Path],
                    create_dirs: bool = True, indent: int = 2) -> None:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary
        file_path: Output file path
        create_dirs: Whether to create parent directories
        indent: JSON indentation
    """
    file_path = Path(file_path)

    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=indent, default=str)
    except Exception as e:
        raise ValueError(f"Error saving JSON config to {file_path}: {e}")


def check_file_exists(file_path: Union[str, Path], raise_error: bool = False) -> bool:
    """
    Check if file exists.

    Args:
        file_path: Path to check
        raise_error: Whether to raise FileNotFoundError if file doesn't exist

    Returns:
        True if file exists, False otherwise

    Raises:
        FileNotFoundError: If file doesn't exist and raise_error=True
    """
    file_path = Path(file_path)
    exists = file_path.exists()

    if not exists and raise_error:
        raise FileNotFoundError(f"File not found: {file_path}")

    return exists


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path.stat().st_size


def create_output_directory(output_path: Union[str, Path]) -> Path:
    """
    Create output directory if it doesn't exist.

    Args:
        output_path: Directory path to create

    Returns:
        Path object of created directory
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def list_files_with_extension(directory: Union[str, Path], extension: str) -> List[Path]:
    """
    List all files with specified extension in directory.

    Args:
        directory: Directory to search
        extension: File extension (e.g., '.csv', '.json')

    Returns:
        List of file paths with the specified extension
    """
    directory = Path(directory)

    if not directory.exists():
        return []

    if not extension.startswith('.'):
        extension = '.' + extension

    return list(directory.glob(f"*{extension}"))


def backup_file(file_path: Union[str, Path], backup_suffix: str = ".bak") -> Optional[Path]:
    """
    Create a backup copy of a file.

    Args:
        file_path: Path to file to backup
        backup_suffix: Suffix to add to backup file

    Returns:
        Path to backup file, or None if original doesn't exist
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return None

    backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)

    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception:
        return None