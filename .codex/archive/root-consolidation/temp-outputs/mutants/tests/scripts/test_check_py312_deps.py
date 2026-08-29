"""
Test check_py312_deps.py script.

Ensures dependency compatibility checker works correctly.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def cleanup_mocks():
    """Automatically reset all mocks after each test."""
    yield
    mock.patch.stopall()


import importlib.util

# Import the script module
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Load the script as a module
script_path = Path(__file__).parent.parent.parent / "scripts" / "check_py312_deps.py"
spec = importlib.util.spec_from_file_location("check_py312_deps", script_path)
check_py312_deps = importlib.util.module_from_spec(spec)
sys.modules["check_py312_deps"] = check_py312_deps
spec.loader.exec_module(check_py312_deps)

# Import functions from the loaded module
from check_py312_deps import (
    check_package_py312_support,
    load_dependencies_from_pyproject,
    parse_dependency_spec,
)


class TestParseDependencySpec:
    """Test dependency specification parsing."""

    def test_simple_package(self):
        """Test parsing simple package name."""
        name, constraint, is_conditional = parse_dependency_spec("numpy")
        assert name == "numpy", "name is not valid"
        assert constraint is None, "constraint is not valid"
        assert is_conditional is False, "is_conditional is not valid"

    def test_package_with_version(self):
        """Test parsing package with version constraint."""
        name, constraint, is_conditional = parse_dependency_spec("numpy>=1.26,<3")
        assert name == "numpy", "name is not valid"
        assert constraint == ">=1.26,<3"
        assert is_conditional is False, "is_conditional is not valid"

    def test_package_with_extras(self):
        """Test parsing package with extras."""
        name, constraint, is_conditional = parse_dependency_spec("ray[serve]>=2.9,<3")
        assert name == "ray", "name is not valid"
        assert constraint == ">=2.9,<3"
        assert is_conditional is False, "is_conditional is not valid"

    def test_package_with_exact_version(self):
        """Test parsing package with exact version."""
        name, constraint, is_conditional = parse_dependency_spec("hydra-core==1.3.2")
        assert name == "hydra-core", "name is not valid"
        assert constraint == "==1.3.2", "constraint is not valid"
        assert is_conditional is False, "is_conditional is not valid"

    def test_conditional_dependency(self):
        """Test parsing conditional dependency with environment marker."""
        name, _constraint, is_conditional = parse_dependency_spec(
            "importlib-metadata; python_version < '3.10'"
        )
        assert name == "importlib-metadata", "Data must not be empty"
        assert is_conditional is True, "is_conditional is not valid"


class TestCheckPackagePy312Support:
    """Test package Python 3.12 support checking."""

    @patch("subprocess.run")
    def test_compatible_package(self, mock_run):
        """Test checking a compatible package."""
        # Mock pip index versions
        mock_run.side_effect = [
            MagicMock(
                returncode=0,
                stdout="Available versions: 2.0.0, 1.9.0\nBest match: 2.0.0",
                stderr="",
            ),
            MagicMock(
                returncode=0,
                stdout="Name: numpy\nVersion: 2.0.0\nRequires-Python: >=3.9",
                stderr="",
            ),
        ]

        result = check_package_py312_support("numpy")

        assert result["name"] == "numpy", "Result must not be empty"
        assert result["supports_312"] is True, "Result must not be empty"
        assert result["error"] is None, "Result must not be empty"

    @patch("subprocess.run")
    def test_package_with_312_explicit(self, mock_run):
        """Test package that explicitly mentions 3.12."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="Available versions: 1.0.0", stderr=""),
            MagicMock(
                returncode=0,
                stdout="Name: test\nVersion: 1.0.0\nRequires-Python: >=3.11,<3.13",
                stderr="",
            ),
        ]

        result = check_package_py312_support("test")

        assert result["supports_312"] is True, "Result must not be empty"

    @patch("subprocess.run")
    def test_package_query_error(self, mock_run):
        """Test handling of package query error."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="ERROR: No matching distribution found",
        )

        result = check_package_py312_support("nonexistent-package")

        assert result["error"] is not None, "Value must be initialized"
        assert "Failed to query PyPI" in result["error"], "Result must not be empty"

    @patch("subprocess.run")
    def test_timeout_handling(self, mock_run):
        """Test timeout handling during package check."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("pip", 30)

        result = check_package_py312_support("slow-package")

        assert result["error"] == "Timeout querying PyPI", "Result must not be empty"


class TestLoadDependenciesFromPyproject:
    """Test loading dependencies from pyproject.toml."""

    def test_loads_dependencies(self):
        """Test that dependencies are loaded successfully."""
        deps = load_dependencies_from_pyproject()

        assert isinstance(deps, list)
        assert len(deps) > 0, "Deps must not be empty"

        # Check for known dependencies
        dep_names = [parse_dependency_spec(d)[0] for d in deps]
        assert "pytest" in dep_names or "numpy" in dep_names or "torch" in dep_names

    def test_includes_optional_dependencies(self):
        """Test that optional dependencies are included."""
        deps = load_dependencies_from_pyproject()

        # Should include both main and optional dependencies
        assert len(deps) > 30, "Deps must not be empty"


class TestMain:
    """Test main function integration."""

    @patch("check_py312_deps.load_dependencies_from_pyproject")
    @patch("check_py312_deps.check_package_py312_support")
    def test_main_all_compatible(self, mock_check, mock_load):
        """Test main function with all compatible packages."""
        mock_load.return_value = ["numpy>=1.26", "torch>=2.0"]
        mock_check.return_value = {
            "name": "test",
            "version": "1.0.0",
            "supports_312": True,
            "latest_version": "1.0.0",
            "python_requires": ">=3.9",
            "error": None,
        }

        from check_py312_deps import main

        with patch("builtins.print"):  # Suppress output
            exit_code = main()

        assert exit_code == 0, "exit_code is not valid"

    @patch("check_py312_deps.load_dependencies_from_pyproject")
    @patch("check_py312_deps.check_package_py312_support")
    def test_main_with_incompatible(self, mock_check, mock_load):
        """Test main function with incompatible package."""
        mock_load.return_value = ["old-package==1.0"]
        mock_check.return_value = {
            "name": "old-package",
            "version": "1.0.0",
            "supports_312": False,
            "latest_version": "1.0.0",
            "python_requires": ">=3.8,<3.11",
            "error": None,
        }

        from check_py312_deps import main

        with patch("builtins.print"):  # Suppress output
            exit_code = main()

        assert exit_code == 1, "exit_code is not valid"


@pytest.mark.integration
class TestIntegration:
    """Integration tests for dependency checker."""

    def test_script_runs_without_error(self):
        """Test that script runs without crashing."""
        import subprocess

        result = subprocess.run(
            [sys.executable, "scripts/check_py312_deps.py"],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutes timeout
            cwd=Path(__file__).parent.parent.parent,
        )

        # Script should run (may pass or fail depending on actual compatibility)
        assert result.returncode in [0, 1]
        assert "Python 3.12 Dependency Compatibility Checker" in result.stdout, "Result must not be empty"
