# src/codex_ml/analysis/metrics.py
from __future__ import annotations
import math
import ast


def mccabe_minimal(ast_tree: ast.AST) -> int:
    """Return a rough McCabe complexity: branch nodes + 1."""
    branches = (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.Try, ast.With, ast.BoolOp)
    return 1 + sum(1 for n in ast.walk(ast_tree) if isinstance(n, branches))


def perplexity_from_mean_nll(mean_nll: float | None):
    """Convert mean negative log-likelihood to perplexity."""
    try:
        return math.exp(float(mean_nll))
    except Exception:  # pragma: no cover - defensive
        return None
