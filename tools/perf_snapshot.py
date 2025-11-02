#!/usr/bin/env python3
"""
Parse a training log and extract performance snapshot for status automation.

Output:
  JSON with training.throughput_steps_per_sec, training.epoch_time_seconds, inference.latency_p50_ms, etc.

Usage:
  python tools/perf_snapshot.py --log runs/examples/train.log --out perf_snapshot.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Any


def parse_log(log_path: Path) -> Dict[str, Any]:
    text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    data = {"training": {}, "inference": {}, "memory": {}}

    # Parse training metrics
    for line in text.splitlines():
        m = re.search(r"steps/s:\s*([0-9.]+)", line)
        if m:
            data["training"]["throughput_steps_per_sec"] = float(m.group(1))
        m = re.search(r"epoch_time_s:\s*([0-9.]+)", line)
        if m:
            data["training"]["epoch_time_seconds"] = float(m.group(1))
        m = re.search(r"latency_p50_ms:\s*([0-9.]+)", line)
        if m:
            data["inference"]["latency_p50_ms"] = float(m.group(1))
        m = re.search(r"latency_p95_ms:\s*([0-9.]+)", line)
        if m:
            data["inference"]["latency_p95_ms"] = float(m.group(1))
        m = re.search(r"peak_ram_gb:\s*([0-9.]+)", line)
        if m:
            data["memory"]["peak_ram_gb"] = float(m.group(1))

    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Extract performance snapshot from log")
    ap.add_argument("--log", required=True, help="Path to training log")
    ap.add_argument("--out", default="perf_snapshot.json", help="Output JSON path")
    args = ap.parse_args(argv)

    snapshot = parse_log(Path(args.log))
    out = Path(args.out)
    out.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
