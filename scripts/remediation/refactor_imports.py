#!/usr/bin/env python3
"""
Refactor Imports

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/remediation/refactor_imports.py [options]
    
    Examples:
    $ python scripts/remediation/refactor_imports.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


"""
import logging
logger = logging.getLogger(__name__)
Refactor Import Tool (safe AST-based import rewrites)

Usage:
  # Dry-run showing proposed changes
  python scripts/remediation/refactor_imports.py --mapping '{"training":"src.training","tokenization":"src.tokenization"}' --dry-run

  # Apply in small batches (commit-per-batch)
  python scripts/remediation/refactor_imports.py --mapping mappings.json --apply --batch-size 20

Notes:
- The tool updates Import and ImportFrom AST nodes to replace base module names.
- Uses ast for correctness; preserves formatting by writing back source (best-effort).
- Recommended workflow: run --dry-run, review diffs, run with --apply --batch-size.
"""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC_DIRS = [ROOT / "src", ROOT]
PY_FILES = list(ROOT.rglob("*.py"))


def load_mappings(mapping_arg: str) -> dict[str, str]:
    # mapping_arg can be a JSON string or path to a JSON file
    p = Path(mapping_arg)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    try:
        return json.loads(mapping_arg)
    except Exception as e:
        logger.debug(f"Exception: {e}")
        raise RuntimeError(f"Invalid mapping: {e}")


def find_candidate_files() -> list[Path]:
    files = []
    for p in ROOT.rglob("*.py"):
        # skip virtualenvs, audit_artifacts, .git, etc.
        if any(part in p.parts for part in ("audit_artifacts", ".git", "venv", "__pycache__")):
            continue
        files.append(p)
    return files


def process_file(path: Path, mappings: dict[str, str]) -> tuple[bool, str]:
    """
    Returns (changed, new_source)
    """
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        logger.debug(f"SyntaxError: {e}")
        return False, src
    changed = False

    class ImportRefactor(ast.NodeTransformer):
        def visit_Import(self, node: ast.Import):
            for alias in node.names:
                base = alias.name.split(".")[0]
                if base in mappings:
                    new_name = alias.name.replace(base, mappings[base], 1)
                    alias.name = new_name
                    nonlocal changed
                    changed = True
            return node

        def visit_ImportFrom(self, node: ast.ImportFrom):
            if node.module:
                base = node.module.split(".")[0]
                if base in mappings:
                    node.module = node.module.replace(base, mappings[base], 1)
                    nonlocal changed
                    changed = True
            return node

    new_tree = ImportRefactor().visit(tree)
    if not changed:
        return False, src
    # Try to unparse AST back to source. Use ast.unparse if available (Py3.9+).
    try:
        new_src = ast.unparse(new_tree)
    except Exception:
        # Fallback: simple textual replacement (best-effort), preserve original spacing
        new_src = src
        for old, new in mappings.items():
            # replace common patterns in import statements
            new_src = new_src.replace(f"import {old}", f"import {new}")
            new_src = new_src.replace(f"from {old}", f"from {new}")
    return True, new_src


def run_dry_run(mappings: dict[str, str], limit: int = 100) -> list[tuple[Path, str]]:
    candidates = find_candidate_files()
    changes = []
    for p in candidates:
        try:
            changed, new_src = process_file(p, mappings)
            if changed:
                changes.append((p, new_src))
            if len(changes) >= limit:
                break
        except Exception as e:
            logger.debug(f"Exception: {e}")
            print(f"Warning: skipping {p}: {e}")
    return changes


def apply_changes(changes: list[tuple[Path, str]], commit_per_batch: int = 20):
    idx = 0
    total = len(changes)
    while idx < total:
        batch = changes[idx : idx + commit_per_batch]
        for path, new_src in batch:
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            path.write_text(new_src, encoding="utf-8")
        # Run tests for safety
        print(f"Applied batch {idx // commit_per_batch + 1}, running tests...")
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "tests/validation/"],
            capture_output=True,
            text=True,
        )
        print(res.stdout)
        if res.returncode != 0:
            print("Tests failed after applying batch; reverting batch.")
            for path, _ in batch:
                backup = path.with_suffix(path.suffix + ".bak")
                if backup.exists():
                    shutil.copy2(backup, path)
            raise RuntimeError("Tests failed after refactor; reverted batch.")
        # Commit batch
        subprocess.run(["git", "add"] + [str(p) for p, _ in batch], check=True)
        subprocess.run(["git", "commit", "-m", f"refactor: update imports (batch)"], check=True)
        idx += commit_per_batch
    print("All batches applied successfully.")


def main():
    parser = argparse.ArgumentParser(description="Refactor imports from legacy roots to src.*")
    parser.add_argument(
        "--mapping",
        required=True,
        help="JSON string or path to JSON mapping file for old->new prefixes",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Do not write files; show proposed changes"
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes (use with care)")
    parser.add_argument(
        "--batch-size", type=int, default=20, help="Commit per N files when applying"
    )
    parser.add_argument("--limit", type=int, default=500, help="Max files to inspect")
    args = parser.parse_args()

    mappings = load_mappings(args.mapping)
    print(f"Loaded mappings: {mappings}")
    changes = run_dry_run(mappings, limit=args.limit)
    print(f"Candidate files with proposed changes: {len(changes)}")
    for p, new_src in changes[:20]:
        print(f"--- {p} ---")
        print(new_src.splitlines()[:10])
        print("...")

    if args.dry_run:
        print("Dry-run: no changes applied.")
        return

    if args.apply:
        if not changes:
            print("No changes to apply.")
            return
        apply_changes(changes, commit_per_batch=args.batch_size)
    else:
        print("Run with --apply to apply changes (commits per batch).")


if __name__ == "__main__":
    main()
