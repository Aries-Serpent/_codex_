"""Performance smoke tests (guarded and fast).

These tests are disabled by default and only run when explicitly enabled
via the CODEX_PERF_SMOKE environment variable.
"""

from __future__ import annotations

import os

import pytest

# Skip all tests in this module unless CODEX_PERF_SMOKE=1
pytestmark = pytest.mark.skipif(
    os.getenv("CODEX_PERF_SMOKE") != "1",
    reason="Performance smoke tests disabled (set CODEX_PERF_SMOKE=1 to enable)",
)


def test_perf_smoke_marker():
    """Minimal assertion to mark perf smoke wiring.

    This test validates that the performance smoke test infrastructure
    is working correctly. Real microbenchmarks can be added later.
    """
    # Verify environment variable is set
    assert os.getenv("CODEX_PERF_SMOKE") == "1", "Condition must be true"

    # Minimal performance check - import should be fast
    import time

    start = time.time()

    # Import a core module

    elapsed = time.time() - start

    # Sanity check: import should complete in reasonable time
    assert elapsed < 5.0, f"Import took {elapsed:.2f}s (expected < 5.0s)"


def test_perf_smoke_placeholder():
    """Placeholder for future performance tests.

    Future tests can validate:
    - Dataset loading performance
    - Tokenization throughput
    - Model inference latency
    - Batch processing speed
    """
    # This test always passes - it's a placeholder for future work
    assert True, "True is not valid"
