"""
Integration Tests for CI Workflow Validation

This module provides integration tests that simulate the GitHub Actions
CI environment and validate the complete workflow execution.

Specifically tests the fix for GitHub Actions job #61098313515 where
a missing `import json` statement caused CI failure.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "ci" / "validate_cargo_features.py"


class TestCIWorkflowIntegration:
    """Integration tests for CI validation workflow."""

    def test_ci_validation_script_integration(self) -> None:
        """
        Integration test for CI validation workflow.

        Simulates GitHub Actions environment and validates:
        1. Script executes successfully
        2. Exit code is 0 for valid Cargo.toml
        3. No NameError or import issues
        4. Output contains success indicators
        """
        # Simulate CI environment
        env = os.environ.copy()
        env["CI"] = "true"
        env["GITHUB_ACTIONS"] = "true"

        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env=env,
            timeout=30,
        )

        # Validate success
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "✅ All Cargo.toml feature validations passed!" in result.stdout, "Result must not be empty"
        assert "NameError" not in result.stderr, "Result must not be empty"
        # Ensure there are no json-related error messages in stderr
        if "json" in result.stderr.lower():
            assert "json.dumps" not in result.stderr, "json.dumps should not appear in error output"

    def test_ci_script_exit_codes(self) -> None:
        """Test that script returns proper exit codes."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30,
        )

        # Valid Cargo.toml should return exit code 0
        assert result.returncode == 0, "Result must not be empty"

    def test_ci_script_no_import_errors(self) -> None:
        """Test that script has no import errors."""
        # Try importing the module directly
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import sys; sys.path.insert(0, '{SCRIPT_PATH.parent}'); import validate_cargo_features",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Import error: {result.stderr}"
        assert "NameError" not in result.stderr, "Result must not be empty"
        assert "ModuleNotFoundError" not in result.stderr or "tomli" in result.stderr, "Result must not be empty"

    def test_ci_script_json_dumps_works(self) -> None:
        """
        Regression test: Verify json.dumps is accessible.

        This specifically tests the fix for the missing import that caused
        the original CI failure. Line 71 uses json.dumps() to serialize
        feature lists.
        """
        test_code = f"""
import sys
sys.path.insert(0, '{SCRIPT_PATH.parent}')
import validate_cargo_features as vcf

# Verify json is imported
assert hasattr(vcf, 'json'), "json module not imported"

# Verify json.dumps works (this was the failing line)
result = vcf.json.dumps({{'test': ['value1', 'value2']}})
assert 'test' in result, "Result must not be empty"
logger.info("✅ json.dumps works correctly")
"""
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"json.dumps test failed: {result.stderr}"
        assert "✅ json.dumps works correctly" in result.stdout, "Result must not be empty"

    def test_ci_script_with_invalid_cargo_toml(self, tmp_path: Path) -> None:
        """Test script correctly detects invalid Cargo.toml."""
        # Create a simple test script that validates a temporary Cargo.toml
        invalid_cargo = tmp_path / "Cargo.toml"
        invalid_cargo.write_text("""
[package]
name = "test"

[dependencies]
pyo3 = "0.18"
""")

        test_code = f"""
import sys
sys.path.insert(0, '{SCRIPT_PATH.parent}')
from validate_cargo_features import validate_cargo_features
from pathlib import Path
from codex.logging.structured_logger import logger

is_valid, errors = validate_cargo_features(Path('{invalid_cargo}'))
logger.info(f"is_valid: {{is_valid}}")
logger.info(f"errors: {{errors}}")
sys.exit(0 if not is_valid else 1)  # Expect invalid (is_valid=False)
"""
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Should detect invalid Cargo.toml: {result.stdout}"
        assert "is_valid: False" in result.stdout, "Result must not be empty"

    def test_ci_script_environment_variables(self) -> None:
        """Test script works with various CI environment variables."""
        env_configs = [
            {"CI": "true"},
            {"GITHUB_ACTIONS": "true"},
            {"CI": "true", "GITHUB_ACTIONS": "true"},
            {},  # No CI environment
        ]

        for env_config in env_configs:
            env = os.environ.copy()
            env.update(env_config)

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                env=env,
                timeout=30,
            )

            # Script should succeed regardless of CI environment
            assert result.returncode == 0, f"Script failed with env {env_config}: {result.stderr}"


class TestRustSwarmCIWorkflow:
    """Tests specific to the rust_swarm_ci.yml workflow."""

    def test_workflow_validation_step_simulation(self) -> None:
        """
        Simulate the exact step from rust_swarm_ci.yml:

        - name: Validate Cargo.toml features
          run: python scripts/ci/validate_cargo_features.py
        """
        result = subprocess.run(
            ["python", str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30,
        )

        # This is the exact command run in CI
        assert result.returncode == 0, f"Workflow step would fail: {result.stderr}\n{result.stdout}"

    def test_workflow_output_format(self) -> None:
        """Test that output format matches CI expectations."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30,
        )

        # Check expected output elements
        assert "Validating Cargo.toml" in result.stdout, "Result must not be empty"
        assert "Location:" in result.stdout, "Result must not be empty"

        if result.returncode == 0:
            assert "✅" in result.stdout, "Result must not be empty"
            assert "Validated:" in result.stdout, "Result must not be empty"
            assert "[features] section exists" in result.stdout, "Result must not be empty"
            assert "'python' feature declared" in result.stdout, "Result must not be empty"
            assert "'extension-module' feature declared" in result.stdout, "Result must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
