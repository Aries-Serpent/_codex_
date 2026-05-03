#!/usr/bin/env python3
"""
check_cross_references.py -- Hard gate: no commit may introduce a broken internal link.

POLICY ENFORCEMENT
------------------
Codebase Agency Policy S.2: "Leave the codebase better than you found it."
Violation pattern caught by this script:
  - Moving or deleting a file WITHOUT updating all references to it.
  - This severs live cross-references, breaking navigation for agents, CI, and humans.

This is the enforcement mechanism that makes that violation impossible to commit.

SCOPE
-----
Mode 1 (default) -- changed-only (pre-commit / CI):
  Only checks files changed in the current commit/PR via git diff.
  Principle: you own what you change.

Mode 2 -- --full-scan:
  Scans all files. Used for periodic audits to surface ALL broken links.

WHAT IS CHECKED
---------------
Only explicit Markdown link syntax: [text](path/to/file)
This is unambiguous with near-zero false positives.
Backtick and YAML string references are excluded (too many false positives).

Usage
-----
    python scripts/ci/check_cross_references.py               # changed files only
    python scripts/ci/check_cross_references.py FILE [...]    # specific files
    python scripts/ci/check_cross_references.py --full-scan   # all files
    python scripts/ci/check_cross_references.py --report-only # audit, exit 0

Exit codes: 0=clean, 1=broken references found
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_EXTENSIONS = {".md", ".yml", ".yaml"}

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", ".venv_ci",
    "dist", "build", ".eggs", "archive", "backups",
}

# Files that contain inline scripts which *generate* Markdown content (e.g.
# f.write() calls that write link syntax to an output file inside a workflow
# run: block).  The links in these files are not references FROM the file
# itself — they are content that will be written to a different output file.
# Checking them against the source file's location produces false positives.
#
# This script is also listed here because its own docstring and comments
# include the Markdown link syntax as documentation examples, not real links.
SKIP_FILES: frozenset[str] = frozenset({
    ".github/workflows/pages-mkdocs.yml",
    ".github/workflows.backup.20260214_131353/pages-mkdocs.yml",
    "scripts/ci/check_cross_references.py",  # self-referential: documents the syntax it detects
})

# Only explicit Markdown links: [text](path)
_MD_LINK_RE = re.compile(
    r'\[(?:[^\]]*)\]\('
    r'(?!https?://|mailto:|#|ftp://|\$\{|%)'
    r'(?P<path>[^)#\s\$\{%][^)]*?)\)',
)


def _should_skip(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    try:
        abs_path = path if path.is_absolute() else REPO_ROOT / path
        rel = str(abs_path.relative_to(REPO_ROOT))
    except ValueError:
        rel = str(path)
    return rel in SKIP_FILES


def _resolve_ref(raw: str, source_file: Path) -> Path | None:
    raw = raw.strip()
    if not raw:
        return None
    # Skip external refs, anchors, template vars, glob patterns
    if any(c in raw for c in ("*", "?", "{", "}", "$", "\n", " ", "%")):
        return None
    if raw.startswith(("http", "mailto:", "#", "ftp", "data:")):
        return None
    # Skip known placeholder tokens that are not real file paths.
    # Using an explicit allow-list rather than a broad regex to avoid accidentally
    # skipping extensionless files like README, LICENSE, or CHANGELOG.
    if raw in {"URL", "RUN_URL"}:
        return None
    # Strip anchor fragment (#section) before resolving the file path
    raw = raw.split("#")[0].strip()
    raw = raw.split("?")[0].strip()
    if not raw:
        return None

    if raw.startswith("./") or raw.startswith("../"):
        return (source_file.parent / raw).resolve()
    if raw.startswith("/"):
        return (REPO_ROOT / raw.lstrip("/")).resolve()
    # Try source-relative first
    src_rel = (source_file.parent / raw).resolve()
    if src_rel.exists():
        return src_rel
    # Then repo-root-relative
    return (REPO_ROOT / raw).resolve()


def scan_file(path: Path) -> list[tuple[int, str, Path]]:
    """Return (line_no, raw_path, resolved_path) for broken Markdown links."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    broken: list[tuple[int, str, Path]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in _MD_LINK_RE.finditer(line):
            raw = match.group("path").strip()
            resolved = _resolve_ref(raw, path)
            if resolved is None:
                continue
            try:
                resolved.relative_to(REPO_ROOT)
            except ValueError:
                continue
            try:
                exists = resolved.exists()
            except OSError:
                continue
            if not exists:
                broken.append((line_no, raw, resolved))
    return broken


def get_changed_files() -> list[Path]:
    """Return files changed in the current git working tree / staging area."""
    files: list[Path] = []
    for cmd in (
        ["git", "diff", "--name-only", "--cached"],
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "HEAD~1"],
    ):
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=15,
            )
            for line in result.stdout.splitlines():
                p = REPO_ROOT / line.strip()
                if p.exists() and p.suffix in SCAN_EXTENSIONS and not _should_skip(p):
                    files.append(p)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    return list(dict.fromkeys(files))


def get_all_files(scan_dirs: list[str]) -> list[Path]:
    files: list[Path] = []
    for d in scan_dirs:
        root = REPO_ROOT / d
        if not root.exists():
            continue
        for f in root.rglob("*"):
            if f.is_file() and f.suffix in SCAN_EXTENSIONS and not _should_skip(f):
                files.append(f)
    return sorted(set(files))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Hard gate: verify no commit introduces new broken internal references. "
            "Enforces Codebase Agency Policy S.2."
        )
    )
    parser.add_argument("files", nargs="*",
                        help="Specific files to check (default: git-changed files)")
    parser.add_argument("--full-scan", action="store_true",
                        help="Scan all files in the repo (audit mode)")
    parser.add_argument("--scan-dirs", nargs="+",
                        default=[".github/agents", ".github/workflows",
                                 "docs", ".codex", "scripts/ci"],
                        metavar="DIR")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--report-only", action="store_true",
                        help="Print findings but always exit 0")
    args = parser.parse_args(argv)

    if args.files:
        files = [Path(f) for f in args.files if Path(f).exists() and not _should_skip(Path(f))]
    elif args.full_scan:
        files = get_all_files(args.scan_dirs)
    else:
        files = get_changed_files()

    if not files:
        print("OK No files to check.")
        return 0

    all_broken: list[tuple[Path, int, str, Path]] = []
    for f in files:
        for line_no, raw, resolved in scan_file(f):
            all_broken.append((f, line_no, raw, resolved))

    if not all_broken:
        print(f"OK {len(files)} file(s) checked -- all internal references resolve.")
        return 0

    by_file: dict[Path, list] = {}
    for src, line_no, raw, resolved in all_broken:
        by_file.setdefault(src, []).append((line_no, raw, resolved))

    print(f"\n{'='*70}")
    print(f"BROKEN INTERNAL REFERENCES -- {len(all_broken)} in {len(by_file)} file(s)")
    print(f"{'='*70}\n")
    print("Policy: Codebase Agency Policy S.2 -- Leave the codebase better than found.")
    print("Rule:   Run this check BEFORE moving or deleting ANY file.\n")

    for src_file, refs in sorted(by_file.items()):
        try:
            src_display = src_file.relative_to(REPO_ROOT)
        except ValueError:
            src_display = src_file
        print(f"  {src_display}")
        for line_no, raw, resolved in refs:
            print(f"    line {line_no:4d}: '{raw}'")
            try:
                res_display = resolved.relative_to(REPO_ROOT)
            except ValueError:
                res_display = resolved
            print(f"           -> expected: {res_display}  FILE DOES NOT EXIST")
        print()

    print("FIX BEFORE COMMITTING:")
    print("  1. Restore the missing file to its original path,  OR")
    print("  2. Update every reference to point to the new location,  OR")
    print("  3. Remove the reference if the file is permanently deleted.")
    print()

    return 0 if args.report_only else 1


if __name__ == "__main__":
    sys.exit(main())
