"""
Phase 3: Self-Referential Loops — Reflection Module

Provides introspective self-analysis with recursive depth limiting.
Agents can call reflect() to generate a structured introspection report
about a target module, function, or session state.

Usage (programmatic):
    from codex.reflection import reflect, RecursionGuard

    report = reflect("src/codex/cli.py", depth=2)
    logger.info(report.summary)
"""

from __future__ import annotations

import ast
import contextvars
import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
REFLECTION_DIR = REPO_ROOT / "memory" / "reflections"
MAX_DEPTH = 4  # hard cap to prevent infinite recursion


# ── Recursion guard ───────────────────────────────────────────────────────────

# ContextVar ensures each thread/async-task has its own depth counter, preventing
# concurrent reflect() calls from interfering with each other's recursion limits.
_REFLECT_DEPTH: contextvars.ContextVar[int] = contextvars.ContextVar("_reflect_depth", default=0)


class RecursionGuard:
    """Context manager enforcing a max recursion depth for self-referential analysis.

    Uses a ``contextvars.ContextVar`` so that concurrent threads and async tasks
    each maintain an isolated depth counter, preventing false ``RecursionError``s
    or negative depth when calls interleave.

    A new instance should be created per :func:`reflect` call so that each
    invocation owns its own token stack and cleanup is always correct.
    """

    def __init__(self, max_depth: int = MAX_DEPTH) -> None:
        self.max_depth = max_depth
        # A list of tokens supports nested calls on the same guard instance:
        # each __enter__ pushes a token and __exit__ pops+resets in LIFO order,
        # ensuring the ContextVar is always restored to its pre-entry value even
        # when the same guard is entered multiple times in sequence.
        self._tokens: list[contextvars.Token[int]] = []

    @property
    def depth(self) -> int:
        return _REFLECT_DEPTH.get()

    def __enter__(self) -> RecursionGuard:
        current = _REFLECT_DEPTH.get()
        if current >= self.max_depth:
            raise RecursionError(f"RecursionGuard: max depth {self.max_depth} exceeded")
        self._tokens.append(_REFLECT_DEPTH.set(current + 1))
        return self

    def __exit__(self, *_) -> None:
        if self._tokens:
            _REFLECT_DEPTH.reset(self._tokens.pop())


# ── Reflection report ─────────────────────────────────────────────────────────


@dataclass
class ReflectionReport:
    target: str
    depth: int
    summary: str
    metrics: dict[str, Any] = field(default_factory=dict)
    sub_reports: list[ReflectionReport] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "depth": self.depth,
            "summary": self.summary,
            "metrics": self.metrics,
            "sub_reports": [r.to_dict() for r in self.sub_reports],
            "errors": self.errors,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


# ── AST-based code analysis ───────────────────────────────────────────────────


def _analyze_python_file(path: Path) -> dict[str, Any]:
    """Parse a Python file with AST and extract structural metrics."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError) as exc:
        return {"error": str(exc)}

    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]

    # Detect recursive functions (simple: function that calls itself)
    recursive_funcs = []
    for func in funcs:
        func_name = func.name
        for node in ast.walk(func):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_name:
                    recursive_funcs.append(func_name)
                    break

    lines = source.splitlines()
    sha = hashlib.sha256(source.encode()).hexdigest()[:12]

    return {
        "lines": len(lines),
        "functions": len(funcs),
        "classes": len(classes),
        "imports": len(imports),
        "recursive_functions": recursive_funcs,
        "sha": sha,
    }


# ── Core reflect function ─────────────────────────────────────────────────────


def reflect(target: str, depth: int = 1) -> ReflectionReport:
    """
    Recursively reflect on a target (file path or module name).

    Args:
        target: Relative path to a Python file (from REPO_ROOT), or a module path.
        depth:  Recursion depth (capped at MAX_DEPTH).

    Returns:
        ReflectionReport with structural analysis and optional sub-reports.
    """
    depth = min(depth, MAX_DEPTH)
    errors: list[str] = []
    metrics: dict[str, Any] = {}
    sub_reports: list[ReflectionReport] = []

    # Resolve target to a Path
    candidate = REPO_ROOT / target
    if not candidate.exists():
        # Try as module path (e.g. "codex.cli" → "src/codex/cli.py")
        module_path = target.replace(".", "/")
        for prefix in ["src", "."]:
            candidate = REPO_ROOT / prefix / (module_path + ".py")
            if candidate.exists():
                break
        else:
            candidate = None  # type: ignore[assignment]

    if candidate is None or not candidate.exists():
        return ReflectionReport(
            target=target,
            depth=depth,
            summary=f"Target not found: {target}",
            errors=[f"File not found: {target}"],
        )

    try:
        with RecursionGuard(max_depth=MAX_DEPTH):
            # Analyze this file
            if candidate.suffix == ".py":
                metrics = _analyze_python_file(candidate)
            else:
                text = candidate.read_text(encoding="utf-8", errors="replace")
                metrics = {"lines": len(text.splitlines())}

            rel = candidate.relative_to(REPO_ROOT)
            summary_parts = [f"{rel}: {metrics.get('lines', '?')} lines"]
            if metrics.get("functions"):
                summary_parts.append(f"{metrics['functions']} functions")
            if metrics.get("classes"):
                summary_parts.append(f"{metrics['classes']} classes")
            if metrics.get("recursive_functions"):
                summary_parts.append(f"recursive: {', '.join(metrics['recursive_functions'])}")
            summary = ", ".join(summary_parts)

            # Recurse into imports (if depth > 1)
            if depth > 1 and candidate.suffix == ".py" and not metrics.get("error"):
                try:
                    source = candidate.read_text(encoding="utf-8")
                    tree = ast.parse(source)
                    local_imports: list[str] = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom) and node.module:
                            if node.module.startswith("codex"):
                                local_imports.append(node.module)
                    for mod in local_imports[:3]:  # limit sub-analysis
                        sub_report = reflect(mod, depth=depth - 1)
                        sub_reports.append(sub_report)
                except (SyntaxError, OSError, ValueError) as exc:
                    errors.append(f"Sub-reflection error: {exc}")
                    log.debug("Sub-reflection parse error for %s: %s", target, exc)

    except RecursionError as exc:
        return ReflectionReport(
            target=target,
            depth=depth,
            summary=f"Recursion depth exceeded for: {target}",
            errors=[str(exc)],
        )

    return ReflectionReport(
        target=str(candidate.relative_to(REPO_ROOT)),
        depth=depth,
        summary=summary,
        metrics=metrics,
        sub_reports=sub_reports,
        errors=errors,
    )


def persist_reflection(report: ReflectionReport, label: str = "") -> Path:
    """Persist a reflection report to memory/reflections/."""
    from datetime import datetime, timezone  # local import for optional use

    REFLECTION_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = label or report.target.replace("/", "_").replace(".", "_")
    path = REFLECTION_DIR / f"reflection_{ts}_{slug[:30]}.json"
    path.write_text(report.to_json() + "\n", encoding="utf-8")
    return path
