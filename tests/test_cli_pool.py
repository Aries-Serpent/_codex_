"""Tests for the ``_fix_pool`` helper in :mod:`codex.cli`."""

import concurrent.futures as cf
import os

from codex.cli import _fix_pool
from codex.db import sqlite_patch


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


def test_fix_pool_sets_env(monkeypatch) -> None:
    """Calling ``_fix_pool`` enables SQLite pooling via env var."""
    monkeypatch.delenv("CODEX_SQLITE_POOL", raising=False)
    try:
        _fix_pool(max_workers=0)
        assert os.environ.get("CODEX_SQLITE_POOL") == "1"
    finally:
        executor = getattr(cf, "_executor", None)
        if executor is not None:
            executor.shutdown(wait=True)
            cf._executor = None
        sqlite_patch.disable_pooling()
