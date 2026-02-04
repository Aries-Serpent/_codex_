"""
Smoke Test Suite for Production Readiness

This package contains smoke tests that verify basic functionality
of critical system components. These tests are designed to:

1. Run quickly (< 30 seconds total)
2. Catch obvious regressions
3. Verify module imports and basic operations
4. Test integration points between modules

Usage:
    pytest tests/smoke/ -v
    pytest tests/smoke/test_readiness_smoke.py -v -k "test_memory"
"""

__all__ = []
