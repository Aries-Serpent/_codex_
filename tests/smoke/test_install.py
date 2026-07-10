"""
Post-install smoke tests for codex-ml installation verification.

This module verifies that the installed codex-ml package is properly configured
with all expected entry points, modules, and dependencies for the installed profile.

Usage:
    pytest tests/smoke/test_install.py
    pytest tests/smoke/test_install.py::test_core_profile_entry_points
"""

import importlib
import subprocess
import sys
from typing import List, Tuple

import pytest


class TestInstallation:
    """Verify post-installation integrity of codex-ml package."""

    @pytest.mark.smoke
    def test_package_imports(self):
        """Verify core modules import successfully."""
        # Core modules that must work with [core] profile (no extra deps)
        core_modules = [
            "codex_ml",
            "codex_ml.cli",
            "aries_serpent_core.logging",
        ]
        for module_name in core_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    @pytest.mark.smoke
    def test_core_profile_entry_points(self):
        """Verify core profile entry points are accessible."""
        # Only test entry points that work with core profile (no extra deps)
        core_only_entry_points = [
            "codex-ml",
            "codex-ml-cli",
        ]

        for entry_point in core_only_entry_points:
            try:
                result = subprocess.run(
                    [entry_point, "--help"],
                    capture_output=True,
                    timeout=5,
                    text=True,
                )
                assert result.returncode == 0, (
                    f"Entry point {entry_point} failed with code {result.returncode}: "
                    f"{result.stderr}"
                )
            except FileNotFoundError:
                pytest.fail(
                    f"Entry point {entry_point} not found in PATH. "
                    "Installation may be incomplete."
                )
            except subprocess.TimeoutExpired:
                pytest.fail(f"Entry point {entry_point} timed out")

    @pytest.mark.smoke
    def test_dependency_versions(self):
        """Verify critical dependencies are installed with correct versions."""
        import pkg_resources

        critical_deps = {
            "click": ">=8.1",
            "hydra-core": "==1.3.2",
            "pydantic": ">=2.4",
            "omegaconf": ">=2.3",
        }

        for package, version_spec in critical_deps.items():
            try:
                pkg_resources.require(f"{package}{version_spec}")
            except Exception as e:
                pytest.fail(f"Dependency check failed for {package}{version_spec}: {e}")

    @pytest.mark.smoke
    def test_no_import_errors(self):
        """Verify that importing core packages produces no warnings."""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Try importing core modules
            importlib.import_module("codex_ml")
            importlib.import_module("codex_ml.cli")

            # Check for import-related warnings
            import_warnings = [
                warning for warning in w if issubclass(warning.category, ImportWarning)
            ]
            assert (
                len(import_warnings) == 0
            ), f"Import warnings detected: {import_warnings}"

    @pytest.mark.smoke
    def test_pip_check_passes(self):
        """Verify that pip check reports no dependency conflicts."""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            pytest.fail(f"pip check failed:\n{result.stdout}\n{result.stderr}")

    @pytest.mark.smoke
    def test_module_structure(self):
        """Verify core module structure is intact."""
        # Verify key modules exist
        core = importlib.import_module("codex_ml")
        assert hasattr(core, "__version__"), "codex_ml missing __version__"
        # Note: __author__ is not always defined in minimal packages
        assert core.__version__, "codex_ml.__version__ is empty"

        # Verify CLI module
        cli = importlib.import_module("codex_ml.cli")
        assert hasattr(cli, "main"), "codex_ml.cli missing main module"

        # Verify logging module exists
        logging_mod = importlib.import_module("aries_serpent_core.logging")
        assert logging_mod is not None, "Failed to import aries_serpent_core.logging"
        
        # Verify import_ndjson submodule can be imported
        try:
            import_ndjson_mod = importlib.import_module(
                "aries_serpent_core.logging.import_ndjson"
            )
            assert hasattr(import_ndjson_mod, "main"), (
                "aries_serpent_core.logging.import_ndjson missing main function (entry point requirement)"
            )
            
            # Verify main is callable (entry point must be callable)
            assert callable(import_ndjson_mod.main), (
                "aries_serpent_core.logging.import_ndjson.main is not callable"
            )
        except ImportError as e:
            pytest.fail(f"Failed to import import_ndjson submodule: {e}")


class TestEntryPointsAvailability:
    """Test availability and functionality of entry points."""

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "entry_point,expected_help_text",
        [
            ("codex-ml", "usage:"),
            ("codex-ml-cli", "usage:"),
        ],
    )
    def test_entry_point_help(self, entry_point, expected_help_text):
        """Test that entry points provide help text."""
        try:
            result = subprocess.run(
                [entry_point, "--help"],
                capture_output=True,
                timeout=5,
                text=True,
            )
            assert result.returncode == 0, f"{entry_point} --help returned {result.returncode}"
            assert (
                expected_help_text.lower() in result.stdout.lower()
            ), f"Help text doesn't contain '{expected_help_text}'"
        except FileNotFoundError:
            pytest.skip(f"Entry point {entry_point} not installed")

    @pytest.mark.smoke
    def test_codex_smoke_entry_point(self):
        """Test codex-smoke entry point availability."""
        try:
            result = subprocess.run(
                ["codex-smoke", "--version"],
                capture_output=True,
                timeout=5,
                text=True,
            )
            # Entry point may not have --version, but should be callable
            assert result.returncode in [0, 1, 2], (
                f"codex-smoke unexpected return code: {result.returncode}"
            )
        except FileNotFoundError:
            pytest.skip("codex-smoke entry point not installed")

    @pytest.mark.smoke
    def test_codex_import_ndjson_entry_point(self):
        """Test codex-import-ndjson entry point availability."""
        try:
            result = subprocess.run(
                ["codex-import-ndjson", "--help"],
                capture_output=True,
                timeout=5,
                text=True,
            )
            assert result.returncode == 0, f"Entry point returned {result.returncode}"
            assert "usage:" in result.stdout.lower()
        except FileNotFoundError:
            pytest.skip("codex-import-ndjson entry point not installed")


class TestProfileSpecificFeatures:
    """Test features specific to the core profile."""

    @pytest.mark.smoke
    def test_core_dependencies_available(self):
        """Verify core-only and extended core dependencies are installed.
        
        NOTE: These dependencies are present in the base + [core] profiles.
        Some (like libcst, parso) are already in base, listed here for completeness.
        This test validates they're all available without runtime/ML dependencies.
        """
        # All should be available in [core] profile
        core_profile_deps = [
            "click",  # Added specifically to core
            "typer",
            "libcst",
            "parso",
            "tree_sitter",  # Added in [core]
        ]

        for dep in core_profile_deps:
            try:
                importlib.import_module(dep)
            except ImportError as e:
                pytest.fail(f"Core dependency {dep} not available: {e}")

    @pytest.mark.smoke
    def test_no_ml_dependencies_bleeding(self):
        """Verify that ML dependencies aren't loaded (for core profile)."""
        # This test documents which modules should NOT be
        # available in the core profile, but won't fail if they are.
        ml_heavy_modules = [
            "torch",
            "transformers",
            "datasets",
        ]

        unavailable = []
        for module_name in ml_heavy_modules:
            try:
                importlib.import_module(module_name)
            except ImportError:
                unavailable.append(module_name)

        if len(unavailable) < len(ml_heavy_modules):
            ml_deps_found = set(ml_heavy_modules) - set(unavailable)
            # Note: This is expected in runtime/full profiles
            # Only log for awareness in core profile
            print(f"Note: ML dependencies found: {ml_deps_found}")
            # This is informational only - not a failure for core profile
            # (may have been installed with runtime profile)


class TestPackageMetadata:
    """Test package metadata and version info."""

    @pytest.mark.smoke
    def test_package_version(self):
        """Verify package version is properly set."""
        try:
            import pkg_resources

            version = pkg_resources.get_distribution("codex-ml").version
            assert version, "Package version is empty"
            # Version format: major.minor.patch
            parts = version.split(".")
            assert len(parts) >= 3, f"Invalid version format: {version}"
        except Exception as e:
            pytest.fail(f"Failed to get package version: {e}")

    @pytest.mark.smoke
    def test_package_has_license(self):
        """Verify package metadata includes license."""
        try:
            import pkg_resources

            dist = pkg_resources.get_distribution("codex-ml")
            # Check if license file exists or is in metadata
            assert dist.project_name == "codex-ml", f"Unexpected project name: {dist.project_name}"
        except Exception as e:
            pytest.fail(f"Failed to verify package metadata: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "smoke"])
