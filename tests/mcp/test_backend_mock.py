"""
Test Backend Mock

Test module for backend mock.
"""

# Tests for the mock backend
import pytest
from src.mcp.backends.mock_backend import InMemoryMockBackend
from src.mcp.backends.interface import VectorItem


@pytest.fixture
def mock_backend() -> InMemoryMockBackend:
    b = InMemoryMockBackend()
    b.connect()
    return b


def test_upsert_and_query(mock_backend: InMemoryMockBackend):
    namespace = "testns"
    items = [
        VectorItem({"id": "a", "embedding": [1.0, 0.0], "content": "apple", "metadata": {"tag": "fruit"}}),
        VectorItem({"id": "b", "embedding": [0.9, 0.1], "content": "apricot", "metadata": {"tag": "fruit"}}),
        VectorItem({"id": "c", "embedding": [0.0, 1.0], "content": "banana", "metadata": {"tag": "fruit"}}),
    ]
    mock_backend.upsert_batch(namespace, items)
    results = mock_backend.query_top_k(namespace, [1.0, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0]["id"] in {"a", "b"}
    assert results[0]["score"] >= results[1]["score"]


def test_delete_and_health(mock_backend: InMemoryMockBackend):
    ns = "delns"
    item = VectorItem({"id": "x", "embedding": [0.5, 0.5], "content": "x", "metadata": {}})
    mock_backend.upsert_batch(ns, [item])
    assert mock_backend.delete(ns, "x") is True
    # delete again returns False
    assert mock_backend.delete(ns, "x") is False
    health = mock_backend.health_check()
    assert health["status"] == "ok"
