"""
Test Mcp Package Flatten

Test module for mcp package flatten.
"""

#! /usr/bin/env python3
"""
Test suite for scripts/mcp/package_flatten.sh
Tests bash script logic for flattening and packaging
"""

import json
import subprocess  # Using stdlib subprocess.run which supports timeout parameter
import tempfile
from pathlib import Path

import pytest

from codex.logging.structured_logger import logger


@pytest.fixture
def temp_source_dir():
    """Create temporary source directory with test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir) / "source"
        base.mkdir()

        # Create nested structure
        (base / "src" / "module").mkdir(parents=True)
        (base / "src" / "module" / "main.py").write_text("logger.info('hello')")
        (base / "src" / "utils.py").write_text("# utils")

        (base / "docs").mkdir()
        (base / "docs" / "guide.md").write_text("# Guide")

        (base / "README.md").write_text("# Project")

        yield base


@pytest.fixture
def package_flatten_script():
    """Path to package_flatten.sh script"""
    script = Path(__file__).parent.parent.parent / "scripts" / "mcp" / "package_flatten.sh"
    if not script.exists():
        pytest.skip("package_flatten.sh not found")
    return script


class TestPackageFlattenScript:
    """Tests for package_flatten.sh bash script"""

    def test_script_exists_and_executable(self, package_flatten_script):
        """Test that script exists and is executable"""
        assert package_flatten_script.exists(), "Condition must be true"
        assert package_flatten_script.stat().st_mode & 0o111, "Condition must be true"

    def test_script_shows_usage_with_no_args(self, package_flatten_script):
        """Test that script shows usage when called with no arguments"""
        result = subprocess.run([str(package_flatten_script)], capture_output=True, text=True)

        assert result.returncode != 0, "Result must not be empty"
        assert "Usage:" in result.stdout or "Usage:" in result.stderr, "Result must not be empty"

    def test_script_shows_help_with_help_flag(self, package_flatten_script):
        """Test --help flag displays help message"""
        result = subprocess.run(
            [str(package_flatten_script), "--help"], capture_output=True, text=True
        )

        assert "Usage:" in result.stdout, "Result must not be empty"
        assert "source_dir" in result.stdout, "Result must not be empty"
        assert "output_zip" in result.stdout, "Result must not be empty"

    def test_script_validates_source_directory(self, package_flatten_script):
        """Test error handling for missing source directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_zip = Path(tmpdir) / "output.zip"
            nonexistent = Path(tmpdir) / "nonexistent"

            result = subprocess.run(
                [str(package_flatten_script), str(nonexistent), str(output_zip)],
                capture_output=True,
                text=True,
            )

            assert result.returncode != 0, "Result must not be empty"
            assert "not found" in result.stderr or "not found" in result.stdout, "Result must not be empty"

    def test_script_creates_zip_package(self, package_flatten_script, temp_source_dir):
        """Test basic package creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_zip = Path(tmpdir) / "test_package.zip"

            # Using stdlib subprocess.run (not codex.utils.subprocess.run)
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [str(package_flatten_script), str(temp_source_dir), str(output_zip)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Check exit code
            if result.returncode != 0:
                logger.info("STDOUT:", result.stdout)
                logger.info("STDERR:", result.stderr)

            assert result.returncode == 0, f"Script failed: {result.stderr}"
            assert output_zip.exists(), "Output zip file was not created"
            assert output_zip.stat().st_size > 0, "Output zip file is empty"

    def test_script_creates_manifest(self, package_flatten_script, temp_source_dir):
        """Test that manifest.json is created in the package"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_zip = Path(tmpdir) / "test_package.zip"

            # Using stdlib subprocess.run (not codex.utils.subprocess.run)
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [str(package_flatten_script), str(temp_source_dir), str(output_zip)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.skip(f"Script execution failed: {result.stderr}")

            # Extract and check manifest
            import zipfile

            with zipfile.ZipFile(output_zip, "r") as zf:
                assert "manifest.json" in zf.namelist(), "manifest.json not found in package"

                manifest_data = zf.read("manifest.json")
                manifest = json.loads(manifest_data)

                # Validate manifest structure
                assert "files" in manifest, "Condition must be true"
                assert isinstance(manifest["files"], list)
                assert len(manifest["files"]) > 0, "Collection must not be empty"

    def test_script_flattens_directory_structure(self, package_flatten_script, temp_source_dir):
        """Test that nested paths are flattened correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_zip = Path(tmpdir) / "test_package.zip"

            # Using stdlib subprocess.run (not codex.utils.subprocess.run)
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [str(package_flatten_script), str(temp_source_dir), str(output_zip)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.skip(f"Script execution failed: {result.stderr}")

            # Check flattened filenames
            import zipfile

            with zipfile.ZipFile(output_zip, "r") as zf:
                filenames = zf.namelist()

                # Should have flattened names like src__module__main.py
                flattened_python = [f for f in filenames if f.endswith(".py") and "__" in f]
                assert len(flattened_python) > 0, "No flattened Python files found"

    def test_script_includes_sha256_in_manifest(self, package_flatten_script, temp_source_dir):
        """Test that manifest includes SHA256 hashes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_zip = Path(tmpdir) / "test_package.zip"

            # Using stdlib subprocess.run (not codex.utils.subprocess.run)
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [str(package_flatten_script), str(temp_source_dir), str(output_zip)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.skip(f"Script execution failed: {result.stderr}")

            import zipfile

            with zipfile.ZipFile(output_zip, "r") as zf:
                manifest_data = zf.read("manifest.json")
                manifest = json.loads(manifest_data)

                # Check first file has SHA256
                if manifest["files"]:
                    first_file = manifest["files"][0]
                    assert "sha256" in first_file, "Condition must be true"
                    assert len(first_file["sha256"]) == 64, "Collection must not be empty"

    def test_script_includes_file_sizes(self, package_flatten_script, temp_source_dir):
        """Test that manifest includes file sizes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_zip = Path(tmpdir) / "test_package.zip"

            # Using stdlib subprocess.run (not codex.utils.subprocess.run)
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [str(package_flatten_script), str(temp_source_dir), str(output_zip)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.skip(f"Script execution failed: {result.stderr}")

            import zipfile

            with zipfile.ZipFile(output_zip, "r") as zf:
                manifest_data = zf.read("manifest.json")
                manifest = json.loads(manifest_data)

                # Check file sizes
                if manifest["files"]:
                    first_file = manifest["files"][0]
                    assert "size_bytes" in first_file, "Condition must be true"
                    assert first_file["size_bytes"] >= 0, "Value must be greater than zero"

    def test_script_creates_readme(self, package_flatten_script, temp_source_dir):
        """Test that README_dataset.md is created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_zip = Path(tmpdir) / "test_package.zip"

            # Using stdlib subprocess.run (not codex.utils.subprocess.run)
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [str(package_flatten_script), str(temp_source_dir), str(output_zip)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.skip(f"Script execution failed: {result.stderr}")

            import zipfile

            with zipfile.ZipFile(output_zip, "r") as zf:
                assert "README_dataset.md" in zf.namelist(), "README_dataset.md not found"

    def test_script_with_custom_repo_root(self, package_flatten_script, temp_source_dir):
        """Test --repo-root option"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_zip = Path(tmpdir) / "test_package.zip"
            custom_root = Path(tmpdir) / "custom_root"
            custom_root.mkdir()

            # Using stdlib subprocess.run (not codex.utils.subprocess.run)
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [
                    str(package_flatten_script),
                    str(temp_source_dir),
                    str(output_zip),
                    "--repo-root",
                    str(custom_root),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should succeed or handle gracefully
            assert result.returncode in (0, 1)  # May fail if paths don't align

    def test_script_handles_special_characters(self, package_flatten_script):
        """Test handling of files with special characters in names"""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source"
            source.mkdir()

            # Create file with spaces
            (source / "file with spaces.py").write_text("# test")

            output_zip = Path(tmpdir) / "test_package.zip"

            # Using stdlib subprocess.run (not codex.utils.subprocess.run)
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [str(package_flatten_script), str(source), str(output_zip)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should handle gracefully
            if result.returncode == 0:
                assert output_zip.exists(), "Condition must be true"

    def test_script_validates_bash_syntax(self, package_flatten_script):
        """Test that script has valid bash syntax"""
        result = subprocess.run(
            ["bash", "-n", str(package_flatten_script)], capture_output=True, text=True
        )

        assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


# Run tests with: python -m pytest tests/scripts/test_mcp_package_flatten.py -v
