"""
Metrics Module

This module provides functionality for metrics.

Usage:
    from analysis.metrics import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# src/codex_ml/analysis/metrics.py
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast  # noqa: E402
import math  # noqa: E402


def mccabe_minimal(ast_tree: ast.AST) -> int:
    """Return a rough McCabe complexity: branch nodes + 1."""
    branches = (
        ast.If,
        ast.For,
        ast.While,
        ast.And,
        ast.Or,
        ast.Try,
        ast.With,
        ast.BoolOp,
    )
    return 1 + sum(1 for n in ast.walk(ast_tree) if isinstance(n, branches))


def perplexity_from_mean_nll(mean_nll: float | None) -> float | None:
    """Convert mean negative log-likelihood to perplexity."""
    try:
        return math.exp(float(mean_nll))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover - defensive
        return None
