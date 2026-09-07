"""Compatibility wrapper for the legacy ``codex.api.rag_api`` import path."""

from __future__ import annotations

from aries_serpent_core.api.rag_api import (  # noqa: F401
    BuildIndexRequest,
    BuildIndexResponse,
    QueryRequest,
    QueryResult,
    MergeIndicesRequest,
    _ensure_subpath,
    _safe_join_under_base,
    _validate_path_segment,
    app,
    build_index,
    merge_indices,
    query_index,
)


class RAGAPI:
    """Minimal async-compatible container for legacy RAG API tests."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


__all__ = [
    "BuildIndexRequest",
    "BuildIndexResponse",
    "MergeIndicesRequest",
    "QueryRequest",
    "QueryResult",
    "RAGAPI",
    "_ensure_subpath",
    "_safe_join_under_base",
    "_validate_path_segment",
    "app",
    "build_index",
    "merge_indices",
    "query_index",
]
