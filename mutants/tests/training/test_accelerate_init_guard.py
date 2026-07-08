"""
Tests for training.accelerate_init_guard module.

This module contains tests for the legacy accelerate_init_guard compatibility layer.
"""

import warnings


class TestLegacyImport:
    """Tests for legacy import compatibility."""

    def test_import_functions_exist(self):
        """Test all exported functions exist."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from training.accelerate_init_guard import (
                AccelerateInitResult,
                get_distributed_env_info,
                is_accelerate_available,
                is_gpu_available,
                safe_accelerate_init,
            )

            # All should be importable
            assert AccelerateInitResult is not None, "AccelerateInitResult must be initialized"
            assert callable(get_distributed_env_info), "Condition must be true"
            assert callable(is_accelerate_available), "Condition must be true"
            assert callable(is_gpu_available), "Condition must be true"
            assert callable(safe_accelerate_init), "Condition must be true"

    def test_all_exports(self):
        """Test __all__ exports."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from training.accelerate_init_guard import __all__

            expected = [
                "AccelerateInitResult",
                "get_distributed_env_info",
                "is_accelerate_available",
                "is_gpu_available",
                "safe_accelerate_init",
            ]

            for item in expected:
                assert item in __all__, "Item must not be empty"

    def test_is_accelerate_available(self):
        """Test is_accelerate_available returns bool."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from training.accelerate_init_guard import is_accelerate_available

            result = is_accelerate_available()
            assert isinstance(result, bool)

    def test_is_gpu_available(self):
        """Test is_gpu_available returns bool."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from training.accelerate_init_guard import is_gpu_available

            result = is_gpu_available()
            # Should return bool (True or False depending on environment)
            assert isinstance(result, bool)

    def test_get_distributed_env_info(self):
        """Test get_distributed_env_info returns dict."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from training.accelerate_init_guard import get_distributed_env_info

            result = get_distributed_env_info()
            assert isinstance(result, dict)
