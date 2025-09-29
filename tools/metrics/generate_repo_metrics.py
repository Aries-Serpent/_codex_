#!/usr/bin/env python3
"""Generate repository metrics and lightweight audits.

This utility can operate on the local working tree (default) or, when
``GITHUB_OWNER``, ``GITHUB_REPO`` and ``GIT_SHA`` are provided, it will fetch a
recursive tree listing via the GitHub API (metadata only). The latter path is
best-effort and remains offline by default so the script is safe to run in
restricted environments.

Outputs (created if missing):
- ``artifacts/metrics/loc_by_dir.csv``
- ``artifacts/metrics/docstring_coverage.json``
- ``artifacts/metrics/import_graph.json``
- ``artifacts/metrics/cycles.json``
- ``artifacts/docs_link_audit/links.json``
- ``artifacts/notebook_checks/nb_load_check.json``
- ``reports/repo_map.md`` (per-directory counts)

Key behaviors:
- Line counts rely on a simple UTF-8 reader with ``errors="ignore"`` so that
  binary or malformed files never halt execution.
- Docstring coverage uses the Python ``ast`` module and ignores paths containing
  ``tests`` to keep the signal focused on library code.
- Import graph analysis is limited to modules within ``src/``.
- Notebook load checks use ``nbformat`` when available; otherwise the script
  records that the optional dependency is missing.
- Markdown link auditing only verifies relative paths exist; HTTP links are
  recorded but never fetched, keeping the run offline-friendly.

Guardrails:
- The script never mutates CI configuration.
- Network access is only attempted when the GitHub environment variables are
  explicitly provided.
"""

from __future__ import annotations

import ast
import csv
import json
import os
import pathlib
import re
from collections import defaultdict
from typing import Iterable

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART_DIR = ROOT / "artifacts"
MET_DIR = ART_DIR / "metrics"
DOCS_AUD_DIR = ART_DIR / "docs_link_audit"
NB_DIR = ART_DIR / "notebook_checks"
REPORTS_DIR = ROOT / "reports"

for destination in (MET_DIR, DOCS_AUD_DIR, NB_DIR, REPORTS_DIR):
    destination.mkdir(parents=True, exist_ok=True)

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".nox",
    ".tox",
    "__pycache__",
    "artifacts",
    "build",
    "dist",
    "logs",
    "mlruns",
    "nox_sessions",
    "site-packages",
    "temp",
    "venv",
    ".venv",
}

TEXTUAL_LOCS = {
    ".py",
    ".md",
    ".rst",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".cfg",
    ".ini",
    ".ipynb",
}
IMPORT_PATTERN = re.compile(r"^(?:from\s+([.\w]+)\s+import|import\s+([.\w]+))", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _should_skip(path: pathlib.Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def iter_files(base: pathlib.Path) -> Iterable[pathlib.Path]:
    for candidate in base.rglob("*"):
        if not candidate.is_file():
            continue
        if _should_skip(candidate):
            continue
        yield candidate


def _top_level_dir(path: pathlib.Path) -> str:
    parts = path.parts
    return parts[0] if parts else ""


def _read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _count_lines(path: pathlib.Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return sum(1 for _ in handle)
    except Exception:
        return 0


def _files_from_local() -> list[pathlib.Path]:
    return list(iter_files(ROOT))


def _files_from_github() -> list[pathlib.Path]:
    import json as _json
    import urllib.request

    owner = os.environ["GITHUB_OWNER"]
    repo = os.environ["GITHUB_REPO"]
    sha = os.environ["GIT_SHA"]
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request) as response:  # pragma: no cover - network optional
        payload = _json.loads(response.read().decode("utf-8"))
    files: list[pathlib.Path] = []
    for entry in payload.get("tree", []):
        if entry.get("type") == "blob":
            files.append(ROOT / entry["path"])
    return files


def _collect_files() -> list[pathlib.Path]:
    if all(key in os.environ for key in ("GITHUB_OWNER", "GITHUB_REPO", "GIT_SHA")):
        try:
            return _files_from_github()
        except Exception as exc:  # pragma: no cover - defensive guard
            print(f"[metrics] GitHub mode failed: {exc}; falling back to local scan.")
    return _files_from_local()


def _write_loc_by_dir(files: Iterable[pathlib.Path]) -> dict[str, dict[str, int]]:
    rows: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "loc": 0})
    for absolute in files:
        try:
            relative = absolute.relative_to(ROOT)
        except ValueError:
            relative = absolute
        key = _top_level_dir(relative)
        bucket = rows[key]
        bucket["files"] += 1
        if absolute.suffix.lower() in TEXTUAL_LOCS:
            bucket["loc"] += _count_lines(absolute)
    output = MET_DIR / "loc_by_dir.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dir", "files", "loc"])
        for name in sorted(rows):
            writer.writerow([name, rows[name]["files"], rows[name]["loc"]])
    return rows


def _docstring_coverage(files: Iterable[pathlib.Path]) -> dict[str, int]:
    totals = {
        "module_total": 0,
        "module_with_doc": 0,
        "class_total": 0,
        "class_with_doc": 0,
        "function_total": 0,
        "function_with_doc": 0,
    }
    for path in files:
        if path.suffix != ".py" or "tests" in path.parts:
            continue
        source = _read_text(path)
        try:
            tree = ast.parse(source or "", filename=str(path))
        except SyntaxError:
            continue
        totals["module_total"] += 1
        if ast.get_docstring(tree):
            totals["module_with_doc"] += 1
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                totals["class_total"] += 1
                if ast.get_docstring(node):
                    totals["class_with_doc"] += 1
            elif isinstance(node, ast.FunctionDef):
                totals["function_total"] += 1
                if ast.get_docstring(node):
                    totals["function_with_doc"] += 1
    (MET_DIR / "docstring_coverage.json").write_text(
        json.dumps(totals, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return totals


def _import_graph(files: Iterable[pathlib.Path]) -> tuple[dict[str, list[str]], list[list[str]]]:
    src_root = ROOT / "src"
    edges: dict[str, set[str]] = defaultdict(set)
    nodes: set[str] = set()
    for path in files:
        if path.suffix != ".py":
            continue
        try:
            rel = path.relative_to(src_root)
        except ValueError:
            continue
        module = ".".join(rel.with_suffix("").parts)
        nodes.add(module)
        text = _read_text(path)
        for match in IMPORT_PATTERN.finditer(text):
            target = (match.group(1) or match.group(2) or "").split()[0]
            if target and not target.startswith("."):
                edges[module].add(target)
    graph = {key: sorted(values) for key, values in sorted(edges.items())}
    (MET_DIR / "import_graph.json").write_text(
        json.dumps(graph, indent=2),
        encoding="utf-8",
    )

    cycles: list[list[str]] = []
    colours = {node: "white" for node in nodes}
    stack: list[str] = []

    def visit(current: str) -> None:
        colours[current] = "gray"
        stack.append(current)
        for neighbour in edges.get(current, ()):  # pragma: no branch - simple loop
            if neighbour not in colours:
                continue
            colour = colours[neighbour]
            if colour == "white":
                visit(neighbour)
            elif colour == "gray":
                try:
                    start = stack.index(neighbour)
                except ValueError:
                    continue
                cycle = stack[start:] + [neighbour]
                if cycle not in cycles:
                    cycles.append(cycle)
        stack.pop()
        colours[current] = "black"

    for node in sorted(nodes):
        if colours[node] == "white":
            visit(node)

    (MET_DIR / "cycles.json").write_text(json.dumps(cycles, indent=2), encoding="utf-8")
    return graph, cycles


def _notebook_checks() -> None:
    try:
        import nbformat  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        (NB_DIR / "nb_load_check.json").write_text(
            json.dumps({"status": "nbformat-missing", "error": str(exc)}, indent=2),
            encoding="utf-8",
        )
        return

    results: dict[str, dict[str, str]] = {}
    for notebook in ROOT.rglob("*.ipynb"):
        if _should_skip(notebook):
            continue
        try:
            nbformat.read(str(notebook), as_version=4)
        except Exception as exc:  # pragma: no cover - best-effort logging
            results[str(notebook)] = {"load": "error", "msg": str(exc)}
        else:
            results[str(notebook)] = {"load": "ok"}
    (NB_DIR / "nb_load_check.json").write_text(
        json.dumps(results, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _link_audit() -> None:
    results: list[dict[str, object]] = []
    for markdown in ROOT.rglob("*.md"):
        if _should_skip(markdown):
            continue
        text = _read_text(markdown)
        for match in MARKDOWN_LINK.finditer(text):
            destination = match.group(2).strip()
            if destination.startswith(("http://", "https://")):
                results.append(
                    {
                        "file": str(markdown),
                        "type": "external",
                        "target": destination,
                        "exists": None,
                    }
                )
                continue
            target = destination.split("#", 1)[0].split("?", 1)[0]
            resolved = (markdown.parent / target).resolve()
            results.append(
                {
                    "file": str(markdown),
                    "type": "relative",
                    "target": destination,
                    "exists": resolved.exists(),
                }
            )
    (DOCS_AUD_DIR / "links.json").write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )


def _write_repo_map(rows: dict[str, dict[str, int]]) -> None:
    repo_label = ROOT.name or "repository"
    lines = [
        f"# {repo_label}: Repo Map snapshot",
        "",
        "| dir | files | loc |",
        "|---:|-----:|----:|",
    ]
    for name in sorted(rows):
        files = rows[name]["files"]
        loc = rows[name]["loc"]
        lines.append(f"| {name} | {files} | {loc} |")
    (REPORTS_DIR / "repo_map.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    files = _collect_files()
    rows = _write_loc_by_dir(files)
    _docstring_coverage(files)
    _import_graph(files)
    _notebook_checks()
    _link_audit()
    _write_repo_map(rows)
    print("[metrics] DONE")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
