#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Merge schema_validation_results.json into status report JSON under automation.schema_validation"
    )
    ap.add_argument("--report", required=True)
    ap.add_argument("--results", default="schema_validation_results.json")
    args = ap.parse_args(argv)

    report = Path(args.report)
    results = Path(args.results)
    if not report.exists() or not results.exists():
        print("[FAIL] Missing report or results")
        return 1

    data = json.loads(report.read_text(encoding="utf-8"))
    res = json.loads(results.read_text(encoding="utf-8"))
    automation = data.get("automation", {})
    automation["schema_validation"] = res.get("schema_validation_results", [])
    data["automation"] = automation
    report.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[OK] Merged {len(automation['schema_validation'])} schema results into {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
