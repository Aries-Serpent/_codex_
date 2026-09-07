"""Compatibility wrapper for the legacy ``codex.api.auth_routes`` import path."""

from __future__ import annotations

from aries_serpent_core.api.auth_routes import create_auth_router

# Preserve the historical simple-type name used by older import sites.
AuthRouter = object

__all__ = ["AuthRouter", "create_auth_router"]
