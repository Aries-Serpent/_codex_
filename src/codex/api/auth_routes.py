"""Compatibility wrapper for the legacy ``codex.api.auth_routes`` import path."""

from __future__ import annotations

from aries_serpent_core.api.auth_routes import create_auth_router
from aries_serpent_core.auth.authenticator import Authenticator

# Preserve historical names used by older import sites.
AuthRouter = object

__all__ = ["AuthRouter", "Authenticator", "create_auth_router"]
