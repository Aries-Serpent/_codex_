#!/usr/bin/env python
"""
Analyze Legacy Usage

Purpose:
    Analyzes legacy_usage

Usage:
    python scripts/remediation/analyze_legacy_usage.py [options]

    Examples:
    $ python scripts/remediation/analyze_legacy_usage.py --help

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

import argparse
import ast
import csv
import logging
import sys
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
# Note: 'hydra' removed - it refers to PyPI package, not local module
LEGACY_MODULES = {"training", "tokenization", "models"}


class ImportVisitor(ast.NodeVisitor):
    def __init__(self, filepath, include_relative=False):
        self.filepath = filepath
        self.include_relative = include_relative
        self.found = []

    def visit_Import(self, node):
        for alias in node.names:
            self._check(alias.name, node.lineno, is_relative=False, level=0)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module or ""
        level = getattr(node, "level", 0) or 0
        is_relative = level >= 1
        # Respect flag: ignore relative imports unless explicitly requested
        if is_relative and not self.include_relative:
            self.generic_visit(node)
            return
        self._check(module, node.lineno, is_relative=is_relative, level=level)
        self.generic_visit(node)

    def _check(self, module_name, lineno, is_relative=False, level=0):
        if not module_name:
            return
        base = module_name.split(".")[0]
        if base in LEGACY_MODULES:
            self.found.append(
                {
                    "file": str(self.filepath),
                    "line": lineno,
                    "module": base,
                    "full_import": module_name,
                    "relative": bool(is_relative),
                    "level": int(level),
                }
            )


def scan_dirs(dirs, include_relative=False):
    results = []
    count = 0
    for d in dirs:
        if not d.exists():
            continue
        for py_file in sorted(d.rglob("*.py")):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                visitor = ImportVisitor(
                    py_file.relative_to(ROOT), include_relative=include_relative
                )
                visitor.visit(tree)
                results.extend(visitor.found)
                count += 1
            except Exception as e:
                logger.debug(f"Exception: {e}")
                print(f"[ERR] parsing {py_file}: {e}", file=sys.stderr)
    print(
        f"[*] Scanned {count} files. Found {len(results)} legacy import occurrences (include_relative={include_relative})."
    )
    return results


def write_report(results):
    out_path = ROOT / ".codex" / "reports" / "legacy_import_usage.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["module", "full_import", "file", "line", "relative", "level"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"[+] Report written to {out_path}")
    summary = defaultdict(int)
    rel_summary = defaultdict(int)
    for r in results:
        summary[r["module"]] += 1
        if r.get("relative"):
            rel_summary[r["module"]] += 1
    print("\n--- Usage Summary ---")
    for mod, c in summary.items():
        rel = rel_summary.get(mod, 0)
        print(f"  {mod}: {c} references (relative: {rel})")


def main():
    parser = argparse.ArgumentParser(description="Legacy import usage analyzer")
    parser.add_argument(
        "--root-only",
        action="store_true",
        help="Scan only repository root (exclude src/tests/scripts/deploy)",
    )
    parser.add_argument(
        "--include-tests", action="store_true", help="Include tests/ in scan (default: included)"
    )
    parser.add_argument(
        "--include-relative",
        action="store_true",
        help="Include relative ImportFrom entries (level >= 1) in the output",
    )
    args = parser.parse_args()

    print(f"[*] Scanning codebase at {ROOT} for legacy imports: {LEGACY_MODULES}")
    if args.root_only:
        dirs_to_scan = [ROOT]
    else:
        dirs_to_scan = [ROOT / "src", ROOT / "scripts", ROOT / "deploy"]
        # Include tests by default unless explicitly excluded
        if args.include_tests or not hasattr(args, "exclude_tests"):
            dirs_to_scan.append(ROOT / "tests")

    results = scan_dirs(dirs_to_scan, include_relative=args.include_relative)
    write_report(results)

    if any(d["module"] == "hydra" for d in results):
        print(
            "\n[!] CRITICAL: Found 'hydra' imports which may shadow the PyPI package. Review and remediate."
        )


if __name__ == "__main__":
    main()
