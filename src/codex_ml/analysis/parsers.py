# src/codex_ml/analysis/parsers.py
# Tiered parsing: ast -> libcst -> parso -> degraded metrics-only
from __future__ import annotations
from dataclasses import dataclass
import ast

try:
    import libcst as cst  # optional
except Exception:  # pragma: no cover - optional dependency
    cst = None
try:
    import parso  # optional
except Exception:  # pragma: no cover - optional dependency
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
    except SyntaxError:
        pass
    # Secondary: LibCST (formatting-preserving)
    if cst is not None:
        try:
            return ParseResult(mode="cst", cst_tree=cst.parse_module(code))
        except Exception:
            pass
    # Tertiary: Parso (tolerant/partial)
    if parso is not None:
        try:
            return ParseResult(mode="parso", parso_tree=parso.parse(code))
        except Exception:
            pass
    # Last resort: degraded
    return ParseResult(mode="degraded", degraded=True)
