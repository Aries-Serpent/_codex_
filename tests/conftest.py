#!/usr/bin/env python3
"""
Conftest to avoid ImportError during collection when optional heavy dependencies
are not installed in the CI/test environment.
"""
from __future__ import annotations

import importlib
import importlib.machinery
import importlib.util
import logging
import os
import random
import sys
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"


def pytest_configure(config: pytest.Config) -> None:
    """Relax coverage enforcement during collection-only runs.

    The repository defaults enforce a coverage threshold via ``pytest.ini``. When
    running in ``--collect-only`` mode (as used by smoke checks for import
    validation), no tests execute and coverage would be reported as zero, causing
    an unnecessary failure. This hook disables coverage enforcement and raises
    the fail-under floor to zero for collection-only invocations while keeping
    the existing defaults for actual test runs.
    """

    if getattr(config.option, "collectonly", False):
        if hasattr(config.option, "cov_fail_under"):
            config.option.cov_fail_under = 0
        cov_plugin = config.pluginmanager.get_plugin("_cov")
        if cov_plugin:
            config.pluginmanager.unregister(cov_plugin)


# Ensure local stub packages (e.g., ./yaml, ./omegaconf) do not shadow real
# site-packages modules when they are installed. We still keep the repository
# root on sys.path for project imports but move it to the end of the search
# order so optional dependency discovery prefers the genuine distributions.
if (src_str := str(SRC_ROOT)) not in sys.path:
    sys.path.insert(0, src_str)
if (repo_str := str(REPO_ROOT)) in sys.path:
    sys.path.remove(repo_str)
    sys.path.append(repo_str)

_ALIASES = {
    "data": "src.data",
    "security": "src.security",
}
for alias, target in _ALIASES.items():
    try:
        sys.modules[alias] = importlib.import_module(target)
    except (ImportError, ModuleNotFoundError) as exc:
        logger.debug(f"Could not create alias {alias} -> {target}: {exc}")
        continue

try:
    utils_pkg = importlib.import_module("utils")
    if hasattr(utils_pkg, "__path__"):
        utils_pkg.__path__.append(str(SRC_ROOT / "utils"))
        utils_pkg.__path__.append(str(REPO_ROOT / "utils"))
    sys.modules["utils"] = utils_pkg
except (ImportError, ModuleNotFoundError) as exc:
    logger.debug(f"Could not set up utils package: {exc}")
    try:
        sys.modules["utils"] = importlib.import_module("src.utils")
    except (ImportError, ModuleNotFoundError) as nested_exc:
        # Fallback failed - utils package unavailable, tests will skip if needed
        logger.debug(f"Could not import src.utils: {nested_exc}")

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

    try:
        primary_spec = importlib.util.find_spec(modname)
    except ValueError:
        primary_spec = None
    if primary_spec and not _is_stub_module(modname, primary_spec):
        return primary_spec

    clean_paths = [p for p in sys.path if not Path(p).resolve().is_relative_to(REPO_ROOT)]
    try:
        alternate = importlib.machinery.PathFinder.find_spec(modname, clean_paths)
    except ValueError:
        alternate = None
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
                    reason = (
                        f"skipped: optional dependency missing for {marker}: {', '.join(missing)}"
                    )
                    item.add_marker(pytest.mark.skip(reason=reason))

        if "heavy_dep" in item.keywords:
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
        assert (
            current > baseline
        ), f"Expected pool to grow beyond {baseline}, current size {current}"

    def assert_pool_size(expected: int):
        current = _pool_size()
        assert current == expected, f"Expected pool size {expected}, got {current}"

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


@pytest.fixture(autouse=True)
def set_deterministic_seed():
    """
    Autouse fixture to set deterministic seeds for randomness sources.
    This prevents flakiness arising from non-deterministic RNG state.
    """
    seed = int(os.environ.get("CODEX_TEST_SEED", "42"))
    random.seed(seed)

    # Guard optional numpy usage without adding a hard dependency
    try:
        import numpy as np

        np.random.seed(seed)
    except Exception:  # pragma: no cover - numpy not required for all environments
        pass

    # Guard optional torch usage without adding a hard dependency
    try:
        import torch

        torch.manual_seed(seed)
        # If using CUDA in CI, prefer CPU determinism by default.
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            # Optional deterministic flags (may slow tests)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except Exception:
        # Torch not installed or not desired in CI; ignore.
        pass

    yield
    # nothing to cleanup; leave RNG state as-is for test isolation
