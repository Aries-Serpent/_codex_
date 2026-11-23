"""RAG retriever construction and cache margin tests."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from aries_serpent_core.rag import retriever


def _bare_retriever() -> retriever.Retriever:
    instance = retriever.Retriever.__new__(retriever.Retriever)
    instance.faiss_index = None
    instance.model = None
    instance.chunks_metadata = []
    instance.index_metadata = {}
    instance.index_dir = "."
    instance.index_name = "docs"
    instance.tenant_id = "tenant"
    instance.model_name = "model"
    instance.cache_dir = None
    return instance


def test_retriever_query_covers_unloaded_and_invalid_inputs() -> None:
    instance = _bare_retriever()
    assert instance.query("text") == []

    instance.faiss_index = object()
    assert instance.query(" ") == []
    assert instance.query("text") == []


def test_load_model_covers_empty_and_tfidf_fallback(monkeypatch) -> None:
    instance = _bare_retriever()
    instance._load_model()
    assert instance.model is None

    instance.chunks_metadata = [{"text": ""}, {"text": "indexed chunk"}]
    instance.index_metadata = {"dimension": 8}
    instance.faiss_index = None
    monkeypatch.setattr(retriever, "SentenceTransformer", None)

    from aries_serpent_core.rag import embeddings

    fitted = []

    class Provider:
        def __init__(self, max_features: int) -> None:
            assert max_features == 8

        def encode(self, texts):
            fitted.extend(texts)
            return texts

    monkeypatch.setattr(embeddings, "TfidfEmbeddingProvider", Provider)
    instance._load_model()
    assert fitted == ["indexed chunk"]
    assert isinstance(instance.model, Provider)

    instance.chunks_metadata = [{"text": ""}]
    instance._load_model()
    assert instance.model is None


def test_multi_index_constructor_skips_unloaded_and_failed_indices(monkeypatch) -> None:
    class FakeRetriever:
        def __init__(self, *, index_name, **_kwargs) -> None:
            if index_name == "broken":
                raise ValueError("broken index")
            self.faiss_index = None if index_name == "empty" else object()

    monkeypatch.setattr(retriever, "Retriever", FakeRetriever)
    multi = retriever.MultiIndexRetriever(
        [
            {"index_name": "empty"},
            {"index_name": "broken", "tenant_id": "other"},
            {"index_name": "loaded"},
        ]
    )
    assert len(multi.retrievers) == 1
    assert multi.retrievers[0].faiss_index is not None


def test_cached_retriever_initialization_and_expired_cache(monkeypatch) -> None:
    def init(self, index_dir, index_name, tenant_id, model_name, cache_dir=None, **_kwargs):
        self.faiss_index = None
        self.model = None
        self.chunks_metadata = []
        self.index_metadata = {}

    monkeypatch.setattr(retriever.Retriever, "__init__", init)
    cached = retriever.CachedRetriever(
        cache_ttl=60,
        cache_maxsize=4,
        normalize_queries=False,
    )

    assert cached.normalize_queries is False
    assert cached._normalize_query("  Exact  ") == "  Exact  "
    cached.query_cache.put("stale", [{"text": "old"}])
    cached.cache_timestamps["stale"] = 0
    assert not cached._is_cache_valid("stale")
    cached.invalidate_expired()
    assert "stale" not in cached.query_cache.cache
    assert cached.get_cache_stats()["valid_entries"] == 0


def test_rag_retriever_loads_and_delegates(monkeypatch) -> None:
    expected = [{"text": "result"}]

    class FakeRetriever:
        def __init__(self, **_kwargs) -> None:
            pass

        def query(self, text, *, top_k, min_score):
            assert (text, top_k, min_score) == ("query", 3, 0.2)
            return expected

    monkeypatch.setattr(retriever, "Retriever", FakeRetriever)
    facade = retriever.RAGRetriever(device="cpu").load(index_name="docs")
    assert facade.query("query", top_k=3, min_score=0.2) == expected


def test_cached_retriever_removes_expired_entry_before_requery(monkeypatch) -> None:
    cached = retriever.CachedRetriever.__new__(retriever.CachedRetriever)
    cached.cache_ttl = 0
    cached.normalize_queries = True
    cached.query_cache = retriever.LRUCache(maxsize=10)
    cached.cache_timestamps = {}
    key = cached._make_cache_key("query", 5, None)
    cached.query_cache.put(key, [{"text": "stale"}])
    cached.cache_timestamps[key] = 0
    monkeypatch.setattr(cached, "query", lambda *_args, **_kwargs: [{"text": "fresh"}])

    result = cached.query_with_cache("query")

    assert result == [{"text": "fresh"}]
    assert cached.query_cache.get(key) == result
    assert cached.cache_timestamps[key] > 0
