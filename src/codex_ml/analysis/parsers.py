"""
Parsers Module

This module provides functionality for parsers.

Usage:
    from analysis.parsers import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# src/codex_ml/analysis/parsers.py
# Tiered parsing: ast -> libcst -> parso -> degraded metrics-only
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast  # noqa: E402
from dataclasses import dataclass  # noqa: E402

try:
    import libcst as cst  # optional
except (ImportError, AttributeError):  # pragma: no cover - optional dependency
    cst = None
try:
    import parso  # optional
except (ValueError, TypeError):  # pragma: no cover - optional dependency
    parso = None


@dataclass
class ParseResult:
    mode: str
    ast_tree: object | None = None
    cst_tree: object | None = None
    parso_tree: object | None = None
    degraded: bool = False


def parse_tiered(code: str) -> ParseResult:
    """Parse *code* using tiered fallbacks.

    Order: stdlib ``ast`` -> ``libcst`` -> ``parso`` -> degraded.
    The first successful parser determines the mode.
    """
    # Primary: stdlib AST
    try:
        return ParseResult(mode="ast", ast_tree=ast.parse(code))
    except SyntaxError as e:
        type(e).__name__
        logger.debug("SyntaxError: <ERROR_TYPE>")
        logger.warning("SyntaxError: <ERROR_TYPE>", exc_info=True)
    # Secondary: LibCST (formatting-preserving)
    if cst is not None:
        try:
            return ParseResult(mode="cst", cst_tree=cst.parse_module(code))
        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    # Tertiary: Parso (tolerant/partial)
    if parso is not None:
        try:
            return ParseResult(mode="parso", parso_tree=parso.parse(code))
        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    # Last resort: degraded
    return ParseResult(mode="degraded", degraded=True)
