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
pytest.importorskip(
    "numpy",
    reason="numpy not installed — RAG coverage tests require the full RAG extras",
)


def _import_retriever():
    """Import codex.rag.retriever with a clearer error message on failure."""
    try:
        from codex.rag import retriever as _mod
    except ImportError as exc:
        raise ImportError(
            "Failed to import codex.rag.retriever; ensure codex.rag and its "
            "dependencies are installed. Original error: "
            f"{exc.__class__.__name__}: {exc}"
        ) from exc
    return _mod


# ===========================================================================
# retriever.py — _load_model error paths (lines 78-103)
# ===========================================================================


class TestRetrieverLoadModelErrors:
    """Cover _load_model() branches that are not exercised by the main test suite."""

    def test_load_model_raises_when_sentence_transformers_none(self):
        _mod = _import_retriever()

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
            with patch(
                "codex.rag._model_utils.safe_load_sentence_transformer",
                side_effect=RuntimeError("load failed"),
            ):
                r = _mod.Retriever.__new__(_mod.Retriever)
                r.model_name = "test-model"
                r.cache_dir = None
                with pytest.raises(RuntimeError, match="load failed"):
                    r._load_model()

    def test_load_model_propagates_value_error(self):
        _mod = _import_retriever()

        sentinel = MagicMock()
        with patch.object(_mod, "SentenceTransformer", sentinel):
            with patch(
                "codex.rag._model_utils.safe_load_sentence_transformer",
                side_effect=ValueError("bad value"),
            ):
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
        _mod = _import_retriever()

        with patch("codex.rag.indexer.load_index", side_effect=RuntimeError("corrupt index")):
            with pytest.raises(RuntimeError, match="corrupt index"):
                _mod.Retriever(index_dir=str(tmp_path), index_name="test")


# ===========================================================================
# retriever.py — Retriever.reload (lines 261-262)
# ===========================================================================


class TestRetrieverReload:
    def test_reload_calls_load_index(self, tmp_path):
        _mod = _import_retriever()

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
        assert len(results) == 2, "Results must not be empty"
        assert results[0]["index_name"] == "idx1", "Result must not be empty"

    def test_query_handles_retriever_exception(self):
        from codex.rag import retriever as _mod

        mir = _mod.MultiIndexRetriever.__new__(_mod.MultiIndexRetriever)
        r1 = MagicMock()
        r1.index_name = "broken"
        r1.tenant_id = "t1"
        r1.query.side_effect = RuntimeError("index unavailable")
        mir.retrievers = [r1]

        results = mir.query("test", top_k=5)
        assert results == [], "Result must not be empty"

    def test_get_stats_delegates_to_retrievers(self):
        from codex.rag import retriever as _mod

        mir = _mod.MultiIndexRetriever.__new__(_mod.MultiIndexRetriever)
        r1 = MagicMock()
        r1.get_stats.return_value = {"index": "idx1", "num_chunks": 10}
        mir.retrievers = [r1]
        stats = mir.get_stats()
        assert stats[0]["index"] == "idx1", "Condition must be true"


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
        assert cr._normalize_query("  Hello WORLD  ") == "hello world", "Condition must be true"

    def test_normalize_query_off_returns_original(self):
        cr = self._make_cached_retriever()
        cr.normalize_queries = False
        assert cr._normalize_query("  Hello  ") == "  Hello  ", "Condition must be true"

    def test_make_cache_key_is_deterministic(self):
        cr = self._make_cached_retriever()
        k1 = cr._make_cache_key("test query", 5, None)
        k2 = cr._make_cache_key("test query", 5, None)
        assert k1 == k2, "k1 is not valid"

    def test_make_cache_key_varies_with_params(self):
        cr = self._make_cached_retriever()
        k1 = cr._make_cache_key("test", 5, None)
        k2 = cr._make_cache_key("test", 10, None)
        assert k1 != k2, "k1 is not valid"

    def test_is_cache_valid_false_for_missing_key(self):
        cr = self._make_cached_retriever()
        assert cr._is_cache_valid("nonexistent_key") is False, "Condition must be true"

    def test_is_cache_valid_becomes_false_after_explicit_invalidation(self):
        """Verify that removing the timestamp entry invalidates _is_cache_valid.

        _is_cache_valid() checks cache_timestamps (not query_cache) for TTL
        validity.  Invalidation is performed by removing the key from
        cache_timestamps; query_cache is NOT consulted by _is_cache_valid(),
        so clearing it would have no bearing on the result.
        """
        import time

        cr = self._make_cached_retriever()
        key = "k1"
        cr.query_cache.put(key, [{"text": "cached"}])
        cr.cache_timestamps[key] = time.time()
        assert cr._is_cache_valid(key) is True, "Condition must be true"

        # Remove timestamp entry — this is the authoritative invalidation path.
        cr.cache_timestamps.pop(key, None)
        assert cr._is_cache_valid(key) is False, "Condition must be true"

    def test_is_cache_valid_false_for_expired_entry(self):
        import time

        cr = self._make_cached_retriever()
        cr.cache_ttl = 0  # immediately expired
        cr.cache_timestamps["k1"] = time.time() - 1
        assert cr._is_cache_valid("k1") is False, "Condition must be true"

    def test_cache_hit_returns_cached_results(self):
        import time

        cr = self._make_cached_retriever()
        cached = [{"text": "cached", "score": 0.1}]
        key = cr._make_cache_key("hello", 5, None)
        cr.query_cache.put(key, cached)
        cr.cache_timestamps[key] = time.time()

        with patch.object(cr, "query", side_effect=AssertionError("should not call")):
            results = cr.query_with_cache("hello", top_k=5)
        assert results == cached, "Result must not be empty"

    def test_cache_miss_calls_query_and_caches(self):
        cr = self._make_cached_retriever()
        expected = [{"text": "result", "score": 0.2}]

        with patch.object(cr, "query", return_value=expected):
            results = cr.query_with_cache("new query", top_k=5)

        assert results == expected, "Result must not be empty"
        key = cr._make_cache_key("new query", 5, None)
        assert cr.query_cache.get(key) == expected, "Condition must be true"

    def test_clear_cache_empties_all(self):
        import time

        cr = self._make_cached_retriever()
        cr.query_cache.put("k1", [])
        cr.cache_timestamps["k1"] = time.time()
        cr.clear_cache()
        assert len(cr.cache_timestamps) == 0, "Collection must not be empty"

    def test_get_cache_stats_includes_ttl(self):
        cr = self._make_cached_retriever()
        stats = cr.get_cache_stats()
        assert stats["ttl"] == 60, "Condition must be true"

    def test_invalidate_expired_removes_stale_entries(self):
        import time

        cr = self._make_cached_retriever()
        cr.cache_ttl = 0  # immediately expired
        cr.cache_timestamps["k1"] = time.time() - 1
        cr.query_cache.put("k1", [])
        cr.invalidate_expired()
        assert "k1" not in cr.cache_timestamps, "Condition must be true"


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
        assert rr._retriever is mock_retriever, "_retriever is not valid"

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
        assert has_meta_tensors(model) is True, "has_meta_tens is not valid"

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
        assert has_meta_tensors(model) is True, "has_meta_tens is not valid"

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
        assert has_meta_tensors(model) is True, "has_meta_tens is not valid"

    def test_model_device_attribute_meta_returns_true(self):
        from codex.rag.utils import has_meta_tensors

        device = SimpleNamespace(type="meta")
        model = SimpleNamespace(
            parameters=lambda: iter([]),
            buffers=lambda: iter([]),
            device=device,
        )
        assert has_meta_tensors(model) is True, "has_meta_tens is not valid"

    def test_exception_in_has_meta_tensors_returns_none(self):
        from codex.rag.utils import has_meta_tensors

        model = SimpleNamespace(parameters=MagicMock(side_effect=RuntimeError("boom")))
        result = has_meta_tensors(model)
        assert result is None, "Result must not be empty"

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
        assert result is False, "Result must not be empty"

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
        assert result is False, "Result must not be empty"


# ===========================================================================
# utils.py — safe_model_to_device meta/None/import paths (lines 182-315)
# ===========================================================================


class TestSafeModelToDevice:
    def test_returns_model_when_has_meta_tensors_is_none(self):
        from codex.rag.utils import safe_model_to_device

        model = object()
        with patch("codex.rag.utils.has_meta_tensors", return_value=None):
            result = safe_model_to_device(model, device="cpu")
        assert result is model, "Result must not be empty"

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
        assert result is model, "Result must not be empty"

    def test_meta_path_skips_reset_when_no_modules(self):
        from codex.rag.utils import safe_model_to_device

        model = SimpleNamespace()
        materialized = SimpleNamespace()
        model.to_empty = MagicMock(return_value=materialized)

        with patch("codex.rag.utils.has_meta_tensors", return_value=True):
            result = safe_model_to_device(model, device="cpu")
        assert result is materialized, "Result must not be empty"

    def test_import_error_falls_back_to_try_model_to(self):
        from codex.rag.utils import safe_model_to_device

        model = SimpleNamespace()
        model.to = MagicMock(return_value=model)

        with patch("codex.rag.utils.has_meta_tensors", side_effect=ImportError("no torch")):
            result = safe_model_to_device(model, device="cpu")
        assert result is model, "Result must not be empty"

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
        assert result is model, "Result must not be empty"
        model.to.assert_called()

    def test_typeerror_fallback_to_positional(self):
        from codex.rag.utils import _try_model_to

        model = MagicMock()
        model.to.side_effect = [TypeError("no kwargs"), model]
        result = _try_model_to(model, "cpu")
        assert result is model, "Result must not be empty"

    def test_returns_model_when_no_to_method(self):
        from codex.rag.utils import _try_model_to

        model = SimpleNamespace()  # no .to()
        result = _try_model_to(model, "cpu")
        assert result is model, "Result must not be empty"


# ===========================================================================
# _model_utils.py — safe_load_sentence_transformer error paths (lines 80-100)
# ===========================================================================


class TestModelUtilsSafeLoad:
    def test_raises_on_load_failure(self):
        pytest.importorskip(
            "sentence_transformers",
            reason="sentence_transformers not installed — skipping meta-tensor load tests",
        )
        from codex.rag._model_utils import safe_load_sentence_transformer

        with patch(
            "sentence_transformers.SentenceTransformer",
            side_effect=RuntimeError("simulated load failure"),
        ):
            with pytest.raises(RuntimeError, match="simulated load failure"):
                safe_load_sentence_transformer("nonexistent-model-xyz", None)

    def test_raises_attributeerror_on_missing_to_empty(self):
        """Raise RuntimeError when meta fallback returns a model without to_empty()."""
        pytest.importorskip(
            "sentence_transformers",
            reason="sentence_transformers not installed — skipping meta-tensor load tests",
        )
        from codex.rag import _model_utils as _mu

        no_to_empty_model = MagicMock(spec=[])  # no to_empty attribute

        # First call (device="cpu") → NotImplementedError triggers meta-tensor fallback.
        # Second call (device="meta") → returns a model without to_empty.
        with (
            patch(
                "sentence_transformers.SentenceTransformer",
                side_effect=[NotImplementedError("meta tensor"), no_to_empty_model],
            ),
            pytest.raises(RuntimeError, match="to_empty"),
        ):
            _mu.safe_load_sentence_transformer("test-model", None)

    def test_meta_fallback_materializes_and_returns_model(self, monkeypatch):
        """Meta fallback should materialize to CPU and verify all params are non-meta."""
        from codex.rag._model_utils import safe_load_sentence_transformer

        fake_st_module = SimpleNamespace()
        materialized_model = MagicMock()
        materialized_model.named_parameters.return_value = [
            ("encoder.weight", SimpleNamespace(is_meta=False))
        ]
        meta_model = MagicMock()
        meta_model.to_empty.return_value = materialized_model

        fake_constructor = MagicMock(
            side_effect=[NotImplementedError("meta tensor"), meta_model]
        )
        fake_st_module.SentenceTransformer = fake_constructor
        monkeypatch.setitem(sys.modules, "sentence_transformers", fake_st_module)

        result = safe_load_sentence_transformer("test-model", None)

        assert result is materialized_model
        meta_model.to_empty.assert_called_once_with(device="cpu")
        materialized_model.eval.assert_called_once_with()

    def test_meta_fallback_raises_when_meta_params_remain(self, monkeypatch):
        """Meta fallback should fail if any parameter remains on the meta device."""
        from codex.rag._model_utils import safe_load_sentence_transformer

        fake_st_module = SimpleNamespace()
        materialized_model = MagicMock()
        materialized_model.named_parameters.return_value = [
            ("encoder.weight", SimpleNamespace(is_meta=True))
        ]
        meta_model = MagicMock()
        meta_model.to_empty.return_value = materialized_model

        fake_constructor = MagicMock(
            side_effect=[NotImplementedError("meta tensor"), meta_model]
        )
        fake_st_module.SentenceTransformer = fake_constructor
        monkeypatch.setitem(sys.modules, "sentence_transformers", fake_st_module)

        with pytest.raises(RuntimeError, match="Meta tensors still present"):
            safe_load_sentence_transformer("test-model", None)


# ===========================================================================
# indexer.py — embed_chunks ImportError path (lines 105-109)
# ===========================================================================


class TestIndexerEmbedChunksImportError:
    def test_embed_chunks_raises_on_missing_sentence_transformers(self):
        from codex.rag import indexer as _mod

        with patch.dict("sys.modules", {"sentence_transformers": None}):
            with pytest.raises(ImportError):
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
        assert result.success is False, "Result must not be empty"


# ===========================================================================
# ingestion/chunker.py — SentenceChunker edge cases
# ===========================================================================


class TestSentenceChunkerEdgeCases:
    """Cover SentenceChunker edge cases for whitespace-only split results."""

    def test_sentence_chunker_handles_whitespace_only_split(self):
        """Verify SentenceChunker filters out whitespace-only sentences."""
        from codex.rag.ingestion.chunker import ChunkingConfig, ChunkingStrategy, SentenceChunker

        config = ChunkingConfig(
            strategy=ChunkingStrategy.SENTENCE,
            chunk_size=50,
            min_chunk_size=5,
        )
        chunker = SentenceChunker(config)
        # Text with excessive whitespace that creates empty splits
        text = "First sentence.    \n\n\n    Second sentence."
        chunks = chunker.chunk(text)
        # All chunks should have non-whitespace content
        for chunk in chunks:
            assert chunk.text.strip(), f"Chunk should not be whitespace-only: {chunk.text!r}"

    def test_fixed_size_chunker_min_chunk_size_filter(self):
        """Cover FixedSizeChunker filtering of sub-minimum chunks."""
        from codex.rag.ingestion.chunker import ChunkingConfig, ChunkingStrategy, FixedSizeChunker

        config = ChunkingConfig(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100,
            min_chunk_size=50,
            chunk_overlap=10,
        )
        chunker = FixedSizeChunker(config)
        # Short text that would create a small trailing chunk
        text = "A" * 120  # Will be split into 100 + 30 (with overlap)
        chunks = chunker.chunk(text)
        # The trailing 30-char chunk should be filtered out (< min_chunk_size)
        for chunk in chunks:
            assert len(chunk.text) >= config.min_chunk_size, f"Chunk too small: {len(chunk.text)}"
