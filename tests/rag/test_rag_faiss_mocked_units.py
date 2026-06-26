from __future__ import annotations

import json
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

from codex.rag.cache.embedding_cache import EmbeddingCache
from codex.rag.embeddings import CachedEmbeddingProvider, OpenAIEmbeddingProvider
from codex.rag.indexer import persist_index
from codex.rag.retriever import Retriever


def test_openai_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key not provided"):
        OpenAIEmbeddingProvider()


def test_cached_embedding_provider_cache_hit(tmp_path):
    class StubProvider:
        def __init__(self):
            self.calls = 0

        def encode(self, texts, **_kwargs):
            self.calls += 1
            return np.ones((len(texts), 3), dtype=np.float32)

        def get_dimension(self):
            return 3

    provider = StubProvider()
    cached = CachedEmbeddingProvider(provider=provider, cache_dir=str(tmp_path))
    first = cached.encode(["a", "b"], cache_key="k1")
    second = cached.encode(["a", "b"], cache_key="k1")
    assert provider.calls == 1, "calls is not valid"
    np.testing.assert_allclose(first, second)


def test_persist_index_with_faiss_mock(monkeypatch, tmp_path):
    class FakeIndex:
        def __init__(self, dim):
            self.dim = dim
            self.ntotal = 0

        def add(self, vecs):
            self.ntotal += len(vecs)

    class FakeFaiss:
        def IndexFlatL2(self, dim):
            return FakeIndex(dim)

        def write_index(self, index, path):
            Path(path).write_text(f"fake-index:{index.ntotal}", encoding="utf-8")

    from codex.rag import indexer

    monkeypatch.setattr(indexer, "faiss", FakeFaiss())
    embeddings = np.random.randn(2, 4).astype(np.float32)
    chunks = [(0, 4, "one"), (5, 9, "two")]
    out = persist_index(
        index_name="mocked",
        embeddings=embeddings,
        chunks=chunks,
        tenant_id="tenant",
        index_dir=str(tmp_path),
    )
    assert (out / "index.faiss").exists(), "Condition must be true"
    assert (out / "chunks.json").exists(), "Condition must be true"
    assert json.loads((out / "metadata.json").read_text(encoding="utf-8"))["num_vectors"] == 2


def test_retriever_query_with_mocked_faiss(monkeypatch):
    class FakeIndex:
        ntotal = 2

        def search(self, _embeddings, top_k):
            distances = np.array([[0.2, 0.8]], dtype=np.float32)
            indices = np.array([[0, 1]], dtype=np.int64)
            return distances[:, :top_k], indices[:, :top_k]

    class FakeModel:
        def encode(self, *_args, **_kwargs):
            return np.array([[0.1, 0.2]], dtype=np.float32)

    def fake_load_index(self):
        self.faiss_index = FakeIndex()
        self.chunks_metadata = [
            {"id": 0, "text": "alpha", "start": 0, "end": 40, "file": "a.py", "text_hash": "a1"},
            {"id": 1, "text": "beta", "start": 40, "end": 80, "file": "b.py", "text_hash": "b2"},
        ]
        self.index_metadata = {}

    def fake_load_model(self):
        self.model = FakeModel()

    monkeypatch.setattr(Retriever, "_load_index", fake_load_index)
    monkeypatch.setattr(Retriever, "_load_model", fake_load_model)

    retriever = Retriever(index_dir=".", index_name="x", tenant_id="t")
    results = retriever.query("query", top_k=2, min_score=0.5)
    assert len(results) == 1, "Results must not be empty"
    assert results[0]["file"] == "a.py", "Result must not be empty"


def test_embedding_cache_set_get_non_numeric_value():
    cache = EmbeddingCache(max_size=10)
    cache.set("string-key", "value")
    result = cache.get("string-key")
    assert result is not None, "result must be initialized"
