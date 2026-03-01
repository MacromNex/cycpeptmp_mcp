"""MCP Server for Cyclic Peptide Tools

Provides both synchronous and asynchronous (submit) APIs for all tools.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

# Import utilities and job manager
from utils import setup_script_paths, check_dependencies, format_error_response, validate_smiles_input, check_repo_availability
from jobs.manager import job_manager

# Setup paths
PATHS = setup_script_paths()

# Create MCP server
mcp = FastMCP("cycpep-tools")

# ==============================================================================
# Server Health and Information
# ==============================================================================

@mcp.tool()
def get_server_info() -> dict:
    """
    Get information about the CycPep MCP server and available tools.

    Returns:
        Dictionary with server version, available tools, and dependencies
    """
    missing_deps = check_dependencies()
    repo_available = check_repo_availability()

    return {
        "status": "success",
        "server": "cycpep-tools",
        "version": "1.0.0",
        "description": "Cyclic Peptide Computational Tools",
        "tools": {
            "sync": ["validate_cyclic_peptide", "convert_sequence_to_smiles", "calculate_peptide_properties"],
            "async": ["submit_structure_prediction", "submit_membrane_permeability", "submit_batch_analysis"],
            "job_management": ["get_job_status", "get_job_result", "get_job_log", "cancel_job", "list_jobs"]
        },
        "dependencies": {
            "missing": missing_deps,
            "repo_available": repo_available
        }
    }

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted cyclic peptide computation job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)

@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed cyclic peptide computation job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)

@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)

@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running cyclic peptide computation job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)

@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted cyclic peptide computation jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Synchronous Tools (for fast operations < 10 min)
# ==============================================================================

@mcp.tool()
def validate_cyclic_peptide(
    smiles: str,
    output_file: Optional[str] = None
) -> dict:
    """
    Validate a cyclic peptide SMILES string and calculate molecular properties.

    Fast operation - returns results immediately.

    Args:
        smiles: SMILES string of the cyclic peptide to validate
        output_file: Optional path to save validation results as CSV

    Returns:
        Dictionary with validation results and molecular properties
    """
    try:
        # Validate input
        validation = validate_smiles_input(smiles)
        if not validation["valid"]:
            return {"status": "error", "error": validation["error"]}

        # Import and run validation
        from validate_peptide import run_validate_peptide

        result = run_validate_peptide(
            smiles=smiles,
            output_file=output_file
        )
        return {"status": "success", **result}

    except ImportError as e:
        return format_error_response(e, "Failed to import validation script")
    except Exception as e:
        return format_error_response(e, "Validation failed")

@mcp.tool()
def calculate_peptide_properties(
    input_file: Optional[str] = None,
    smiles: Optional[str] = None,
    output_file: Optional[str] = None
) -> dict:
    """
    Calculate molecular properties for cyclic peptides.

    Can process either a single SMILES string or a CSV file with multiple peptides.
    Fast operation for small datasets.

    Args:
        input_file: Path to CSV file with SMILES column (optional)
        smiles: Single SMILES string (optional - use this OR input_file)
        output_file: Path to save results as CSV (optional)

    Returns:
        Dictionary with calculated properties
    """
    try:
        if not input_file and not smiles:
            return {"status": "error", "error": "Either input_file or smiles must be provided"}

        if smiles:
            validation = validate_smiles_input(smiles)
            if not validation["valid"]:
                return {"status": "error", "error": validation["error"]}

        # Use validate_peptide script for properties (it includes property calculation)
        from validate_peptide import run_validate_peptide

        result = run_validate_peptide(
            input_file=input_file,
            smiles=smiles,
            output_file=output_file
        )
        return {"status": "success", **result}

    except FileNotFoundError as e:
        return format_error_response(e, "Input file not found")
    except Exception as e:
        return format_error_response(e, "Property calculation failed")

@mcp.tool()
def convert_sequence_to_smiles(
    sequence: str,
    cyclization_type: str = "head_to_tail",
    output_file: Optional[str] = None
) -> dict:
    """
    Convert a peptide sequence to cyclic peptide SMILES.

    Args:
        sequence: Amino acid sequence using one-letter codes (e.g., "ACDEFGHIK")
        cyclization_type: Type of cyclization (head_to_tail, disulfide, sidechain)
        output_file: Optional path to save the SMILES result

    Returns:
        Dictionary with generated SMILES and cyclization information
    """
    try:
        # Basic sequence validation
        if not sequence:
            return {"status": "error", "error": "Empty sequence"}

        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        invalid_chars = set(sequence.upper()) - valid_aa
        if invalid_chars:
            return {"status": "error", "error": f"Invalid amino acid codes: {invalid_chars}"}

        # For now, return a placeholder response since sequence_to_smiles script wasn't in Step 5
        # This would need the actual script implementation
        result = {
            "sequence": sequence.upper(),
            "cyclization_type": cyclization_type,
            "smiles": f"[Placeholder SMILES for {sequence}]",
            "message": "Sequence to SMILES conversion is a placeholder - requires implementation"
        }

        if output_file:
            import json
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            result["output_file"] = output_file

        return {"status": "success", **result}

    except Exception as e:
        return format_error_response(e, "Sequence conversion failed")

# ==============================================================================
# Submit Tools (for long-running operations > 10 min)
# ==============================================================================

@mcp.tool()
def submit_membrane_permeability(
    smiles: str,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a membrane permeability prediction job for a cyclic peptide.

    This task typically takes 3+ minutes and uses the full CycPeptMP pipeline.
    Returns a job_id for tracking progress.

    Args:
        smiles: SMILES string of the cyclic peptide
        output_dir: Directory to save prediction outputs (optional)
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs
    """
    try:
        # Validate input
        validation = validate_smiles_input(smiles)
        if not validation["valid"]:
            return {"status": "error", "error": validation["error"]}

        # Check if repo is available
        if not check_repo_availability():
            return {
                "status": "error",
                "error": "CycPeptMP repository not available. Membrane permeability prediction requires the full repo."
            }

        script_path = str(SCRIPTS_DIR / "predict_membrane_permeability.py")

        return job_manager.submit_job(
            script_path=script_path,
            args={
                "smiles": smiles,
                "output_dir": output_dir
            },
            job_name=job_name or f"permeability_{smiles[:20]}"
        )

    except Exception as e:
        return format_error_response(e, "Failed to submit permeability job")

@mcp.tool()
def submit_batch_analysis(
    input_file: str,
    output_prefix: str = "batch_analysis",
    database_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a comprehensive batch analysis job for multiple cyclic peptides.

    For large datasets (>100 peptides), this should be run as a background job.
    Includes molecular properties, diversity analysis, and optional similarity search.

    Args:
        input_file: Path to CSV file with SMILES column
        output_prefix: Prefix for output files
        database_file: Optional database CSV for similarity comparison
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking the batch analysis
    """
    try:
        # Validate input file exists
        if not Path(input_file).exists():
            return {"status": "error", "error": f"Input file not found: {input_file}"}

        script_path = str(SCRIPTS_DIR / "batch_analysis.py")

        args = {
            "input": input_file,
            "output": output_prefix
        }

        if database_file:
            if not Path(database_file).exists():
                return {"status": "error", "error": f"Database file not found: {database_file}"}
            args["database"] = database_file

        return job_manager.submit_job(
            script_path=script_path,
            args=args,
            job_name=job_name or f"batch_{Path(input_file).stem}"
        )

    except Exception as e:
        return format_error_response(e, "Failed to submit batch analysis job")

@mcp.tool()
def submit_structure_prediction(
    smiles: str,
    num_conformers: int = 10,
    optimize: bool = True,
    output_format: str = "pdb",
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a 3D structure prediction job for a cyclic peptide.

    This task may take 10+ minutes depending on peptide size and conformer count.
    Generates multiple 3D conformers and optionally optimizes them.

    Args:
        smiles: SMILES string of the cyclic peptide
        num_conformers: Number of conformers to generate (default: 10)
        optimize: Whether to energy-minimize structures (default: True)
        output_format: Output format (pdb, sdf, mol2)
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking structure prediction
    """
    try:
        # Validate input
        validation = validate_smiles_input(smiles)
        if not validation["valid"]:
            return {"status": "error", "error": validation["error"]}

        # For now, return a placeholder since we don't have a structure prediction script
        # This would require implementing the actual 3D generation script
        return {
            "status": "error",
            "error": "Structure prediction not implemented yet. Would require 3D conformation generation script."
        }

    except Exception as e:
        return format_error_response(e, "Failed to submit structure prediction job")

# ==============================================================================
# Utility Tools
# ==============================================================================

@mcp.tool()
def cleanup_old_jobs(days_old: int = 7) -> dict:
    """
    Clean up job files older than specified days to free disk space.

    Args:
        days_old: Number of days to keep job files (default: 7)

    Returns:
        Dictionary with cleanup results
    """
    try:
        result = job_manager.cleanup_old_jobs(days_old)
        return result
    except Exception as e:
        return format_error_response(e, "Job cleanup failed")

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    # Check dependencies at startup
    missing_deps = check_dependencies()
    if missing_deps:
        logger.warning(f"Missing dependencies: {missing_deps}")
        logger.warning("Some tools may not work properly")

    logger.info("Starting CycPep MCP Server...")
    logger.info(f"Scripts directory: {SCRIPTS_DIR}")
    logger.info(f"Repository available: {check_repo_availability()}")

    mcp.run()