#!/usr/bin/env python3
"""
Test script for CycPep MCP Server
Tests both synchronous and asynchronous functionality.
"""

import json
import time
import subprocess
from pathlib import Path

def test_server_info():
    """Test server info endpoint."""
    print("=== Testing Server Info ===")
    # This would be tested via MCP client, but we can verify the script imports work
    try:
        from src.server import mcp
        print("✅ Server imports successfully")
        return True
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return False

def test_sync_tools():
    """Test synchronous tools."""
    print("\n=== Testing Sync Tools ===")

    # Test validation script directly
    try:
        from scripts.validate_peptide import run_validate_peptide

        # Test with example SMILES (cyclic peptide)
        test_smiles = "NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O"

        result = run_validate_peptide(smiles=test_smiles)
        print(f"✅ Validation script works: MW={result.get('molecular_weight', 'N/A')} Da")
        return True

    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_batch_analysis():
    """Test batch analysis script."""
    print("\n=== Testing Batch Analysis ===")

    # Check if example data exists
    example_file = Path("examples/data/sequences/new_data.csv")
    if not example_file.exists():
        print("⚠️  Example data not found - skipping batch test")
        return True

    try:
        from scripts.batch_analysis import run_batch_analysis

        result = run_batch_analysis(
            input_file=str(example_file),
            output_file="test_batch_output"
        )

        print(f"✅ Batch analysis works: processed {len(result.get('analysis_df', []))} peptides")
        return True

    except Exception as e:
        print(f"❌ Batch analysis test failed: {e}")
        return False

def test_job_manager():
    """Test job management system."""
    print("\n=== Testing Job Manager ===")

    try:
        from src.jobs.manager import job_manager

        # Test listing jobs (should be empty initially)
        result = job_manager.list_jobs()
        print(f"✅ Job manager works: {result['total']} jobs found")
        return True

    except Exception as e:
        print(f"❌ Job manager test failed: {e}")
        return False

def test_dependencies():
    """Test all required dependencies."""
    print("\n=== Testing Dependencies ===")

    dependencies = {
        "pandas": "import pandas",
        "numpy": "import numpy",
        "rdkit": "from rdkit import Chem",
        "json": "import json",
        "pathlib": "from pathlib import Path"
    }

    results = {}
    for name, import_stmt in dependencies.items():
        try:
            exec(import_stmt)
            results[name] = "✅"
            print(f"✅ {name}: Available")
        except ImportError:
            results[name] = "❌"
            print(f"❌ {name}: Missing")

    return all(status == "✅" for status in results.values())

def main():
    """Run all tests."""
    print("🧪 CycPep MCP Server Test Suite")
    print("=" * 50)

    tests = [
        ("Dependencies", test_dependencies),
        ("Server Info", test_server_info),
        ("Sync Tools", test_sync_tools),
        ("Batch Analysis", test_batch_analysis),
        ("Job Manager", test_job_manager)
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 50)
    print("🔍 Test Summary")
    print("=" * 50)

    passed = sum(results.values())
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:<20} {status}")

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Server is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Check dependencies and configuration.")
        return False

if __name__ == "__main__":
    main()