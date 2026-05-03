"""FastAPI-based MCP HTTP prototype.

This module exposes preview-ready HTTP endpoints for MCP while keeping
compatibility with JSON-RPC behavior defined in `mcp.server`. It targets
Cloudflare Workers (edge proxy) and Fly.io (persistent container) hosts.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Iterable
from typing import Any, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

DEFAULT_API_KEY = "dev-key"  # pragma: allowlist secret
DEFAULT_TOP_K = 5
MAX_TOP_K = 50


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

    @field_validator("query")
    @classmethod
    def _ensure_query(cls, value: str) -> str:
        """Require non-empty query strings."""
        if not value or not value.strip():
            raise ValueError("query cannot be empty")
        return value


class ContextUpsertRequest(BaseModel):
    """Request payload for /mcp/v1/context."""

    items: list[ContextItem]

    @field_validator("items")
    @classmethod
    def _ensure_items(cls, value: list[ContextItem]) -> list[ContextItem]:
        if not value:
            raise ValueError("at least one item is required")
        return value


class InMemoryVectorStore:
    """Minimal in-memory vector store for previews.

    This is intentionally simple to stay offline-friendly. Replace with Chroma,
    Supabase, or Pinecone when scaling beyond previews.
    """

    def __init__(self, items: Optional[list[ContextItem]] = None) -> None:
        self._items: list[ContextItem] = items or []

    @classmethod
    def seeded(cls) -> InMemoryVectorStore:
        """Create a store with seed data for smoke tests."""
        seed_items = [
            ContextItem(id="demo-1", content="codex mcp prototype", metadata={"scope": "repo"}),
            ContextItem(
                id="demo-2",
                content="cloudflare workers edge",
                metadata={"scope": "edge"},
            ),
            ContextItem(
                id="demo-3",
                content="fly io persistent mcp",
                metadata={"scope": "container"},
            ),
        ]
        return cls(items=seed_items)

    def upsert_many(self, items: Iterable[ContextItem]) -> int:
        """Insert or replace items by id."""
        new_items = list(items)
        index = {item.id: item for item in self._items}
        for item in new_items:
            index[item.id] = item
        self._items = list(index.values())
        return len(new_items)

    def query(
        self, query: str, top_k: int, filters: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
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

    def count(self) -> int:
        return len(self._items)


def _get_expected_api_key() -> Optional[str]:
    offline = os.environ.get("MCP_OFFLINE", "false").lower() == "true"
    if offline:
        return None
    key = os.environ.get("MCP_API_KEY", DEFAULT_API_KEY)
    if key == DEFAULT_API_KEY:
        logger.warning("MCP server using default dev API key — set MCP_API_KEY for production")
    return key


def _extract_auth_key(x_api_key: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    return None


def _enforce_rate_limit(enabled: bool = False) -> None:
    """Placeholder rate limiter hook.

    For previews the limiter is disabled. Connect this to Redis/Durable Objects
    before production rollout.
    """

    if enabled:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )


def _validate_auth(x_api_key: Optional[str], authorization: Optional[str]) -> None:
    expected = _get_expected_api_key()
    if expected is None:
        return

    provided = _extract_auth_key(x_api_key, authorization)
    if provided is None or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def create_app(store: Optional[InMemoryVectorStore] = None) -> FastAPI:
    store = store or InMemoryVectorStore.seeded()

    app = FastAPI(title="Codex MCP HTTP Prototype", version="0.1.0")
    app.state.vector_store = store

    def _auth_dependency(
        x_mcp_api_key: Optional[str] = Header(None),
        authorization: Optional[str] = Header(None),
    ) -> None:
        _validate_auth(x_mcp_api_key, authorization)

    def _rate_limit_dependency() -> None:
        _enforce_rate_limit(enabled=False)

    @app.get("/mcp/v1/health")
    def health() -> dict[str, Any]:
        return {
            "status": "healthy",
            "documents": app.state.vector_store.count(),
            "timestamp": int(time.time()),
        }

    @app.post(
        "/mcp/v1/query",
        dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)],
    )
    def query(request: QueryRequest) -> dict[str, Any]:
        results = app.state.vector_store.query(request.query, request.top_k, request.filters)
        return {"results": results}

    @app.post(
        "/mcp/v1/context",
        dependencies=[Depends(_auth_dependency), Depends(_rate_limit_dependency)],
    )
    def push_context(request: ContextUpsertRequest) -> dict[str, Any]:
        upserted = app.state.vector_store.upsert_many(request.items)
        return {"upserted": upserted}

    @app.exception_handler(HTTPException)
    def http_exception_handler(
        _: Any, exc: HTTPException
    ) -> JSONResponse:  # pragma: no cover - FastAPI standard hook
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 8000)),
    )
