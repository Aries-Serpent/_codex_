#!/usr/bin/env python3
"""
Conftest to avoid ImportError during collection when optional heavy dependencies
are not installed in the CI/test environment.
"""
from __future__ import annotations

import importlib
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Ensure local stub packages (e.g., ./yaml, ./omegaconf) do not shadow real
# site-packages modules when they are installed. We still keep the repository
# root on sys.path for project imports but move it to the end of the search
# order so optional dependency discovery prefers the genuine distributions.
if (repo_str := str(REPO_ROOT)) in sys.path:
    sys.path.remove(repo_str)
    sys.path.append(repo_str)

HEAVY_MODULES = [
    "numpy",
    "torch",
    "transformers",
    "tensorflow",
    "jax",
    "sentencepiece",
]

OPTIONAL_DEP_MARKERS: dict[str, list[str]] = {
    "requires_torch": ["torch"],
    "requires_transformers": ["transformers"],
    "requires_tensorflow": ["tensorflow"],
    "requires_jax": ["jax"],
    "requires_numpy": ["numpy"],
    "requires_sentencepiece": ["sentencepiece"],
}

def _is_stub_module(name: str, spec: importlib.machinery.ModuleSpec | None = None) -> bool:
    """Return True when ``name`` resolves to an in-repo stub instead of the real package."""

    module = sys.modules.get(name)
    if getattr(module, "IS_CODEX_STUB", False):
        return True

    spec = spec or importlib.util.find_spec(name)
    if spec is None:
        return False

    origin = getattr(spec, "origin", None)
    if not origin:
        return False

    origin_path = Path(origin).resolve()
    return origin_path.is_relative_to(REPO_ROOT / name)


def _find_spec_prefer_real(modname: str) -> importlib.machinery.ModuleSpec | None:
    """Resolve ``modname`` while preferring non-stub site-packages specs."""

    primary_spec = importlib.util.find_spec(modname)
    if primary_spec and not _is_stub_module(modname, primary_spec):
        return primary_spec

    clean_paths = [
        p
        for p in sys.path
        if not Path(p).resolve().is_relative_to(REPO_ROOT)
    ]
    alternate = importlib.machinery.PathFinder.find_spec(modname, clean_paths)
    if alternate and not _is_stub_module(modname, alternate):
        return alternate

    return primary_spec or alternate


def _missing_modules(modules: list[str]) -> list[str]:
    missing: list[str] = []

    for mod in modules:
        spec = _find_spec_prefer_real(mod)
        if spec is None or _is_stub_module(mod, spec):
            missing.append(mod)

    return missing


_ORIGINAL_IMPORTORSKIP = pytest.importorskip


def _importorskip_optional_dep(
    modname: str,
    minversion: str | None = None,
    reason: str | None = None,
):
    """Skip when ``modname`` only resolves to an in-repo stub.

    ``pytest.importorskip`` treats stub packages as if the real dependency is installed,
    which causes guarded tests to run and fail on attribute errors. This wrapper checks
    whether the resolved module is a local stub and forces a skip so the tests behave as
    expected when optional ML dependencies are absent.
    """

    spec = _find_spec_prefer_real(modname)
    if spec is None or _is_stub_module(modname, spec):
        message = reason or f"{modname} is not installed"
        raise pytest.skip.Exception(message, allow_module_level=True)

    return _ORIGINAL_IMPORTORSKIP(modname, minversion=minversion, reason=reason)


pytest.importorskip = _importorskip_optional_dep

def pytest_collection_modifyitems(session, config, items):
    for item in items:
        for marker, modules in OPTIONAL_DEP_MARKERS.items():
            if marker in item.keywords:
                missing = _missing_modules(modules)
                if missing:
                    reason = f"skipped: optional dependency missing for {marker}: {', '.join(missing)}"
                    item.add_marker(pytest.mark.skip(reason=reason))

        if 'heavy_dep' in item.keywords:
            missing = _missing_modules(HEAVY_MODULES)
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
    if request.node.get_closest_marker("pool_disable_reuse"):
        original_get = manager.get_connection

        def _get_connection_no_reuse(*args, **kwargs):
            original_pooling_state = DBManager._POOL_ENABLED
            DBManager._POOL_ENABLED = False
            try:
                return original_get(*args, **kwargs)
            finally:
                DBManager._POOL_ENABLED = original_pooling_state

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
