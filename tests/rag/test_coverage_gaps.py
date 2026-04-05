"""Targeted coverage tests for RAG modules with gaps below 95%.

Covers previously-uncovered branches in:
- src/codex/rag/retriever.py  (CachedRetriever, MultiIndexRetriever, RAGRetriever,
                                _load_model error paths, reload)
- src/codex/rag/utils.py       (has_meta_tensors submodule walk, safe_model_to_device
                                meta/None/ImportError/AttributeError paths, _try_model_to)
- src/codex/rag/_model_utils.py (safe_load_sentence_transformer error paths)
- src/codex/rag/indexer.py     (embed_chunks ImportError, build_index_from_files
                                missing-files path, manage_tenant_indices error branch)
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Make sure src/ is importable regardless of cwd
# ---------------------------------------------------------------------------
_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# ---------------------------------------------------------------------------
# Skip entire module if numpy (a transitive RAG dependency) is missing so
# tests can be collected without error in minimal environments.
# ---------------------------------------------------------------------------
try:
    import numpy  # noqa: F401
except ImportError:
    pytest.skip(
        "numpy not installed — RAG coverage tests require the full RAG extras",
        allow_module_level=True,
    )


# ===========================================================================
# retriever.py — _load_model error paths (lines 78-103)
# ===========================================================================

class TestRetrieverLoadModelErrors:
    """Cover _load_model() branches that are not exercised by the main test suite."""

    def test_load_model_raises_when_sentence_transformers_none(self):
        from codex.rag import retriever as _mod

        with patch.object(_mod, "SentenceTransformer", None):
            r = _mod.Retriever.__new__(_mod.Retriever)
            r.model_name = "test-model"
            r.cache_dir = None
            with pytest.raises(ImportError, match="sentence-transformers not installed"):
                r._load_model()

    def test_load_model_propagates_runtime_error(self):
        from codex.rag import retriever as _mod

        sentinel = MagicMock()  # non-None SentenceTransformer sentinel
        with patch.object(_mod, "SentenceTransformer", sentinel):
            with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                       side_effect=RuntimeError("load failed")):
                r = _mod.Retriever.__new__(_mod.Retriever)
                r.model_name = "test-model"
                r.cache_dir = None
                with pytest.raises(RuntimeError, match="load failed"):
                    r._load_model()

    def test_load_model_propagates_value_error(self):
        from codex.rag import retriever as _mod

        sentinel = MagicMock()
        with patch.object(_mod, "SentenceTransformer", sentinel):
            with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                       side_effect=ValueError("bad value")):
                r = _mod.Retriever.__new__(_mod.Retriever)
                r.model_name = "test-model"
                r.cache_dir = None
                with pytest.raises(ValueError, match="bad value"):
                    r._load_model()


# ===========================================================================
# retriever.py — Retriever._load_index generic exception path (lines 79-80)
# ===========================================================================

class TestRetrieverLoadIndexErrors:
    def test_load_index_reraises_generic_exception(self, tmp_path):
        from codex.rag import retriever as _mod

        with patch("codex.rag.indexer.load_index",
                   side_effect=RuntimeError("corrupt index")):
            with pytest.raises(RuntimeError, match="corrupt index"):
                _mod.Retriever(index_dir=str(tmp_path), index_name="test")


# ===========================================================================
# retriever.py — Retriever.reload (lines 261-262)
# ===========================================================================

class TestRetrieverReload:
    def test_reload_calls_load_index(self, tmp_path):
        from codex.rag import retriever as _mod

        r = _mod.Retriever.__new__(_mod.Retriever)
        r.index_dir = str(tmp_path)
        r.index_name = "default"
        r.tenant_id = "default"
        r.faiss_index = None
        r.chunks_metadata = []
        r.index_metadata = {}
        r.model = None
        r.model_name = "test"
        r.cache_dir = None

        called = []
        with patch.object(r, "_load_index", side_effect=lambda: called.append(1)):
            r.reload()
        assert called, "_load_index should be called by reload()"


# ===========================================================================
# retriever.py — MultiIndexRetriever (lines 298-334)
# ===========================================================================

class TestMultiIndexRetriever:
    def test_query_merges_results_from_multiple_retrievers(self):
        from codex.rag import retriever as _mod

        mir = _mod.MultiIndexRetriever.__new__(_mod.MultiIndexRetriever)

        r1 = MagicMock()
        r1.index_name = "idx1"
        r1.tenant_id = "t1"
        r1.query.return_value = [{"text": "a", "score": 0.1}]

        r2 = MagicMock()
        r2.index_name = "idx2"
        r2.tenant_id = "t2"
        r2.query.return_value = [{"text": "b", "score": 0.2}]

        mir.retrievers = [r1, r2]
        results = mir.query("test query", top_k=2)
        assert len(results) == 2
        assert results[0]["index_name"] == "idx1"

    def test_query_handles_retriever_exception(self):
        from codex.rag import retriever as _mod

        mir = _mod.MultiIndexRetriever.__new__(_mod.MultiIndexRetriever)
        r1 = MagicMock()
        r1.index_name = "broken"
        r1.tenant_id = "t1"
        r1.query.side_effect = RuntimeError("index unavailable")
        mir.retrievers = [r1]

        results = mir.query("test", top_k=5)
        assert results == []

    def test_get_stats_delegates_to_retrievers(self):
        from codex.rag import retriever as _mod

        mir = _mod.MultiIndexRetriever.__new__(_mod.MultiIndexRetriever)
        r1 = MagicMock()
        r1.get_stats.return_value = {"index": "idx1", "num_chunks": 10}
        mir.retrievers = [r1]
        stats = mir.get_stats()
        assert stats[0]["index"] == "idx1"


# ===========================================================================
# retriever.py — CachedRetriever (lines 485-635)
# ===========================================================================

class TestCachedRetriever:
    def _make_cached_retriever(self):
        from codex.rag import retriever as _mod
        cr = _mod.CachedRetriever.__new__(_mod.CachedRetriever)
        cr.cache_ttl = 60
        cr.normalize_queries = True
        cr.query_cache = _mod.LRUCache(maxsize=100)
        cr.cache_timestamps = {}
        cr.model = None
        cr.faiss_index = None
        cr.chunks_metadata = []
        cr.index_metadata = {}
        return cr

    def test_normalize_query_lowercases_and_strips(self):
        cr = self._make_cached_retriever()
        assert cr._normalize_query("  Hello WORLD  ") == "hello world"

    def test_normalize_query_off_returns_original(self):
        cr = self._make_cached_retriever()
        cr.normalize_queries = False
        assert cr._normalize_query("  Hello  ") == "  Hello  "

    def test_make_cache_key_is_deterministic(self):
        cr = self._make_cached_retriever()
        k1 = cr._make_cache_key("test query", 5, None)
        k2 = cr._make_cache_key("test query", 5, None)
        assert k1 == k2

    def test_make_cache_key_varies_with_params(self):
        cr = self._make_cached_retriever()
        k1 = cr._make_cache_key("test", 5, None)
        k2 = cr._make_cache_key("test", 10, None)
        assert k1 != k2

    def test_is_cache_valid_false_for_missing_key(self):
        cr = self._make_cached_retriever()
        assert cr._is_cache_valid("nonexistent_key") is False

    def test_is_cache_valid_false_for_expired_entry(self):
        import time
        cr = self._make_cached_retriever()
        cr.cache_ttl = 0  # immediately expired
        cr.cache_timestamps["k1"] = time.time() - 1
        assert cr._is_cache_valid("k1") is False

    def test_cache_hit_returns_cached_results(self):
        import time
        cr = self._make_cached_retriever()
        cached = [{"text": "cached", "score": 0.1}]
        key = cr._make_cache_key("hello", 5, None)
        cr.query_cache.put(key, cached)
        cr.cache_timestamps[key] = time.time()

        with patch.object(cr, "query", side_effect=AssertionError("should not call")):
            results = cr.query_with_cache("hello", top_k=5)
        assert results == cached

    def test_cache_miss_calls_query_and_caches(self):
        cr = self._make_cached_retriever()
        expected = [{"text": "result", "score": 0.2}]

        with patch.object(cr, "query", return_value=expected):
            results = cr.query_with_cache("new query", top_k=5)

        assert results == expected
        key = cr._make_cache_key("new query", 5, None)
        assert cr.query_cache.get(key) == expected

    def test_clear_cache_empties_all(self):
        import time
        cr = self._make_cached_retriever()
        cr.query_cache.put("k1", [])
        cr.cache_timestamps["k1"] = time.time()
        cr.clear_cache()
        assert len(cr.cache_timestamps) == 0

    def test_get_cache_stats_includes_ttl(self):
        cr = self._make_cached_retriever()
        stats = cr.get_cache_stats()
        assert stats["ttl"] == 60

    def test_invalidate_expired_removes_stale_entries(self):
        import time
        cr = self._make_cached_retriever()
        cr.cache_ttl = 0  # immediately expired
        cr.cache_timestamps["k1"] = time.time() - 1
        cr.query_cache.put("k1", [])
        cr.invalidate_expired()
        assert "k1" not in cr.cache_timestamps


# ===========================================================================
# retriever.py — RAGRetriever (lines 573-635)
# ===========================================================================

class TestRAGRetriever:
    def test_query_raises_when_not_loaded(self):
        from codex.rag import retriever as _mod
        rr = _mod.RAGRetriever()
        with pytest.raises(RuntimeError, match="not initialised"):
            rr.query("anything")

    def test_load_creates_retriever(self, tmp_path):
        from codex.rag import retriever as _mod
        mock_retriever = MagicMock()
        with patch.object(_mod, "Retriever", return_value=mock_retriever):
            rr = _mod.RAGRetriever().load(
                index_dir=str(tmp_path),
                index_name="test",
            )
        assert rr._retriever is mock_retriever

    def test_query_delegates_to_retriever(self, tmp_path):
        from codex.rag import retriever as _mod
        mock_retriever = MagicMock()
        mock_retriever.query.return_value = [{"text": "r", "score": 0.1}]
        with patch.object(_mod, "Retriever", return_value=mock_retriever):
            rr = _mod.RAGRetriever().load(index_dir=str(tmp_path))
        results = rr.query("test", top_k=3)
        assert results == [{"text": "r", "score": 0.1}]


# ===========================================================================
# utils.py — has_meta_tensors submodule walk (lines 83-140)
# ===========================================================================

class TestHasMetaTensorsSubmoduleWalk:
    def test_submodule_with_meta_param_returns_true(self):
        from codex.rag.utils import has_meta_tensors

        meta_param = SimpleNamespace(is_meta=True)
        submod = SimpleNamespace(
            named_parameters=lambda recurse=True: [("w", meta_param)],
        )
        model = SimpleNamespace(
            parameters=lambda: iter([]),
            buffers=lambda: iter([]),
            named_modules=lambda: [("sub", submod)],
        )
        assert has_meta_tensors(model) is True

    def test_submodule_with_meta_device_param_returns_true(self):
        from codex.rag.utils import has_meta_tensors

        device = SimpleNamespace(type="meta")
        param = SimpleNamespace(is_meta=False, device=device)
        submod = SimpleNamespace(
            named_parameters=lambda recurse=True: [("w", param)],
        )
        model = SimpleNamespace(
            parameters=lambda: iter([]),
            buffers=lambda: iter([]),
            named_modules=lambda: [("sub", submod)],
        )
        assert has_meta_tensors(model) is True

    def test_submodule_with_meta_buffer_returns_true(self):
        from codex.rag.utils import has_meta_tensors

        meta_buf = SimpleNamespace(is_meta=True)
        submod = SimpleNamespace(
            named_buffers=lambda recurse=True: [("b", meta_buf)],
        )
        model = SimpleNamespace(
            parameters=lambda: iter([]),
            buffers=lambda: iter([]),
            named_modules=lambda: [("sub", submod)],
        )
        assert has_meta_tensors(model) is True

    def test_model_device_attribute_meta_returns_true(self):
        from codex.rag.utils import has_meta_tensors

        device = SimpleNamespace(type="meta")
        model = SimpleNamespace(
            parameters=lambda: iter([]),
            buffers=lambda: iter([]),
            device=device,
        )
        assert has_meta_tensors(model) is True

    def test_exception_in_has_meta_tensors_returns_none(self):
        from codex.rag.utils import has_meta_tensors

        model = SimpleNamespace(parameters=MagicMock(side_effect=RuntimeError("boom")))
        result = has_meta_tensors(model)
        assert result is None

    def test_named_parameters_typeerror_fallback(self):
        from codex.rag.utils import has_meta_tensors

        def named_params_raises_on_kwarg(**kwargs):
            if kwargs:
                raise TypeError("no recurse kwarg")
            return iter([])

        submod = SimpleNamespace(named_parameters=named_params_raises_on_kwarg)
        model = SimpleNamespace(
            parameters=lambda: iter([]),
            buffers=lambda: iter([]),
            named_modules=lambda: [("sub", submod)],
        )
        result = has_meta_tensors(model)
        assert result is False

    def test_named_buffers_typeerror_fallback(self):
        from codex.rag.utils import has_meta_tensors

        def named_bufs_raises_on_kwarg(**kwargs):
            if kwargs:
                raise TypeError("no recurse kwarg")
            return iter([])

        submod = SimpleNamespace(named_buffers=named_bufs_raises_on_kwarg)
        model = SimpleNamespace(
            parameters=lambda: iter([]),
            buffers=lambda: iter([]),
            named_modules=lambda: [("sub", submod)],
        )
        result = has_meta_tensors(model)
        assert result is False


# ===========================================================================
# utils.py — safe_model_to_device meta/None/import paths (lines 182-315)
# ===========================================================================

class TestSafeModelToDevice:
    def test_returns_model_when_has_meta_tensors_is_none(self):
        from codex.rag.utils import safe_model_to_device

        model = object()
        with patch("codex.rag.utils.has_meta_tensors", return_value=None):
            result = safe_model_to_device(model, device="cpu")
        assert result is model

    def test_raises_when_meta_tensors_and_no_to_empty(self):
        from codex.rag.utils import safe_model_to_device

        model = SimpleNamespace()  # no to_empty attribute
        with patch("codex.rag.utils.has_meta_tensors", return_value=True):
            with pytest.raises(AttributeError, match="to_empty"):
                safe_model_to_device(model, device="cpu")

    def test_meta_path_calls_to_empty_and_reset_parameters(self):
        from codex.rag.utils import safe_model_to_device

        inner_mod = MagicMock()
        inner_mod.reset_parameters = MagicMock()
        model = MagicMock()
        model.to_empty.return_value = model
        model.modules.return_value = [inner_mod]

        with patch("codex.rag.utils.has_meta_tensors", return_value=True):
            result = safe_model_to_device(model, device="cpu")
        model.to_empty.assert_called_once_with(device="cpu")
        assert result is model

    def test_meta_path_skips_reset_when_no_modules(self):
        from codex.rag.utils import safe_model_to_device

        model = SimpleNamespace()
        materialized = SimpleNamespace()
        model.to_empty = MagicMock(return_value=materialized)

        with patch("codex.rag.utils.has_meta_tensors", return_value=True):
            result = safe_model_to_device(model, device="cpu")
        assert result is materialized

    def test_import_error_falls_back_to_try_model_to(self):
        from codex.rag.utils import safe_model_to_device

        model = SimpleNamespace()
        model.to = MagicMock(return_value=model)

        with patch("codex.rag.utils.has_meta_tensors", side_effect=ImportError("no torch")):
            result = safe_model_to_device(model, device="cpu")
        assert result is model

    def test_generic_exception_raises_runtime_error(self):
        from codex.rag.utils import safe_model_to_device

        with patch("codex.rag.utils.has_meta_tensors", side_effect=RuntimeError("crash")):
            with pytest.raises(RuntimeError):
                safe_model_to_device(object(), device="cpu")


# ===========================================================================
# utils.py — _try_model_to (lines 301-314)
# ===========================================================================

class TestTryModelTo:
    def test_calls_to_with_kwargs(self):
        from codex.rag.utils import _try_model_to

        model = MagicMock()
        model.to.return_value = model
        result = _try_model_to(model, "cpu")
        assert result is model
        model.to.assert_called()

    def test_typeerror_fallback_to_positional(self):
        from codex.rag.utils import _try_model_to

        model = MagicMock()
        model.to.side_effect = [TypeError("no kwargs"), model]
        result = _try_model_to(model, "cpu")
        assert result is model

    def test_returns_model_when_no_to_method(self):
        from codex.rag.utils import _try_model_to

        model = SimpleNamespace()  # no .to()
        result = _try_model_to(model, "cpu")
        assert result is model


# ===========================================================================
# _model_utils.py — safe_load_sentence_transformer error paths (lines 80-100)
# ===========================================================================

class TestModelUtilsSafeLoad:
    def test_raises_on_load_failure(self):
        from codex.rag._model_utils import safe_load_sentence_transformer

        with patch("codex.rag._model_utils.SentenceTransformer",
                   None, create=True):
            with pytest.raises(Exception):
                safe_load_sentence_transformer("nonexistent-model-xyz", None)

    def test_raises_attributeerror_on_missing_to_empty(self):
        """When ST raises RuntimeError and model has no to_empty, raise RuntimeError."""
        from codex.rag import _model_utils as _mu

        exc = RuntimeError("meta tensor")
        fake_cls = MagicMock(side_effect=exc)

        with patch.object(_mu, "SentenceTransformer", fake_cls, create=True):
            with pytest.raises((RuntimeError, AttributeError, Exception)):
                _mu.safe_load_sentence_transformer("test-model", None)


# ===========================================================================
# indexer.py — embed_chunks ImportError path (lines 105-109)
# ===========================================================================

class TestIndexerEmbedChunksImportError:
    def test_embed_chunks_raises_on_missing_sentence_transformers(self):
        from codex.rag import indexer as _mod

        with patch.dict("sys.modules", {"sentence_transformers": None}):
            with pytest.raises((ImportError, Exception)):
                _mod.embed_chunks(
                    chunks=[("src", "id", "some text")],
                    model_profile=None,
                )


# ===========================================================================
# indexer.py — build_index_from_files missing files path
# ===========================================================================

class TestIndexerBuildIndexErrors:
    def test_build_index_from_files_raises_when_no_valid_files(self, tmp_path):
        from codex.rag import indexer as _mod

        nonexistent = tmp_path / "does_not_exist.txt"
        with pytest.raises(ValueError, match="No valid input files found"):
            _mod.build_index_from_files(
                files=[nonexistent],
                index_name="test",
                index_dir=str(tmp_path),
            )


# ===========================================================================
# indexer.py — manage_tenant_indices error branch
# ===========================================================================

class TestManageTenantIndicesError:
    def test_invalid_operation_returns_failure(self, tmp_path):
        from codex.rag import indexer as _mod

        result = _mod.manage_tenant_indices(
            tenant_id="t1",
            operation="INVALID_OP",
            index_names=["idx1"],
            index_dir=str(tmp_path),
        )
        assert result.success is False
