from __future__ import annotations

from typing import Any, Iterable


class MockAdapter:
    """
    Minimal mock adapter for local dev and tests.
    """

    def __init__(self):
        self.query_calls: list[dict[str, Any]] = []
        self.upsert_calls: list[dict[str, Any]] = []
        self.delete_calls: list[dict[str, Any]] = []

    def connect(self) -> None:
        return None

    def query_top_k(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def upsert_batch(self, namespace: str, items: Iterable[dict[str, Any]]) -> None:
        self.upsert_calls.append({"namespace": namespace, "items": list(items)})

    def delete(self, namespace: str, id: str) -> bool:
        self.delete_calls.append({"namespace": namespace, "id": id})
        return True

    def health_check(self) -> dict[str, Any]:
        return {"status": "ok", "adapter": "mock"}
