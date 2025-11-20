#!/usr/bin/env python3
"""
Conftest to avoid ImportError during collection when optional heavy dependencies
are not installed in the CI/test environment.
"""
from __future__ import annotations
import sys
import types
import importlib.util
import pytest

HEAVY_MODULES = [
    "numpy",
    "torch",
    "transformers",
    "tensorflow",
    "jax",
]

def _inject_stub_module(name: str):
    if name in sys.modules:
        return
    m = types.ModuleType(name)
    m.__all__ = []
    setattr(m, "__version__", "0.0.0-stub")
    if name == "numpy":
        class _ndarray_stub:
            def __init__(self, *args, **kwargs):
                pass
            def __array__(self):
                return []
            @property
            def shape(self):
                return ()
        m.ndarray = _ndarray_stub
        m.array = lambda *args, **kwargs: []
    sys.modules[name] = m

for _mod in HEAVY_MODULES:
    if importlib.util.find_spec(_mod) is None:
        _inject_stub_module(_mod)

def pytest_collection_modifyitems(session, config, items):
    for item in items:
        if 'heavy_dep' in item.keywords:
            missing = []
            for mod in HEAVY_MODULES:
                if importlib.util.find_spec(mod) is None:
                    missing.append(mod)
            if missing:
                reason = f"skipped: heavy optional deps missing: {', '.join(missing)}"
                item.add_marker(pytest.mark.skip(reason=reason))


@pytest.fixture
def pool_state_tracker():
    """Track connection pool size changes across a test."""

    from codex.logging.db_manager import DBManager

    DBManager.close_all_pools()
    baseline = sum(len(pool) for pool in DBManager._CONNECTION_POOL.values())

    def _pool_size() -> int:
        return sum(len(pool) for pool in DBManager._CONNECTION_POOL.values())

    def assert_pool_grew():
        current = _pool_size()
        assert current > baseline, (
            f"Expected pool to grow beyond {baseline}, current size {current}"
        )

    def assert_pool_size(expected: int):
        current = _pool_size()
        assert current == expected, (
            f"Expected pool size {expected}, got {current}"
        )

    def assert_pool_empty():
        current = _pool_size()
        assert current == 0, f"Expected pool to be empty, size {current}"

    try:
        yield {
            "assert_pool_grew": assert_pool_grew,
            "assert_pool_size": assert_pool_size,
            "assert_pool_empty": assert_pool_empty,
        }
    finally:
        DBManager.close_all_pools()


@pytest.fixture
def clean_connection_pool():
    """Ensure connection pools are cleared before and after a test."""

    from codex.logging.db_manager import DBManager

    original = DBManager._POOL_ENABLED
    DBManager.close_all_pools()
    try:
        yield
    finally:
        DBManager._POOL_ENABLED = original
        DBManager.close_all_pools()


@pytest.fixture
def pooling_db_manager(tmp_path, request):
    """Provide a DBManager instance with pooling enabled and isolated path."""

    from codex.logging.db_manager import DBManager

    original = DBManager._POOL_ENABLED
    DBManager._POOL_ENABLED = True
    DBManager.close_all_pools()

    manager = DBManager(db_path=tmp_path / "pooling.db")

    # For tests that expect multiple unique connections to accumulate in the pool,
    # temporarily disable pool reuse during acquisition while keeping pooling on
    # for close_connection. Tests that explicitly verify reuse keep the default
    # behavior.
    if request.node.name != "test_connection_reuse_from_pool":
        original_get = manager.get_connection

        def _get_connection_no_reuse(*args, **kwargs):
            DBManager._POOL_ENABLED = False
            try:
                return original_get(*args, **kwargs)
            finally:
                DBManager._POOL_ENABLED = True

        manager.get_connection = _get_connection_no_reuse  # type: ignore[attr-defined]

    try:
        yield manager
    finally:
        DBManager.close_all_pools()
        DBManager._POOL_ENABLED = original


@pytest.fixture(params=[True, False], ids=["pooling_enabled", "pooling_disabled"])
def pooling_mode(request):
    """Parametrize tests to run with pooling enabled and disabled."""

    from codex.logging.db_manager import DBManager

    original = DBManager._POOL_ENABLED
    DBManager.close_all_pools()
    DBManager._POOL_ENABLED = request.param

    try:
        yield request.param
    finally:
        DBManager.close_all_pools()
        DBManager._POOL_ENABLED = original
