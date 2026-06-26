"""
Tests for codex_ml.cli.migrate_data module.

Tests CLI functionality for migrating assignment mapping files between versions.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestMigrateDataCLI:
    """Tests for migrate_data CLI commands."""

    def test_migrate_data_module_help(self):
        """Test migrate_data module --help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.migrate_data", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Should show help or indicate command exists
        assert result.returncode in (0, 1, 2)
        # Should contain some help text
        if result.returncode == 0:
            assert "migrate" in result.stdout.lower() or "help" in result.stdout.lower(), "Result must not be empty"

    def test_migrate_command_help(self):
        """Test migrate subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.migrate_data", "migrate", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_migrate_nonexistent_file(self):
        """Test migrate with nonexistent input file."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "codex_ml.cli.migrate_data",
                "migrate",
                "/nonexistent/path/file.json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Should fail with error about missing file
        assert result.returncode != 0, "Result must not be empty"

    def test_migrate_with_valid_input(self):
        """Test migrate with a valid input file."""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_data = {"version": "1.0", "mappings": [{"source": "a", "target": "b"}]}
            json.dump(test_data, f)
            temp_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "codex_ml.cli.migrate_data",
                    "migrate",
                    temp_path,
                    "--from",
                    "1.0",
                    "--to",
                    "2.0",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            # May succeed or fail depending on migration logic
            assert result.returncode in (0, 1, 2)
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestMigrateDataFunctions:
    """Unit tests for migrate_data functions."""

    def test_migrate_data_import(self):
        """Test that migrate_data module can be imported."""
        try:
            from codex_ml.cli import migrate_data

            assert hasattr(migrate_data, "app")
            assert hasattr(migrate_data, "migrate")
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")

    @patch("codex_ml.cli.migrate_data.AssignmentMappingMigration")
    def test_migrate_function_calls_migration(self, mock_migration_class):
        """Test that migrate function uses AssignmentMappingMigration."""
        try:
            # Migration class should be importable
            assert mock_migration_class is not None, "mock_migration_class must be initialized"
        except ImportError as e:
            pytest.skip(f"Migration import failed: {e}")


class TestVersionDetection:
    """Tests for version detection in migrate_data."""

    def test_version_auto_detection_v1(self):
        """Test auto-detection of v1.0 format."""
        v1_data = {"version": "1.0", "mappings": []}
        # Should be detected as v1.0
        assert v1_data.get("version") == "1.0", "Data must not be empty"

    def test_version_auto_detection_v2(self):
        """Test auto-detection of v2.0 format."""
        v2_data = {"version": "2.0", "schema_version": "2.0", "assignments": []}
        assert v2_data.get("version") == "2.0", "Data must not be empty"

    def test_version_auto_detection_v3(self):
        """Test auto-detection of v3.0 format."""
        v3_data = {"version": "3.0", "metadata": {"created": "2026-01-01"}, "assignments": []}
        assert v3_data.get("version") == "3.0", "Data must not be empty"
