#!/bin/bash
# Quick Setup Script for CycPeptMP MCP
# CycPeptMP: Accurate and efficient model for predicting membrane permeability of cyclic peptides
# Uses multi-level molecular features (atom, monomer, peptide) with data augmentation
# Source: https://github.com/akiyamalab/cycpeptmp

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Setting up CycPeptMP MCP ==="

# Step 1: Create main Python 3.10 environment
echo "[1/8] Creating Python 3.10 environment..."
(command -v mamba >/dev/null 2>&1 && mamba create -p ./env python=3.10 pip -y) || \
(command -v conda >/dev/null 2>&1 && conda create -p ./env python=3.10 pip -y) || \
(echo "Warning: Neither mamba nor conda found, creating venv instead" && python3 -m venv ./env)

# Step 2: Install MCP server dependencies
echo "[2/8] Installing MCP server dependencies..."
./env/bin/pip install fastmcp loguru click pandas numpy tqdm

# Step 3: Install RDKit and visualization packages
echo "[3/8] Installing RDKit and visualization packages..."
(command -v mamba >/dev/null 2>&1 && mamba install -p ./env -c conda-forge rdkit matplotlib-base pillow sqlalchemy -y) || \
(command -v conda >/dev/null 2>&1 && conda install -p ./env -c conda-forge rdkit matplotlib-base pillow sqlalchemy -y) || \
./env/bin/pip install rdkit

# Step 4: Ensure fastmcp is properly installed
echo "[4/8] Finalizing fastmcp installation..."
./env/bin/pip install --force-reinstall --no-cache-dir fastmcp

# Step 5: Create Python 3.9 environment for CycPeptMP core (Mordred compatibility)
echo "[5/8] Creating Python 3.9 environment for CycPeptMP core..."
(command -v mamba >/dev/null 2>&1 && mamba create -p ./env_py39 python=3.9 pip -y) || \
(command -v conda >/dev/null 2>&1 && conda create -p ./env_py39 python=3.9 pip -y) || \
(echo "Warning: Creating fallback py39 env with venv" && python3 -m venv ./env_py39)

# Step 6: Install CycPeptMP dependencies in Python 3.9 environment
echo "[6/8] Installing CycPeptMP dependencies in Python 3.9 environment..."
./env_py39/bin/pip install numpy==1.25.0 pandas==1.4.4 torch==2.0.0

# Step 7: Install RDKit in Python 3.9 environment
echo "[7/8] Installing RDKit in Python 3.9 environment..."
(command -v mamba >/dev/null 2>&1 && mamba install -p ./env_py39 -c conda-forge rdkit -y) || \
(command -v conda >/dev/null 2>&1 && conda install -p ./env_py39 -c conda-forge rdkit -y) || \
./env_py39/bin/pip install rdkit

# Step 8: Install Mordred (requires Python 3.9)
echo "[8/8] Installing Mordred descriptor calculator..."
./env_py39/bin/pip install mordred

echo ""
echo "=== CycPeptMP MCP Setup Complete ==="
echo "Note: Two environments created:"
echo "  - ./env (Python 3.10): MCP server"
echo "  - ./env_py39 (Python 3.9): CycPeptMP core with Mordred"
echo "For input files, download from: https://zenodo.org/records/15166699"
echo "To run the MCP server: ./env/bin/python src/server.py"
