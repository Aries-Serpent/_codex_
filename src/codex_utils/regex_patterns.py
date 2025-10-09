"""Compatibility shim exposing regex patterns from the repository package."""

from __future__ import annotations

from codex_utils.regex_patterns import ENV_ASSIGNMENT, PEM_BLOCK  # type: ignore F401

__all__ = ["ENV_ASSIGNMENT", "PEM_BLOCK"]
