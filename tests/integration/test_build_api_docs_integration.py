"""Integration tests for src/tools/build_api_docs.py discovery and index creation."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Get repository root
REPO_ROOT = Path(__file__).parent.parent.parent
SCRIPT_PATH = REPO_ROOT / "src" / "tools" / "build_api_docs.py"


@pytest.mark.integration
class TestBuildAPIDocsIntegration:
    """Integration tests for the build_api_docs.py script."""

    def test_script_runs_successfully_with_fake_module(self, tmp_path):
        """Test that script runs and identifies codex_ml when it's available."""
        # Create a fake codex_ml package
        pkg_dir = tmp_path / "codex_ml"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("# fake codex_ml for testing")

        # Create submodules
        (pkg_dir / "peft.py").write_text("# fake peft module")

        dist_dir = pkg_dir / "distributed"
        dist_dir.mkdir()
        (dist_dir / "__init__.py").write_text("# fake distributed module")

        # Prepare environment with PYTHONPATH
        env = os.environ.copy()
        env_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{tmp_path!s}{os.pathsep}{env_pythonpath}" if env_pythonpath else str(tmp_path)
        )

        # Run the script
        script = SCRIPT_PATH
        assert script.exists(), f"Script must exist at {script}"

        result = subprocess.run(
            [sys.executable, str(script), "--verbose", "--output-dir", str(tmp_path / "test_docs")],
            capture_output=True,
            text=True,
            env=env,
        )

        # Check output
        output = result.stdout + result.stderr

        # Should log that codex_ml is importable
        assert "codex_ml" in output, f"Expected 'codex_ml' in output; got: {output}"
        assert "Final module list to document" in output, "Condition must be true"
        assert result.returncode == 0, output
        assert (tmp_path / "test_docs" / "index.html").is_file()

    def test_script_excludes_optional_with_flag(self, tmp_path):
        """Test that --skip-optional excludes optional modules."""
        # Create a fake codex_ml package
        pkg_dir = tmp_path / "codex_ml"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("# fake codex_ml")

        env = os.environ.copy()
        env["PYTHONPATH"] = str(tmp_path)

        script = SCRIPT_PATH
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--skip-optional",
                "--verbose",
                "--output-dir",
                str(tmp_path / "test_docs"),
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        output = result.stdout + result.stderr

        # Final module list should NOT include codex_ml when --skip-optional is used
        # Check the final module list log entry
        assert result.returncode == 0, output
        final_list_line = next(
            line for line in output.splitlines() if "Final module list to document" in line
        )
        assert "codex_ml" not in final_list_line
        assert (tmp_path / "test_docs" / "index.html").is_file()

    def test_script_handles_missing_modules_gracefully(self, tmp_path):
        """Test that script doesn't crash when optional modules are missing."""
        script = SCRIPT_PATH

        # Run without any special PYTHONPATH - optional modules may not be available
        run_kwargs = {
            "args": [
                sys.executable,
                str(script),
                "--verbose",
                "--output-dir",
                str(tmp_path / "test_api_docs"),
            ],
            "capture_output": True,
            "text": True,
        }
        if sys.version_info >= (3, 5):
            run_kwargs["timeout"] = 30
        result = subprocess.run(**run_kwargs)

        output = result.stdout + result.stderr

        # Script should handle missing modules gracefully
        # It should either succeed or fail gracefully with a clear message
        # We mainly want to ensure it doesn't crash unexpectedly
        if result.returncode != 0:
            # If it fails, should be with a clear error message
            assert "No modules available" in output or "Failed to build" in output
        else:
            assert (tmp_path / "test_api_docs" / "index.html").is_file()

    def test_environment_variable_skip_optional(self, tmp_path):
        """Test that CODEX_SKIP_OPTIONAL_IMPORTS environment variable works."""
        # Create fake codex_ml
        pkg_dir = tmp_path / "codex_ml"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("# fake")

        env = os.environ.copy()
        env["PYTHONPATH"] = str(tmp_path)
        env["CODEX_SKIP_OPTIONAL_IMPORTS"] = "1"

        script = SCRIPT_PATH
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--verbose",
                "--output-dir",
                str(tmp_path / "test_docs"),
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        output = result.stdout + result.stderr

        # When env var is set, codex_ml should not be in final list
        assert result.returncode == 0, output
        final_list_line = next(
            line for line in output.splitlines() if "Final module list to document" in line
        )
        assert "codex.cli" in final_list_line
        assert "codex.logging" in final_list_line
        assert "codex_ml" not in final_list_line

    def test_fail_on_missing_with_skip_optional_succeeds(self, tmp_path):
        """Test --fail-on-missing combined with --skip-optional succeeds."""
        script = SCRIPT_PATH

        # Use --skip-optional to not request codex_ml at all
        # This should succeed even with --fail-on-missing because we're
        # only requesting core modules which are available
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--fail-on-missing",
                "--skip-optional",
                "--output-dir",
                str(tmp_path / "test_docs"),
            ],
            capture_output=True,
            text=True,
        )

        # Should succeed because we're not requesting optional modules
        assert result.returncode == 0, result.stdout + result.stderr
        assert (tmp_path / "test_docs" / "index.html").is_file()
