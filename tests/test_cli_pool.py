"""Tests for the ``_fix_pool`` helper in :mod:`codex.cli`."""

import concurrent.futures as cf
import os
import sqlite3

from codex.cli import _fix_pool
from codex.db import sqlite_patch


def test_fix_pool_executor_created() -> None:
    """Ensure ``_fix_pool`` installs a global thread executor."""
    try:
        _fix_pool(max_workers=2)
        executor = getattr(cf, "_executor", None)
        assert isinstance(executor, cf.ThreadPoolExecutor)
        assert executor._max_workers == 2, "_max_workers is not valid"
        fut = executor.submit(lambda: 41 + 1)
        assert fut.result() == 42, "Result must not be empty"
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
        assert os.environ.get("CODEX_SQLITE_POOL") == "1", "Condition must be true"
    finally:
        executor = getattr(cf, "_executor", None)
        if executor is not None:
            executor.shutdown(wait=True)
            cf._executor = None
        sqlite_patch.disable_pooling()


# ---------------------------------------------------------------------------
# Gap C: _fix_pool warm loop — sqlite3.Error / OSError exception handling
# ---------------------------------------------------------------------------


def _cleanup_pool() -> None:
    executor = getattr(cf, "_executor", None)
    if executor is not None:
        executor.shutdown(wait=True)
        cf._executor = None
    sqlite_patch.disable_pooling()


def _get_cli_click_module():
    """Return the underlying cli.py module where _fix_pool and sqlite3 live."""
    import sys

    # The function is loaded as codex._cli_click (the physical cli.py file)
    return sys.modules["codex._cli_click"]


def test_fix_pool_sqlite_operational_error_aborts_warm_loop_no_propagation(
    monkeypatch,
) -> None:
    """_fix_pool with sqlite3.connect raising OperationalError does not propagate."""
    cli_module = _get_cli_click_module()

    monkeypatch.setattr(
        cli_module,
        "sqlite3",
        type(
            "FakeSqlite3",
            (),
            {
                "connect": staticmethod(
                    lambda *a, **kw: (_ for _ in ()).throw(
                        sqlite3.OperationalError("disk I/O error")
                    )
                ),
                "Error": sqlite3.Error,
            },
        )(),
    )
    try:
        # Must not raise
        _fix_pool(max_workers=2)
    finally:
        _cleanup_pool()


def test_fix_pool_oserror_aborts_warm_loop_no_propagation(
    monkeypatch,
) -> None:
    """_fix_pool with sqlite3.connect raising OSError does not propagate."""
    cli_module = _get_cli_click_module()

    monkeypatch.setattr(
        cli_module,
        "sqlite3",
        type(
            "FakeSqlite3",
            (),
            {
                "connect": staticmethod(
                    lambda *a, **kw: (_ for _ in ()).throw(OSError("no such device"))
                ),
                "Error": sqlite3.Error,
            },
        )(),
    )
    try:
        # Must not raise
        _fix_pool(max_workers=2)
    finally:
        _cleanup_pool()
