#!/usr/bin/env python3
"""Add pytest.importorskip() guards to test files with unguarded optional imports.

Reads .codex/fragile_tests.json (produced by fragile_tests_scan.py) and adds
pytest.importorskip("pkg") lines before unguarded top-level imports.

Usage:
    python .codex/scripts/add_import_guards.py [--dry-run] [--packages numpy,torch,...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FRAGILE_JSON = REPO_ROOT / ".codex" / "fragile_tests.json"

# Map base package → importorskip name
PKG_MAP = {
    "numpy": "numpy",
    "np": "numpy",
    "torch": "torch",
    "hypothesis": "hypothesis",
    "typer": "typer",
    "transformers": "transformers",
    "mlflow": "mlflow",
    "datasets": "datasets",
    "responses": "responses",
    "pandas": "pandas",
    "sentence_transformers": "sentence_transformers",
    "faiss": "faiss",
}


def add_guard_to_file(filepath: Path, packages: set[str], dry_run: bool = False) -> bool:
    """Add importorskip guards to a single file. Returns True if modified."""
    content = filepath.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")

    # Check if pytest is already imported
    has_pytest_import = any(
        re.match(r"^\s*import pytest\s*$", line) for line in lines
    )

    # Find the first unguarded import line for each package
    guards_needed = set()
    for pkg in packages:
        skip_name = PKG_MAP.get(pkg, pkg)
        # Check if importorskip already present for this package
        if f'importorskip("{skip_name}")' in content or f"importorskip('{skip_name}')" in content:
            continue
        guards_needed.add(skip_name)

    if not guards_needed:
        return False

    if dry_run:
        print(f"  Would add guards for: {', '.join(sorted(guards_needed))}")
        return True

    # Find insertion point: after last __future__ import, or after module docstring
    # First pass: find the __future__ import (MUST be first real statement)
    insert_idx = 0
    in_docstring = False
    docstring_char = None
    future_line = -1

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Track docstrings
        if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
            docstring_char = stripped[:3]
            if stripped.count(docstring_char) >= 2:
                # Single-line docstring
                insert_idx = i + 1
                continue
            in_docstring = True
            continue
        if in_docstring:
            if docstring_char and docstring_char in stripped:
                in_docstring = False
                insert_idx = i + 1
            continue
        # Track __future__ import (always takes priority)
        if stripped.startswith("from __future__"):
            insert_idx = i + 1
            future_line = i
            continue
        if stripped == "import pytest":
            insert_idx = i + 1
            continue
        # Stop at first non-import, non-blank, non-comment line after docstring
        if stripped and not stripped.startswith("#") and not stripped.startswith("import ") and not stripped.startswith("from "):
            break

    # Safety: if __future__ exists but is after current insert_idx, move past it
    if future_line >= 0 and insert_idx <= future_line:
        insert_idx = future_line + 1

    # Safety: if 'import pytest' exists anywhere, guards MUST be after it
    if has_pytest_import:
        for i, line in enumerate(lines):
            if line.strip() == "import pytest" or line.strip().startswith("import pytest  #"):
                if insert_idx <= i:
                    insert_idx = i + 1
                break

    # Build guard lines
    guard_lines = []
    if not has_pytest_import:
        guard_lines.append("import pytest")
        guard_lines.append("")

    for pkg in sorted(guards_needed):
        guard_lines.append(f'pytest.importorskip("{pkg}")')

    guard_lines.append("")  # blank line after guards

    # Insert guards
    new_lines = lines[:insert_idx] + guard_lines + lines[insert_idx:]
    filepath.write_text("\n".join(new_lines), encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Add pytest.importorskip guards")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument(
        "--packages",
        default="numpy,torch,hypothesis,typer,transformers,mlflow,datasets,responses",
        help="Comma-separated list of packages to guard",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=0,
        help="Maximum files to modify (0 = all)",
    )
    args = parser.parse_args()

    if not FRAGILE_JSON.exists():
        print("Run fragile_tests_scan.py first to generate .codex/fragile_tests.json")
        return 1

    data = json.loads(FRAGILE_JSON.read_text())
    target_pkgs = set(args.packages.split(","))

    modified = 0
    for filepath_str, imports in sorted(data.items()):
        filepath = REPO_ROOT / filepath_str
        if not filepath.exists():
            continue

        # Get base packages for this file that match our targets
        file_pkgs = set()
        for imp in imports:
            base = imp.split(".")[0]
            if base in target_pkgs or PKG_MAP.get(base, base) in target_pkgs:
                file_pkgs.add(base)

        if not file_pkgs:
            continue

        if args.dry_run:
            print(f"[DRY RUN] {filepath_str}:")

        if add_guard_to_file(filepath, file_pkgs, dry_run=args.dry_run):
            modified += 1
            if not args.dry_run:
                print(f"  ✅ Guarded: {filepath_str} ({', '.join(sorted(file_pkgs))})")

        if args.max_files and modified >= args.max_files:
            break

    print(f"\n{'Would modify' if args.dry_run else 'Modified'}: {modified} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
