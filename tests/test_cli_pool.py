"""Tests for the ``_fix_pool`` helper in :mod:`codex.cli`."""

import concurrent.futures as cf

from codex.cli import _fix_pool


def test_fix_pool_executor_created() -> None:
    """Ensure ``_fix_pool`` installs a global thread executor."""
    try:
        _fix_pool(max_workers=2)
        executor = getattr(cf, "_executor", None)
        assert isinstance(executor, cf.ThreadPoolExecutor)
        assert executor._max_workers == 2
        fut = executor.submit(lambda: 41 + 1)
        assert fut.result() == 42
    finally:
        executor = getattr(cf, "_executor", None)
        if executor is not None:
            executor.shutdown(wait=True)
            cf._executor = None
