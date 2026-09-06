"""Compatibility shim for `codex.api.rag_api`."""

from __future__ import annotations


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


__all__ = ["RAGAPI"]
