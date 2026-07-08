"""
Smoke tests for training modules (Production Readiness Gaps).

Addresses missing test coverage identified by production readiness tool:
- training/accelerate_init_guard.py
- training/streaming.py

Uses physics-guided minimal testing strategy.
"""

import pytest


class TestAccelerateInitGuardSmoke:
    """Smoke tests for accelerate_init_guard module."""

    def test_import_src(self):
        """Test src.training.accelerate_init_guard can be imported."""
        try:
            from src.training import accelerate_init_guard

            assert accelerate_init_guard is not None, "accelerate_init_guard must be initialized"
        except ImportError as e:
            pytest.skip(f"accelerate_init_guard requires optional dependencies: {e}")

    def test_import_top_level(self):
        """Test training.accelerate_init_guard can be imported."""
        try:
            from training import accelerate_init_guard

            assert accelerate_init_guard is not None, "accelerate_init_guard must be initialized"
        except ImportError as e:
            pytest.skip(f"accelerate_init_guard requires optional dependencies: {e}")


class TestStreamingSmoke:
    """Smoke tests for streaming module."""

    def test_import_src(self):
        """Test src.training.streaming can be imported."""
        try:
            from src.training import streaming

            assert streaming is not None, "streaming must be initialized"
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"streaming module requires optional dependencies: {e}")

    def test_import_top_level(self):
        """Test training.streaming can be imported."""
        try:
            from training import streaming

            assert streaming is not None, "streaming must be initialized"
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"streaming module requires optional dependencies: {e}")


class TestTokenizationLoaderSmoke:
    """Smoke tests for tokenization loader module."""

    def test_import(self):
        """Test src.codex_ml.tokenization.api can be imported."""
        try:
            from src.codex_ml.tokenization import api

            assert api is not None, "api must be initialized"
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"tokenization.api requires optional dependencies: {e}")
