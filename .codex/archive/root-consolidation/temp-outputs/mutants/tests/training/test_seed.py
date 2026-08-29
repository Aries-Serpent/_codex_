"""Tests for src.training.seed module.

Phase 6 tests covering:
- ensure_global_seed function
- Default seed behavior
- Seed resolution logic
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


class TestEnsureGlobalSeed:
    """Tests for ensure_global_seed function."""

    @pytest.fixture
    def ensure_global_seed(self):
        """Import ensure_global_seed function."""
        try:
            from src.training.seed import ensure_global_seed

            return ensure_global_seed
        except ImportError:
            pytest.skip("src.training.seed not available")
            return None

    def test_returns_default_seed_when_none_provided(self, ensure_global_seed):
        """Test that default seed (42) is returned when None is passed."""
        with patch("src.training.seed._set_seed") as mock_set_seed:
            result = ensure_global_seed(None)
            assert result == 42, "Result must not be empty"
            mock_set_seed.assert_called_once_with(42, deterministic=True)

    def test_returns_provided_seed(self, ensure_global_seed):
        """Test that provided seed is returned."""
        with patch("src.training.seed._set_seed") as mock_set_seed:
            result = ensure_global_seed(123)
            assert result == 123, "Result must not be empty"
            mock_set_seed.assert_called_once_with(123, deterministic=True)

    def test_converts_seed_to_int(self, ensure_global_seed):
        """Test that seed is converted to int."""
        with patch("src.training.seed._set_seed") as mock_set_seed:
            result = ensure_global_seed(42.5)
            assert result == 42, "Result must not be empty"
            assert isinstance(result, int)
            mock_set_seed.assert_called_once_with(42, deterministic=True)

    def test_deterministic_flag_passed(self, ensure_global_seed):
        """Test deterministic flag is passed to set_seed."""
        with patch("src.training.seed._set_seed") as mock_set_seed:
            ensure_global_seed(42, deterministic=False)
            mock_set_seed.assert_called_once_with(42, deterministic=False)

    def test_deterministic_true_by_default(self, ensure_global_seed):
        """Test deterministic is True by default."""
        with patch("src.training.seed._set_seed") as mock_set_seed:
            ensure_global_seed(42)
            mock_set_seed.assert_called_once_with(42, deterministic=True)


class TestLegacySeedModule:
    """Tests for legacy training/seed.py shim module."""

    def test_import_legacy_shim_emits_deprecation_warning(self):
        """Test that importing legacy shim emits deprecation warning."""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                # Force reimport
                import importlib
                import sys

                if "training.seed" in sys.modules:
                    del sys.modules["training.seed"]
                importlib.import_module("training.seed")
            except ImportError:
                pytest.skip("training.seed shim not available")

            # Check for deprecation warning
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1, "Deprecation_warnings must not be empty"

    def test_legacy_shim_exports_ensure_global_seed(self):
        """Test that legacy shim exports ensure_global_seed."""
        try:
            from training.seed import ensure_global_seed

            assert callable(ensure_global_seed), "Condition must be true"
        except ImportError:
            pytest.skip("training.seed shim not available")
