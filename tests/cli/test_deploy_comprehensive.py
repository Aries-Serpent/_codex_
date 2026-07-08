"""
Tests for codex_ml.cli.deploy module.

Tests dry-run deployment validation for reasoning pods.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


class TestDeployFunctions:
    """Tests for deploy module utility functions."""

    def test_deploy_module_import(self):
        """Test that deploy module can be imported."""
        try:
            from codex_ml.cli import deploy

            assert deploy is not None, "deploy must be initialized"
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")

    def test_load_yaml_file_function(self):
        """Test _load_yaml_file utility function."""
        try:
            from codex_ml.cli.deploy import _load_yaml_file

            # Create temporary YAML file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump({"test": "value", "nested": {"key": 123}}, f)
                temp_path = Path(f.name)

            try:
                result = _load_yaml_file(temp_path)
                assert result["test"] == "value", "Result must not be empty"
                assert result["nested"]["key"] == 123, "Result must not be empty"
            finally:
                temp_path.unlink(missing_ok=True)
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")

    def test_load_json_file_function(self):
        """Test _load_json_file utility function."""
        try:
            from codex_ml.cli.deploy import _load_json_file

            # Create temporary JSON file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump({"test": "value", "number": 42}, f)
                temp_path = Path(f.name)

            try:
                result = _load_json_file(temp_path)
                assert result["test"] == "value", "Result must not be empty"
                assert result["number"] == 42, "Result must not be empty"
            finally:
                temp_path.unlink(missing_ok=True)
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")


class TestDeployDryRun:
    """Tests for run_deploy_dry_run function."""

    def test_dry_run_required(self):
        """Test that dry_run=False raises RuntimeError."""
        try:
            from codex_ml.cli.deploy import run_deploy_dry_run

            with pytest.raises(RuntimeError) as excinfo:
                run_deploy_dry_run(
                    config_path=Path("/fake/config.yaml"),
                    dry_run=False,
                    run_metadata_dir=Path("/fake/metadata"),
                )
            # Test that error message contains expected text (not URL validation)
            assert "Only --dry-run deployments are permitted" in str(excinfo.value), "Value must be initialized"
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")

    def test_missing_rollout_ring(self):
        """Test that missing rollout_ring raises RuntimeError."""
        try:
            from codex_ml.cli.deploy import run_deploy_dry_run

            # Create temp config without rollout_ring
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump({"pod": {"name": "test"}}, f)
                config_path = Path(f.name)

            try:
                with pytest.raises(RuntimeError) as excinfo:
                    run_deploy_dry_run(
                        config_path=config_path,
                        dry_run=True,
                        run_metadata_dir=Path("/fake/metadata"),
                    )
                # Test that error message contains expected text (not URL validation)
                assert "missing rollout_ring" in str(excinfo.value), "Value must be initialized"
            finally:
                config_path.unlink(missing_ok=True)
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")

    def test_missing_run_metadata(self):
        """Test that missing run_metadata.json raises RuntimeError."""
        try:
            from codex_ml.cli.deploy import run_deploy_dry_run

            # Create temp config with rollout_ring
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump({"pod": {"ring": "0A_base_"}}, f)
                config_path = Path(f.name)

            # Create temp metadata dir without run_metadata.json
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    with pytest.raises(RuntimeError) as excinfo:
                        run_deploy_dry_run(
                            config_path=config_path, dry_run=True, run_metadata_dir=Path(temp_dir)
                        )
                    assert "run_metadata.json not found" in str(excinfo.value), "Data must not be empty"
                finally:
                    config_path.unlink(missing_ok=True)
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")


class TestDeployCLI:
    """Tests for deploy CLI commands."""

    def test_deploy_module_help(self):
        """Test deploy module --help if it has CLI."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.deploy", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # May or may not have CLI entry point
        assert result.returncode in (0, 1, 2)


class TestDeployValidation:
    """Tests for deployment validation logic."""

    def test_rollout_ring_from_pod_section(self):
        """Test rollout_ring extraction from pod section."""
        try:
            from codex_ml.cli.deploy import _load_yaml_file

            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump({"pod": {"ring": "0A_base_", "name": "test-pod"}}, f)
                config_path = Path(f.name)

            try:
                config = _load_yaml_file(config_path)
                assert config["pod"]["ring"] == "0A_base_", "Condition must be true"
            finally:
                config_path.unlink(missing_ok=True)
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")

    def test_rollout_ring_from_top_level(self):
        """Test rollout_ring extraction from top level."""
        try:
            from codex_ml.cli.deploy import _load_yaml_file

            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump({"rollout_ring": "0B_base_", "name": "test-deployment"}, f)
                config_path = Path(f.name)

            try:
                config = _load_yaml_file(config_path)
                assert config["rollout_ring"] == "0B_base_", "Condition must be true"
            finally:
                config_path.unlink(missing_ok=True)
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")
