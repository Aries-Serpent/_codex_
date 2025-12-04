#!/usr/bin/env python3
"""
Simple data drift check comparing label distributions.

Usage:
  python tools/data_drift_check.py --ref data/train.stats.json --cur data/new.stats.json --threshold 0.2
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def drift_score(ref: dict, cur: dict) -> float:
    """Compute max absolute difference in label distribution."""
    ref_dist = ref.get("hist", {}).get("label", {})
    cur_dist = cur.get("hist", {}).get("label", {})
    all_keys = set(ref_dist.keys()) | set(cur_dist.keys())
    diffs = [abs(ref_dist.get(k, 0.0) - cur_dist.get(k, 0.0)) for k in all_keys]
    return round(max(diffs), 6) if diffs else 0.0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check data drift")
    ap.add_argument("--ref", required=True, help="Reference stats JSON")
    ap.add_argument("--cur", required=True, help="Current stats JSON")
    ap.add_argument("--threshold", type=float, default=0.2, help="Drift threshold")
    args = ap.parse_args(argv)

    ref = json.loads(Path(args.ref).read_text(encoding="utf-8"))
    cur = json.loads(Path(args.cur).read_text(encoding="utf-8"))
    score = drift_score(ref, cur)

    print(f"Drift score: {score:.4f} (threshold: {args.threshold})")
    if score > args.threshold:
        print("[WARN] Drift exceeds threshold")
        return 1
    print("[OK] Drift within acceptable range")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
