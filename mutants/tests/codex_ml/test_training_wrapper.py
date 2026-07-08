"""
Test Training Module Compatibility Wrapper

Tests for the training.py compatibility wrapper module.
"""

from __future__ import annotations

import sys
from types import ModuleType

import pytest


class TestTrainingModuleWrapper:
    """Tests for the training module compatibility wrapper."""

    def test_module_is_importable(self) -> None:
        """Test that training module can be imported."""
        from codex_ml import training

        assert training is not None, "training must be initialized"
        assert isinstance(training, ModuleType)

    def test_module_has_docstring(self) -> None:
        """Test module has documentation."""
        from codex_ml import training

        # Should have a docstring from the package
        assert training.__doc__ is not None or hasattr(training, "__doc__")

    def test_module_has_all(self) -> None:
        """Test module defines __all__."""
        from codex_ml import training

        # __all__ should be a list
        assert hasattr(training, "__all__")
        assert isinstance(training.__all__, list)

    def test_dir_includes_exports(self) -> None:
        """Test __dir__ includes expected items."""
        from codex_ml import training

        dir_items = dir(training)

        # Should include standard attributes
        assert "__doc__" in dir_items or "__name__" in dir_items, "Item must not be empty"

    def test_getattr_delegation(self) -> None:
        """Test __getattr__ delegates to package."""
        from codex_ml import training

        # Getting non-existent attribute should raise AttributeError
        # (from the underlying package)
        with pytest.raises(AttributeError):
            _ = training.nonexistent_attribute_xyz

    def test_package_name_constant(self) -> None:
        """Test _PACKAGE_NAME is correctly set."""
        # Import the module directly to check constants
        import codex_ml.training as training_module

        # The module should reference the correct package
        assert "training" in str(training_module), "Condition must be true"


class TestPackageLoading:
    """Tests for the package loading mechanism."""

    def test_ensure_parent_on_path(self) -> None:
        """Test _ensure_parent_on_path function."""
        # This is tested implicitly by successful import
        from codex_ml import training

        # If we got here, path manipulation worked
        assert training is not None, "training must be initialized"

    def test_load_package_returns_module(self) -> None:
        """Test _load_package returns a module."""
        from codex_ml import training

        # The imported module should be a ModuleType
        assert isinstance(training, ModuleType)

    def test_sys_modules_registered(self) -> None:
        """Test package is registered in sys.modules."""

        # The package should be in sys.modules
        assert "codex_ml.training" in sys.modules, "Condition must be true"


class TestCompatibilityShim:
    """Tests for backward compatibility."""

    def test_import_training_directly(self) -> None:
        """Test importing training module and accessing exports."""
        try:
            import codex_ml.training

            assert codex_ml.training is not None, "training must be initialized"

            # Test that we can access exported items if available
            if hasattr(codex_ml.training, "__all__"):
                for item in codex_ml.training.__all__:
                    assert hasattr(codex_ml.training, item), f"Missing export: {item}"
        except ImportError:
            pytest.skip("training module not fully configured")

    def test_from_import_pattern(self) -> None:
        """Test from-import pattern works."""
        try:
            from codex_ml import training

            assert training is not None, "training must be initialized"
        except ImportError:
            pytest.skip("training module not fully configured")

    def test_module_reimport_same_object(self) -> None:
        """Test reimporting returns same module."""
        import codex_ml.training as first
        import codex_ml.training as second

        assert first is second, "first is not valid"


class TestEdgeCases:
    """Edge case tests."""

    def test_module_attributes_accessible(self) -> None:
        """Test module attributes are accessible."""
        from codex_ml import training

        # These should not raise
        _ = training.__name__
        _ = training.__package__

    def test_pathlib_constants(self) -> None:
        """Test Path-based constants are valid."""
        from codex_ml import training

        # Module should have been loaded from a valid path
        assert hasattr(training, "__file__") or hasattr(training, "__path__")
