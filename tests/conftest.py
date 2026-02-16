#!/usr/bin/env python3
"""
Conftest to avoid ImportError during collection when optional heavy dependencies
are not installed in the CI/test environment.
"""
from __future__ import annotations

import importlib
import importlib.machinery
import importlib.util
import json
import logging
import os
import random
import sys
from pathlib import Path

import pytest

# Note: These imports are required for conftest to load properly.
# If numpy or torch are not available, many fixtures will be no-ops,
# but conftest itself must load for pytest-xdist workers to function.
try:
    import numpy
except ImportError:
    numpy = None

try:
    import torch
except ImportError:
    torch = None


logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"


# ============================================================================
# CUDA Detection for GPU-Dependent Tests (PR #3178)
# ============================================================================
# Detect CUDA availability at module load time for test skip decorators
if torch is not None and hasattr(torch, 'cuda'):
    try:
        CUDA_AVAILABLE = torch.cuda.is_available()
    except (AttributeError, RuntimeError):
        # CUDA methods may raise errors in some configurations
        CUDA_AVAILABLE = False
else:
    # PyTorch not installed or stub version without CUDA support
    CUDA_AVAILABLE = False


def is_cuda_available() -> bool:
    """
    Check if CUDA is available and functional.

    Returns:
        bool: True if CUDA/GPU is available, False otherwise

    Note:
        This function is used by test skip decorators to gracefully handle
        GPU-dependent tests in CPU-only CI environments.
    """
    return CUDA_AVAILABLE


# Pytest skip marker for CUDA-dependent tests
# Usage: @pytest.mark.skipif(not is_cuda_available(), reason="CUDA not available")
skip_if_no_cuda = pytest.mark.skipif(
    not is_cuda_available(),
    reason="CUDA/GPU not available in this environment"
)


def pytest_configure(config: pytest.Config) -> None:
    """Relax coverage enforcement during collection-only runs.

    The repository defaults enforce a coverage threshold via ``pytest.ini``. When
    running in ``--collect-only`` mode (as used by smoke checks for import
    validation), no tests execute and coverage would be reported as zero, causing
    an unnecessary failure. This hook disables coverage enforcement and raises
    the fail-under floor to zero for collection-only invocations while keeping
    the existing defaults for actual test runs.

    Also registers custom markers for RAG tests and configures PyTorch for CPU-only.
    Also installs custom importorskip wrapper to handle stub modules.
    """
    # Install custom importorskip wrapper (done here to avoid xdist worker issues)
    global _ORIGINAL_IMPORTORSKIP
    if _ORIGINAL_IMPORTORSKIP is None:
        _ORIGINAL_IMPORTORSKIP = pytest.importorskip
        pytest.importorskip = _importorskip_optional_dep
    
    # Note: Do NOT call torch.set_default_device() here.
    # It interferes with SentenceTransformer model loading in PyTorch >=2.0,
    # causing "Cannot copy out of meta tensor" errors. RAG modules already
    # pass device='cpu' explicitly to SentenceTransformer constructors.
    try:
        import torch
        version = getattr(torch, '__version__', 'unknown')
        logger.info(f"✓ PyTorch {version} available (RAG modules use device='cpu' directly)")
    except (ImportError, AttributeError):
        pass  # PyTorch not available or stub module

    # Increase file descriptor limits to prevent resource exhaustion (PR #3178)
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        target_limit = min(hard, 4096)
        if soft < target_limit:
            resource.setrlimit(resource.RLIMIT_NOFILE, (target_limit, hard))
            logger.info(f"✓ File descriptor limit increased to {target_limit} (prevents I/O errors)")
    except Exception as e:
        logger.warning(f"Could not increase file descriptor limit: {e}")

    if getattr(config.option, "collectonly", False):
        if hasattr(config.option, "cov_fail_under"):
            config.option.cov_fail_under = 0
        cov_plugin = config.pluginmanager.get_plugin("_cov")
        if cov_plugin:
            config.pluginmanager.unregister(cov_plugin)

    # Register RAG-specific markers
    config.addinivalue_line(
        "markers", "rag: marks tests as RAG module tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "gpu: marks tests that require GPU (skipped without GPU)"
    )
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )


# Note: pytest_configure_node hook removed in PR #3248 Attempt 15
# The hook didn't work because it runs AFTER CLI argument parsing in workers.
# Solution: Removed xdist parallelization (-n flags) from workflows.
# Workers spawned via execnet.remote_exec() start fresh Python interpreters
# that don't inherit the parent process's plugin registry.

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
    "requires_sentence_transformers": ["sentence_transformers"],
    "requires_faiss": ["faiss"],
    "requires_rag": ["sentence_transformers", "faiss"],
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


# Store reference to original importorskip for wrapper (initialized in pytest_configure)
_ORIGINAL_IMPORTORSKIP = None


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

    try:
        return _ORIGINAL_IMPORTORSKIP(modname, minversion=minversion, reason=reason)
    except (ImportError, OSError) as e:
        # OSError can occur if libraries are missing (e.g., libtorch_global_deps.so)
        message = reason or f"{modname} is not available: {e}"
        raise pytest.skip.Exception(message, allow_module_level=True)


def pytest_collection_modifyitems(session, config, items):
    """Auto-mark slow tests and handle optional dependencies."""

    # Patterns that indicate a test is slow (in test name/path)
    slow_patterns = [
        "sleep(",
        "time.sleep",
        "asyncio.sleep",
        "e2e",
        "end_to_end",
        "docker",
        "deployment",
    ]

    for item in items:
        # Auto-mark slow tests based on patterns in test name/path
        # NOTE: Do NOT auto-mark based on "integration" marker alone.
        # Integration tests should explicitly use @pytest.mark.slow if they're slow.
        if "slow" not in item.keywords:
            # Check if test name/path suggests it's slow
            if any(pattern in item.nodeid.lower() for pattern in slow_patterns):
                item.add_marker(pytest.mark.slow)

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


# ============================================================================
# RAG Module Fixtures (Added 2026-01-08)
# ============================================================================

import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Generator  # noqa: E402


@pytest.fixture
def temp_index_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for RAG index storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_cache_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for RAG cache storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_rag_documents():
    """Provide sample documents for RAG testing."""
    return [
        {
            "id": "doc1",
            "content": "Python is a high-level programming language. " * 20,
            "metadata": {"source": "python_intro", "category": "programming"},
        },
        {
            "id": "doc2",
            "content": "Machine learning uses algorithms to learn from data. " * 20,
            "metadata": {"source": "ml_basics", "category": "ai"},
        },
        {
            "id": "doc3",
            "content": "Docker provides containerization for applications. " * 20,
            "metadata": {"source": "docker_guide", "category": "devops"},
        },
    ]


@pytest.fixture
def sample_rag_corpus(temp_index_dir):
    """Create a sample corpus of files for RAG testing."""
    docs_dir = temp_index_dir / "docs"
    docs_dir.mkdir()

    corpus = {
        "python.txt": "Python is a versatile programming language. " * 30,
        "ml.txt": "Machine learning algorithms process data. " * 30,
        "docker.txt": "Docker containers isolate applications. " * 30,
    }

    files = []
    for filename, content in corpus.items():
        file_path = docs_dir / filename
        file_path.write_text(content)
        files.append(file_path)

    return {
        "files": files,
        "docs_dir": docs_dir,
        "corpus": corpus,
    }


@pytest.fixture
def rag_test_config():
    """Provide standard test configuration for RAG modules."""
    return {
        "chunk_size": 500,
        "overlap": 100,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "index_type": "IndexFlatL2",
        "cache_enabled": True,
    }


# ============================================================================
# PyTorch Profiler and JSON Serialization Fixtures (Added 2026-01-22)
# ============================================================================


@pytest.fixture(autouse=True, scope="session")
def disable_torch_profiler():
    """
    Disable PyTorch profiler to prevent type errors in Torch 2.6.0.

    Issue: PyTorch 2.6.0 profiler has breaking changes in type checking
    for ScriptObject vs _RecordFunction, causing RuntimeError in tests.

    Solution: Multi-layered profiler disabling:
    1. Environment variable
    2. Direct C++ profiler API
    3. Python-level profiler context override (no restoration needed - test env only)
    4. Global state manipulation

    Note: Original functions are not restored as this is a test-only fixture
    and the modifications are intentionally persistent for the entire test session.
    """
    # Layer 1: Environment variable (attempted first, before torch import)
    os.environ["PYTORCH_PROFILER_DISABLE"] = "1"
    os.environ["KINETO_LOG_LEVEL"] = "5"  # Suppress profiler logging

    # Layer 2: Import torch and disable at C++ level
    try:
        import torch

        # Method A: Disable via C++ API (if available)
        if hasattr(torch, '_C') and hasattr(torch._C, '_profiler'):
            try:
                torch._C._profiler._set_profiler_enabled(False)
            except (AttributeError, RuntimeError, TypeError):
                # Best-effort: C++ profiler API may not be available in all PyTorch versions
                logger.debug(
                    "Failed to disable torch C++ profiler via _set_profiler_enabled; "
                    "continuing without C++ profiler changes.",
                    exc_info=True,
                )

        # Method B: Disable via Python profiler module
        if hasattr(torch, 'profiler'):
            try:
                # Override profiler context managers to no-op
                # Note: Not restored - test session should have profiler disabled
                def noop_init(self, *args, **kwargs):
                    """No-op profiler initialization."""
                    self.enabled = False
                    self.use_cuda = False
                    self.record_shapes = False
                    self.profile_memory = False
                    self.with_stack = False

                torch.profiler.profile.__init__ = noop_init
            except (AttributeError, TypeError):
                # Best-effort: profiler API may have changed or be unavailable
                logger.debug(
                    "Failed to disable torch profiler via Python API; "
                    "torch.profiler.profile may be unavailable or changed.",
                    exc_info=True,
                )

        # Method C: Monkey-patch record_function to no-op
        if hasattr(torch, 'autograd') and hasattr(torch.autograd, 'profiler'):
            try:
                # Override record_function to no-op
                # Note: Not restored - test session should have profiler disabled
                class NoOpRecordFunction:
                    """No-op context manager for record_function."""
                    def __init__(self, *args, **kwargs):
                        pass
                    def __enter__(self):
                        return self
                    def __exit__(self, *args):
                        pass

                torch.autograd.profiler.record_function = NoOpRecordFunction
            except (AttributeError, TypeError):
                # Best-effort patching: older/newer torch versions may not expose this API.
                # In that case, we skip the monkey-patch and continue with the default behavior.
                logger.debug(
                    "torch.autograd.profiler.record_function could not be patched to NoOpRecordFunction",
                    exc_info=True,
                )

        # Method D: Disable autograd profiler globally
        if hasattr(torch, 'autograd') and hasattr(torch.autograd, 'profiler'):
            try:
                torch.autograd.profiler.emit_nvtx(enabled=False)
                # Note: Removed torch.autograd.profiler.profile(enabled=False) as profile is a class/context manager, not a function
            except (AttributeError, TypeError, RuntimeError) as exc:
                # Best-effort: emit_nvtx API may not be available
                logger.debug("Failed to disable autograd profiler globally: %s", exc)
                pass

    except (ImportError, OSError) as exc:
        # Torch not installed or failed to load (e.g., missing shared libraries)
        # This is expected in CI environments without full CUDA setup
        logger.debug("Torch import failed (expected in some CI environments): %s", exc)
        pass

    yield

    # Cleanup environment variables
    os.environ.pop("PYTORCH_PROFILER_DISABLE", None)
    os.environ.pop("KINETO_LOG_LEVEL", None)


@pytest.fixture
def mock_json_serializable():
    """
    Helper fixture to make MagicMock objects JSON serializable.

    Usage:
        def test_example(mock_json_serializable):
            mock_obj = MagicMock()
            json.dumps(mock_obj)  # Works with this fixture
    """
    from unittest.mock import MagicMock

    original_default = json.JSONEncoder.default

    def mock_default(encoder_self, obj):
        if isinstance(obj, MagicMock):
            return {"_mock": str(obj), "_mock_name": obj._mock_name or "MagicMock"}
        return original_default(encoder_self, obj)

    json.JSONEncoder.default = mock_default

    yield

    json.JSONEncoder.default = original_default


# =============================================================================
# Shared Test Fixtures and Utilities
# =============================================================================

@pytest.fixture
def mock_transformer_model():
    """Provide a shared MockTransformerModel for testing."""
    from unittest.mock import Mock

    import torch

    class MockTransformerModel(torch.nn.Module):
        """Mock transformer model for testing."""

        def __init__(self, num_layers=2, num_heads=4, seq_len=10, hidden_dim=64):
            super().__init__()
            self.num_layers = num_layers
            self.num_heads = num_heads
            self.seq_len = seq_len
            self.hidden_dim = hidden_dim
            # Pre-generate attention weights to avoid exhaustion
            self._attention_weights = self._generate_mock_attention()
            # Configure model attributes
            self.config = type('Config', (), {
                'num_hidden_layers': num_layers,
                'num_attention_heads': num_heads,
                'hidden_size': hidden_dim
            })()

        def _generate_mock_attention(self):
            """Generate realistic attention weight tensors."""
            weights = []
            for _ in range(self.num_layers):
                layer_weights = torch.softmax(
                    torch.randn(1, self.num_heads, self.seq_len, self.seq_len),
                    dim=-1
                )
                weights.append(layer_weights)
            return weights

        def get_attention_weights(self, layer_idx=None):
            """Return attention weights for specified layer or all layers."""
            if layer_idx is not None:
                return self._attention_weights[layer_idx]
            return self._attention_weights

        def forward(self, input_ids, attention_mask=None, output_attentions=False):
            batch_size = input_ids.size(0)
            seq_len = input_ids.size(1)

            attentions = []
            for _ in range(self.num_layers):
                attn = torch.softmax(
                    torch.randn(batch_size, self.num_heads, seq_len, seq_len),
                    dim=-1
                )
                attentions.append(attn)

            mock_output = Mock()
            mock_output.attentions = attentions if output_attentions else None
            mock_output.last_hidden_state = torch.randn(batch_size, seq_len, self.hidden_dim)

            return mock_output

    return MockTransformerModel(num_layers=2, num_heads=4, seq_len=10)


@pytest.fixture
def serializable_mock_model():
    """Provide a JSON-serializable mock model for evaluation tests."""
    from dataclasses import asdict, dataclass

    @dataclass
    class SerializableModelConfig:
        """Test model config that supports JSON serialization."""
        model_type: str = "test_transformer"
        num_layers: int = 2
        num_heads: int = 4
        hidden_size: int = 512
        vocab_size: int = 50257

        def to_dict(self):
            return asdict(self)

        def to_json(self):
            import json
            return json.dumps(self.to_dict())

    class MockSerializableModel:
        """Mock model with JSON serialization support."""

        def __init__(self):
            self.config = SerializableModelConfig()
            self._call_count = 0

        def __call__(self, *args, **kwargs):
            self._call_count += 1
            return {"loss": 0.5, "logits": [[0.1, 0.9]]}

        def to_dict(self):
            """Enable JSON serialization."""
            return {
                "config": self.config.to_dict(),
                "call_count": self._call_count
            }

        def __repr__(self):
            return f"MockSerializableModel(config={self.config})"

    return MockSerializableModel()


# ============================================================================
# RAG Module Fixtures - pytest-xdist compatible
# ============================================================================
# These fixtures are designed to work safely with pytest-xdist workers.
# They check for dependencies during test execution rather than at module
# import time, preventing worker crashes during test collection.

@pytest.fixture(scope="session")
def sentence_transformers_available():
    """Check if sentence_transformers is available (session-scoped for performance)."""
    try:
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.fixture(scope="session")
def faiss_available():
    """Check if faiss is available (session-scoped for performance)."""
    try:
        import faiss  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.fixture(scope="session")
def rag_dependencies_available(sentence_transformers_available, faiss_available):
    """Check if all RAG dependencies are available."""
    return sentence_transformers_available and faiss_available


@pytest.fixture
def require_sentence_transformers(sentence_transformers_available):
    """Skip test if sentence_transformers is not available."""
    if not sentence_transformers_available:
        pytest.skip("sentence_transformers is not installed")


@pytest.fixture
def require_faiss(faiss_available):
    """Skip test if faiss is not available."""
    if not faiss_available:
        pytest.skip("faiss is not installed")


@pytest.fixture
def require_rag_dependencies(rag_dependencies_available):
    """Skip test if RAG dependencies (sentence_transformers, faiss) are not available."""
    if not rag_dependencies_available:
        pytest.skip("RAG dependencies (sentence_transformers, faiss) are not installed")


@pytest.fixture(autouse=True)
def ensure_cpu_device():
    """
    Ensure tests use CPU device and avoid meta tensor issues.
    Applied automatically to all tests to prevent PyTorch meta tensor errors.

    Note: We do NOT call torch.set_default_device() because it interferes
    with SentenceTransformer model loading in PyTorch >=2.0, causing
    "Cannot copy out of meta tensor" errors. RAG modules pass device='cpu'
    explicitly to SentenceTransformer constructors instead.
    """
    try:
        import torch

        # Check if this is a stub/placeholder torch module
        if not hasattr(torch, 'Tensor') or not callable(getattr(torch, 'manual_seed', None)):
            # Stub torch module, skip fixture
            yield
            return

        # Ensure deterministic behavior
        torch.manual_seed(0)

        yield

        # Cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except (ImportError, AttributeError):
        # torch not available or is a stub, skip fixture
        yield


@pytest.fixture
def mock_sentence_transformer(monkeypatch):
    """
    Enhanced mock SentenceTransformer to avoid actual model downloads in tests.
    Use this fixture when you want to test RAG logic without loading real models.

    Improvements (2026-02-10):
    - Added get_sentence_embedding_dimension() method
    - Enhanced encode() to handle kwargs properly
    - Added modules() method for meta tensor compatibility
    - Patches multiple import paths for indexer/embeddings/retriever modules
    """
    class MockSentenceTransformer:
        def __init__(self, model_name, cache_folder=None, device="cpu", trust_remote_code=False, use_auth_token=None):
            self.model_name = model_name
            self.device = device
            self.cache_folder = cache_folder
            self.trust_remote_code = trust_remote_code
            self.use_auth_token = use_auth_token

        def encode(self, texts, batch_size=32, show_progress_bar=False,
                   convert_to_numpy=True, **kwargs):
            import numpy as np
            # Return dummy embeddings with correct shape
            if isinstance(texts, str):
                texts = [texts]
            embeddings = np.random.randn(len(texts), 384).astype(np.float32)
            return embeddings if convert_to_numpy else embeddings.tolist()

        def get_sentence_embedding_dimension(self):
            """Return embedding dimension for FAISS index creation."""
            return 384

        def to(self, device):
            self.device = device
            return self

        def to_empty(self, device):
            self.device = device
            return self

        def eval(self):
            return self

        def parameters(self):
            # Return empty generator to avoid meta tensor checks
            return iter([])

        def modules(self):
            # Return empty generator for meta tensor compatibility
            return iter([])

    try:
        import sentence_transformers  # noqa: F401 - Testing optional dependency availability
        # Patch multiple import paths for comprehensive coverage
        monkeypatch.setattr(
            "sentence_transformers.SentenceTransformer",
            MockSentenceTransformer
        )
        # Also patch in specific modules that import it
        try:
            monkeypatch.setattr(
                "codex.rag.embeddings.SentenceTransformer",
                MockSentenceTransformer
            )
        except AttributeError:
            pass
        try:
            monkeypatch.setattr(
                "codex.rag.indexer.SentenceTransformer",
                MockSentenceTransformer
            )
        except AttributeError:
            pass
        try:
            monkeypatch.setattr(
                "codex.rag.retriever.SentenceTransformer",
                MockSentenceTransformer
            )
        except AttributeError:
            pass
    except ImportError:
        # sentence_transformers not available, nothing to mock
        pass

    return MockSentenceTransformer




@pytest.fixture(scope="session", autouse=True)
def setup_audit_artifacts(tmp_path_factory):
    """
    Create audit_artifacts directory for tests using pytest's temporary directory system.

    This fixture runs once per test session and ensures the directory
    structure required by depth gating tests exists in an isolated temp location.
    Sets the CODEX_AUDIT_DIR environment variable to point to the temporary directory.
    """
    # Use pytest's temp directory factory for isolated test artifacts
    audit_dir = tmp_path_factory.mktemp("audit_artifacts")

    # Create required files
    context_index = audit_dir / "context_index.json"
    context_index.write_text(json.dumps({
        "version": "1.0",
        "contexts": [],
        "metadata": {
            "created": "test-session",
            "purpose": "test-fixture"
        }
    }, indent=2))

    # Set environment variable so tests can find the temp audit directory
    original_audit_dir = os.environ.get("CODEX_AUDIT_DIR")
    os.environ["CODEX_AUDIT_DIR"] = str(audit_dir)

    yield audit_dir

    # Restore original environment variable
    if original_audit_dir is not None:
        os.environ["CODEX_AUDIT_DIR"] = original_audit_dir
    else:
        os.environ.pop("CODEX_AUDIT_DIR", None)


# ==============================================================================
# RESOURCE MANAGEMENT FIXTURES (PR #3178 - Fix 744 Test Failures)
# ==============================================================================
# These fixtures prevent resource exhaustion that was causing fatal crashes
# at 57% test completion. See .codex/COMPLETE_TEST_FAILURE_ANALYSIS_744_ISSUES.md
#
# Root cause: File handle leaks causing:
#   - ValueError: I/O operation on closed file
#   - lost sys.stderr
#   - Process termination with exit code 1
#
# Solution: Global resource management + monitoring + forced cleanup
# ==============================================================================

@pytest.fixture(scope="session", autouse=True)
def session_resource_manager():
    """Manage resources across entire test session to prevent exhaustion.

    This fixture addresses the resource exhaustion crash at 57% test completion
    (Job 62915466799) that blocked 474+ tests from running.

    Features:
    - Tracks initial open files
    - Monitors resource usage
    - Reports leaks at session end
    - Forces garbage collection

    See: .codex/COMPLETE_TEST_FAILURE_ANALYSIS_744_ISSUES.md
    """
    import gc
    import warnings

    # Track initial state
    initial_files = set()
    try:
        import psutil
        process = psutil.Process()
        initial_files = set(f.path for f in process.open_files())
        logger.info(f"✓ Session resource manager: {len(initial_files)} files open at start")
    except (ImportError, Exception) as e:
        logger.debug(f"psutil not available for resource tracking: {e}")

    yield

    # Cleanup and report phase
    gc.collect()

    try:
        import psutil
        process = psutil.Process()
        final_files = set(f.path for f in process.open_files())
        leaked = final_files - initial_files

        if leaked:
            leak_count = len(leaked)
            warnings.warn(
                f"Resource leak detected: {leak_count} file(s) still open at session end",
                ResourceWarning
            )
            # Show first 5 leaked files
            for f in list(leaked)[:5]:
                warnings.warn(f"  Leaked file: {f}", ResourceWarning)

            if leak_count > 5:
                warnings.warn(f"  ... and {leak_count - 5} more", ResourceWarning)
        else:
            logger.info("✓ No resource leaks detected at session end")
    except Exception:  # Best-effort cleanup; psutil may not be available
        pass


@pytest.fixture(autouse=True)
def protect_stderr():
    """Protect stderr/stdout from being closed or corrupted.

    This fixture prevents the "lost sys.stderr" fatal error that terminated
    the test run at 57% completion.

    Issue: Tests were modifying or closing sys.stderr without restoration,
    causing subsequent tests to fail with I/O errors.

    Solution: Save and restore stderr/stdout for every test.
    """
    import sys
    from typing import Any

    class _NonClosingStream:
        """Proxy stream that prevents tests from closing stderr/stdout."""

        def __init__(self, stream: Any) -> None:
            self._stream = stream

        def __getattr__(self, name: str) -> Any:
            return getattr(self._stream, name)

        def write(self, data: str) -> int:
            return self._stream.write(data)

        def flush(self) -> None:
            self._stream.flush()

        def close(self) -> None:
            # Intentionally ignore close attempts from tests.
            return None

    original_stderr = sys.stderr
    original_stdout = sys.stdout

    # Wrap stderr/stdout so tests can't close them mid-run.
    sys.stderr = _NonClosingStream(original_stderr)
    sys.stdout = _NonClosingStream(original_stdout)

    yield

    # Restore if modified or closed
    try:
        if sys.stderr is not original_stderr:
            sys.stderr = original_stderr
        if sys.stdout is not original_stdout:
            sys.stdout = original_stdout
    except Exception:
        # Force restore on any error
        sys.stderr = original_stderr
        sys.stdout = original_stdout


@pytest.fixture(autouse=True)
def force_file_cleanup():
    """Force cleanup of file handles after each test.

    This fixture addresses file handle leaks that accumulated over 48 minutes
    of test execution, eventually exhausting available file descriptors.

    Strategy:
    - Force garbage collection after each test
    - Explicitly close lingering file objects
    - Prevent file handle accumulation
    """
    yield

    # Cleanup phase
    import gc
    import os
    gc.collect()

    if os.environ.get("CODEX_FORCE_FILE_CLEANUP", "0") != "1":
        return

    if not hasattr(force_file_cleanup, "_counter"):
        force_file_cleanup._counter = 0  # type: ignore[attr-defined]
    force_file_cleanup._counter += 1  # type: ignore[attr-defined]

    # Only run full file-handle scans periodically to avoid large slowdowns.
    if force_file_cleanup._counter % 20 != 0:  # type: ignore[attr-defined]
        return

    # Close any lingering file objects found by garbage collector
    import logging
    import sys

    handler_streams = []
    for handler_ref in logging._handlerList:
        handler = handler_ref()
        if handler is not None and getattr(handler, "stream", None) is not None:
            handler_streams.append(handler.stream)

    protected_streams = (
        sys.stdout,
        sys.stderr,
        sys.__stdout__,
        sys.__stderr__,
        sys.__stdin__,
        *handler_streams,
    )
    for obj in gc.get_objects():
        try:
            close_method = getattr(obj, "close", None)
            closed_attr = getattr(obj, "closed", None)
            name_attr = getattr(obj, "name", None)
        except Exception:
            continue  # Skip objects with unsafe attribute access

        try:
            # Check if object is file-like
            if close_method is not None and closed_attr is not None and name_attr is not None:
                if any(obj is stream for stream in protected_streams):
                    continue
                if name_attr in ("<stdin>", "<stdout>", "<stderr>"):
                    continue
                if not closed_attr and not isinstance(name_attr, int):
                    # It's an open file object (not stdin/stdout/stderr which have int names)
                    try:
                        close_method()
                    except Exception:
                        pass  # Already closed or not closeable
        except (ReferenceError, AttributeError):
            pass  # Object was garbage collected during iteration


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    """Monitor resources during test execution.

    This hook tracks file handles and memory usage per test, providing warnings
    when leaks are detected. This enables early identification of problematic tests
    before they accumulate and cause session-level failures.

    Warnings are issued when:
    - File handles increase by more than 5
    - Memory usage increases by more than 20%

    See: .codex/TEST_FAILURE_REMEDIATION_PLANSET_PR3178.md Phase 2
    """
    import warnings

    before_files = 0
    before_memory = 0

    try:
        import psutil
        process = psutil.Process()
        before_files = len(process.open_files())
        before_memory = process.memory_info().rss / 1024 / 1024  # MB
    except Exception:  # psutil optional; skip resource tracking if unavailable
        pass

    yield

    try:
        import psutil
        process = psutil.Process()
        after_files = len(process.open_files())
        after_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Check for leaks
        if after_files > before_files + 5:
            warnings.warn(
                f"{item.nodeid}: File handle leak detected "
                f"({before_files} → {after_files}, +{after_files - before_files})",
                ResourceWarning
            )

        if after_memory > before_memory * 1.2:  # 20% increase
            warnings.warn(
                f"{item.nodeid}: Memory leak detected "
                f"({before_memory:.1f}MB → {after_memory:.1f}MB, "
                f"+{after_memory - before_memory:.1f}MB)",
                ResourceWarning
            )
    except Exception:  # psutil optional; skip leak check if unavailable
        pass
