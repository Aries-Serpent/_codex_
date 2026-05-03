"""
Automated Documentation Generator (PS-19d).

Scan source modules for docstrings, calculate documentation coverage,
and generate summary reports.

Usage:
    python scripts/ci/auto_doc_generator.py
    python scripts/ci/auto_doc_generator.py --json
    python scripts/ci/auto_doc_generator.py --coverage-threshold 80
    python scripts/ci/auto_doc_generator.py --output report.json
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIRS = [REPO_ROOT / "src", REPO_ROOT / "scripts"]


def _extract_module_info(filepath: Path) -> dict:
    """Extract documentation info from a Python module."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except Exception:  # non-parseable files
        return {"file": str(filepath), "parseable": False}

    module_doc = ast.get_docstring(tree) or ""
    classes = []
    functions = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node) or ""
            classes.append({"name": node.name, "has_docstring": bool(doc)})
        elif isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node) or ""
            functions.append({"name": node.name, "has_docstring": bool(doc)})

    total = 1 + len(classes) + len(functions)  # module + classes + functions
    documented = (1 if module_doc else 0) + sum(1 for c in classes if c["has_docstring"]) + sum(
        1 for f in functions if f["has_docstring"]
    )

    return {
        "file": str(filepath.relative_to(REPO_ROOT)),
        "parseable": True,
        "module_docstring": bool(module_doc),
        "classes": len(classes),
        "functions": len(functions),
        "documented": documented,
        "total": total,
        "coverage": round(documented / total * 100, 1) if total > 0 else 100.0,
    }


def scan_directory(directory: Path) -> list[dict]:
    """Scan a directory for Python files and extract doc info."""
    if not directory.exists():
        return []
    results = []
    for py_file in sorted(directory.rglob("*.py")):
        if "__pycache__" in str(py_file):
            continue
        info = _extract_module_info(py_file)
        if info.get("parseable", False):
            results.append(info)
    return results


def calculate_coverage(results: list[dict]) -> tuple[int, int, float]:
    """Calculate overall documentation coverage."""
    total_items = sum(r.get("total", 0) for r in results)
    documented_items = sum(r.get("documented", 0) for r in results)
    coverage = round(documented_items / total_items * 100, 1) if total_items > 0 else 0.0
    return documented_items, total_items, coverage


def main() -> int:
    """CLI entry point."""
    threshold = 80.0
    output_path = None

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--coverage-threshold" and i + 1 < len(args):
            threshold = float(args[i + 1])
        elif arg == "--output" and i + 1 < len(args):
            output_path = args[i + 1]

    all_results = []
    for src_dir in SRC_DIRS:
        all_results.extend(scan_directory(src_dir))

    documented, total, coverage = calculate_coverage(all_results)

    low_coverage = [r for r in all_results if r.get("coverage", 100) < threshold]

    report = {
        "timestamp": __import__("datetime").datetime.now(
            tz=__import__("datetime").timezone.utc
        ).isoformat(),
        "total_files": len(all_results),
        "total_items": total,
        "documented_items": documented,
        "coverage_percent": coverage,
        "threshold": threshold,
        "status": "pass" if coverage >= threshold else "below_threshold",
        "low_coverage_files": len(low_coverage),
    }

    if "--json" in args:
        report["files"] = all_results
        report["low_coverage"] = low_coverage
        output = json.dumps(report, indent=2, default=str)
        if output_path:
            Path(output_path).write_text(output, encoding="utf-8")
            print(f"Report written to {output_path}")
        else:
            print(output)
        return 0

    print("Documentation Coverage Report")
    print(f"  Files scanned: {len(all_results)}")
    print(f"  Items: {documented}/{total} documented ({coverage}%)")
    print(f"  Threshold: {threshold}%")
    print(f"  Status: {'✅ PASS' if coverage >= threshold else '⚠️ BELOW THRESHOLD'}")
    if low_coverage:
        print(f"\n  Files below {threshold}% coverage ({len(low_coverage)}):")
        for f in low_coverage[:10]:
            print(f"    {f['file']}: {f['coverage']}%")
        if len(low_coverage) > 10:
            print(f"    ... and {len(low_coverage) - 10} more")

    if output_path:
        Path(output_path).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"\nReport written to {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
