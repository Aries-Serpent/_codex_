#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Merge rate-limit snapshot into today's status report under automation.connectors")
    ap.add_argument("--report", default=f"reports/daily/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json")
    ap.add_argument("--snapshot", default="connectors/ratelimit_snapshot.json")
    args = ap.parse_args(argv)

    report_p = Path(args.report)
    snap_p = Path(args.snapshot)
    if not report_p.exists():
        print(f"[WARN] Report missing: {report_p}")
        return 0
    if not snap_p.exists():
        print(f"[WARN] Snapshot missing: {snap_p}")
        return 0

    report = read_json(report_p)
    snap = read_json(snap_p)

    auto = report.get("automation", {}) or {}
    connectors = auto.get("connectors", {}) or {}
    connectors["github"] = {
        "captured_utc": snap.get("captured_utc"),
        "status": snap.get("status"),
        "endpoint": snap.get("endpoint"),
        "resources": (snap.get("data", {}) or {}).get("resources", {}),
    }
    auto["connectors"] = connectors
    report["automation"] = auto

    report_p.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[OK] Merged rate-limit snapshot into {report_p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
