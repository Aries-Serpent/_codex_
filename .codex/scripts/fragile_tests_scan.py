#!/usr/bin/env python3
"""
fragile_tests_scan.py

Scan the repository tests/ directory for top-level unguarded imports of optional
third-party packages (e.g. numpy, torch, hypothesis, typer, responses).

Purpose:
- Help maintainers find fragile test modules that will raise ModuleNotFoundError
  or ImportError during pytest collection on minimal developer environments.
- Output:
  - fragile_tests.json : JSON map of test-file -> list of unguarded imports
  - printed markdown table summary to stdout

Usage:
  python .codex/scripts/fragile_tests_scan.py

Behavior:
- Considers imports inside try/except blocks or lines containing `importorskip`
  to be guarded and therefore not fragile.
- Conservative: focuses on explicit top-level import statements in test files.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

# Packages considered optional for tests (extend as needed)
OPTIONAL_PKGS: set[str] = {
    "numpy",
    "np",
    "torch",
    "hypothesis",
    "typer",
    "responses",
    "datasets",
    "mlflow",
    "transformers",
    "sentence_transformers",
    "faiss",
    "pandas",
}

REPO_ROOT = Path.cwd()
TESTS_DIR = REPO_ROOT / "tests"
OUT_JSON = REPO_ROOT / ".codex" / "fragile_tests.json"


def _collect_try_ranges(tree: ast.AST) -> list[tuple[int, int]]:
    """Collect approximate (start_lineno, end_lineno) ranges for Try nodes."""
    ranges: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            start = getattr(node, "lineno", None) or 0
            # Get end from last body node if possible; fallback to start
            end = start
            if node.body:
                last = node.body[-1]
                end = getattr(last, "end_lineno", getattr(last, "lineno", start))
            ranges.append((start, end))
    return ranges


def _is_line_in_ranges(lineno: int, ranges: list[tuple[int, int]]) -> bool:
    for a, b in ranges:
        if a <= lineno <= b:
            return True
    return False


def analyze_file(path: Path) -> tuple[bool, list[str]]:
    """
    Analyze a single test file for fragile top-level imports.

    Returns:
      (is_fragile, list_of_unprotected_imports)
    """
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False, []

    try:
        tree = ast.parse(source)
    except Exception:
        # Syntax error files are ignored for this scan
        return False, []

    fragile_imports: list[str] = []

    # Lines that invoke pytest.importorskip are treated as guarding imports.
    guarded_lines: set[int] = set()
    if "importorskip" in source:
        for i, line in enumerate(source.splitlines(), start=1):
            if "importorskip" in line:
                guarded_lines.add(i)

    try_ranges = _collect_try_ranges(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            lineno = getattr(node, "lineno", 0)
            if lineno in guarded_lines or _is_line_in_ranges(lineno, try_ranges):
                continue
            for alias in node.names:
                name = (alias.asname or alias.name).split(".")[0]
                if name in OPTIONAL_PKGS:
                    fragile_imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            lineno = getattr(node, "lineno", 0)
            if lineno in guarded_lines or _is_line_in_ranges(lineno, try_ranges):
                continue
            module = node.module or ""
            base = module.split(".")[0] if module else ""
            if base in OPTIONAL_PKGS:
                fragile_imports.append(module)

    return (len(fragile_imports) > 0, fragile_imports)


def discover_tests() -> list[Path]:
    if not TESTS_DIR.exists():
        return []
    # Look for test files in tests/ recursively
    candidates = sorted(set(TESTS_DIR.rglob("test_*.py")) | set(TESTS_DIR.rglob("*test*.py")))
    return [p for p in candidates if p.is_file()]


def main() -> int:
    test_files = discover_tests()
    results: dict[str, list[str]] = {}

    for f in test_files:
        fragile, imps = analyze_file(f)
        if fragile:
            results[str(f.relative_to(REPO_ROOT))] = imps

    OUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")

    if results:
        print("| Test file | Unguarded optional imports |")
        print("|---|---|")
        for file, imps in results.items():
            print(f"| `{file}` | {', '.join(imps)} |")
        print()
        print(f"Found {len(results)} fragile test files. Detailed JSON written to {OUT_JSON}")
        return 0
    print("No fragile test files (top-level unguarded optional imports) found under tests/.")
    print("Note: tests may still transitively import modules that require optional packages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
