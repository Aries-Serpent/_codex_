"""Tests for src.training.seed module.

Phase 6 tests covering:
- ensure_global_seed function
- Default seed behavior
- Seed resolution logic
"""

from __future__ import annotations

import importlib
import warnings
from unittest.mock import patch

import pytest


class TestEnsureGlobalSeed:
    """Tests for ensure_global_seed function."""

    @pytest.fixture
    def ensure_global_seed(self):
        """Import ensure_global_seed function."""
        try:
            from training.seed import ensure_global_seed

            return ensure_global_seed
        except ImportError:
            pytest.skip("src.training.seed not available")
            return None

    def test_returns_default_seed_when_none_provided(self, ensure_global_seed):
        """Test that default seed (42) is returned when None is passed."""
        with patch("training.seed._set_seed") as mock_set_seed:
            result = ensure_global_seed(None)
            assert result == 42, "Result must not be empty"
            mock_set_seed.assert_called_once_with(42, deterministic=True)

    def test_returns_provided_seed(self, ensure_global_seed):
        """Test that provided seed is returned."""
        with patch("training.seed._set_seed") as mock_set_seed:
            result = ensure_global_seed(123)
            assert result == 123, "Result must not be empty"
            mock_set_seed.assert_called_once_with(123, deterministic=True)

    def test_converts_seed_to_int(self, ensure_global_seed):
        """Test that seed is converted to int."""
        with patch("training.seed._set_seed") as mock_set_seed:
            result = ensure_global_seed(42.5)
            assert result == 42, "Result must not be empty"
            assert isinstance(result, int)
            mock_set_seed.assert_called_once_with(42, deterministic=True)

    def test_deterministic_flag_passed(self, ensure_global_seed):
        """Test deterministic flag is passed to set_seed."""
        with patch("training.seed._set_seed") as mock_set_seed:
            ensure_global_seed(42, deterministic=False)
            mock_set_seed.assert_called_once_with(42, deterministic=False)

    def test_deterministic_true_by_default(self, ensure_global_seed):
        """Test deterministic is True by default."""
        with patch("training.seed._set_seed") as mock_set_seed:
            ensure_global_seed(42)
            mock_set_seed.assert_called_once_with(42, deterministic=True)


class TestTrainingSeedModule:
    """Tests for the training.seed module."""

    def test_import_does_not_emit_deprecation_warning(self):
        """Importing the current training.seed module is not deprecated."""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            # Importing the training package may also load this unrelated,
            # deprecated tokenizer compatibility module.
            warnings.filterwarnings(
                "ignore",
                message=r"codex_ml\.interfaces\.tokenizer_hf is deprecated;.*",
                category=DeprecationWarning,
            )
            module = importlib.import_module("training.seed")
            importlib.reload(module)

        assert not any(issubclass(item.category, DeprecationWarning) for item in caught)

    def test_module_exports_ensure_global_seed(self):
        """Test that training.seed exports ensure_global_seed."""
        from training.seed import ensure_global_seed

        assert callable(ensure_global_seed), "Condition must be true"
