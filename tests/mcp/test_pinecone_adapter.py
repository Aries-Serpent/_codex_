"""
Test Pinecone Adapter

Test module for pinecone adapter.
"""

# Unit tests for PineconeAdapter using monkeypatch to fake pinecone SDK.
# Tests are import-safe and do not require provider credentials or network access.

import pytest

from mcp.backends.pinecone_adapter import PineconeAdapter


class FakeIndex:
    def __init__(self):
        self._data = {}

    def upsert(self, vectors=None, namespace=None):
        for id_, vec, md in vectors or []:
            key = f"{namespace}:{id_}"
            self._data[key] = {"id": id_, "vector": vec, "metadata": md}

    def query(self, vector=None, top_k=5, filter=None, namespace=None):
        matches = []
        for key, val in self._data.items():
            if namespace is not None and not key.startswith(f"{namespace}:"):
                continue
            score = sum(x * y for x, y in zip(vector, val["vector"]))
            matches.append({"id": val["id"], "score": score, "metadata": val["metadata"]})
        matches.sort(key=lambda m: m["score"], reverse=True)
        return {"matches": matches[:top_k]}

    def delete(self, ids=None, namespace=None):
        for id_ in ids or []:
            key = f"{namespace}:{id_}"
            if key in self._data:
                del self._data[key]


class FakePineconeModule:
    def __init__(self):
        self._indexes = {}

    def init(self, api_key=None, environment=None):
        pass

    def Index(self, name):
        idx = self._indexes.get(name)
        if not idx:
            idx = FakeIndex()
            self._indexes[name] = idx
        return idx


@pytest.fixture(autouse=True)
def fake_pinecone(monkeypatch):
    fake = FakePineconeModule()
    monkeypatch.setitem(__import__("sys").modules, "pinecone", fake)
    # Ensure unit tests can call fake index by enabling live-tests guard in test scope
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "true")
    monkeypatch.setenv("PINECONE_API_KEY", "test")
    monkeypatch.setenv("PINECONE_ENV", "test")
    yield fake


def test_pinecone_adapter_upsert_query_delete():
    adapter = PineconeAdapter(index_name="testidx")
    adapter.connect()
    ns = "tenantA"
    items = [
        {"id": "i1", "embedding": [1.0, 0.0], "content": "a", "metadata": {"k": "v"}},
        {"id": "i2", "embedding": [0.9, 0.1], "content": "b", "metadata": {"k": "v"}},
    ]
    adapter.upsert_batch(ns, items)
    res = adapter.query_top_k(ns, [1.0, 0.0], top_k=2)
    assert isinstance(res, list)
    assert len(res) >= 1, "Res must not be empty"
    assert res[0]["id"] in {"i1", "i2"}
    deleted = adapter.delete(ns, "i1")
    assert deleted is True, "deleted is not valid"
    res2 = adapter.query_top_k(ns, [1.0, 0.0], top_k=5)
    ids = [r["id"] for r in res2]
    assert "i1" not in ids, "Condition must be true"


def test_pinecone_health_disconnected(monkeypatch):
    # Clear env to simulate missing credentials; adapter should be disconnected but health returns shape
    monkeypatch.delenv("PINECONE_API_KEY", raising=False)
    monkeypatch.delenv("PINECONE_ENV", raising=False)
    adapter = PineconeAdapter(index_name="testidx2")
    adapter.connect()
    h = adapter.health_check()
    assert "status" in h, "Condition must be true"
    assert h["adapter"] == "pinecone", "Condition must be true"
