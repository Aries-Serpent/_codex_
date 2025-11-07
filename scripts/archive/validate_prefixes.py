#!/usr/bin/env python
"""
Prefix Enforcement Validator (BUNDLE_PREFIX_MODE)

Purpose:
- When BUNDLE_PREFIX_MODE=1, enforce allowed prefixes for bundle-like artifacts.
- Allowed prefixes: patchset_, bundle_, har_
- Targets audit_artifacts paths (bundles/, baselines/ optional future)

Behavior:
- Scan audit_artifacts/bundles for files not starting with allowed prefixes
- Emit a JSON report and non-zero exit if violations found (unless --warn-only)

Usage:
  BUNDLE_PREFIX_MODE=1 python scripts/archive/validate_prefixes.py
  python scripts/archive/validate_prefixes.py --warn-only

Outputs:
- audit_artifacts/prefix_validation_report.json
"""

from __future__ import annotations
import os, sys, json
from pathlib import Path
from typing import List, Dict

ALLOWED_PREFIXES = ("patchset_", "bundle_", "har_")
REPORT_PATH = Path("audit_artifacts/prefix_validation_report.json")

def validate_prefixes(root: Path) -> Dict[str, List[str]]:
    violations: List[str] = []
    if not root.exists():
        return {"checked": [], "violations": [], "allowed": list(ALLOWED_PREFIXES)}
    candidates = []
    bundles = root / "bundles"
    if bundles.exists():
        candidates.extend(sorted(p.as_posix() for p in bundles.iterdir() if p.is_file()))
    # Future: add baselines or other dirs if policy expands.
    for rel in candidates:
        name = Path(rel).name
        if not name.startswith(ALLOWED_PREFIXES):
            violations.append(rel)
    return {"checked": candidates, "violations": violations, "allowed": list(ALLOWED_PREFIXES)}

def main(argv=None):
    warn_only = False
    if argv is None:
        argv = sys.argv[1:]
    if "--warn-only" in argv:
        warn_only = True
    enforce = os.getenv("BUNDLE_PREFIX_MODE", "0") in {"1", "true", "TRUE", "on", "ON", "yes", "YES"}
    root = Path("audit_artifacts")
    report = validate_prefixes(root)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if enforce and report["violations"] and not warn_only:
        print(f"[ERR] Prefix violations found: {len(report['violations'])}. See {REPORT_PATH}", file=sys.stderr)
        return 3
    if report["violations"]:
        print(f"[WARN] Prefix violations: {len(report['violations'])}. See {REPORT_PATH}", file=sys.stderr)
    else:
        print("[INFO] No prefix violations detected.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
