#!/usr/bin/env python3
"""
Score capabilities and compute normalized weights.

Input:
  audit_artifacts/capabilities_raw.json

Output:
  audit_artifacts/capabilities_scored.json with weight field added

Heuristic:
  score = severity * confidence
  weight = score / sum(scores)

Usage:
  python tools/capability_score.py
"""
from __future__ import annotations

import json
from pathlib import Path


def score_capabilities(caps: list) -> list:
    scored = []
    total = 0.0
    for c in caps:
        severity = int(c.get("severity", 1))
        confidence = int(c.get("confidence", 1))
        score = severity * confidence
        total += score
        c["score"] = score
        scored.append(c)

    # Normalize
    for c in scored:
        c["weight"] = c["score"] / max(1, total)

    return scored


def main() -> int:
    raw = Path("audit_artifacts/capabilities_raw.json")
    out = Path("audit_artifacts/capabilities_scored.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    if not raw.exists():
        print(f"[FAIL] {raw} not found; run capability_autodiscover.py first")
        return 1

    data = json.loads(raw.read_text(encoding="utf-8"))
    caps = data.get("suggested_capabilities", [])
    scored = score_capabilities(caps)
    result = {"capabilities": scored}
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {out} with {len(scored)} scored capabilities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
