# src/codex_ml/analysis/extractors.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
import ast

try:
    import libcst as cst  # optional
except Exception:  # pragma: no cover - optional dependency
    cst = None


@dataclass
class Extraction:
    imports: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)


class _ImportVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.items: List[Dict[str, Any]] = []

    def visit_Import(self, node: ast.Import) -> None:  # pragma: no cover - simple
        for n in node.names:
            self.items.append({"type": "import", "name": n.name, "asname": n.asname})

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # pragma: no cover - simple
        for n in node.names:
            self.items.append(
                {
                    "type": "from",
                    "module": node.module,
                    "name": n.name,
                    "asname": n.asname,
                    "level": node.level,
                }
            )


class _FuncVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.items: List[Dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # pragma: no cover - simple
        self.items.append(
            {
                "name": node.name,
                "decorators": [
                    ast.unparse(d) if hasattr(ast, "unparse") else "" for d in node.decorator_list
                ],
                "args": [a.arg for a in node.args.args],
                "returns": getattr(getattr(node, "returns", None), "id", None),
            }
        )
        self.generic_visit(node)


class _ClassVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.items: List[Dict[str, Any]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # pragma: no cover - simple
        bases = [
            ast.unparse(b) if hasattr(ast, "unparse") else getattr(getattr(b, "id", None), "id", None)
            for b in node.bases
        ]
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        self.items.append({"name": node.name, "bases": bases, "methods": methods})
        self.generic_visit(node)


def extract_ast(tree: ast.AST) -> Extraction:
    """AST-based extraction."""
    out = Extraction()
    iv = _ImportVisitor()
    iv.visit(tree)
    out.imports = iv.items
    fv = _FuncVisitor()
    fv.visit(tree)
    out.functions = fv.items
    cv = _ClassVisitor()
    cv.visit(tree)
    out.classes = cv.items
    # Patterns: simple boolean indicators
    out.patterns.append({"context_managers": any(isinstance(n, ast.With) for n in ast.walk(tree))})
    out.patterns.append(
        {
            "comprehensions": any(
                isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)) for n in ast.walk(tree)
            )
        }
    )
    return out


def extract_cst(module: Any) -> Extraction:  # pragma: no cover - simple
    """Minimal CST extraction preserving formatting."""
    out = Extraction()
    try:
        for n in module.body:  # type: ignore[attr-defined]
            if cst and isinstance(n, cst.SimpleStatementLine):
                code = n.code
                if "import " in code:
                    out.imports.append({"raw": code})
    except Exception:
        pass
    return out


def extract_parso(tree: Any) -> Extraction:  # pragma: no cover - simple
    """Minimal tolerant extraction for Parso parse trees."""
    return Extraction()


def extract_degraded(code: str) -> Extraction:
    """Regex/line-based approximations when parsing fails."""
    import re

    out = Extraction()
    for m in re.finditer(r"^\s*def\s+(\w+)\(", code, re.M):
        out.functions.append({"name": m.group(1), "approx": True})
    for m in re.finditer(r"^\s*class\s+(\w+)\(", code, re.M):
        out.classes.append({"name": m.group(1), "approx": True})
    for m in re.finditer(r"^\s*import\s+([\w\.]+)", code, re.M):
        out.imports.append({"type": "import", "name": m.group(1), "approx": True})
    return out
