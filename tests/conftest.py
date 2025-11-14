from __future__ import annotations

import builtins
import importlib
import importlib.util
import os
import pathlib
import random
import sys

import pytest

# Ensure pytest-cov plugin is loaded even if autoload is disabled by environment
pytest_plugins = ["pytest_cov"]

from codex_ml.utils.torch_checks import REINSTALL_COMMAND, inspect_torch
from tests.helpers.optional_dependencies import OPTIONAL_DEPENDENCY_REASONS

try:
    import numpy as np
except Exception:  # pragma: no cover - numpy optional
    np = None  # type: ignore[assignment]

TORCH_STATUS = None
TORCH_SKIP_REASON = ""

try:
    import torch as _torch
except Exception as exc:  # pragma: no cover - torch optional
    torch = None  # type: ignore[assignment]
    TORCH_SKIP_REASON = f"torch import failed: {exc!r}"
else:
    status = inspect_torch(_torch)
    TORCH_STATUS = status
    if status.ok:
        torch = _torch  # type: ignore[assignment]
    else:  # pragma: no cover - guard for stub installs
        TORCH_SKIP_REASON = (
            f"{status.detail}. Reinstall via: {status.reinstall_hint or REINSTALL_COMMAND}"
        )
        # Treat the stub as missing so pytest.importorskip("torch") will skip
        # affected tests instead of failing mid-import.
        sys.stderr.write(f"[tests] {TORCH_SKIP_REASON}\n")
        sys.modules["torch"] = None
        torch = None  # type: ignore[assignment]


def pytest_configure(config: pytest.Config) -> None:  # pragma: no cover - setup
    seed = 123
    random.seed(seed)
    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    if np is not None:
        np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)


def pytest_report_header(config: pytest.Config) -> list[str]:  # pragma: no cover - summary
    header: list[str] = []
    if TORCH_SKIP_REASON:
        header.append(f"PyTorch unavailable: {TORCH_SKIP_REASON}")
    elif TORCH_STATUS is not None and TORCH_STATUS.ok:
        details = TORCH_STATUS.summary()
        header.append(f"PyTorch detected: {details}")
    return header


def pytest_addoption(parser: pytest.Parser) -> None:  # pragma: no cover - option wiring
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


_TRAINING_OPTIONAL_ALLOWLIST: frozenset[str] = frozenset(
    {
        "test_checkpoint_integrity.py",
        "test_checkpoint_rng_restore.py",
        "test_checkpoint_manifest.py",
    }
)


OPTIONAL_TEST_GROUPS: dict[str, tuple[str, ...]] = {
    "tests.checkpointing.test_schema_v2": (),
    "tests.checkpointing.test_canonical_json": (),
    "tests.checkpointing": ("torch",),
    "tests.cli": ("yaml", "omegaconf", "torch"),
    "tests.config": ("yaml", "omegaconf"),
    "tests.data.test_cache_flush_threshold": ("numpy",),
    "tests.data.test_load_dataset": ("omegaconf",),
    "tests.data.test_safety_filter": ("omegaconf",),
    "tests.eval": ("torch",),
    "tests.gates": ("omegaconf", "torch"),
    "tests.interfaces": ("omegaconf", "torch"),
    "tests.modeling": ("torch", "transformers"),
    "tests.models": ("torch", "transformers"),
    "tests.monitoring": ("omegaconf",),
    "tests.multilingual": ("transformers", "sentencepiece"),
    "tests.pipeline": ("omegaconf", "yaml", "torch"),
    "tests.privacy": ("torch",),
    "tests.smoke": ("omegaconf", "yaml"),
    "tests.tokenization": ("transformers", "sentencepiece"),
    "tests.training": ("torch", "omegaconf", "yaml"),
    "tests.test_checkpoint": ("torch",),
    "tests.test_engine_hf_trainer": ("torch", "transformers"),
    "tests.test_engine_hf_trainer_grad_accum": ("torch", "transformers"),
    "tests.test_engine_hf_trainer_lora": ("torch", "transformers", "peft"),
    "tests.test_metric_curves": ("torch",),
    "tests.test_metrics_logging": ("torch",),
    "tests.test_metrics_tb": ("torch",),
    "tests.test_modeling": ("torch",),
    "tests.test_pipeline_smoke": ("omegaconf", "yaml", "torch"),
    "tests.test_symbolic_pipeline": ("torch", "omegaconf"),
    "tests.test_tokenization": ("transformers", "sentencepiece"),
    "tests.test_tokenizer_batch_encode": ("transformers", "sentencepiece"),
    "tests.test_tokenizer_ids": ("transformers", "sentencepiece"),
    "tests.test_training_arguments_flags": ("torch", "transformers"),
}


OPTIONAL_MARKERS: dict[str, str] = {
    "requires_transformers": "transformers",
    "requires_torch": "torch",
    "requires_sentencepiece": "sentencepiece",
    "requires_fsspec": "fsspec",
}


def _module_available(name: str) -> bool:
    if name == "torch" and TORCH_SKIP_REASON:
        return False
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return name in sys.modules
    return spec is not None


def _missing_modules(names: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    for name in names:
        if name == "torch" and TORCH_SKIP_REASON:
            missing.append(f"torch ({TORCH_SKIP_REASON})")
            continue
        try:
            __import__(name)
        except Exception:
            reason = OPTIONAL_DEPENDENCY_REASONS.get(name)
            if reason:
                missing.append(f"{name} ({reason})")
            else:
                missing.append(name)
    return missing


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="need --runslow to run")
    else:
        skip_slow = None
    run_deferred = os.getenv("RUN_DEFERRED_TESTS", "0") == "1"
    skip_deferred = (
        None
        if run_deferred
        else pytest.mark.skip(reason="deferred module (set RUN_DEFERRED_TESTS=1 to enable)")
    )
    for item in items:
        if skip_deferred and "deferred" in item.keywords:
            item.add_marker(skip_deferred)
            continue
        if skip_slow and "slow" in item.keywords:
            item.add_marker(skip_slow)
        for marker_name, module_name in OPTIONAL_MARKERS.items():
            if item.get_closest_marker(marker_name) and not _module_available(module_name):
                reason = module_name
                if module_name == "torch" and TORCH_SKIP_REASON:
                    reason = f"torch ({TORCH_SKIP_REASON})"
                elif module_name in OPTIONAL_DEPENDENCY_REASONS:
                    reason = f"{module_name} ({OPTIONAL_DEPENDENCY_REASONS[module_name]})"
                item.add_marker(pytest.mark.skip(reason=f"optional dependency missing: {reason}"))
                break
        module_name = getattr(item.module, "__name__", "")
        for prefix, deps in OPTIONAL_TEST_GROUPS.items():
            if module_name.startswith(prefix):
                if prefix == "tests.cli" and os.getenv("CODEX_CLI_LIGHTWEIGHT", "0") == "1":
                    break
                if prefix == "tests.training":
                    try:
                        filename = pathlib.Path(item.fspath).name
                    except Exception:  # pragma: no cover - defensive
                        filename = ""
                    if filename in _TRAINING_OPTIONAL_ALLOWLIST:
                        missing: list[str] = []
                    else:
                        missing = _missing_modules(deps)
                else:
                    missing = _missing_modules(deps)
                if missing:
                    reason = f"optional dependency missing: {', '.join(sorted(set(missing)))}"
                    item.add_marker(pytest.mark.skip(reason=reason))
                break


def _gpu_available() -> bool:
    try:
        import torch.cuda as _cuda

        import torch

        if not hasattr(torch, "cuda"):
            return False
        return hasattr(_cuda, "is_available") and _cuda.is_available()
    except Exception:
        return False


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    """
    Policy:
      - GPU tests are *skipped by default* (Codex has no GPU).
      - Set RUN_GPU_TESTS=1 to opt-in.
      - If RUN_GPU_TESTS=1 but no GPU is actually present, print a friendly message and skip.
      - Network tests are skipped by default; opt-in with RUN_NET_TESTS=1.
    """
    if "gpu" in item.keywords:
        want_gpu = os.getenv("RUN_GPU_TESTS", "0") == "1"
        have_gpu = _gpu_available()
        if not want_gpu:
            item.add_marker(
                pytest.mark.skip(
                    reason="GPU test skipped by default (RUN_GPU_TESTS!=1). Codex has no GPU."
                )
            )
            return
        if not have_gpu:
            print(
                "\n[tests] You set RUN_GPU_TESTS=1, but no CUDA GPU is available "
                "in this environment. "
                "Skipping GPU-marked test gracefully."
            )
            item.add_marker(pytest.mark.skip(reason="RUN_GPU_TESTS=1 but no CUDA GPU available."))
            return

    if "net" in item.keywords:
        want_net = os.getenv("RUN_NET_TESTS", "0") == "1"
        if not want_net:
            item.add_marker(
                pytest.mark.skip(reason="Network test skipped by default (RUN_NET_TESTS!=1).")
            )


@pytest.fixture(autouse=True)
def _isolate_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    yield


_OPTIONAL_DEPS = [
    "zstandard",
    "pandas",
    "duckdb",
    "datasets",
    "fastapi",
    "httpx",
    "sentencepiece",
    "sklearn",
    "h5py",
]


def pytest_ignore_collect(collection_path: pathlib.Path, config: pytest.Config) -> bool:
    if not collection_path.is_file():
        return False
    try:
        text = collection_path.read_text(encoding="utf-8")
    except Exception:
        return False
    for name in _OPTIONAL_DEPS:
        if name in text:
            try:
                __import__(name)
            except Exception:
                return True
    return False


@pytest.fixture
def no_sentencepiece(monkeypatch):
    orig_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "sentencepiece":
            raise ImportError("sentencepiece missing")
        return orig_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.delitem(sys.modules, "sentencepiece", raising=False)
    monkeypatch.delitem(sys.modules, "codex_ml.tokenization.sentencepiece_adapter", raising=False)
    yield


# ============================================================================
# DB MANAGER POOLING FIXTURES (Connection Pooling Test Infrastructure)
# ============================================================================

@pytest.fixture
def isolated_db_manager():
    """Provide isolated DBManager module for testing.
    
    Removes DBManager from module cache before test, ensuring clean state.
    Useful for tests that need to reload the module with different configs.
    
    Yields:
        None (side effect: clears module cache)
    
    Example:
        def test_something(isolated_db_manager):
            # DBManager can now be imported fresh
            from codex.logging.db_manager import DBManager
    """
    # Remove module from cache if present
    module_name = 'codex.logging.db_manager'
    if module_name in sys.modules:
        del sys.modules[module_name]
    
    yield
    
    # Cleanup: Remove module after test
    if module_name in sys.modules:
        del sys.modules[module_name]


@pytest.fixture
def clean_connection_pool():
    """Ensure connection pool starts and ends empty.
    
    Clears connection pool before and after test to prevent state pollution.
    Also closes all connections to prevent resource leaks.
    
    Yields:
        None (side effect: clears pool)
    
    Example:
        def test_pooling(clean_connection_pool):
            # Pool is guaranteed empty at start
            from codex.logging.db_manager import DBManager
            assert len(DBManager._CONNECTION_POOL) == 0
    """
    # Import after isolation (if used with isolated_db_manager)
    from codex.logging.db_manager import DBManager
    
    # Clear pool before test
    DBManager.close_all_pools()
    DBManager._CONNECTION_POOL.clear()
    
    yield
    
    # Cleanup: Clear pool after test
    DBManager.close_all_pools()
    DBManager._CONNECTION_POOL.clear()


@pytest.fixture
def enable_pooling(isolated_db_manager, clean_connection_pool):
    """Enable connection pooling for test duration with proper cleanup.
    
    Combines module isolation + pool cleanup + environment patching + reload.
    This is the primary fixture for tests that need pooling enabled.
    
    Yields:
        dict: Pooling configuration and state
            - 'enabled': True if pooling successfully enabled
            - 'original_flag': Original _POOL_ENABLED value
            - 'original_env': Original CODEX_SQLITE_POOL value
    
    Example:
        def test_pool_behavior(enable_pooling):
            from codex.logging.db_manager import DBManager
            assert DBManager._POOL_ENABLED is True
            # Test pooling behavior
    
    Notes:
        - Automatically reloads db_manager module
        - Restores original state after test
        - Validates pooling is actually enabled
    """
    # Save original environment
    original_env = os.environ.get('CODEX_SQLITE_POOL')
    
    # Enable pooling via environment
    os.environ['CODEX_SQLITE_POOL'] = '1'
    
    # Reload module to pick up environment variable
    import codex.logging.db_manager
    importlib.reload(codex.logging.db_manager)
    from codex.logging.db_manager import DBManager
    
    # Save original flag (should be True after reload)
    original_flag = DBManager._POOL_ENABLED
    
    # Validate pooling is enabled (fail fast if not)
    if not DBManager._POOL_ENABLED:
        raise RuntimeError(
            "enable_pooling fixture failed: DBManager._POOL_ENABLED is False "
            "after reload with CODEX_SQLITE_POOL=1. This indicates a module "
            "reload issue or import-time evaluation problem."
        )
    
    # Yield configuration state
    yield {
        'enabled': DBManager._POOL_ENABLED,
        'original_flag': original_flag,
        'original_env': original_env
    }
    
    # Restore original environment
    if original_env is None:
        os.environ.pop('CODEX_SQLITE_POOL', None)
    else:
        os.environ['CODEX_SQLITE_POOL'] = original_env
    
    # Reload again to restore original flag
    importlib.reload(codex.logging.db_manager)


@pytest.fixture
def pooling_db_manager(enable_pooling, tmp_path):
    """Provide DBManager instance with pooling enabled.
    
    Creates a fully initialized DBManager with pooling enabled and
    schema initialized. Useful for tests that need a ready-to-use
    pooled database.
    
    Args:
        enable_pooling: Fixture that enables pooling
        tmp_path: Pytest fixture for temporary directory
    
    Yields:
        DBManager: Initialized manager with pooling enabled
    
    Example:
        def test_with_manager(pooling_db_manager):
            conn = pooling_db_manager.get_connection()
            # Use connection
            pooling_db_manager.close_connection(conn)
            # Connection is returned to pool
    """
    from codex.logging.db_manager import DBManager
    
    # Create database in temp directory
    db_path = tmp_path / "pooling_test.db"
    
    # Create and initialize manager
    manager = DBManager(db_path=db_path)
    manager.init_schema()
    
    # Validate pooling is enabled
    assert DBManager._POOL_ENABLED is True, \
        "pooling_db_manager fixture requires pooling to be enabled"
    
    yield manager
    
    # Cleanup: Close all connections
    DBManager.close_all_pools()


@pytest.fixture
def pooled_connection(pooling_db_manager):
    """Provide a connection from the pool with automatic cleanup.
    
    Gets a connection from the pool, yields it for testing, then
    returns it to the pool. Useful for tests that need to work
    with a single pooled connection.
    
    Args:
        pooling_db_manager: Manager with pooling enabled
    
    Yields:
        sqlite3.Connection: Pooled database connection
    
    Example:
        def test_connection_usage(pooled_connection):
            cursor = pooled_connection.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
    """
    from codex.logging.db_manager import DBManager
    
    # Get connection from pool
    conn = pooling_db_manager.get_connection()
    
    # Verify it's a valid connection
    assert conn is not None, "Failed to get connection from pool"
    
    yield conn
    
    # Return to pool
    pooling_db_manager.close_connection(conn)


@pytest.fixture
def verify_pooling_enabled():
    """Post-test validation that pooling was actually enabled during test.
    
    Use this fixture in tests that claim to test pooling behavior to
    prevent false positives from module caching issues.
    
    Yields:
        callable: Validation function that checks pooling state
    
    Example:
        def test_pooling_feature(enable_pooling, verify_pooling_enabled):
            from codex.logging.db_manager import DBManager
            # Test pooling feature
            verify_pooling_enabled()  # Explicit validation
    
    Raises:
        AssertionError: If pooling was not actually enabled
    """
    def validate():
        """Check that pooling is actually enabled."""
        from codex.logging.db_manager import DBManager
        
        assert DBManager._POOL_ENABLED is True, \
            "Test claims to use pooling but DBManager._POOL_ENABLED is False. " \
            "This indicates the test is not actually exercising pooling code paths."
    
    yield validate


@pytest.fixture
def pool_state_tracker(enable_pooling):
    """Track connection pool state changes during test.
    
    Records pool size at start/end and provides assertions for validating
    pool behavior. Useful for debugging pool-related issues.
    
    Yields:
        dict: Pool state tracker with methods
            - 'initial_size': Pool size at test start
            - 'assert_pool_grew()': Assert pool has more connections
            - 'assert_pool_empty()': Assert pool is empty
            - 'get_current_size()': Get current pool size
    
    Example:
        def test_pool_growth(pool_state_tracker):
            from codex.logging.db_manager import DBManager
            db = DBManager(...)
            conn = db.get_connection()
            db.close_connection(conn)
            pool_state_tracker['assert_pool_grew']()
    """
    from codex.logging.db_manager import DBManager
    
    # Record initial state
    initial_size = sum(len(pool) for pool in DBManager._CONNECTION_POOL.values())
    
    def get_current_size():
        return sum(len(pool) for pool in DBManager._CONNECTION_POOL.values())
    
    def assert_pool_grew():
        current = get_current_size()
        assert current > initial_size, \
            f"Pool should have grown (initial: {initial_size}, current: {current})"
    
    def assert_pool_empty():
        current = get_current_size()
        assert current == 0, \
            f"Pool should be empty (current size: {current})"
    
    def assert_pool_size(expected):
        current = get_current_size()
        assert current == expected, \
            f"Pool size mismatch (expected: {expected}, current: {current})"
    
    tracker = {
        'initial_size': initial_size,
        'get_current_size': get_current_size,
        'assert_pool_grew': assert_pool_grew,
        'assert_pool_empty': assert_pool_empty,
        'assert_pool_size': assert_pool_size
    }
    
    yield tracker


@pytest.fixture(params=[True, False], ids=['pooling_enabled', 'pooling_disabled'])
def pooling_mode(request):
    """Parametrize tests to run with pooling both enabled and disabled.
    
    Useful for tests that should work correctly regardless of pooling state.
    
    Args:
        request: Pytest request object
    
    Yields:
        bool: True if pooling enabled, False if disabled
    
    Example:
        def test_basic_operations(pooling_mode, tmp_path):
            # This test runs twice: once with pooling, once without
            if pooling_mode:
                os.environ['CODEX_SQLITE_POOL'] = '1'
            else:
                os.environ.pop('CODEX_SQLITE_POOL', None)
            
            import importlib
            import codex.logging.db_manager
            importlib.reload(codex.logging.db_manager)
            from codex.logging.db_manager import DBManager
            
            db = DBManager(tmp_path / "test.db")
            # Test basic operations
    """
    pooling_enabled = request.param
    
    # Save original state
    original_env = os.environ.get('CODEX_SQLITE_POOL')
    
    # Configure pooling
    if pooling_enabled:
        os.environ['CODEX_SQLITE_POOL'] = '1'
    else:
        os.environ.pop('CODEX_SQLITE_POOL', None)
    
    # Reload module
    import codex.logging.db_manager
    importlib.reload(codex.logging.db_manager)
    
    yield pooling_enabled
    
    # Restore
    if original_env is None:
        os.environ.pop('CODEX_SQLITE_POOL', None)
    else:
        os.environ['CODEX_SQLITE_POOL'] = original_env
    
    importlib.reload(codex.logging.db_manager)
