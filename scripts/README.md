# MCP Scripts

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported (rdkit, numpy, pandas)
2. **Self-Contained**: Functions inlined where possible to avoid repo dependencies
3. **Configurable**: Parameters externalized to config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping

## Scripts

| Script | Description | Repo Dependent | Config | Status |
|--------|-------------|----------------|--------|--------|
| `validate_peptide.py` | Validate SMILES and calculate properties | No | `configs/validate_peptide_config.json` | ✅ Working |
| `batch_analysis.py` | Comprehensive batch analysis | No | `configs/batch_analysis_config.json` | ✅ Working |
| `predict_membrane_permeability.py` | Membrane permeability prediction | Yes (models) | `configs/predict_membrane_permeability_config.json` | ⚠️ Repo dependent |

## Usage

### Prerequisites

```bash
# Activate environment (prefer mamba over conda)
mamba activate ./env_py39  # or: conda activate ./env_py39
```

### Script Examples

#### Validate Cyclic Peptides

```bash
# Single SMILES validation
python scripts/validate_peptide.py --smiles "NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O"

# Batch validation from CSV
python scripts/validate_peptide.py --input examples/data/sequences/new_data.csv --output results/validation.csv

# With custom config
python scripts/validate_peptide.py --input input.csv --output output.csv --config configs/custom_validate.json
```

#### Batch Analysis

```bash
# Basic batch analysis
python scripts/batch_analysis.py --input examples/data/sequences/new_data.csv --output results/batch_analysis

# With database comparison (if available)
python scripts/batch_analysis.py --input input.csv --output analysis --database repo/cycpeptmp/data/CycPeptMPDB_Peptide_All.csv

# Custom similarity threshold
python scripts/batch_analysis.py --input input.csv --output analysis --similarity-threshold 0.8
```

#### Membrane Permeability Prediction

**Note**: This script requires the full CycPeptMP repository and trained models.

```bash
# Single SMILES prediction
python scripts/predict_membrane_permeability.py --smiles "PEPTIDE_SMILES_STRING"

# Batch prediction
python scripts/predict_membrane_permeability.py --input examples/data/sequences/new_data.csv --output results/predictions.csv
```

## Shared Library

Common functions are organized in `scripts/lib/`:

| Module | Functions | Description |
|--------|-----------|-------------|
| `io.py` | 9 | File loading/saving utilities |
| `molecules.py` | 12 | RDKit molecular operations |
| `validation.py` | 7 | Input validation functions |

### Using the Shared Library

```python
from scripts.lib import canonicalize_smiles, load_csv_with_validation
from scripts.lib.molecules import calculate_molecular_properties

# Canonicalize SMILES
canonical = canonicalize_smiles("CC1CCCCC1")

# Load and validate CSV
df = load_csv_with_validation("input.csv", required_columns=['SMILES'])

# Calculate properties
from rdkit import Chem
mol = Chem.MolFromSmiles("CC1CCCCC1")
props = calculate_molecular_properties(mol)
```

## Configuration Files

Each script has an associated configuration file in `configs/`:

- `validate_peptide_config.json` - Validation thresholds and checks
- `batch_analysis_config.json` - Analysis parameters and similarity settings
- `predict_membrane_permeability_config.json` - Model and pipeline settings
- `default_config.json` - Default values for all scripts

### Example Config Usage

```bash
# Use custom config
python scripts/validate_peptide.py --input data.csv --config my_config.json
```

```json
{
  "molecular_weight": {
    "min_warning": 300,
    "max_warning": 2500
  },
  "validation": {
    "check_cyclicity": true,
    "check_peptide_elements": true
  }
}
```

## For MCP Wrapping (Step 6)

Each script exports a main function that can be wrapped as MCP tools:

### Validate Peptide

```python
from scripts.validate_peptide import run_validate_peptide

@mcp.tool()
def validate_cyclic_peptide(smiles: str, output_file: str = None):
    """Validate cyclic peptide SMILES and calculate molecular properties."""
    result = run_validate_peptide(smiles=smiles, output_file=output_file)
    return result['result']
```

### Batch Analysis

```python
from scripts.batch_analysis import run_batch_analysis

@mcp.tool()
def analyze_cyclic_peptides(input_file: str, output_prefix: str = "analysis"):
    """Comprehensive batch analysis of cyclic peptides."""
    result = run_batch_analysis(input_file=input_file, output_file=output_prefix)
    return {
        'summary': result['summary'],
        'diversity': result['diversity'],
        'output_files': result['output_files']
    }
```

### Membrane Permeability Prediction

```python
from scripts.predict_membrane_permeability import run_predict_membrane_permeability

@mcp.tool()
def predict_membrane_permeability(smiles: str):
    """Predict membrane permeability of cyclic peptide."""
    result = run_predict_membrane_permeability(smiles=smiles)
    if result['success']:
        return result['result']['predictions']
    else:
        return {"error": result['error']}
```

## Dependencies

### Essential (All Scripts)
- Python 3.9+
- pandas >= 1.3.0
- numpy >= 1.20.0
- rdkit >= 2022.03.0

### For Membrane Permeability Prediction
- torch >= 1.11.0
- mordred >= 1.2.0
- Full CycPeptMP repository access

### Optional (Enhanced Features)
- scipy >= 1.7.0 (statistical functions)
- scikit-learn >= 1.0.0 (similarity metrics)

## Testing

All scripts have been tested with the example data:

```bash
# Test validation
python scripts/validate_peptide.py --input examples/data/sequences/new_data.csv --output test_validation.csv

# Test batch analysis
python scripts/batch_analysis.py --input examples/data/sequences/new_data.csv --output test_batch

# Test membrane permeability (requires repo)
python scripts/predict_membrane_permeability.py --input examples/data/sequences/new_data.csv --output test_predictions.csv
```

## Troubleshooting

### Common Issues

1. **RDKit Import Error**
   ```bash
   # Install RDKit in conda environment
   mamba install -c conda-forge rdkit
   ```

2. **Missing Config Files**
   ```bash
   # Use default config or create custom
   python script.py --config configs/default_config.json
   ```

3. **Membrane Permeability Script Fails**
   - Ensure you're in the `./env_py39` environment
   - Check that `repo/cycpeptmp/` directory exists
   - Verify all CycPeptMP dependencies are installed

4. **Output Directory Not Found**
   - Scripts automatically create output directories
   - Check file permissions if creation fails

### Performance Tips

- Use `mamba` instead of `conda` for faster environment management
- For large datasets, consider processing in chunks
- Memory usage scales with input size for similarity calculations

## Contributing

When modifying scripts:

1. Maintain the main function signature for MCP compatibility
2. Keep dependencies minimal
3. Update configuration files if adding new parameters
4. Test with example data before committing
5. Update this README if adding new functionality