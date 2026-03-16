"""Compatibility shim exposing regex patterns from the repository package."""

from __future__ import annotations

from codex_utils.regex_patterns import (  # type: ignore[import-untyped]  # noqa: F401
    ENV_ASSIGNMENT,
    PEM_BLOCK,
)

__all__ = ["ENV_ASSIGNMENT", "PEM_BLOCK"]
