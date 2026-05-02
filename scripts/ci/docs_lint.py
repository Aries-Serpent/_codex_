#!/usr/bin/env python3
"""docs_lint.py — MkDocs documentation health linter.

Checks every page registered in the MkDocs nav for:
  1. Broken fence closers   (```text used as closer instead of ```)
  2. Stub pages             (< STUB_WORD_THRESHOLD words)
  3. Non-.md nav entries    (.py, .html etc. that MkDocs can't theme)
  4. Missing nav files      (referenced in nav but not on disk)
  5. Unclosed fences        (fence opened but never closed)
  6. Dead internal links    (relative Markdown links that don't resolve)

Exit codes:
  0  all checks pass
  1  one or more issues found (--fix may repair some)
  2  configuration / usage error

Flags:
  --check    (default) report issues, exit 1 if any
  --fix      auto-repair broken fence closers in-place, then report remaining
  --strict   also fail on stub pages and non-.md entries (default: warnings only)
  --json     write machine-readable report to stdout (implies --check)
  --config   path to mkdocs.yml (default: mkdocs.yml)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STUB_WORD_THRESHOLD = 80  # pages with fewer words are flagged as stubs
OPENER = re.compile(r"^(`{3,}|~{3,})\s*(\S.*)?$")  # fence opener line
MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)#\s]+)(?:#[^)]*)?\)")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Issue:
    path: str
    line: Optional[int]
    kind: str          # BROKEN_CLOSER | UNCLOSED_FENCE | STUB | NON_MD_NAV | MISSING_FILE | DEAD_LINK
    severity: str      # error | warning
    message: str
    fixable: bool = False

    def as_dict(self) -> dict:
        return {
            "path": self.path,
            "line": self.line,
            "kind": self.kind,
            "severity": self.severity,
            "message": self.message,
            "fixable": self.fixable,
        }


@dataclass
class LintResult:
    issues: List[Issue] = field(default_factory=list)

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def fixable(self) -> List[Issue]:
        return [i for i in self.issues if i.fixable]


# ---------------------------------------------------------------------------
# Nav extraction
# ---------------------------------------------------------------------------


def _extract_nav_entries(mkdocs_path: Path) -> list[str]:
    """Return list of file paths from the nav: block of mkdocs.yml using a
    line-by-line state machine.

    This avoids two pitfalls:
    - ``yaml.safe_load`` fails when mkdocs.yml contains Python constructor
      tags (e.g. ``!!python/name:mermaid2.fence_mermaid_custom``).
    - A greedy regex applied to the whole file matches lines outside the
      ``nav:`` block (e.g. plugin config entries).
    """
    entries: list[str] = []
    in_nav = False
    nav_indent: int | None = None

    try:
        lines = mkdocs_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return entries

    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if not in_nav:
            if stripped.startswith("nav:"):
                in_nav = True
                nav_indent = indent
            continue

        # A non-empty, non-list line at the same or shallower indent as the
        # ``nav:`` key signals the start of the next top-level YAML key.
        if (
            nav_indent is not None
            and indent <= nav_indent
            and stripped
            and not stripped.startswith("-")
        ):
            break

        # Match ``- Title: path/to/file.md`` or ``- path/to/file.md``
        m = re.match(r"-\s+(?:[^:]+:\s+)?(\S+\.md)\s*$", stripped)
        if m:
            value = m.group(1)
            if not value.startswith("http"):
                entries.append(value)

    return entries


# ---------------------------------------------------------------------------
# Per-file checks
# ---------------------------------------------------------------------------


def _check_fences(doc_path: str, lines: list[str]) -> list[Issue]:
    """Check for broken fence closers and unclosed fences."""
    issues: list[Issue] = []
    in_fence = False
    fence_char = ""
    fence_depth = 0
    fence_start = 0

    for i, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip("\n").rstrip("\r")

        if not in_fence:
            m = OPENER.match(line)
            if m:
                in_fence = True
                fence_char = m.group(1)[0]
                fence_depth = len(m.group(1))
                fence_start = i
        else:
            # Valid closer: same char ×depth, no info string
            valid_close = re.match(
                r"^(" + re.escape(fence_char) + r"{" + str(fence_depth) + r",})\s*$",
                line,
            )
            if valid_close:
                in_fence = False
                continue

            # Invalid closer: same char ×depth + info string (e.g. ```text)
            bad_close = re.match(
                r"^(" + re.escape(fence_char) + r"{" + str(fence_depth) + r",})\s*\S.*$",
                line,
            )
            if bad_close:
                issues.append(Issue(
                    path=doc_path,
                    line=i,
                    kind="BROKEN_CLOSER",
                    severity="error",
                    message=(
                        f"Fence closer has info string "
                        f"('{line.strip()}'). "
                        f"CommonMark requires closers to have no info string. "
                        f"Replace with '{fence_char * fence_depth}'."
                    ),
                    fixable=True,
                ))
                in_fence = False

    if in_fence:
        issues.append(Issue(
            path=doc_path,
            line=fence_start,
            kind="UNCLOSED_FENCE",
            severity="error",
            message=f"Fence opened at line {fence_start} is never closed.",
            fixable=True,
        ))
    return issues


def _check_stub(doc_path: str, text: str) -> list[Issue]:
    word_count = len(text.split())
    if word_count < STUB_WORD_THRESHOLD:
        return [Issue(
            path=doc_path,
            line=None,
            kind="STUB",
            severity="warning",
            message=f"Page has only {word_count} words (threshold: {STUB_WORD_THRESHOLD}). "
                    f"Consider expanding or merging with a related page.",
            fixable=False,
        )]
    return []


def _check_dead_links(doc_path: str, text: str, docs_root: Path) -> list[Issue]:
    """Detect relative Markdown links that point to non-existent files."""
    issues: list[Issue] = []
    page_dir = (docs_root / doc_path).parent
    for i, line in enumerate(text.splitlines(), 1):
        for _label, href in MD_LINK.findall(line):
            # Skip anchors, external links, and mailto
            if href.startswith(("http", "mailto", "#")):
                continue
            target = (page_dir / href).resolve()
            if not target.exists():
                # Also try with .md extension appended
                target_md = Path(str(target) + ".md")
                if not target_md.exists():
                    issues.append(Issue(
                        path=doc_path,
                        line=i,
                        kind="DEAD_LINK",
                        severity="warning",
                        message=f"Relative link '{href}' does not resolve to an existing file.",
                        fixable=False,
                    ))
    return issues


# ---------------------------------------------------------------------------
# Auto-fix
# ---------------------------------------------------------------------------


def _fix_fences(p: Path) -> int:
    """Fix broken fence closers in-place. Returns number of fixes applied."""
    original = p.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    new_lines: list[str] = []
    in_fence = False
    fence_char = ""
    fence_depth = 0
    fixes = 0

    for line in lines:
        s = line.rstrip("\n").rstrip("\r")
        if not in_fence:
            m = OPENER.match(s)
            if m:
                in_fence = True
                fence_char = m.group(1)[0]
                fence_depth = len(m.group(1))
            new_lines.append(line)
        else:
            mc = re.match(
                r"^(" + re.escape(fence_char) + r"{" + str(fence_depth) + r",})\s*$", s
            )
            if mc:
                in_fence = False
                new_lines.append(line)
                continue
            mb = re.match(
                r"^(" + re.escape(fence_char) + r"{" + str(fence_depth) + r",})\s*\S.*$", s
            )
            if mb:
                ending = "\r\n" if line.endswith("\r\n") else "\n"
                new_lines.append(fence_char * fence_depth + ending)
                in_fence = False
                fixes += 1
                continue
            new_lines.append(line)

    if in_fence:
        new_lines.append(fence_char * fence_depth + "\n")
        fixes += 1

    result = "".join(new_lines)
    if result != original:
        p.write_text(result, encoding="utf-8")
    return fixes


# ---------------------------------------------------------------------------
# Main linting pass
# ---------------------------------------------------------------------------


def lint(
    mkdocs_path: Path,
    docs_root: Path,
    fix: bool = False,
    strict: bool = False,
    check_links: bool = True,
) -> LintResult:
    result = LintResult()
    nav_entries = _extract_nav_entries(mkdocs_path)

    for entry in nav_entries:
        # --- NON_MD_NAV check ---
        if not entry.endswith(".md"):
            sev = "error" if strict else "warning"
            result.issues.append(Issue(
                path=entry,
                line=None,
                kind="NON_MD_NAV",
                severity=sev,
                message=(
                    f"Nav entry '{entry}' is not a Markdown file. "
                    f"MkDocs cannot apply Material theme to non-.md files. "
                    f"Create a .md wrapper page instead."
                ),
                fixable=False,
            ))
            continue

        p = docs_root / entry
        # --- MISSING_FILE check ---
        if not p.exists():
            result.issues.append(Issue(
                path=entry,
                line=None,
                kind="MISSING_FILE",
                severity="error",
                message=f"File '{p}' referenced in nav does not exist.",
                fixable=False,
            ))
            continue

        # Fix fences before re-checking (if --fix)
        if fix:
            n = _fix_fences(p)
            if n:
                print(f"  🔧 Auto-fixed {n} fence closer(s) in {entry}", file=sys.stderr)

        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines(keepends=True)

        # --- FENCE checks ---
        result.issues.extend(_check_fences(entry, lines))

        # --- STUB check --- (always enabled)
        stubs = _check_stub(entry, text)
        if strict:
            for s in stubs:
                s.severity = "error"
        result.issues.extend(stubs)

        # --- DEAD_LINK checks ---
        if check_links:
            result.issues.extend(_check_dead_links(entry, text, docs_root))

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_issues(result: LintResult, strict: bool) -> None:
    by_file: dict[str, list[Issue]] = {}
    for iss in result.issues:
        by_file.setdefault(iss.path, []).append(iss)

    for path, issues in sorted(by_file.items()):
        for iss in issues:
            loc = f":{iss.line}" if iss.line else ""
            icon = "❌" if iss.severity == "error" else "⚠️ "
            fix_tag = " [fixable]" if iss.fixable else ""
            print(f"{icon} {path}{loc} [{iss.kind}]{fix_tag}")
            print(f"   {iss.message}")

    errors = len(result.errors)
    warnings = len(result.warnings)
    fixable = len(result.fixable)
    print(
        f"\n{'─'*60}\n"
        f"{'✅ PASS' if errors == 0 else '❌ FAIL'}  "
        f"{errors} error(s), {warnings} warning(s)  "
        f"({fixable} fixable with --fix)"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint MkDocs documentation pages for formatting issues."
    )
    parser.add_argument("--fix", action="store_true",
                        help="Auto-repair broken fence closers in-place")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors (stubs, non-.md nav entries)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON report to stdout")
    parser.add_argument("--no-links", action="store_true",
                        help="Skip dead-link checks (faster)")
    parser.add_argument("--config", default="mkdocs.yml",
                        help="Path to mkdocs.yml (default: mkdocs.yml)")
    args = parser.parse_args(argv)

    mkdocs_path = Path(args.config)
    if not mkdocs_path.exists():
        print(f"ERROR: mkdocs.yml not found at '{mkdocs_path}'", file=sys.stderr)
        return 2

    docs_root = mkdocs_path.parent / "docs"
    if not docs_root.exists():
        print(f"ERROR: docs/ directory not found at '{docs_root}'", file=sys.stderr)
        return 2

    result = lint(
        mkdocs_path=mkdocs_path,
        docs_root=docs_root,
        fix=args.fix,
        strict=args.strict,
        check_links=not args.no_links,
    )

    if args.json:
        print(json.dumps(
            {
                "pass": len(result.errors) == 0,
                "errors": len(result.errors),
                "warnings": len(result.warnings),
                "fixable": len(result.fixable),
                "issues": [i.as_dict() for i in result.issues],
            },
            indent=2,
        ))
    else:
        _print_issues(result, args.strict)

    return 0 if len(result.errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
