#!/usr/bin/env python3
"""
Analyze capability maturity and produce audit_artifacts/gaps.json.

Inputs:
- audit_artifacts/capabilities_scored.json (from tools/capability_score.py)

Heuristics:
- maturity = confidence / 5.0
- low_maturity if maturity < --maturity-threshold (default: 0.70)
- high_risk if severity >= --severity-threshold (default: 4)

Output:
- audit_artifacts/gaps.json with entries including id (assigned later), name, severity, confidence, weight, maturity, flags
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def load_scored(path: Path) -> List[Dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("capabilities", [])


def analyze(caps: List[Dict], maturity_threshold: float, severity_threshold: int) -> Dict:
    items = []
    for i, c in enumerate(caps, start=1):
        name = c.get("name", f"unknown-{i}")
        severity = int(c.get("severity", 1))
        confidence = int(c.get("confidence", 1))
        weight = float(c.get("weight", 0.0))
        maturity = max(0.0, min(1.0, confidence / 5.0))
        low_maturity = maturity < maturity_threshold
        high_risk = severity >= severity_threshold
        if low_maturity or high_risk:
            items.append(
                {
                    "idx": i,
                    "name": name,
                    "severity": severity,
                    "confidence": confidence,
                    "weight": weight,
                    "maturity": maturity,
                    "flags": {
                        "low_maturity": low_maturity,
                        "high_risk": high_risk,
                    },
                    "notes": c.get("gaps", "") or "",
                }
            )
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "maturity_threshold": maturity_threshold,
        "severity_threshold": severity_threshold,
        "low_maturity_count": sum(1 for x in items if x["flags"]["low_maturity"]),
        "high_risk_count": sum(1 for x in items if x["flags"]["high_risk"]),
        "items": items,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Analyze capability maturity and risk")
    ap.add_argument("--scored", default="audit_artifacts/capabilities_scored.json")
    ap.add_argument("--out", default="audit_artifacts/gaps.json")
    ap.add_argument("--maturity-threshold", type=float, default=0.70)
    ap.add_argument("--severity-threshold", type=int, default=4)
    args = ap.parse_args(argv)

    scored_path = Path(args.scored)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not scored_path.exists():
        print(f"[FAIL] Scored capabilities not found: {scored_path}")
        return 1

    caps = load_scored(scored_path)
    report = analyze(caps, args.maturity_threshold, args.severity_threshold)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {out_path} (items={len(report['items'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
