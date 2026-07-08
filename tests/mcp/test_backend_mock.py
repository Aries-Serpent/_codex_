"""
Test Backend Mock

Test module for backend mock.
"""

# Tests for the mock backend
import pytest

from mcp.backends.interface import VectorItem
from mcp.backends.mock_backend import InMemoryMockBackend


@pytest.fixture
def mock_backend() -> InMemoryMockBackend:
    b = InMemoryMockBackend()
    b.connect()
    return b


def test_upsert_and_query(mock_backend: InMemoryMockBackend):
    namespace = "testns"
    items = [
        VectorItem(
            {"id": "a", "embedding": [1.0, 0.0], "content": "apple", "metadata": {"tag": "fruit"}}
        ),
        VectorItem(
            {"id": "b", "embedding": [0.9, 0.1], "content": "apricot", "metadata": {"tag": "fruit"}}
        ),
        VectorItem(
            {"id": "c", "embedding": [0.0, 1.0], "content": "banana", "metadata": {"tag": "fruit"}}
        ),
    ]
    mock_backend.upsert_batch(namespace, items)
    results = mock_backend.query_top_k(namespace, [1.0, 0.0], top_k=2)
    assert len(results) == 2, "Results must not be empty"
    assert results[0]["id"] in {"a", "b"}
    assert results[0]["score"] >= results[1]["score"], "Value must be greater than zero"


def test_delete_and_health(mock_backend: InMemoryMockBackend):
    ns = "delns"
    item = VectorItem({"id": "x", "embedding": [0.5, 0.5], "content": "x", "metadata": {}})
    mock_backend.upsert_batch(ns, [item])
    deleted_first = mock_backend.delete(ns, "x")
    assert deleted_first is True, "deleted_first is not valid"
    # delete again returns False
    deleted_second = mock_backend.delete(ns, "x")
    assert deleted_second is False, "deleted_second is not valid"
    health = mock_backend.health_check()
    assert health["status"] == "ok", "Condition must be true"
