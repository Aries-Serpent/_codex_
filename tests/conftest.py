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
    
    Also registers custom markers for RAG tests.
    """

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


# ============================================================================
# RAG Module Fixtures (Added 2026-01-08)
# ============================================================================

import tempfile
from pathlib import Path
from typing import Generator

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
    import torch
    from unittest.mock import Mock
    
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
    import json
    
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

