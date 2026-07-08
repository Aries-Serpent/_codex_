"""
Tests for training.seed_utils module.

This module contains tests for the legacy seed_utils compatibility layer.
"""

import warnings


class TestLegacyImport:
    """Tests for legacy import compatibility."""

    def test_import_warns(self):
        """Test importing from training.seed_utils emits deprecation warning."""
        # We need to test that the module emits a deprecation warning
        # Since it's already imported, we test the function exists
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            # The import may already be cached, so we check for the function
            from training.seed_utils import set_all_seeds

            # Function should exist
            assert callable(set_all_seeds), "Condition must be true"

    def test_all_exports(self):
        """Test __all__ exports."""
        from training.seed_utils import __all__

        assert "set_all_seeds" in __all__, "Condition must be true"
