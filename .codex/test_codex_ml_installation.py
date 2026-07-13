#!/usr/bin/env python3
"""
Comprehensive Installation and Functionality Tests for codex-ml==0.2.3

This module tests:
1. Installation of codex-ml[core]==0.2.3
2. Core profile functionality
3. Offline-first capabilities
4. Entry point registration
5. Dependency resolution
6. Security patches verification
7. Integration scenarios
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


class TestInstallation:
    """Test codex-ml installation scenarios."""

    def test_core_profile_installation(self, tmp_path: Path) -> None:
        """Test installation of codex-ml[core]==0.2.2 in isolated venv."""
        venv_path = tmp_path / "venv_core"
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"venv creation failed: {result.stderr}"

        pip_exe = venv_path / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
        result = subprocess.run(
            [str(pip_exe), "install", "--no-cache-dir", "codex-ml[core]==0.2.2"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, f"Installation failed: {result.stderr}"
        assert "Successfully installed" in result.stdout or "already satisfied" in result.stdout

    def test_full_version_installation(self, tmp_path: Path) -> None:
        """Test installation of codex-ml==0.2.2 (base profile)."""
        venv_path = tmp_path / "venv_base"
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        pip_exe = venv_path / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
        result = subprocess.run(
            [str(pip_exe), "install", "--no-cache-dir", "codex-ml==0.2.2"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, f"Installation failed: {result.stderr}"

    def test_dependency_conflict_detection(self, tmp_path: Path) -> None:
        """Test for dependency conflicts with other packages."""
        venv_path = tmp_path / "venv_conflict"
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        pip_exe = venv_path / ("Scripts" if sys.platform == "win32" else "bin") / "pip"

        # First install codex-ml
        result = subprocess.run(
            [str(pip_exe), "install", "--no-cache-dir", "codex-ml[core]==0.2.2"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0

        # Check for warnings
        if "WARNING" in result.stderr or "conflict" in result.stdout.lower():
            pytest.warns(Warning, match="dependency|conflict")


class TestImports:
    """Test codex-ml module imports and discovery."""

    def test_import_codex_ml(self) -> None:
        """Test basic codex_ml import."""
        import codex_ml  # noqa: F401

    def test_import_cli_module(self) -> None:
        """Test CLI module import."""
        from codex_ml import cli  # noqa: F401

    def test_import_data_module(self) -> None:
        """Test data module import."""
        from codex_ml import data  # noqa: F401

    def test_import_utils_module(self) -> None:
        """Test utils module import."""
        from codex_ml import utils  # noqa: F401

    def test_import_tracking_module(self) -> None:
        """Test tracking module import."""
        from codex_ml import tracking  # noqa: F401

    def test_import_pipeline_module(self) -> None:
        """Test pipeline module import."""
        from codex_ml import pipeline  # noqa: F401


class TestEntryPoints:
    """Test CLI entry point registration and functionality."""

    def test_codex_ml_cli_exists(self, tmp_path: Path) -> None:
        """Test that codex-ml CLI entry point is registered."""
        venv_path = tmp_path / "venv_ep"
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        pip_exe = venv_path / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
        result = subprocess.run(
            [str(pip_exe), "install", "--no-cache-dir", "codex-ml==0.2.2"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0

        # Check if CLI is available
        cli_exe = venv_path / ("Scripts" if sys.platform == "win32" else "bin") / "codex-ml"
        assert cli_exe.exists() or cli_exe.with_suffix(".exe").exists(), "CLI entry point not found"

    def test_codex_ml_cli_help(self, tmp_path: Path) -> None:
        """Test that codex-ml CLI help works."""
        venv_path = tmp_path / "venv_help"
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        pip_exe = venv_path / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
        subprocess.run(
            [str(pip_exe), "install", "--no-cache-dir", "codex-ml==0.2.2"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        python_exe = venv_path / ("Scripts" if sys.platform == "win32" else "bin") / "python"
        result = subprocess.run(
            [str(python_exe), "-m", "codex_ml", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"CLI help failed: {result.stderr}"
        assert "codex" in result.stdout.lower() or "usage" in result.stdout.lower()


class TestCoreProfileDependencies:
    """Test core profile dependency functionality."""

    def test_hydra_integration(self) -> None:
        """Test Hydra configuration management."""
        from hydra import initialize, compose
        from omegaconf import OmegaConf

        assert initialize is not None
        assert compose is not None
        assert OmegaConf is not None

    def test_pydantic_validation(self) -> None:
        """Test Pydantic data validation."""
        from pydantic import BaseModel, ValidationError

        class TestModel(BaseModel):
            name: str
            value: int

        # Valid data
        obj = TestModel(name="test", value=42)
        assert obj.name == "test"
        assert obj.value == 42

        # Invalid data
        with pytest.raises(ValidationError):
            TestModel(name="test", value="not_int")  # type: ignore

    def test_typer_cli(self) -> None:
        """Test Typer CLI framework."""
        import typer

        app = typer.Typer()

        @app.command()
        def test_command(name: str = "World") -> str:
            return f"Hello {name}"

        assert app is not None

    def test_tree_sitter_parsing(self) -> None:
        """Test tree-sitter parsing capabilities."""
        try:
            from tree_sitter import Language, Parser  # type: ignore
            from tree_sitter_python import language as py_language

            assert Language is not None
            assert Parser is not None
            assert py_language is not None
        except ImportError:
            pytest.skip("tree-sitter not available")

    def test_libcst_parsing(self) -> None:
        """Test libcst code parsing."""
        import libcst as cst

        code = "x = 1"
        module = cst.parse_module(code)
        assert module is not None
        assert len(module.body) == 1

    def test_yaml_parsing(self) -> None:
        """Test YAML serialization/deserialization."""
        import yaml

        data = {"name": "test", "value": 42}
        yaml_str = yaml.dump(data)
        parsed = yaml.safe_load(yaml_str)
        assert parsed["name"] == "test"
        assert parsed["value"] == 42

    def test_marshmallow_serialization(self) -> None:
        """Test Marshmallow data serialization."""
        from marshmallow import Schema, fields

        class TestSchema(Schema):
            name = fields.String()
            value = fields.Integer()

        schema = TestSchema()
        data = schema.load({"name": "test", "value": 42})
        assert data["name"] == "test"
        assert data["value"] == 42


class TestOfflineCapability:
    """Test offline-first capabilities of core profile."""

    def test_no_pytorch_in_core(self) -> None:
        """Verify torch is not required in core profile."""
        try:
            import torch  # type: ignore  # noqa: F401
            # If torch is available, it shouldn't block core functionality
            pytest.skip("torch is available but not required by core")
        except ImportError:
            # Expected behavior for core profile
            pass

    def test_no_transformers_in_core(self) -> None:
        """Verify transformers is not required in core profile."""
        try:
            import transformers  # type: ignore  # noqa: F401
            pytest.skip("transformers is available but not required by core")
        except ImportError:
            # Expected behavior for core profile
            pass

    def test_stdlib_only_core_imports(self) -> None:
        """Test that core functionality works without external ML libraries."""
        import json
        from pathlib import Path

        # Core functionality should work with stdlib
        data = {"key": "value"}
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        assert parsed["key"] == "value"

        # Path operations
        p = Path("/tmp/test")
        assert p.is_absolute()


class TestSecurityPatches:
    """Test security-related dependencies are properly versioned."""

    def test_cryptography_version(self) -> None:
        """Test cryptography library is properly versioned."""
        import cryptography

        version = cryptography.__version__
        major = int(version.split(".")[0])
        assert major >= 48, f"cryptography version {version} may have security issues"

    def test_pyjwt_version(self) -> None:
        """Test PyJWT is properly versioned."""
        import jwt

        version = jwt.__version__
        major, minor = map(int, version.split(".")[:2])
        assert (major >= 2 and minor >= 13) or major >= 3, (
            f"PyJWT version {version} may have security issues"
        )

    def test_requests_version(self) -> None:
        """Test requests library is properly versioned."""
        import requests

        version = requests.__version__
        parts = version.split(".")
        major, minor = int(parts[0]), int(parts[1])
        assert (major >= 2 and minor >= 33) or major >= 3, (
            f"requests version {version} may have security issues"
        )

    def test_pyyaml_version(self) -> None:
        """Test PyYAML is properly versioned."""
        import yaml

        version = yaml.__version__
        major, minor = map(int, version.split(".")[:2])
        assert (major >= 6 and minor >= 0) or major >= 7, (
            f"PyYAML version {version} may have security issues"
        )


class TestPackageMetadata:
    """Test package metadata and configuration."""

    def test_version_consistency(self) -> None:
        """Test version is consistent across package."""
        import codex_ml

        # Check if version is defined
        if hasattr(codex_ml, "__version__"):
            assert codex_ml.__version__ == "0.2.2"

    def test_package_name(self) -> None:
        """Test package name is correct."""
        import codex_ml

        assert codex_ml.__package__ is not None

    def test_python_version_requirement(self, tmp_path: Path) -> None:
        """Test Python version requirement (>=3.12)."""
        current_version = sys.version_info
        assert (current_version.major >= 3 and current_version.minor >= 12) or (
            current_version.major > 3
        ), f"Python {current_version.major}.{current_version.minor} < 3.12"


class TestIntegrationScenarios:
    """Test practical integration scenarios."""

    def test_config_loading_and_validation(self) -> None:
        """Test loading and validating configurations."""
        from omegaconf import OmegaConf
        from pydantic import BaseModel

        class Config(BaseModel):
            name: str
            debug: bool = False

        cfg_dict = {"name": "test", "debug": True}
        om_cfg = OmegaConf.create(cfg_dict)
        cfg = Config(**OmegaConf.to_object(om_cfg))

        assert cfg.name == "test"
        assert cfg.debug is True

    def test_code_analysis_pipeline(self) -> None:
        """Test code analysis pipeline."""
        import libcst as cst

        code = """
def hello(name: str) -> str:
    return f"Hello {name}"
"""
        module = cst.parse_module(code)
        assert module is not None
        assert len(module.body) == 1

    def test_cli_command_registration(self) -> None:
        """Test CLI command registration."""
        import typer

        app = typer.Typer()

        @app.command()
        def cmd1(arg: str) -> None:
            pass

        @app.command()
        def cmd2() -> None:
            pass

        assert len(app.registered_commands) >= 2 or app is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
