#!/usr/bin/env python
"""
Offline API docs validator.

Features:
- Programmatic pdoc build to a stable output directory (artifacts/docs/api).
- Import scan for a given package; classifies failures into 'errors' vs 'optional_misses'.
- JSON summary printed to stdout for manual/local gating.

Exit code:
- Always 0 (non-blocking). Use 'ok' and arrays in the JSON output to gate
  manually or in local scripts.

Usage:
  python tools/validate_api_docs.py --package codex_ml --out artifacts/docs/api
    --allow-optional wandb tensorboard --summary
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import pkgutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


def _scan_imports(root_pkg: str, allow_optional: List[str]) -> Dict[str, Any]:
    errors: List[str] = []
    optional_misses: List[str] = []

    try:
        pkg = importlib.import_module(root_pkg)
    except Exception as exc:
        return {
            "root_import_ok": False,
            "root_error": f"{type(exc).__name__}: {exc}",
            "errors": [root_pkg],
            "optional_misses": [],
        }

    # Discover submodules safely
    pkg_path = getattr(pkg, "__path__", None)
    if not pkg_path:
        return {
            "root_import_ok": True,
            "root_error": "",
            "errors": [],
            "optional_misses": [],
        }

    for modinfo in pkgutil.walk_packages(pkg_path, prefix=f"{root_pkg}."):
        modname = modinfo.name
        try:
            importlib.import_module(modname)
        except Exception as exc:
            # If the missing module is an allowlisted optional dependency, record as optional_miss
            lowered = str(exc).lower()
            if any(
                opt.lower() in lowered or modname == opt or modname.startswith(opt + ".")
                for opt in allow_optional
            ):
                optional_misses.append(modname)
            else:
                errors.append(f"{modname}: {type(exc).__name__}: {exc}")

    return {
        "root_import_ok": True,
        "root_error": "",
        "errors": errors,
        "optional_misses": optional_misses,
    }


def _build_pdoc(root_pkg: str, out_dir: Path) -> Dict[str, Any]:
    result = {"built": False, "file_count": 0, "out_dir": str(out_dir), "notes": ""}
    if importlib.util.find_spec('pdoc') is None:
        result["notes"] = "pdoc unavailable"
        return result

    try:
        out_dir.mkdir(parents=True, exist_ok=True)

        # Use subprocess to call pdoc CLI (most reliable method)
        # Ensure PYTHONPATH includes src directory
        env = os.environ.copy()
        repo_root = Path(__file__).parent.parent.resolve()
        src_dir = repo_root / "src"

        if src_dir.exists():
            pythonpath = env.get("PYTHONPATH", "")
            if pythonpath:
                env["PYTHONPATH"] = f"{src_dir}:{pythonpath}"
            else:
                env["PYTHONPATH"] = str(src_dir)

        cmd = [
            sys.executable,
            "-m",
            "pdoc",
            "--html",
            "--output-dir",
            str(out_dir),
            "--force",
            root_pkg,
        ]

        result_proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        if result_proc.returncode == 0:
            # Count HTML outputs
            html_files = list(out_dir.rglob("*.html"))
            result["built"] = True
            result["file_count"] = len(html_files)
        else:
            result["notes"] = f"pdoc CLI failed: {result_proc.stderr or result_proc.stdout}"

        return result
    except Exception as exc:
        result["notes"] = f"pdoc build failed: {type(exc).__name__}: {exc}"
        return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Offline API docs validator (pdoc-based)")
    ap.add_argument("--package", default="codex_ml", help="Root package to document")
    ap.add_argument(
        "--out",
        default="artifacts/docs/api",
        help="Output directory for generated docs",
    )
    ap.add_argument(
        "--allow-optional",
        nargs="*",
        default=["wandb", "tensorboard"],
        help="Optional deps to allow",
    )
    ap.add_argument("--summary", action="store_true", help="Print a human-readable summary as well")
    ns = ap.parse_args()

    out_dir = Path(ns.out).expanduser().resolve()

    # Add src to path if needed
    repo_root = Path(__file__).parent.parent.resolve()
    src_dir = repo_root / "src"
    if src_dir.exists() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    import_report = _scan_imports(ns.package, ns.allow_optional)
    build_report = _build_pdoc(ns.package, out_dir)

    ok = (
        bool(import_report.get("root_import_ok", False))
        and not import_report.get("errors")
        and bool(build_report.get("built", False))
        and int(build_report.get("file_count", 0)) > 0
    )

    payload: Dict[str, Any] = {
        "ok": ok,
        "package": ns.package,
        "out_dir": str(out_dir),
        "import_report": import_report,
        "build_report": build_report,
        "env": {
            "python": sys.version,
            "cwd": str(Path.cwd()),
        },
    }

    print(json.dumps(payload, indent=2, sort_keys=True))
    if ns.summary:
        print("\n=== SUMMARY ===")
        print(f"OK: {ok}")
        if import_report.get("errors"):
            print(f"Errors: {len(import_report['errors'])}")
        if import_report.get("optional_misses"):
            print(f"Optional misses: {len(import_report['optional_misses'])}")
        print(f"Files generated: {build_report.get('file_count', 0)}")
        if build_report.get("notes"):
            print(f"Notes: {build_report['notes']}")


if __name__ == "__main__":
    main()
