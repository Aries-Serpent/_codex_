#!/usr/bin/env python3
"""docs_sync.py — Keep MkDocs documentation in sync with the codebase.

Two mechanisms work together:

1. **Sync markers** — Embed a code snippet or file excerpt that is automatically
   kept up to date by this script:

       <!-- SYNC:src/codex/auth/user_model.py::User -->
       ```python
       ... (auto-generated — do not edit) ...
       ```
       <!-- /SYNC -->

   The marker resolves to:
     - ``path``           — raw file excerpt (first 50 lines by default)
     - ``path::ClassName`` — full class body extracted via AST
     - ``path::ClassName.method`` — single method body

2. **Stale page detection** — compares the git last-modified date of each doc
   against the last-modified dates of any source files it references.  Reports
   (or opens a GitHub issue for) docs that have not been updated after their
   source changed.

Usage
-----
    # Report stale pages and sync-marker drift (no changes)
    python scripts/ci/docs_sync.py --check

    # Auto-apply all sync markers and report remaining stale pages
    python scripts/ci/docs_sync.py --fix

    # Update only sync markers (no stale report)
    python scripts/ci/docs_sync.py --fix --no-stale

    # JSON output for CI integration
    python scripts/ci/docs_sync.py --check --json

Exit codes
----------
    0  everything up to date
    1  issues found (sync drift or stale pages)
    2  configuration error
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from textwrap import dedent
from typing import Optional

# ---------------------------------------------------------------------------
# Regex / constants
# ---------------------------------------------------------------------------

SYNC_OPEN  = re.compile(r"<!--\s*SYNC:([^\s>]+)\s*-->")
SYNC_CLOSE = re.compile(r"<!--\s*/SYNC\s*-->")
FENCE_RE   = re.compile(r"^(`{3,}|~{3,})", re.MULTILINE)

STALE_EXTENSIONS = {".py", ".yaml", ".yml", ".toml", ".json"}
STALE_SRC_ROOTS  = ["src", "scripts", ".github/workflows"]

# Lines of context shown when rendering a raw file excerpt
RAW_EXCERPT_LINES = 60


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SyncIssue:
    doc_path: str
    line: int
    marker: str
    kind: str        # DRIFT | MISSING_SOURCE | PARSE_ERROR | STALE
    message: str
    fixable: bool

    def as_dict(self) -> dict:
        return {
            "doc_path": self.doc_path,
            "line": self.line,
            "marker": self.marker,
            "kind": self.kind,
            "message": self.message,
            "fixable": self.fixable,
        }


@dataclass
class SyncResult:
    issues: list[SyncIssue] = field(default_factory=list)
    fixed: int = 0

    @property
    def errors(self) -> list[SyncIssue]:
        return [i for i in self.issues if i.kind in ("DRIFT", "MISSING_SOURCE", "STALE")]


# ---------------------------------------------------------------------------
# AST extraction helpers
# ---------------------------------------------------------------------------


def _extract_class(source: str, class_name: str) -> Optional[str]:
    """Return the full source of a class, including decorators."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    src_lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            start = node.lineno - 1
            # Walk decorators
            if node.decorator_list:
                start = min(d.lineno for d in node.decorator_list) - 1
            end = node.end_lineno  # type: ignore[attr-defined]
            return "\n".join(src_lines[start:end])
    return None


def _extract_method(source: str, class_name: str, method_name: str) -> Optional[str]:
    """Return the source of a single method inside a class."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    src_lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == method_name:
                        start = item.lineno - 1
                        if item.decorator_list:
                            start = min(d.lineno for d in item.decorator_list) - 1
                        end = item.end_lineno  # type: ignore[attr-defined]
                        return "\n".join(src_lines[start:end])
    return None


def _extract_function(source: str, func_name: str) -> Optional[str]:
    """Return the source of a top-level function."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    src_lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == func_name:
                start = node.lineno - 1
                if node.decorator_list:
                    start = min(d.lineno for d in node.decorator_list) - 1
                end = node.end_lineno  # type: ignore[attr-defined]
                return "\n".join(src_lines[start:end])
    return None


def resolve_marker(marker: str, repo_root: Path) -> tuple[Optional[str], Optional[str]]:
    """Resolve a SYNC marker to (lang, content) or (None, error_message)."""
    # Format: path[::ClassName[.method]]
    parts = marker.split("::", 1)
    file_part = parts[0].strip()
    symbol   = parts[1].strip() if len(parts) > 1 else None

    src_path = repo_root / file_part
    if not src_path.exists():
        return None, f"Source file not found: {file_part}"

    raw = src_path.read_text(encoding="utf-8", errors="replace")

    # Determine language from extension
    ext_lang = {
        ".py": "python", ".yaml": "yaml", ".yml": "yaml",
        ".json": "json",  ".sh": "bash",   ".md": "markdown",
        ".toml": "toml",  ".txt": "",
    }
    lang = ext_lang.get(src_path.suffix, "")

    if symbol is None:
        # Raw excerpt — first RAW_EXCERPT_LINES lines
        lines = raw.splitlines()[:RAW_EXCERPT_LINES]
        content = "\n".join(lines)
        if len(raw.splitlines()) > RAW_EXCERPT_LINES:
            content += f"\n# ... ({len(raw.splitlines()) - RAW_EXCERPT_LINES} more lines)"
        return lang, content

    # Symbol-based extraction
    if "." in symbol:
        class_name, method_name = symbol.split(".", 1)
        extracted = _extract_method(raw, class_name, method_name)
        if extracted is None:
            extracted = _extract_function(raw, method_name)
        if extracted is None:
            return None, f"Symbol '{symbol}' not found in {file_part}"
        return lang, dedent(extracted)
    # Try class first, then function
    extracted = _extract_class(raw, symbol)
    if extracted is None:
        extracted = _extract_function(raw, symbol)
    if extracted is None:
        return None, f"Symbol '{symbol}' not found in {file_part}"
    return lang, dedent(extracted)


# ---------------------------------------------------------------------------
# Sync marker processing
# ---------------------------------------------------------------------------


def _render_block(lang: str, content: str, marker: str) -> str:
    """Render a SYNC block including open/close markers."""
    fence = "```"
    return (
        f"<!-- SYNC:{marker} -->\n"
        f"<!-- auto-generated — do not edit between markers -->\n"
        f"{fence}{lang}\n"
        f"{content}\n"
        f"{fence}\n"
        f"<!-- /SYNC -->"
    )


def process_file(
    doc_path: Path,
    repo_root: Path,
    fix: bool,
) -> tuple[list[SyncIssue], int]:
    """Process all SYNC markers in a single doc file.

    Returns (issues, fixes_applied).
    """
    issues: list[SyncIssue] = []
    fixes = 0
    original = doc_path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    rel_path = str(doc_path.relative_to(repo_root / "docs"))

    # Collect all SYNC regions
    regions: list[tuple[int, int, str]] = []  # (open_lineno, close_lineno, marker)
    i = 0
    while i < len(lines):
        m = SYNC_OPEN.search(lines[i])
        if m:
            open_line = i
            marker = m.group(1)
            # Find the closing marker
            j = i + 1
            while j < len(lines) and not SYNC_CLOSE.search(lines[j]):
                j += 1
            if j < len(lines):
                regions.append((open_line, j, marker))
                i = j + 1
                continue
        i += 1

    if not regions:
        return issues, fixes

    # Process regions in reverse order so line numbers stay valid
    new_lines = list(lines)
    for open_line, close_line, marker in reversed(regions):
        lang, content = resolve_marker(marker, repo_root)

        if content is None:
            # lang holds the error message
            issues.append(SyncIssue(
                doc_path=rel_path,
                line=open_line + 1,
                marker=marker,
                kind="MISSING_SOURCE",
                message=f"Cannot resolve SYNC marker: {lang}",
                fixable=False,
            ))
            continue

        expected_block = _render_block(lang, content, marker)
        current_block  = "".join(new_lines[open_line:close_line + 1]).rstrip("\n")

        if current_block.strip() != expected_block.strip():
            issues.append(SyncIssue(
                doc_path=rel_path,
                line=open_line + 1,
                marker=marker,
                kind="DRIFT",
                message=f"Sync block is out of date with source: {marker}",
                fixable=True,
            ))
            if fix:
                replacement = [line + "\n" for line in expected_block.splitlines()]
                new_lines[open_line:close_line + 1] = replacement
                fixes += 1

    if fix and fixes > 0:
        doc_path.write_text("".join(new_lines), encoding="utf-8")

    return issues, fixes


# ---------------------------------------------------------------------------
# Stale page detection
# ---------------------------------------------------------------------------


def _git_mtime(path: Path) -> Optional[float]:
    """Return the Unix timestamp of the last git commit that touched path."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        ts = result.stdout.strip()
        return float(ts) if ts else None
    except Exception:
        return None


def _referenced_sources(doc_text: str, repo_root: Path) -> list[Path]:
    """Find all src/ paths mentioned in a doc (code paths, SYNC markers, inline refs)."""
    found = []
    # SYNC markers
    for m in SYNC_OPEN.finditer(doc_text):
        file_part = m.group(1).split("::")[0]
        p = repo_root / file_part
        if p.exists():
            found.append(p)
    # Inline backtick references to source files
    for match in re.finditer(r"`(src/[^\s`]+\.py)`", doc_text):
        p = repo_root / match.group(1)
        if p.exists():
            found.append(p)
    # Explicit workflow references
    for match in re.finditer(r"`(\.github/workflows/[^\s`]+\.yml)`", doc_text):
        p = repo_root / match.group(1)
        if p.exists():
            found.append(p)
    return found


def detect_stale(
    mkdocs_path: Path,
    docs_root: Path,
    repo_root: Path,
) -> list[SyncIssue]:
    """Return SyncIssues for docs that are older than their referenced sources."""
    issues: list[SyncIssue] = []
    raw = mkdocs_path.read_text(encoding="utf-8")
    doc_paths = sorted(set(re.findall(r":\s+([a-zA-Z0-9_./-]+\.md)", raw)))

    for dp in doc_paths:
        p = docs_root / dp
        if not p.exists():
            continue
        doc_mtime = _git_mtime(p)
        if doc_mtime is None:
            continue  # untracked file — skip

        text = p.read_text(encoding="utf-8", errors="replace")
        sources = _referenced_sources(text, repo_root)
        for src in sources:
            src_mtime = _git_mtime(src)
            if src_mtime and src_mtime > doc_mtime:
                issues.append(SyncIssue(
                    doc_path=dp,
                    line=None,
                    marker=str(src.relative_to(repo_root)),
                    kind="STALE",
                    message=(
                        f"Source '{src.relative_to(repo_root)}' was modified after "
                        f"this doc was last updated. Review and update if needed."
                    ),
                    fixable=False,
                ))

    return issues


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync documentation with codebase.")
    parser.add_argument("--fix", action="store_true",
                        help="Auto-apply sync markers in-place")
    parser.add_argument("--no-stale", action="store_true",
                        help="Skip stale-page detection")
    parser.add_argument("--json", dest="json_out", action="store_true",
                        help="Output JSON report")
    parser.add_argument("--config", default="mkdocs.yml")
    args = parser.parse_args(argv)

    repo_root   = Path(args.config).parent
    mkdocs_path = repo_root / "mkdocs.yml"
    docs_root   = repo_root / "docs"

    if not mkdocs_path.exists():
        print("ERROR: mkdocs.yml not found", file=sys.stderr)
        return 2

    result = SyncResult()

    # --- Process SYNC markers in all nav docs ---
    raw = mkdocs_path.read_text(encoding="utf-8")
    doc_paths = sorted(set(re.findall(r":\s+([a-zA-Z0-9_./-]+\.md)", raw)))

    for dp in doc_paths:
        p = docs_root / dp
        if not p.exists():
            continue
        issues, fixed = process_file(p, repo_root, fix=args.fix)
        result.issues.extend(issues)
        result.fixed += fixed

    # --- Stale detection ---
    if not args.no_stale:
        result.issues.extend(detect_stale(mkdocs_path, docs_root, repo_root))

    # --- Output ---
    if args.json_out:
        print(json.dumps({
            "pass": len(result.errors) == 0,
            "total_issues": len(result.issues),
            "fixed": result.fixed,
            "issues": [i.as_dict() for i in result.issues],
        }, indent=2))
    else:
        if result.fixed:
            print(f"✅ Auto-fixed {result.fixed} sync block(s).")
        if not result.issues:
            print("✅ All documentation sync markers are up to date.")
        else:
            for iss in result.issues:
                loc = f":{iss.line}" if iss.line else ""
                icon = "❌" if iss.kind in ("DRIFT", "MISSING_SOURCE") else "⚠️ "
                print(f"{icon} {iss.doc_path}{loc} [{iss.kind}]: {iss.message}")
            print(f"\n{'─'*60}")
            errors   = sum(1 for i in result.issues if i.kind in ("DRIFT","MISSING_SOURCE"))
            warnings = len(result.issues) - errors
            fix_hint = " (run --fix to auto-repair)" if any(i.fixable for i in result.issues) else ""
            print(f"{'✅ PASS' if errors == 0 else '❌ FAIL'}  "
                  f"{errors} error(s), {warnings} warning(s){fix_hint}")

    return 0 if len(result.errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
