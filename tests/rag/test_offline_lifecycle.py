"""Exercise the actual public embedding/cache APIs without remote services."""

from unittest.mock import Mock, patch

import pytest

np = pytest.importorskip("numpy")

from aries_serpent_core.rag import embeddings
from aries_serpent_core.rag.cache.embedding_cache import EmbeddingCache
from aries_serpent_core.rag.cache.query_cache import QueryCache, QueryCacheConfig


def test_tfidf_and_cached_embedding_provider_lifecycle(tmp_path):
    pytest.importorskip("sklearn")
    corpus = [
        "autonomous agentic repository governance",
        "faiss vector index semantic retrieval",
        "continuous integration coverage validation gate",
    ]
    provider = embeddings.create_embedding_provider("tfidf", use_cache=False, max_features=16)
    assert isinstance(provider, embeddings.TfidfEmbeddingProvider)
    cached = embeddings.CachedEmbeddingProvider(provider, cache_dir=str(tmp_path))
    with patch.object(provider, "encode", wraps=provider.encode) as encode:
        first = cached.encode(corpus, cache_key="corpus", metadata={"file_mtime": 1})
        second = cached.encode(corpus, cache_key="corpus", metadata={"file_mtime": 1})
        assert encode.call_count == 1
        assert first.shape == (3, 16)
        np.testing.assert_allclose(first, second)
        cached.encode(corpus, cache_key="corpus", metadata={"file_mtime": 2})
        assert encode.call_count == 2
    assert cached.get_stats()["cache_hits"] == 1
    assert cached.get_stats()["cache_misses"] == 2
    cached.clear_cache()
    assert not list(tmp_path.iterdir())
    with pytest.raises(ValueError, match="Unknown provider type"):
        embeddings.create_embedding_provider("invalid_backend_name", use_cache=False)


def test_local_initialization_failure_is_not_swallowed():
    with patch(
        "aries_serpent_core.rag._model_utils.safe_load_sentence_transformer",
        side_effect=OSError("Offline"),
    ):
        with pytest.raises(OSError, match="Offline"):
            embeddings.LocalSentenceTransformerProvider()


def test_openai_factory_uses_mock_client(monkeypatch):
    monkeypatch.delenv("RAG_OPENAI_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key required"):
        embeddings.create_embedding_provider("openai", use_cache=False)
    with patch.object(embeddings, "OpenAI") as client:
        client.return_value.embeddings.create.return_value.data = [Mock(embedding=[1.0, 2.0])]
        provider = embeddings.create_embedding_provider(
            "openai", api_key="test-key", use_cache=False
        )
        assert isinstance(provider, embeddings.OpenAIEmbeddingProvider)
        np.testing.assert_allclose(provider.encode(["offline"]), [[1.0, 2.0]])
        client.assert_called_once_with(api_key="test-key")


def test_embedding_cache_batch_api():
    cache = EmbeddingCache()
    vectors = [np.ones(8, dtype=np.float32), np.full(8, 2, dtype=np.float32)]
    cache.put_batch(["first", "second"], vectors)
    found, indices = cache.get_batch(["first", "missing", "second"])
    assert indices == [0, 2]
    np.testing.assert_allclose(found, vectors)


def test_query_cache_ttl_and_lru():
    with patch("aries_serpent_core.rag.cache.query_cache.time.time", return_value=100):
        cache = QueryCache(QueryCacheConfig(max_size=2, default_ttl=10))
        cache.put("first", [1])
        cache.put("second", [2])
        assert cache.get("first") == [1]
        cache.put("third", [3])
        assert cache.get("second") is None
        assert cache.get_stats().evictions == 1
    with patch("aries_serpent_core.rag.cache.query_cache.time.time", return_value=111):
        assert cache.get("first") is None
        assert cache.get("third") is None
