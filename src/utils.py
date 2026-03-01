"""
Shared utilities for MCP server and tools
"""

import sys
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def setup_script_paths():
    """Setup paths to access scripts and shared libraries."""
    mcp_root = Path(__file__).parent.parent
    scripts_dir = mcp_root / "scripts"

    # Add paths to Python path for imports
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    if str(scripts_dir / "lib") not in sys.path:
        sys.path.insert(0, str(scripts_dir / "lib"))

    return {
        "mcp_root": mcp_root,
        "scripts_dir": scripts_dir,
        "configs_dir": mcp_root / "configs",
        "examples_dir": mcp_root / "examples"
    }

def check_dependencies():
    """Check if required dependencies are available."""
    missing = []

    try:
        import pandas
    except ImportError:
        missing.append("pandas")

    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    try:
        from rdkit import Chem
    except ImportError:
        missing.append("rdkit")

    return missing

def format_error_response(error: Exception, context: str = "") -> Dict[str, Any]:
    """Format error into standardized response."""
    error_type = type(error).__name__
    error_msg = str(error)

    if context:
        error_msg = f"{context}: {error_msg}"

    logger.error(f"{error_type}: {error_msg}")

    return {
        "status": "error",
        "error_type": error_type,
        "error": error_msg
    }

def validate_smiles_input(smiles: str) -> Dict[str, Any]:
    """Basic SMILES validation before processing."""
    if not smiles:
        return {"valid": False, "error": "Empty SMILES string"}

    if len(smiles) > 10000:  # Reasonable length limit
        return {"valid": False, "error": "SMILES string too long"}

    # Basic character validation
    invalid_chars = set(smiles) - set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()[]@+-=#+/\\.")
    if invalid_chars:
        return {"valid": False, "error": f"Invalid characters in SMILES: {invalid_chars}"}

    return {"valid": True}

def check_repo_availability() -> bool:
    """Check if the full CycPeptMP repository is available."""
    try:
        mcp_root = Path(__file__).parent.parent
        repo_path = mcp_root / "repo" / "cycpeptmp"
        return repo_path.exists() and (repo_path / "__init__.py").exists()
    except Exception:
        return False