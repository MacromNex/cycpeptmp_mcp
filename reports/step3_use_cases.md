# Step 3: Use Cases Report

## Scan Information
- **Scan Date**: 2025-12-31
- **Filter Applied**: cyclic peptide membrane permeability prediction using deep learning, atom-level and monomer-level features
- **Python Version**: 3.9.23 (legacy environment)
- **Environment Strategy**: dual (main: Python 3.10.19, legacy: Python 3.9.23)

## Use Cases

### UC-001: Membrane Permeability Prediction
- **Description**: Predict membrane permeability of new cyclic peptides using CycPeptMP's deep learning model with multi-level molecular features (atom, monomer, peptide)
- **Script Path**: `examples/use_case_1_predict_membrane_permeability.py`
- **Complexity**: complex
- **Priority**: high
- **Environment**: `./env_py39` (requires PyTorch, RDKit, Mordred)
- **Source**: `Newdata.ipynb`, README.md main use case

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | CSV | CSV file with SMILES column | --input |
| smiles | string | Single SMILES string | --smiles |
| config | JSON | Model configuration file | --config |
| models | directory | Pre-trained model weights | --models |
| output | string | Output CSV file path | --output |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| predictions | CSV | Permeability predictions (log scale and actual values) |

**Example Usage:**
```bash
# Predict from file
mamba run -p ./env_py39 python examples/use_case_1_predict_membrane_permeability.py \
    --input examples/data/sequences/new_data.csv --output predictions.csv

# Predict single SMILES
mamba run -p ./env_py39 python examples/use_case_1_predict_membrane_permeability.py \
    --smiles "NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)..." \
    --output single_prediction.csv
```

**Example Data**: `examples/data/sequences/new_data.csv` (contains Anidulafungin, Pasireotide)

**Technical Details:**
- Uses pre-trained Fusion model with 60x data augmentation
- 3-fold cross-validation ensemble prediction
- Generates atom-level (graph), monomer-level, and peptide-level features
- Includes 3D conformation generation and molecular descriptor calculation
- Supports both CPU and GPU acceleration via CUDA

---

### UC-002: Cyclic Peptide Validation
- **Description**: Validate SMILES strings and extract molecular properties for cyclic peptides including drug-likeness assessment
- **Script Path**: `examples/use_case_2_validate_cyclic_peptide.py`
- **Complexity**: simple
- **Priority**: high
- **Environment**: `./env_py39` or `./env` (requires RDKit)
- **Source**: Created based on `utils_function.py` functionality

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | CSV | CSV file with SMILES column | --input |
| smiles | string | Single SMILES string | --smiles |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| validation_results | CSV | Validation status and molecular properties |

**Example Usage:**
```bash
# Validate file
mamba run -p ./env_py39 python examples/use_case_2_validate_cyclic_peptide.py \
    --input examples/data/sequences/new_data.csv --output validation.csv

# Validate single SMILES
mamba run -p ./env_py39 python examples/use_case_2_validate_cyclic_peptide.py \
    --smiles "NCCCC[C@@H]1NC(=O)..."
```

**Example Data**: `examples/data/sequences/new_data.csv`

**Features:**
- SMILES validation and canonicalization
- Molecular weight, LogP, TPSA calculation
- Hydrogen bond donors/acceptors
- Ring analysis and cyclicity detection
- Drug-likeness (Lipinski's Rule of Five)
- Monomer composition extraction

---

### UC-003: Batch Analysis and Database Comparison
- **Description**: Comprehensive batch analysis of cyclic peptides with chemical diversity assessment and similarity search against CycPeptMPDB
- **Script Path**: `examples/use_case_3_batch_analysis.py`
- **Complexity**: medium
- **Priority**: medium
- **Environment**: `./env_py39` (requires RDKit)
- **Source**: Created based on database comparison functionality

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | CSV | CSV file with SMILES column | --input |
| database_path | CSV | CycPeptMPDB database file | --database-path |
| compare_flag | flag | Enable database comparison | --compare-with-database |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| properties | CSV | Molecular properties for all peptides |
| summary | JSON | Summary statistics |
| similarities | CSV | Similar peptides in database |
| diversity | JSON | Chemical diversity metrics |

**Example Usage:**
```bash
# Basic analysis
mamba run -p ./env_py39 python examples/use_case_3_batch_analysis.py \
    --input examples/data/sequences/new_data.csv --output batch_analysis

# With database comparison
mamba run -p ./env_py39 python examples/use_case_3_batch_analysis.py \
    --input examples/data/sequences/new_data.csv --output batch_analysis \
    --compare-with-database
```

**Example Data**: `examples/data/sequences/new_data.csv`

**Features:**
- Molecular property calculation for multiple peptides
- Chemical diversity analysis using Tanimoto similarity
- Database similarity search (Tanimoto threshold ≥ 0.7)
- Drug-likeness assessment
- Statistical summaries and reporting

---

## Summary

| Metric | Count |
|--------|-------|
| Total Found | 3 |
| Scripts Created | 3 |
| High Priority | 2 |
| Medium Priority | 1 |
| Low Priority | 0 |
| Demo Data Copied | Yes |

## Demo Data Index

| Source | Destination | Description |
|--------|-------------|-------------|
| `repo/cycpeptmp/data/new_data/new_data.csv` | `examples/data/sequences/new_data.csv` | Sample cyclic peptides (Anidulafungin, Pasireotide) |
| `repo/cycpeptmp/config/CycPeptMP.json` | `examples/data/CycPeptMP.json` | Model configuration and hyperparameters |
| `repo/cycpeptmp/weight/Fusion/` | `examples/data/models/Fusion/` | Pre-trained CycPeptMP model weights (9 files, ~450MB) |

## Use Case Classification

### By Complexity:
- **Simple (1)**: SMILES validation and property calculation
- **Medium (1)**: Batch analysis with database comparison
- **Complex (1)**: Full membrane permeability prediction pipeline

### By Data Requirements:
- **Minimal (2)**: Only requires SMILES strings
- **Full (1)**: Requires pre-trained models and configuration files

### By Computational Requirements:
- **Light (2)**: Basic RDKit operations
- **Heavy (1)**: Deep learning inference with 3D conformation generation

### By MCP Tool Potential:
- **Perfect fit (1)**: UC-001 - Main prediction functionality
- **Good fit (2)**: UC-002, UC-003 - Supporting analysis tools

## Technical Implementation Notes

### Multi-Level Features (UC-001):
1. **Atom-level**: Molecular graphs with 30 atom features
2. **Monomer-level**: Peptide building blocks with 2D/3D descriptors
3. **Peptide-level**: Global molecular descriptors (RDKit + Mordred)

### Data Augmentation:
- SMILES enumeration for atom-level augmentation
- 60x replica training for robustness
- 3-fold cross-validation ensemble

### Performance Considerations:
- **3D Conformation**: Most time-consuming step (RDKit UFF optimization)
- **GPU Acceleration**: Available via CUDA for model inference
- **Memory Usage**: ~2-4GB for typical workflows
- **Batch Processing**: Recommended for large datasets

### Database Integration:
- **CycPeptMPDB**: 7,337 unique cyclic peptides
- **Similarity Search**: Morgan fingerprints + Tanimoto similarity
- **Experimental Data**: LogP values for validation

## Limitations and Future Extensions

1. **MOE Descriptors**: Some 3D descriptors require commercial MOE software
2. **Disulfide Bonds**: Not currently handled in monomer splitting
3. **Large Datasets**: May require chunking for memory management
4. **Real-time Prediction**: Pipeline optimized for batch processing

## Environment Compatibility

All use cases designed to work with the dual environment setup:
- **Development**: Use `./env` for basic tasks
- **Production**: Use `./env_py39` for full CycPeptMP functionality
- **Fallback**: Scripts include error handling for missing dependencies