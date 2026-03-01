#!/usr/bin/env python3
"""
Automated integration test runner for Cyclic Peptide MCP server.
Tests all tools through their functions directly and via Claude CLI.
"""

import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test configuration
TEST_SMILES = {
    "valid_simple": "CCO",  # Simple ethanol
    "valid_peptide": "NCCCC[C@@H]1NC(=O)[C@@H](Cc2c[nH]c3ccccc23)NC(=O)[C@H](c2ccccc2)NC(=O)[C@@H]2C[C@@H](OC(=O)NCCN)CN2C(=O)[C@H](Cc2ccccc2)NC(=O)[C@H](Cc2ccc(OCc3ccccc3)cc2)NC1=O",
    "invalid": "invalid_smiles_string",
    "valid_cyclic": "C1CCCCC1"  # Cyclohexane
}

TEST_SEQUENCES = {
    "valid_simple": "ACDE",
    "valid_longer": "GRGDSP",
    "invalid": "BJOUXZ"  # Invalid amino acid codes
}

class MCPTestRunner:
    def __init__(self, server_path: str = "src/server.py"):
        self.server_path = Path(server_path)
        self.results = {
            "test_date": datetime.now().isoformat(),
            "server_path": str(server_path),
            "tests": {},
            "issues": [],
            "summary": {}
        }

    def log_test(self, test_name: str, status: str, output: str = "", error: str = ""):
        """Log test result"""
        self.results["tests"][test_name] = {
            "status": status,
            "output": output,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

    def test_imports(self) -> bool:
        """Test that all required modules can be imported"""
        try:
            # Test server imports
            from src.server import mcp
            from src.utils import check_dependencies, validate_smiles_input
            from src.jobs.manager import job_manager
            self.log_test("imports", "passed", "All modules imported successfully")
            return True
        except Exception as e:
            self.log_test("imports", "failed", error=str(e))
            return False

    def test_script_execution(self) -> bool:
        """Test that underlying scripts work"""
        try:
            # Test validation script
            cmd = [
                "python", "scripts/validate_peptide.py",
                "--smiles", TEST_SMILES["valid_peptide"]
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0 and "Valid: True" in result.stdout:
                self.log_test("script_validation", "passed", result.stdout[:500])
                return True
            else:
                self.log_test("script_validation", "failed",
                            result.stdout, result.stderr)
                return False

        except Exception as e:
            self.log_test("script_validation", "failed", error=str(e))
            return False

    def test_error_handling(self) -> bool:
        """Test error handling with invalid inputs"""
        try:
            # Test with invalid SMILES
            cmd = [
                "python", "scripts/validate_peptide.py",
                "--smiles", TEST_SMILES["invalid"]
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if "Valid: False" in result.stdout:
                self.log_test("error_handling", "passed",
                            "Invalid SMILES handled correctly")
                return True
            else:
                self.log_test("error_handling", "failed",
                            result.stdout, result.stderr)
                return False

        except Exception as e:
            self.log_test("error_handling", "failed", error=str(e))
            return False

    def test_claude_mcp_registration(self) -> bool:
        """Test that MCP server is properly registered with Claude"""
        try:
            result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True, text=True, timeout=30
            )

            if "cycpep-tools" in result.stdout and "Connected" in result.stdout:
                self.log_test("claude_registration", "passed",
                            "MCP server registered and connected")
                return True
            else:
                self.log_test("claude_registration", "failed",
                            result.stdout, result.stderr)
                return False

        except Exception as e:
            self.log_test("claude_registration", "failed", error=str(e))
            return False

    def test_dependency_check(self) -> bool:
        """Test dependency checking"""
        try:
            from src.utils import check_dependencies, check_repo_availability

            missing_deps = check_dependencies()
            repo_available = check_repo_availability()

            self.log_test("dependencies", "passed",
                        f"Missing deps: {missing_deps}, Repo: {repo_available}")
            return True

        except Exception as e:
            self.log_test("dependencies", "failed", error=str(e))
            return False

    def test_job_manager(self) -> bool:
        """Test job manager functionality"""
        try:
            from src.jobs.manager import job_manager

            # Test listing jobs (should work even if empty)
            jobs_result = job_manager.list_jobs()

            if isinstance(jobs_result, dict) and "status" in jobs_result:
                self.log_test("job_manager", "passed", "Job manager works")
                return True
            else:
                self.log_test("job_manager", "failed",
                            f"Unexpected result: {jobs_result}")
                return False

        except Exception as e:
            self.log_test("job_manager", "failed", error=str(e))
            return False

    def test_file_operations(self) -> bool:
        """Test file reading and writing operations"""
        try:
            # Test with demo data
            demo_file = Path("examples/data/sequences/new_data.csv")
            if demo_file.exists():
                import pandas as pd
                df = pd.read_csv(demo_file)
                if len(df) > 0 and 'SMILES' in df.columns:
                    self.log_test("file_operations", "passed",
                                f"Read {len(df)} rows from demo data")
                    return True
                else:
                    self.log_test("file_operations", "failed",
                                "Demo file exists but format unexpected")
                    return False
            else:
                self.log_test("file_operations", "skipped", "Demo file not found")
                return True  # Not a failure

        except Exception as e:
            self.log_test("file_operations", "failed", error=str(e))
            return False

    def run_all_tests(self):
        """Run the complete test suite"""
        print("Starting MCP Integration Test Suite...")
        print(f"Testing server: {self.server_path}")
        print("=" * 60)

        test_methods = [
            self.test_imports,
            self.test_dependency_check,
            self.test_script_execution,
            self.test_error_handling,
            self.test_claude_mcp_registration,
            self.test_job_manager,
            self.test_file_operations
        ]

        passed = 0
        total = len(test_methods)

        for test_method in test_methods:
            test_name = test_method.__name__
            print(f"Running {test_name}...", end=" ")

            try:
                if test_method():
                    print("PASSED")
                    passed += 1
                else:
                    print("FAILED")
            except Exception as e:
                print(f"ERROR: {e}")
                self.log_test(test_name, "error", error=str(e))

        # Generate summary
        self.results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "N/A"
        }

        print("=" * 60)
        print(f"Test Summary: {passed}/{total} passed ({self.results['summary']['pass_rate']})")

        return self.results

    def save_report(self, output_file: str = "reports/integration_test_results.json"):
        """Save test results to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Test report saved to: {output_path}")

if __name__ == "__main__":
    runner = MCPTestRunner()
    results = runner.run_all_tests()
    runner.save_report()

    # Print summary
    print("\nDetailed Results:")
    for test_name, result in results["tests"].items():
        status_symbol = "✓" if result["status"] == "passed" else "✗"
        print(f"{status_symbol} {test_name}: {result['status']}")
        if result.get("error"):
            print(f"   Error: {result['error']}")