"""
Test Safety Import No Crash

Test module for safety import no crash.
"""
import pytest
    from codex_ml.safety import SafetyFilters


def test_import_safety_filters_no_crash():
    # Importing the safety package should not fail on platforms where
    # POSIX-only modules (e.g., `resource`) are unavailable. The package
    # should expose SafetyFilters regardless.

    assert SafetyFilters is not None, "SafetyFilters must be initialized"
