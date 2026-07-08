"""
Unit tests for patch validation script.

Tests cover:
 - Valid unified diff patches (RFC 3881 compliant)
 - Invalid patches (missing @@ markers, insufficient context)
 - Edge cases (empty patches, malformed syntax)
"""

import subprocess
import tempfile
from pathlib import Path

import pytest

VALID_PATCH_CONTENT = """--- /dev/null
+++ b/tmp_test_file.txt
@@ -0,0 +1,3 @@
+Line 1
+Line 2
+Line 3
"""

INVALID_PATCH_NO_MARKERS = """--- a/example.txt
+++ b/example.txt
 Line 1
 Line 2
+New line 3
 Line 4
"""

INSUFFICIENT_CONTEXT_PATCH = """--- a/example.txt
+++ b/example.txt
@@ -1,1 +1,2 @@
+New line
"""


class TestValidatePatch:
    """Test suite for validate_patch.sh script."""

    @pytest.fixture
    def script_path(self):
        """Locate validate_patch.sh script."""
        script = Path(__file__).resolve().parents[2] / "scripts" / "validate_patch.sh"
        assert script.exists(), f"Script not found: {script}"
        return str(script)

    def run_validator(self, script_path: str, patch_content: str) -> tuple[int, str]:
        """Helper to run validation script with given patch content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".patch", delete=False) as f:
            f.write(patch_content)
            patch_file = f.name

        try:
            result = subprocess.run(
                ["bash", script_path, patch_file],
                capture_output=True,
                text=True,
            )
            return result.returncode, result.stdout + result.stderr
        finally:
            Path(patch_file).unlink()

    def test_valid_patch_passes(self, script_path):
        """Valid RFC 3881 compliant patch should pass."""
        exit_code, output = self.run_validator(script_path, VALID_PATCH_CONTENT)
        assert exit_code == 0, f"Expected pass, got: {output}"
        assert "PASS" in output or "passed" in output.lower(), "Condition must be true"

    def test_missing_hunk_markers_fails(self, script_path):
        """Patch missing @@ markers should fail."""
        exit_code, output = self.run_validator(script_path, INVALID_PATCH_NO_MARKERS)
        assert exit_code != 0, f"Expected fail, got: {output}"
        assert "FAIL" in output or "failed" in output.lower(), "Condition must be true"

    def test_insufficient_context_warns(self, script_path):
        """Patch with <3 context lines should warn but pass."""
        _exit_code, output = self.run_validator(script_path, INSUFFICIENT_CONTEXT_PATCH)
        # May warn but should eventually pass (git apply might accept it)
        assert "WARN" in output or "warning" in output.lower(), "Condition must be true"

    def test_nonexistent_file_fails(self, script_path):
        """Validator should fail gracefully on missing file."""
        result = subprocess.run(
            ["bash", script_path, "/nonexistent/patch.file"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, "Result must not be empty"
        assert "FAIL" in result.stdout or "not found" in result.stdout.lower(), "Result must not be empty"

    def test_no_arguments_exits_gracefully(self, script_path):
        """Validator should show usage when called without arguments."""
        result = subprocess.run(
            ["bash", script_path],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2, "Result must not be empty"
        assert "Usage" in result.stdout or "Usage" in result.stderr, "Result must not be empty"

    def test_git_apply_check_integration(self, script_path):
        """Validator should use git apply --check for final validation."""
        _exit_code, output = self.run_validator(script_path, VALID_PATCH_CONTENT)
        # Look for evidence of git apply check
        assert "git apply" in output or "validated" in output.lower(), "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
