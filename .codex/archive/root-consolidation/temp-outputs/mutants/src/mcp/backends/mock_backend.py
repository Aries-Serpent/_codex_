"""
Mock Backend Module

This module provides functionality for mock backend.

Usage:
    from backends.mock_backend import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# Simple in-memory mock vector backend implementing BackendAdapter
import math
import threading
from collections.abc import Iterable
from typing import Any, Optional

from .interface import BackendAdapter, BackendResponse, VectorItem


def cosine_similarity(a: list[float], b: list[float]) -> float:
    # deterministic and simple
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    lena = math.sqrt(sum(x * x for x in a)) or 1.0
    lenb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (lena * lenb)


class InMemoryMockBackend(BackendAdapter):
    def __init__(self) -> None:
        # storage: namespace -> id -> VectorItem
        self._store: dict[str, dict[str, VectorItem]] = {}
        self._lock = threading.RLock()

    def connect(self) -> None:
        # nothing to connect; keep for parity
        return None

    def upsert_batch(self, namespace: str, items: Iterable[VectorItem]) -> None:
        with self._lock:
            ns = self._store.setdefault(namespace, {})
            for item in items:
                ns[item["id"]] = item.copy()  # type: ignore[assignment]

    def query_top_k(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        with self._lock:
            ns = self._store.get(namespace, {})
            results: list[BackendResponse] = []
            for item in ns.values():
                # simple metadata filter support
                if filters:
                    ok = True
                    for fk, fv in filters.items():
                        if item.get("metadata", {}).get(fk) != fv:
                            ok = False
                            break
                    if not ok:
                        continue
                emb = item.get("embedding")
                if not emb:
                    continue
                score = float(cosine_similarity(query_embedding, emb))
                results.append(
                    BackendResponse(
                        {
                            "id": item["id"],
                            "score": score,
                            "content": item.get("content", ""),
                            "metadata": item.get("metadata", {}),
                        }
                    )
                )
            # stable sort: highest score first; deterministic tie-break by id
            results.sort(key=lambda r: (-r["score"], r["id"]))
            return results[:top_k]

    def delete(self, namespace: str, id: str) -> bool:
        with self._lock:
            ns = self._store.get(namespace, {})
            if id in ns:
                del ns[id]
                return True
            return False

    def health_check(self) -> dict[str, Any]:
        # simple health payload
        return {
            "status": "ok",
            "backend": "mock",
            "namespaces": list(self._store.keys()),
        }
