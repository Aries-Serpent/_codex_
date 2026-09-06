"""Compatibility shim for `codex.api.auth_routes`."""

from __future__ import annotations


class AuthRouter:
    """Lightweight compatibility router used by legacy tests."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def add_api_route(self, *args, **kwargs):
        return None

    def include_router(self, *args, **kwargs):
        return self


__all__ = ["AuthRouter"]
