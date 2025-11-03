#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Tuple
import subprocess
import sys


def load_config(p: Path) -> Dict[str, Any]:
    if not p.exists():
        return {"default_metric": "ssim", "default_threshold": 0.98, "templates": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def resolve_threshold(cfg: Dict[str, Any], template_name: str) -> Tuple[str, float]:
    tcfg = (cfg.get("templates") or {}).get(template_name, {})
    metric = tcfg.get("metric", cfg.get("default_metric", "ssim"))
    thr = float(tcfg.get("threshold", cfg.get("default_threshold", 0.98)))
    return metric, thr


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compare images using per-template thresholds from a JSON config")
    ap.add_argument("--config", default="visual_baseline/thresholds.json", help="Path to thresholds config JSON")
    ap.add_argument("--template", required=True, help="Template filename key to lookup threshold (e.g., report_template_themed.html)")
    ap.add_argument("--baseline", required=True, help="Path to baseline PNG")
    ap.add_argument("--candidate", required=True, help="Path to candidate PNG")
    ap.add_argument("--metric", help="Override metric (ssim or mse)")
    ap.add_argument("--threshold", type=float, help="Override threshold")
    args = ap.parse_args(argv)

    # Validate paths to prevent path traversal attacks
    baseline_path = Path(args.baseline).resolve()
    candidate_path = Path(args.candidate).resolve()
    repo_root = Path.cwd().resolve()
    
    if not (baseline_path.is_relative_to(repo_root) and candidate_path.is_relative_to(repo_root)):
        print("Error: File paths must be within the repository root", file=sys.stderr)
        return 1

    cfg = load_config(Path(args.config))
    metric, threshold = resolve_threshold(cfg, args.template)
    if args.metric:
        metric = args.metric
    if args.threshold is not None:
        threshold = float(args.threshold)

    # Delegate to visual_compare.py
    code = subprocess.call(
        [sys.executable, "tools/visual_compare.py", "--baseline", args.baseline, "--candidate", args.candidate, "--metric", metric, "--threshold", str(threshold)]
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
