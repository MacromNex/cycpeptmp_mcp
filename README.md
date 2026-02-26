# CycPeptMP MCP

> Cyclic Peptide Computational Tools - MCP server for cyclic peptide analysis, property calculation, and membrane permeability prediction

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

The CycPeptMP MCP provides comprehensive computational tools for cyclic peptide research and drug discovery. Built on the CycPeptMP (Cyclic Peptide Membrane Permeability) framework, it offers both fast property calculations and advanced machine learning predictions through an intuitive MCP interface.

### Features
- **Molecular Property Calculation**: Compute drug-like properties, molecular descriptors, and Lipinski's Rule of Five compliance
- **SMILES Validation**: Validate and canonicalize cyclic peptide SMILES structures with cyclicity detection
- **Membrane Permeability Prediction**: ML-based permeability prediction using deep learning models with multi-level molecular features
- **Batch Analysis**: High-throughput analysis for virtual screening with chemical diversity assessment
- **3D Structure Prediction**: Generate multiple 3D conformers with energy optimization (planned)
- **Database Similarity Search**: Compare against cyclic peptide databases using molecular fingerprints

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment (Python 3.10)
├── env_py39/              # Legacy environment (Python 3.9, for CycPeptMP)
├── src/
│   ├── server.py          # MCP server with 13 tools
│   ├── utils.py           # Shared utilities and helpers
│   └── jobs/              # Job management for async operations
├── scripts/
│   ├── validate_peptide.py           # SMILES validation and properties
│   ├── batch_analysis.py             # Comprehensive batch analysis
│   ├── predict_membrane_permeability.py  # ML-based permeability prediction
│   └── lib/                          # Shared utilities
│       ├── molecules.py              # RDKit molecular operations
│       ├── io.py                     # File I/O functions
│       └── validation.py             # Input validation
├── examples/
│   └── data/               # Demo data
│       ├── sequences/      # Sample cyclic peptide SMILES
│       │   └── new_data.csv           # Anidulafungin & Pasireotide samples
│       ├── models/         # Pre-trained CycPeptMP model weights
│       └── CycPeptMP.json  # Model configuration
├── configs/                # Configuration files
│   ├── default_config.json            # Default settings
│   ├── validate_peptide_config.json   # Validation configuration
│   ├── batch_analysis_config.json     # Analysis configuration
│   └── predict_membrane_permeability_config.json  # ML pipeline config
└── jobs/                   # Job storage (created at runtime)
```

---

## Installation

### Quick Setup

Run the automated setup script:

```bash
./quick_setup.sh
```

This will create both environments (Python 3.10 for MCP server and Python 3.9 for CycPeptMP core) and install all dependencies automatically.

### Manual Setup (Advanced)

For manual installation or customization, follow these steps.

#### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+ for MCP server
- Python 3.9 for full CycPeptMP functionality
- RDKit (installed automatically)

#### Create Environment

Following the dual environment setup from `reports/step3_environment.md`:

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cycpeptmp_mcp

# Detect package manager (prefer mamba over conda)
if command -v mamba &> /dev/null; then
    PKG_MGR="mamba"
else
    PKG_MGR="conda"
fi
echo "Using package manager: $PKG_MGR"

# Create main MCP environment (Python 3.10)
$PKG_MGR create -p ./env python=3.10 pip -y

# Activate main environment
$PKG_MGR activate ./env

# Install MCP dependencies
pip install fastmcp loguru click pandas numpy tqdm

# Install RDKit from conda-forge
$PKG_MGR install -c conda-forge rdkit matplotlib-base pillow sqlalchemy

# Force reinstall FastMCP for clean installation
pip install --force-reinstall --no-cache-dir fastmcp

# Create legacy environment for CycPeptMP (Python 3.9)
$PKG_MGR create -p ./env_py39 python=3.9 pip -y

# Activate legacy environment
$PKG_MGR activate ./env_py39

# Install CycPeptMP dependencies with exact versions
pip install numpy==1.25.0 pandas==1.4.4 torch==2.0.0

# Install RDKit and Mordred
$PKG_MGR install -c conda-forge rdkit
pip install mordred

# Return to main environment for MCP server
$PKG_MGR activate ./env
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Environment | Example |
|--------|-------------|-------------|---------|
| `validate_peptide.py` | Validate SMILES and calculate molecular properties | `./env` or `./env_py39` | See below |
| `batch_analysis.py` | Comprehensive analysis with diversity metrics | `./env` or `./env_py39` | See below |
| `predict_membrane_permeability.py` | ML-based permeability prediction | `./env_py39` (requires repo) | See below |

### Script Examples

#### Validate Cyclic Peptide

```bash
# Activate environment
mamba activate ./env

# Validate single SMILES
python scripts/validate_peptide.py \
  --smiles "NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O" \
  --output results/validation.csv

# Validate batch file
python scripts/validate_peptide.py \
  --input examples/data/sequences/new_data.csv \
  --output results/batch_validation.csv
```

**Parameters:**
- `--smiles, -s`: Cyclic peptide SMILES string (required for single validation)
- `--input, -i`: Input CSV file with SMILES column (required for batch)
- `--output, -o`: Output CSV file path (optional)
- `--config`: Configuration file path (optional)

#### Calculate Properties and Analyze Diversity

```bash
# Comprehensive batch analysis
python scripts/batch_analysis.py \
  --input examples/data/sequences/new_data.csv \
  --output results/analysis \
  --similarity-threshold 0.8

# With database comparison (if available)
python scripts/batch_analysis.py \
  --input examples/data/sequences/new_data.csv \
  --output results/analysis \
  --database-path database/cycpeptmpdb.csv
```

**Parameters:**
- `--input, -i`: Input CSV file with SMILES column (required)
- `--output, -o`: Output file prefix (default: "analysis")
- `--database-path`: Database CSV for similarity comparison (optional)
- `--similarity-threshold`: Tanimoto similarity threshold (default: 0.7)

#### Predict Membrane Permeability

```bash
# Activate legacy environment (requires CycPeptMP repository)
mamba activate ./env_py39

# Predict permeability for single peptide
python scripts/predict_membrane_permeability.py \
  --smiles "NCCCC[C@@H]1NC(=O)..." \
  --output results/permeability.csv

# Predict for batch
python scripts/predict_membrane_permeability.py \
  --input examples/data/sequences/new_data.csv \
  --output results/batch_permeability.csv
```

**Note:** This script requires the full CycPeptMP repository and pre-trained models.

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Activate main environment
mamba activate ./env

# Install MCP server for Claude Code
fastmcp install src/server.py --name cycpep-tools

# Verify installation
fastmcp list
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add cycpep-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
# Should show: cycpep-tools: ... - ✓ Connected
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "cycpep-tools": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cycpeptmp_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cycpeptmp_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from cycpep-tools?
```

#### Property Calculation (Fast - Sync API)
```
Calculate molecular properties for this cyclic peptide: NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O
```

#### Structure Validation
```
Validate this cyclic peptide SMILES and tell me if it's drug-like: CCCCCOc1ccc(-c2ccc(-c3ccc(C(=O)N[C@H]4C[C@@H](O)[C@@H](O)NC(=O)[C@@H]5[C@@H](O)[C@@H](C)CN5C(=O)[C@H]([C@@H](C)O)NC(=O)[C@H]([C@H](O)[C@@H](O)c5ccc(O)cc5)NC(=O)[C@@H]5C[C@@H](O)CN5C(=O)[C@H]([C@@H](C)O)NC4=O)cc3)cc2)cc1
```

#### Membrane Permeability Prediction (Submit API)
```
Submit a membrane permeability prediction job for the cyclic peptide Pasireotide with this SMILES: NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O
```

#### Check Job Status
```
Check the status of job abc12345
```

#### Batch Processing
```
Process the cyclic peptides in @examples/data/sequences/new_data.csv and generate a comprehensive analysis including molecular properties and diversity metrics
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/sequences/new_data.csv` | Reference sample SMILES file |
| `@configs/validate_peptide_config.json` | Reference validation config |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "cycpep-tools": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cycpeptmp_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cycpeptmp_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available from cycpep-tools?
> Calculate properties for cyclic peptide with SMILES "NCCCC[C@@H]1NC(=O)..."
> Submit batch analysis for my peptide library
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `validate_cyclic_peptide` | Validate SMILES and calculate molecular properties | `smiles: str`, `output_file: str` (optional) |
| `calculate_peptide_properties` | Calculate molecular properties for single peptides or CSV files | `input_file: str` OR `smiles: str`, `output_file: str` (optional) |
| `convert_sequence_to_smiles` | Convert amino acid sequence to cyclic SMILES | `sequence: str`, `cyclization_type: str` (default: "head_to_tail") |
| `get_server_info` | Get server version and available tools | None |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_membrane_permeability` | Predict membrane permeability using ML | `smiles: str`, `output_dir: str` (optional), `job_name: str` (optional) |
| `submit_batch_analysis` | Comprehensive analysis for large datasets | `input_file: str`, `output_prefix: str`, `database_file: str` (optional) |
| `submit_structure_prediction` | Generate 3D conformers (placeholder) | `smiles: str`, `num_conformers: int`, `optimize: bool` |

### Job Management Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_job_status` | Check job progress | `job_id: str` |
| `get_job_result` | Get results when completed | `job_id: str` |
| `get_job_log` | View execution logs | `job_id: str`, `tail: int` (default: 50) |
| `cancel_job` | Cancel running job | `job_id: str` |
| `list_jobs` | List all jobs | `status: str` (optional filter) |
| `cleanup_old_jobs` | Clean up old job files | `days_old: int` (default: 7) |

---

## Examples

### Example 1: Quick Property Calculation

**Goal:** Calculate drug-like properties for a cyclic peptide

**Using Script:**
```bash
mamba activate ./env
python scripts/validate_peptide.py \
  --smiles "NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O" \
  --output results/properties.csv
```

**Using MCP (in Claude Code):**
```
Calculate molecular properties for Pasireotide: NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O

Tell me the molecular weight, LogP, TPSA, and whether it's drug-like according to Lipinski's Rule of Five.
```

**Expected Output:**
- Molecular weight: 1047.23 Da
- LogP: 3.37
- TPSA: 281.2 Ų
- Lipinski compliance: Partial (MW > 500, but acceptable for cyclic peptides)
- Cyclicity: True

### Example 2: Batch Virtual Screening

**Goal:** Screen a library of cyclic peptides for drug-likeness and diversity

**Using Script:**
```bash
mamba activate ./env
python scripts/batch_analysis.py \
  --input examples/data/sequences/new_data.csv \
  --output results/virtual_screen \
  --similarity-threshold 0.7
```

**Using MCP (in Claude Code):**
```
I want to screen these cyclic peptides for oral bioavailability using @examples/data/sequences/new_data.csv:

Calculate properties for all peptides and identify which ones have:
- Molecular weight < 1000 Da
- LogP between -2 and 5
- TPSA < 250 Ų
- Chemical diversity > 0.5

Also generate a diversity analysis and summary statistics.
```

**Expected Output:**
- Properties table with MW, LogP, TPSA for each peptide
- Drug-likeness assessment for each peptide
- Diversity score: ~0.77 (high diversity)
- Summary statistics: Mean MW = 1093.7 Da, 25% Lipinski compliance

### Example 3: Membrane Permeability Prediction

**Goal:** Predict membrane permeability using deep learning

**Using Script:**
```bash
# Requires CycPeptMP repository and ./env_py39
mamba activate ./env_py39
python scripts/predict_membrane_permeability.py \
  --smiles "NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)..." \
  --output results/permeability.csv
```

**Using MCP (in Claude Code):**
```
Submit membrane permeability prediction for Pasireotide with job name "pasireotide_permeability":

SMILES: NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O

Check the job status every minute and show me the results when complete.
```

**Note:** This requires the full CycPeptMP repository with pre-trained models.

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With | Content |
|------|-------------|----------|---------|
| `sequences/new_data.csv` | Sample cyclic peptides | All property tools | Anidulafungin, Pasireotide |
| `CycPeptMP.json` | Model configuration | Permeability prediction | Hyperparameters, paths |
| `models/Fusion/` | Pre-trained models | Permeability prediction | 9 model files (~450MB) |

### Sample Data Details

**new_data.csv contains:**
- **Anidulafungin**: MW=1140.22 Da, LogP=-0.93, Antifungal cyclic peptide
- **Pasireotide**: MW=1047.23 Da, LogP=3.37, Somatostatin analog

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Key Parameters |
|--------|-------------|----------------|
| `default_config.json` | Default settings for all scripts | timeout, validation, output format |
| `validate_peptide_config.json` | Validation thresholds | MW warnings, cyclicity checks |
| `batch_analysis_config.json` | Analysis parameters | similarity thresholds, diversity metrics |
| `predict_membrane_permeability_config.json` | ML pipeline config | device settings, CycPeptMP paths |

### Config Example

```json
{
  "molecular_weight": {
    "min_warning": 500,
    "max_warning": 2000
  },
  "validation": {
    "check_cyclicity": true,
    "check_peptide_elements": true
  },
  "similarity": {
    "threshold": 0.7,
    "fingerprint": { "radius": 2, "n_bits": 1024 }
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate main environment
mamba create -p ./env python=3.10 -y
mamba activate ./env
pip install fastmcp loguru pandas numpy
mamba install -c conda-forge rdkit

# Recreate legacy environment
mamba create -p ./env_py39 python=3.9 -y
mamba activate ./env_py39
pip install numpy==1.25.0 pandas==1.4.4 torch==2.0.0
mamba install -c conda-forge rdkit
pip install mordred
```

**Problem:** RDKit import errors
```bash
# Install RDKit from conda-forge (not pip)
mamba install -c conda-forge rdkit -y
```

**Problem:** FastMCP import errors
```bash
# Force reinstall FastMCP
pip install --force-reinstall --no-cache-dir fastmcp
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove cycpep-tools
claude mcp add cycpep-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify connection
# Should show: cycpep-tools: ... - ✓ Connected
```

**Problem:** Permission denied when using tools
```
This is normal security behavior. Claude Code will prompt for permission
before executing MCP tools. Click "Allow" to use the tools.
```

**Problem:** Invalid SMILES error
```
Ensure your SMILES string is valid. For cyclic peptides, use proper ring
closure notation. The validation tool can help identify issues:

python scripts/validate_peptide.py --smiles "YOUR_SMILES"
```

### Repository Dependencies

**Problem:** Membrane permeability prediction fails
```bash
# Check if repo is available
python -c "from src.utils import check_repo_availability; print(check_repo_availability())"

# Expected: False (repo not included in MCP distribution)
# Solution: This is expected - membrane permeability requires the full CycPeptMP repository
```

**Problem:** Models not found
```
The membrane permeability prediction requires:
1. Full CycPeptMP repository
2. Pre-trained model weights in examples/data/models/
3. Python 3.9 environment with PyTorch

Use the basic tools (validate_cyclic_peptide, calculate_peptide_properties)
for property calculations without repository dependencies.
```

### Performance Issues

**Problem:** Slow property calculations
```bash
# Check if using correct environment
mamba activate ./env  # Use main environment for basic tools
```

**Problem:** Job stuck in pending
```bash
# Check job directory permissions
mkdir -p jobs
ls -la jobs/

# View job logs
python -c "
from src.server import mcp
status = mcp.list_jobs()
print(status)
"
```

**Problem:** Out of memory during ML prediction
```
The membrane permeability prediction requires 2-3GB RAM.
Close other applications or use a machine with more memory.
```

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Test individual scripts
python scripts/validate_peptide.py --help
python scripts/batch_analysis.py --help

# Test MCP server
python -c "from src.server import mcp; print('Server OK')"

# Run integration tests (if available)
python tests/run_integration_tests.py
```

### Starting Dev Server

```bash
# Run MCP server in dev mode with auto-reload
mamba activate ./env
fastmcp dev src/server.py

# Test server directly
python src/server.py
```

### Adding New Tools

```python
# Add to src/server.py
@mcp.tool()
def my_new_tool(param: str) -> dict:
    """Description for the LLM."""
    try:
        # Your tool logic here
        return {"status": "success", "result": "data"}
    except Exception as e:
        return format_error_response(e, "Tool failed")
```

---

## Performance Metrics

### Tested Performance

| Operation | Dataset Size | Runtime | Memory | Success Rate |
|-----------|--------------|---------|---------|-------------|
| Single validation | 1 peptide | <1 sec | <50MB | 100% |
| Batch properties | 2 peptides | <1 sec | <100MB | 100% |
| Batch analysis | 2 peptides | <1 sec | <100MB | 100% |
| Membrane prediction | 2 peptides | ~227 sec | 2-3GB | 95% |

### Environment Sizes

- **Main Environment (./env)**: ~1.2 GB (includes RDKit and FastMCP)
- **Legacy Environment (./env_py39)**: ~4.8 GB (includes PyTorch with CUDA)

---

## License

Built on the CycPeptMP framework for cyclic peptide membrane permeability prediction.

## Credits

Based on [CycPeptMP](https://github.com/Huang-AI4Medicine/CycPeptMPDB) - Cyclic Peptide Membrane Permeability Database and Predictor