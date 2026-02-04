"""FastAPI-based MCP HTTP prototype.

This module exposes preview-ready HTTP endpoints for MCP while keeping
compatibility with JSON-RPC behavior defined in `mcp.server`. It targets
Cloudflare Workers (edge proxy) and Fly.io (persistent container) hosts.
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import os
import time
from typing import Any, Iterable, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

DEFAULT_API_KEY = "dev-key"  # pragma: allowlist secret
DEFAULT_TOP_K = 5
MAX_TOP_K = 50
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class ContextItem(BaseModel):
    """Represents a stored context item for retrieval."""

    id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    """Request payload for /mcp/v1/query."""

    query: str
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=MAX_TOP_K)
    filters: Optional[dict[str, Any]] = None

    @validator("query")
    def _ensure_query(cls, value: str) -> str:  # noqa: D401
        """Require non-empty query strings."""
        if not value or not value.strip():
            raise ValueError("query cannot be empty")
        return value


class ContextUpsertRequest(BaseModel):
    """Request payload for /mcp/v1/context."""

    items: list[ContextItem]

    @validator("items")
    def _ensure_items(cls, value: list[ContextItem]) -> list[ContextItem]:  # noqa: D401
        if not value:
            raise ValueError("at least one item is required")
        return value


class InMemoryVectorStore:
    """Minimal in-memory vector store for previews.

    This is intentionally simple to stay offline-friendly. Replace with Chroma,
    Supabase, or Pinecone when scaling beyond previews.
    """

    def xǁInMemoryVectorStoreǁ__init____mutmut_orig(self, items: Optional[list[ContextItem]] = None) -> None:
        self._items: list[ContextItem] = items or []

    def xǁInMemoryVectorStoreǁ__init____mutmut_1(self, items: Optional[list[ContextItem]] = None) -> None:
        self._items: list[ContextItem] = None

    def xǁInMemoryVectorStoreǁ__init____mutmut_2(self, items: Optional[list[ContextItem]] = None) -> None:
        self._items: list[ContextItem] = items and []
    
    xǁInMemoryVectorStoreǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInMemoryVectorStoreǁ__init____mutmut_1': xǁInMemoryVectorStoreǁ__init____mutmut_1, 
        'xǁInMemoryVectorStoreǁ__init____mutmut_2': xǁInMemoryVectorStoreǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInMemoryVectorStoreǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁInMemoryVectorStoreǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁInMemoryVectorStoreǁ__init____mutmut_orig)
    xǁInMemoryVectorStoreǁ__init____mutmut_orig.__name__ = 'xǁInMemoryVectorStoreǁ__init__'

    @classmethod
    def seeded(cls) -> "InMemoryVectorStore":
        """Create a store with seed data for smoke tests."""
        seed_items = [
            ContextItem(id="demo-1", content="codex mcp prototype", metadata={"scope": "repo"}),
            ContextItem(id="demo-2", content="cloudflare workers edge", metadata={"scope": "edge"}),
            ContextItem(id="demo-3", content="fly io persistent mcp", metadata={"scope": "container"}),
        ]
        return cls(items=seed_items)

    def xǁInMemoryVectorStoreǁupsert_many__mutmut_orig(self, items: Iterable[ContextItem]) -> int:
        """Insert or replace items by id."""
        new_items = list(items)
        index = {item.id: item for item in self._items}
        for item in new_items:
            index[item.id] = item
        self._items = list(index.values())
        return len(new_items)

    def xǁInMemoryVectorStoreǁupsert_many__mutmut_1(self, items: Iterable[ContextItem]) -> int:
        """Insert or replace items by id."""
        new_items = None
        index = {item.id: item for item in self._items}
        for item in new_items:
            index[item.id] = item
        self._items = list(index.values())
        return len(new_items)

    def xǁInMemoryVectorStoreǁupsert_many__mutmut_2(self, items: Iterable[ContextItem]) -> int:
        """Insert or replace items by id."""
        new_items = list(None)
        index = {item.id: item for item in self._items}
        for item in new_items:
            index[item.id] = item
        self._items = list(index.values())
        return len(new_items)

    def xǁInMemoryVectorStoreǁupsert_many__mutmut_3(self, items: Iterable[ContextItem]) -> int:
        """Insert or replace items by id."""
        new_items = list(items)
        index = None
        for item in new_items:
            index[item.id] = item
        self._items = list(index.values())
        return len(new_items)

    def xǁInMemoryVectorStoreǁupsert_many__mutmut_4(self, items: Iterable[ContextItem]) -> int:
        """Insert or replace items by id."""
        new_items = list(items)
        index = {item.id: item for item in self._items}
        for item in new_items:
            index[item.id] = None
        self._items = list(index.values())
        return len(new_items)

    def xǁInMemoryVectorStoreǁupsert_many__mutmut_5(self, items: Iterable[ContextItem]) -> int:
        """Insert or replace items by id."""
        new_items = list(items)
        index = {item.id: item for item in self._items}
        for item in new_items:
            index[item.id] = item
        self._items = None
        return len(new_items)

    def xǁInMemoryVectorStoreǁupsert_many__mutmut_6(self, items: Iterable[ContextItem]) -> int:
        """Insert or replace items by id."""
        new_items = list(items)
        index = {item.id: item for item in self._items}
        for item in new_items:
            index[item.id] = item
        self._items = list(None)
        return len(new_items)
    
    xǁInMemoryVectorStoreǁupsert_many__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInMemoryVectorStoreǁupsert_many__mutmut_1': xǁInMemoryVectorStoreǁupsert_many__mutmut_1, 
        'xǁInMemoryVectorStoreǁupsert_many__mutmut_2': xǁInMemoryVectorStoreǁupsert_many__mutmut_2, 
        'xǁInMemoryVectorStoreǁupsert_many__mutmut_3': xǁInMemoryVectorStoreǁupsert_many__mutmut_3, 
        'xǁInMemoryVectorStoreǁupsert_many__mutmut_4': xǁInMemoryVectorStoreǁupsert_many__mutmut_4, 
        'xǁInMemoryVectorStoreǁupsert_many__mutmut_5': xǁInMemoryVectorStoreǁupsert_many__mutmut_5, 
        'xǁInMemoryVectorStoreǁupsert_many__mutmut_6': xǁInMemoryVectorStoreǁupsert_many__mutmut_6
    }
    
    def upsert_many(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInMemoryVectorStoreǁupsert_many__mutmut_orig"), object.__getattribute__(self, "xǁInMemoryVectorStoreǁupsert_many__mutmut_mutants"), args, kwargs, self)
        return result 
    
    upsert_many.__signature__ = _mutmut_signature(xǁInMemoryVectorStoreǁupsert_many__mutmut_orig)
    xǁInMemoryVectorStoreǁupsert_many__mutmut_orig.__name__ = 'xǁInMemoryVectorStoreǁupsert_many'

    def xǁInMemoryVectorStoreǁquery__mutmut_orig(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_1(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = None
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_2(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.upper()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_3(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = None
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_4(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters or any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_5(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(None):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_6(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(None) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_7(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) == v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_8(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                break

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_9(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = None
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_10(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 2.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_11(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized not in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_12(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.upper() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_13(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 1.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_14(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                None
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_15(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "XXidXX": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_16(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "ID": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_17(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "XXscoreXX": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_18(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "SCORE": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_19(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "XXcontentXX": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_20(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "CONTENT": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_21(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "XXmetadataXX": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_22(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "METADATA": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_23(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=None, reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_24(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=None)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_25(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_26(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], )
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_27(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: None, reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_28(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["XXscoreXX"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_29(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["SCORE"], reverse=True)
        return matches[:top_k]

    def xǁInMemoryVectorStoreǁquery__mutmut_30(self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Return top_k matches using naive scoring.

        The scoring is simple substring presence + metadata match to keep
        deterministic behavior without heavy dependencies.
        """

        normalized = query.lower()
        matches: list[dict[str, Any]] = []
        for item in self._items:
            if filters and any(item.metadata.get(k) != v for k, v in filters.items()):
                continue

            score = 1.0 if normalized in item.content.lower() else 0.1
            matches.append(
                {
                    "id": item.id,
                    "score": score,
                    "content": item.content,
                    "metadata": item.metadata,
                }
            )

        # Sort by score descending and limit to top_k
        matches.sort(key=lambda m: m["score"], reverse=False)
        return matches[:top_k]
    
    xǁInMemoryVectorStoreǁquery__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInMemoryVectorStoreǁquery__mutmut_1': xǁInMemoryVectorStoreǁquery__mutmut_1, 
        'xǁInMemoryVectorStoreǁquery__mutmut_2': xǁInMemoryVectorStoreǁquery__mutmut_2, 
        'xǁInMemoryVectorStoreǁquery__mutmut_3': xǁInMemoryVectorStoreǁquery__mutmut_3, 
        'xǁInMemoryVectorStoreǁquery__mutmut_4': xǁInMemoryVectorStoreǁquery__mutmut_4, 
        'xǁInMemoryVectorStoreǁquery__mutmut_5': xǁInMemoryVectorStoreǁquery__mutmut_5, 
        'xǁInMemoryVectorStoreǁquery__mutmut_6': xǁInMemoryVectorStoreǁquery__mutmut_6, 
        'xǁInMemoryVectorStoreǁquery__mutmut_7': xǁInMemoryVectorStoreǁquery__mutmut_7, 
        'xǁInMemoryVectorStoreǁquery__mutmut_8': xǁInMemoryVectorStoreǁquery__mutmut_8, 
        'xǁInMemoryVectorStoreǁquery__mutmut_9': xǁInMemoryVectorStoreǁquery__mutmut_9, 
        'xǁInMemoryVectorStoreǁquery__mutmut_10': xǁInMemoryVectorStoreǁquery__mutmut_10, 
        'xǁInMemoryVectorStoreǁquery__mutmut_11': xǁInMemoryVectorStoreǁquery__mutmut_11, 
        'xǁInMemoryVectorStoreǁquery__mutmut_12': xǁInMemoryVectorStoreǁquery__mutmut_12, 
        'xǁInMemoryVectorStoreǁquery__mutmut_13': xǁInMemoryVectorStoreǁquery__mutmut_13, 
        'xǁInMemoryVectorStoreǁquery__mutmut_14': xǁInMemoryVectorStoreǁquery__mutmut_14, 
        'xǁInMemoryVectorStoreǁquery__mutmut_15': xǁInMemoryVectorStoreǁquery__mutmut_15, 
        'xǁInMemoryVectorStoreǁquery__mutmut_16': xǁInMemoryVectorStoreǁquery__mutmut_16, 
        'xǁInMemoryVectorStoreǁquery__mutmut_17': xǁInMemoryVectorStoreǁquery__mutmut_17, 
        'xǁInMemoryVectorStoreǁquery__mutmut_18': xǁInMemoryVectorStoreǁquery__mutmut_18, 
        'xǁInMemoryVectorStoreǁquery__mutmut_19': xǁInMemoryVectorStoreǁquery__mutmut_19, 
        'xǁInMemoryVectorStoreǁquery__mutmut_20': xǁInMemoryVectorStoreǁquery__mutmut_20, 
        'xǁInMemoryVectorStoreǁquery__mutmut_21': xǁInMemoryVectorStoreǁquery__mutmut_21, 
        'xǁInMemoryVectorStoreǁquery__mutmut_22': xǁInMemoryVectorStoreǁquery__mutmut_22, 
        'xǁInMemoryVectorStoreǁquery__mutmut_23': xǁInMemoryVectorStoreǁquery__mutmut_23, 
        'xǁInMemoryVectorStoreǁquery__mutmut_24': xǁInMemoryVectorStoreǁquery__mutmut_24, 
        'xǁInMemoryVectorStoreǁquery__mutmut_25': xǁInMemoryVectorStoreǁquery__mutmut_25, 
        'xǁInMemoryVectorStoreǁquery__mutmut_26': xǁInMemoryVectorStoreǁquery__mutmut_26, 
        'xǁInMemoryVectorStoreǁquery__mutmut_27': xǁInMemoryVectorStoreǁquery__mutmut_27, 
        'xǁInMemoryVectorStoreǁquery__mutmut_28': xǁInMemoryVectorStoreǁquery__mutmut_28, 
        'xǁInMemoryVectorStoreǁquery__mutmut_29': xǁInMemoryVectorStoreǁquery__mutmut_29, 
        'xǁInMemoryVectorStoreǁquery__mutmut_30': xǁInMemoryVectorStoreǁquery__mutmut_30
    }
    
    def query(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInMemoryVectorStoreǁquery__mutmut_orig"), object.__getattribute__(self, "xǁInMemoryVectorStoreǁquery__mutmut_mutants"), args, kwargs, self)
        return result 
    
    query.__signature__ = _mutmut_signature(xǁInMemoryVectorStoreǁquery__mutmut_orig)
    xǁInMemoryVectorStoreǁquery__mutmut_orig.__name__ = 'xǁInMemoryVectorStoreǁquery'

    def count(self) -> int:
        return len(self._items)


def x__get_expected_api_key__mutmut_orig() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_1() -> Optional[str]:
    offline = None
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_2() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").upper() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_3() -> Optional[str]:
    offline = os.environ.get(None, "false").lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_4() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", None).lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_5() -> Optional[str]:
    offline = os.environ.get("false").lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_6() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", ).lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_7() -> Optional[str]:
    offline = os.environ.get("XXMCP_OFFLINEXX", "false").lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_8() -> Optional[str]:
    offline = os.environ.get("mcp_offline", "false").lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_9() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "XXfalseXX").lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_10() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "FALSE").lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_11() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() != "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_12() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "XXtrueXX"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_13() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "TRUE"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_14() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "true"
    if offline:
        return None
    return os.environ.get(None, DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_15() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", None)


def x__get_expected_api_key__mutmut_16() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "true"
    if offline:
        return None
    return os.environ.get(DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_17() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "true"
    if offline:
        return None
    return os.environ.get("MCP_API_KEY", )


def x__get_expected_api_key__mutmut_18() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "true"
    if offline:
        return None
    return os.environ.get("XXMCP_API_KEYXX", DEFAULT_API_KEY)


def x__get_expected_api_key__mutmut_19() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "true"
    if offline:
        return None
    return os.environ.get("mcp_api_key", DEFAULT_API_KEY)

x__get_expected_api_key__mutmut_mutants : ClassVar[MutantDict] = {
'x__get_expected_api_key__mutmut_1': x__get_expected_api_key__mutmut_1, 
    'x__get_expected_api_key__mutmut_2': x__get_expected_api_key__mutmut_2, 
    'x__get_expected_api_key__mutmut_3': x__get_expected_api_key__mutmut_3, 
    'x__get_expected_api_key__mutmut_4': x__get_expected_api_key__mutmut_4, 
    'x__get_expected_api_key__mutmut_5': x__get_expected_api_key__mutmut_5, 
    'x__get_expected_api_key__mutmut_6': x__get_expected_api_key__mutmut_6, 
    'x__get_expected_api_key__mutmut_7': x__get_expected_api_key__mutmut_7, 
    'x__get_expected_api_key__mutmut_8': x__get_expected_api_key__mutmut_8, 
    'x__get_expected_api_key__mutmut_9': x__get_expected_api_key__mutmut_9, 
    'x__get_expected_api_key__mutmut_10': x__get_expected_api_key__mutmut_10, 
    'x__get_expected_api_key__mutmut_11': x__get_expected_api_key__mutmut_11, 
    'x__get_expected_api_key__mutmut_12': x__get_expected_api_key__mutmut_12, 
    'x__get_expected_api_key__mutmut_13': x__get_expected_api_key__mutmut_13, 
    'x__get_expected_api_key__mutmut_14': x__get_expected_api_key__mutmut_14, 
    'x__get_expected_api_key__mutmut_15': x__get_expected_api_key__mutmut_15, 
    'x__get_expected_api_key__mutmut_16': x__get_expected_api_key__mutmut_16, 
    'x__get_expected_api_key__mutmut_17': x__get_expected_api_key__mutmut_17, 
    'x__get_expected_api_key__mutmut_18': x__get_expected_api_key__mutmut_18, 
    'x__get_expected_api_key__mutmut_19': x__get_expected_api_key__mutmut_19
}

def _get_expected_api_key(*args, **kwargs):
    result = _mutmut_trampoline(x__get_expected_api_key__mutmut_orig, x__get_expected_api_key__mutmut_mutants, args, kwargs)
    return result 

_get_expected_api_key.__signature__ = _mutmut_signature(x__get_expected_api_key__mutmut_orig)
x__get_expected_api_key__mutmut_orig.__name__ = 'x__get_expected_api_key'


def x__extract_auth_key__mutmut_orig(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    return None


def x__extract_auth_key__mutmut_1(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization or authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    return None


def x__extract_auth_key__mutmut_2(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith(None):
        return authorization.split(" ", 1)[1]
    return None


def x__extract_auth_key__mutmut_3(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.upper().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    return None


def x__extract_auth_key__mutmut_4(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("XXbearer XX"):
        return authorization.split(" ", 1)[1]
    return None


def x__extract_auth_key__mutmut_5(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("BEARER "):
        return authorization.split(" ", 1)[1]
    return None


def x__extract_auth_key__mutmut_6(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(None, 1)[1]
    return None


def x__extract_auth_key__mutmut_7(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", None)[1]
    return None


def x__extract_auth_key__mutmut_8(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(1)[1]
    return None


def x__extract_auth_key__mutmut_9(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", )[1]
    return None


def x__extract_auth_key__mutmut_10(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.rsplit(" ", 1)[1]
    return None


def x__extract_auth_key__mutmut_11(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split("XX XX", 1)[1]
    return None


def x__extract_auth_key__mutmut_12(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 2)[1]
    return None


def x__extract_auth_key__mutmut_13(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[2]
    return None

x__extract_auth_key__mutmut_mutants : ClassVar[MutantDict] = {
'x__extract_auth_key__mutmut_1': x__extract_auth_key__mutmut_1, 
    'x__extract_auth_key__mutmut_2': x__extract_auth_key__mutmut_2, 
    'x__extract_auth_key__mutmut_3': x__extract_auth_key__mutmut_3, 
    'x__extract_auth_key__mutmut_4': x__extract_auth_key__mutmut_4, 
    'x__extract_auth_key__mutmut_5': x__extract_auth_key__mutmut_5, 
    'x__extract_auth_key__mutmut_6': x__extract_auth_key__mutmut_6, 
    'x__extract_auth_key__mutmut_7': x__extract_auth_key__mutmut_7, 
    'x__extract_auth_key__mutmut_8': x__extract_auth_key__mutmut_8, 
    'x__extract_auth_key__mutmut_9': x__extract_auth_key__mutmut_9, 
    'x__extract_auth_key__mutmut_10': x__extract_auth_key__mutmut_10, 
    'x__extract_auth_key__mutmut_11': x__extract_auth_key__mutmut_11, 
    'x__extract_auth_key__mutmut_12': x__extract_auth_key__mutmut_12, 
    'x__extract_auth_key__mutmut_13': x__extract_auth_key__mutmut_13
}

def _extract_auth_key(*args, **kwargs):
    result = _mutmut_trampoline(x__extract_auth_key__mutmut_orig, x__extract_auth_key__mutmut_mutants, args, kwargs)
    return result 

_extract_auth_key.__signature__ = _mutmut_signature(x__extract_auth_key__mutmut_orig)
x__extract_auth_key__mutmut_orig.__name__ = 'x__extract_auth_key'


def x__enforce_rate_limit__mutmut_orig(enabled: bool = False) -> None:
    """Placeholder rate limiter hook.

    For previews the limiter is disabled. Connect this to Redis/Durable Objects
    before production rollout.
    """

    if enabled:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")


def x__enforce_rate_limit__mutmut_1(enabled: bool = True) -> None:
    """Placeholder rate limiter hook.

    For previews the limiter is disabled. Connect this to Redis/Durable Objects
    before production rollout.
    """

    if enabled:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")


def x__enforce_rate_limit__mutmut_2(enabled: bool = False) -> None:
    """Placeholder rate limiter hook.

    For previews the limiter is disabled. Connect this to Redis/Durable Objects
    before production rollout.
    """

    if enabled:
        raise HTTPException(status_code=None, detail="Rate limit exceeded")


def x__enforce_rate_limit__mutmut_3(enabled: bool = False) -> None:
    """Placeholder rate limiter hook.

    For previews the limiter is disabled. Connect this to Redis/Durable Objects
    before production rollout.
    """

    if enabled:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=None)


def x__enforce_rate_limit__mutmut_4(enabled: bool = False) -> None:
    """Placeholder rate limiter hook.

    For previews the limiter is disabled. Connect this to Redis/Durable Objects
    before production rollout.
    """

    if enabled:
        raise HTTPException(detail="Rate limit exceeded")


def x__enforce_rate_limit__mutmut_5(enabled: bool = False) -> None:
    """Placeholder rate limiter hook.

    For previews the limiter is disabled. Connect this to Redis/Durable Objects
    before production rollout.
    """

    if enabled:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, )


def x__enforce_rate_limit__mutmut_6(enabled: bool = False) -> None:
    """Placeholder rate limiter hook.

    For previews the limiter is disabled. Connect this to Redis/Durable Objects
    before production rollout.
    """

    if enabled:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="XXRate limit exceededXX")


def x__enforce_rate_limit__mutmut_7(enabled: bool = False) -> None:
    """Placeholder rate limiter hook.

    For previews the limiter is disabled. Connect this to Redis/Durable Objects
    before production rollout.
    """

    if enabled:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")


def x__enforce_rate_limit__mutmut_8(enabled: bool = False) -> None:
    """Placeholder rate limiter hook.

    For previews the limiter is disabled. Connect this to Redis/Durable Objects
    before production rollout.
    """

    if enabled:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="RATE LIMIT EXCEEDED")

x__enforce_rate_limit__mutmut_mutants : ClassVar[MutantDict] = {
'x__enforce_rate_limit__mutmut_1': x__enforce_rate_limit__mutmut_1, 
    'x__enforce_rate_limit__mutmut_2': x__enforce_rate_limit__mutmut_2, 
    'x__enforce_rate_limit__mutmut_3': x__enforce_rate_limit__mutmut_3, 
    'x__enforce_rate_limit__mutmut_4': x__enforce_rate_limit__mutmut_4, 
    'x__enforce_rate_limit__mutmut_5': x__enforce_rate_limit__mutmut_5, 
    'x__enforce_rate_limit__mutmut_6': x__enforce_rate_limit__mutmut_6, 
    'x__enforce_rate_limit__mutmut_7': x__enforce_rate_limit__mutmut_7, 
    'x__enforce_rate_limit__mutmut_8': x__enforce_rate_limit__mutmut_8
}

def _enforce_rate_limit(*args, **kwargs):
    result = _mutmut_trampoline(x__enforce_rate_limit__mutmut_orig, x__enforce_rate_limit__mutmut_mutants, args, kwargs)
    return result 

_enforce_rate_limit.__signature__ = _mutmut_signature(x__enforce_rate_limit__mutmut_orig)
x__enforce_rate_limit__mutmut_orig.__name__ = 'x__enforce_rate_limit'


def x__validate_auth__mutmut_orig(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_1(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = None
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_2(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is not None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_3(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = None
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_4(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(None, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_5(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, None)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_6(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_7(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, )
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_8(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None and provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_9(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is not None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_10(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided == expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def x__validate_auth__mutmut_11(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=None, detail="Unauthorized")


def x__validate_auth__mutmut_12(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=None)


def x__validate_auth__mutmut_13(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(detail="Unauthorized")


def x__validate_auth__mutmut_14(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, )


def x__validate_auth__mutmut_15(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="XXUnauthorizedXX")


def x__validate_auth__mutmut_16(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")


def x__validate_auth__mutmut_17(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHORIZED")

x__validate_auth__mutmut_mutants : ClassVar[MutantDict] = {
'x__validate_auth__mutmut_1': x__validate_auth__mutmut_1, 
    'x__validate_auth__mutmut_2': x__validate_auth__mutmut_2, 
    'x__validate_auth__mutmut_3': x__validate_auth__mutmut_3, 
    'x__validate_auth__mutmut_4': x__validate_auth__mutmut_4, 
    'x__validate_auth__mutmut_5': x__validate_auth__mutmut_5, 
    'x__validate_auth__mutmut_6': x__validate_auth__mutmut_6, 
    'x__validate_auth__mutmut_7': x__validate_auth__mutmut_7, 
    'x__validate_auth__mutmut_8': x__validate_auth__mutmut_8, 
    'x__validate_auth__mutmut_9': x__validate_auth__mutmut_9, 
    'x__validate_auth__mutmut_10': x__validate_auth__mutmut_10, 
    'x__validate_auth__mutmut_11': x__validate_auth__mutmut_11, 
    'x__validate_auth__mutmut_12': x__validate_auth__mutmut_12, 
    'x__validate_auth__mutmut_13': x__validate_auth__mutmut_13, 
    'x__validate_auth__mutmut_14': x__validate_auth__mutmut_14, 
    'x__validate_auth__mutmut_15': x__validate_auth__mutmut_15, 
    'x__validate_auth__mutmut_16': x__validate_auth__mutmut_16, 
    'x__validate_auth__mutmut_17': x__validate_auth__mutmut_17
}

def _validate_auth(*args, **kwargs):
    result = _mutmut_trampoline(x__validate_auth__mutmut_orig, x__validate_auth__mutmut_mutants, args, kwargs)
    return result 

_validate_auth.__signature__ = _mutmut_signature(x__validate_auth__mutmut_orig)
x__validate_auth__mutmut_orig.__name__ = 'x__validate_auth'


def x_create_app__mutmut_orig(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_1(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = None

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_2(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store and InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_3(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = None
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_4(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title=None, version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_5(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version=None)
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_6(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_7(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", )
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_8(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="XXCodex MCP HTTP PrototypeXX", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_9(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="codex mcp http prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_10(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="CODEX MCP HTTP PROTOTYPE", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_11(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="XX0.1.0XX")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_12(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = None

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_13(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(None, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_14(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, None)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_15(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_16(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, )

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_17(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=None)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def x_create_app__mutmut_18(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(x_mcp_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=True)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "healthy", "documents": app.state.vector_store.count(), "timestamp": int(time.time())}

    @app.post("/mcp/v1/query", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post("/mcp/v1/context", dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)])
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Any, exc: HTTPException) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app

x_create_app__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_app__mutmut_1': x_create_app__mutmut_1, 
    'x_create_app__mutmut_2': x_create_app__mutmut_2, 
    'x_create_app__mutmut_3': x_create_app__mutmut_3, 
    'x_create_app__mutmut_4': x_create_app__mutmut_4, 
    'x_create_app__mutmut_5': x_create_app__mutmut_5, 
    'x_create_app__mutmut_6': x_create_app__mutmut_6, 
    'x_create_app__mutmut_7': x_create_app__mutmut_7, 
    'x_create_app__mutmut_8': x_create_app__mutmut_8, 
    'x_create_app__mutmut_9': x_create_app__mutmut_9, 
    'x_create_app__mutmut_10': x_create_app__mutmut_10, 
    'x_create_app__mutmut_11': x_create_app__mutmut_11, 
    'x_create_app__mutmut_12': x_create_app__mutmut_12, 
    'x_create_app__mutmut_13': x_create_app__mutmut_13, 
    'x_create_app__mutmut_14': x_create_app__mutmut_14, 
    'x_create_app__mutmut_15': x_create_app__mutmut_15, 
    'x_create_app__mutmut_16': x_create_app__mutmut_16, 
    'x_create_app__mutmut_17': x_create_app__mutmut_17, 
    'x_create_app__mutmut_18': x_create_app__mutmut_18
}

def create_app(*args, **kwargs):
    result = _mutmut_trampoline(x_create_app__mutmut_orig, x_create_app__mutmut_mutants, args, kwargs)
    return result 

create_app.__signature__ = _mutmut_signature(x_create_app__mutmut_orig)
x_create_app__mutmut_orig.__name__ = 'x_create_app'


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 8000)),
    )
