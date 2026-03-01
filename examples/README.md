# CycPeptMP Examples

This directory contains example scripts and demo data for using CycPeptMP to predict membrane permeability of cyclic peptides.

## Use Cases

### 1. Membrane Permeability Prediction (`use_case_1_predict_membrane_permeability.py`)

**Description**: Main use case for predicting membrane permeability of cyclic peptides using deep learning with multi-level molecular features.

**Features**:
- Atom-level features (molecular graphs)
- Monomer-level features (peptide building blocks)
- Peptide-level features (global molecular descriptors)
- Pre-trained CycPeptMP model with 60x data augmentation

**Usage**:
```bash
# Predict from CSV file
mamba run -p ./env_py39 python examples/use_case_1_predict_membrane_permeability.py \
    --input examples/data/sequences/new_data.csv \
    --output predictions.csv

# Predict single SMILES
mamba run -p ./env_py39 python examples/use_case_1_predict_membrane_permeability.py \
    --smiles "NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O" \
    --output single_prediction.csv
```

**Input**: CSV with columns ID, ID_org, SMILES or single SMILES string
**Output**: CSV with permeability predictions (log scale and actual values)
**Environment**: `./env_py39` (requires PyTorch, RDKit, Mordred)

### 2. Cyclic Peptide Validation (`use_case_2_validate_cyclic_peptide.py`)

**Description**: Validate SMILES strings and extract basic molecular properties of cyclic peptides.

**Features**:
- SMILES validation and canonicalization
- Molecular properties (MW, LogP, TPSA, etc.)
- Drug-likeness assessment
- Cyclic structure verification
- Monomer composition analysis

**Usage**:
```bash
# Validate CSV file
mamba run -p ./env_py39 python examples/use_case_2_validate_cyclic_peptide.py \
    --input examples/data/sequences/new_data.csv \
    --output validation_results.csv

# Validate single SMILES
mamba run -p ./env_py39 python examples/use_case_2_validate_cyclic_peptide.py \
    --smiles "NCCCC[C@@H]1NC(=O)..."
```

**Input**: CSV with SMILES column or single SMILES string
**Output**: Validation results with molecular properties
**Environment**: `./env_py39` or `./env` (requires RDKit)

### 3. Batch Analysis (`use_case_3_batch_analysis.py`)

**Description**: Comprehensive batch analysis of multiple cyclic peptides with database comparison.

**Features**:
- Molecular property calculations
- Chemical diversity analysis
- Similarity search against CycPeptMPDB
- Summary statistics and reporting
- Drug-likeness assessment

**Usage**:
```bash
# Basic batch analysis
mamba run -p ./env_py39 python examples/use_case_3_batch_analysis.py \
    --input examples/data/sequences/new_data.csv \
    --output batch_analysis

# With database comparison
mamba run -p ./env_py39 python examples/use_case_3_batch_analysis.py \
    --input examples/data/sequences/new_data.csv \
    --output batch_analysis \
    --compare-with-database
```

**Input**: CSV with SMILES column
**Output**: Multiple files with analysis results
**Environment**: `./env_py39` (requires RDKit)

## Demo Data

### `data/sequences/new_data.csv`
Sample cyclic peptides including:
- **Anidulafungin**: Antifungal cyclic peptide drug
- **Pasireotide**: Somatostatin analog for treating Cushing's disease

### `data/CycPeptMP.json`
Configuration file containing:
- Model hyperparameters
- Feature selection settings
- Data preprocessing parameters
- Normalization statistics

### `data/models/Fusion/`
Pre-trained CycPeptMP model weights:
- `Fusion-60_cv0.cpt`, `cv1.cpt`, `cv2.cpt`: Main models (60x augmentation)
- `Fusion-20_cv*.cpt`: Models with 20x augmentation
- `Fusion-1_cv*.cpt`: Models without augmentation

## Requirements by Use Case

| Use Case | Environment | Key Dependencies |
|----------|-------------|------------------|
| 1. Permeability Prediction | `./env_py39` | torch==2.0.0, rdkit, mordred, numpy, pandas |
| 2. SMILES Validation | `./env_py39` or `./env` | rdkit, numpy, pandas |
| 3. Batch Analysis | `./env_py39` | rdkit, numpy, pandas |

## Expected Outputs

### Use Case 1 - Permeability Prediction
```csv
ID,ID_org,SMILES,pred_cv0,pred_cv1,pred_cv2,pred_mean,pred_permeability
1,Anidulafungin,CCCCCOc1ccc(...),-6.79,-6.78,-6.79,-6.788,1.63e-07
2,Pasireotide,NCCCC[C@@H]1NC(...),-7.02,-7.03,-7.02,-7.024,9.46e-08
```

### Use Case 2 - Validation Results
```csv
ID_org,valid,canonical_smiles,molecular_weight,logp,tpsa,is_cyclic,errors
Anidulafungin,True,CCCCCOc1ccc(...),1140.24,5.23,268.19,True,[]
Pasireotide,True,NCCCC[C@@H]1NC(...),1096.32,1.85,295.27,True,[]
```

### Use Case 3 - Batch Analysis
Multiple output files:
- `batch_analysis_properties.csv`: Molecular properties
- `batch_analysis_summary.json`: Summary statistics
- `batch_analysis_similarities.csv`: Similar peptides in database
- `batch_analysis_diversity.json`: Chemical diversity metrics

## Tips

1. **Environment**: Use `./env_py39` for full functionality with PyTorch models
2. **Performance**: Use Case 1 is computationally intensive due to 3D conformation generation
3. **Memory**: Large datasets may require chunking for processing
4. **CUDA**: GPU acceleration available if CUDA is installed
5. **MOE descriptors**: Some descriptors require commercial MOE software (optional)

## Common Issues

- **Import errors**: Ensure you're using the correct conda environment
- **Memory issues**: Try processing smaller batches
- **Missing weights**: Download model weights if not included
- **RDKit errors**: Some SMILES may fail 3D conformation generation