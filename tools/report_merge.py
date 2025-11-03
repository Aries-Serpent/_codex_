#!/usr/bin/env python3
"""
Merge multiple JSON fragments into a status report JSON (non-destructive).

Usage:
  python tools/report_merge.py --report reports/daily/2025-11-02.json --in coverage_modules.json:coverage_by_module --in perf_snapshot.json:automation.performance
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def deep_set(root: Dict[str, Any], dotted: str, value: Any) -> None:
    keys = dotted.split(".")
    cur = root
    for k in keys[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[keys[-1]] = value


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Merge JSON inputs into a status report")
    ap.add_argument("--report", required=True, help="Path to status report JSON to update")
    ap.add_argument("--in", dest="inputs", action="append", help="SRC_PATH:DEST_DOTTED_PATH", required=True)
    args = ap.parse_args(argv)

    report_path = Path(args.report)
    data = json.loads(report_path.read_text(encoding="utf-8"))

    for spec in args.inputs:
        src, dest = spec.split(":", 1)
        src_json = json.loads(Path(src).read_text(encoding="utf-8"))
        deep_set(data, dest, src_json)

    report_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[OK] Merged {len(args.inputs)} fragment(s) into {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
