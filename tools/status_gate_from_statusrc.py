#!/usr/bin/env python3
"""
Evaluate local gates using .statusrc.json and coverage artifacts.

Checks:
- coverage % >= fail_under_coverage (if .coverage.json present)
- optionally ensure lint/typecheck flags (N/A in this basic script)

Exit:
- 0 on success, 1 on failure (with reasons)
"""
from __future__ import annotations

import json
from pathlib import Path


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def overall_coverage(cov_json: dict) -> float:
    # coverage json schema: "totals": {"percent_covered": float}
    totals = cov_json.get("totals", {})
    return float(totals.get("percent_covered", 0.0))


def main() -> int:
    cfg = read_json(Path(".statusrc.json"), {})
    threshold = float(cfg.get("fail_under_coverage", 0.0))
    cov = read_json(Path(".coverage.json"), {})
    cov_pct = overall_coverage(cov) if cov else 0.0

    ok = True
    reasons = []

    if threshold and cov:
        if cov_pct + 1e-9 < threshold:
            ok = False
            reasons.append(f"coverage {cov_pct:.2f}% < threshold {threshold:.2f}%")
    else:
        reasons.append("coverage check skipped (missing .coverage.json or threshold not set)")

    if ok:
        print(f"[OK] Gates passed (coverage={cov_pct:.2f}%, threshold={threshold:.2f}%)")
        return 0
    else:
        print("[FAIL] " + "; ".join(reasons))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
