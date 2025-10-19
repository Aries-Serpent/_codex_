#!/usr/bin/env python
"""
Status Update Audit Report Generator (v1.1.0)

Purpose:
- Produce a concise Codex Status Update Audit Report as Markdown under reports/
- Summarize current capability scores, low maturity items, integrity chain,
  warnings, and optional regressions/improvements vs a baseline.

Inputs (by default, from .copilot-space/workflow.yaml and audit_artifacts/):
- audit_artifacts/capabilities_scored.json (required)
- audit_artifacts/gaps.json (optional; will compute using threshold if missing)
- audit_run_manifest.json (optional integrity+weights data)
- .copilot-space/workflow.yaml (for thresholds, directories)

Optional:
- --base <path/to/scored.json> to compute deltas vs baseline scored file

Determinism:
- Offline-only, sorted output, no network.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from jinja2 import Environment, FileSystemLoader  # type: ignore

    import yaml  # type: ignore
except Exception as exc:
    print("Missing dependencies. Install via: pip install pyyaml jinja2", file=sys.stderr)
    raise SystemExit(1) from exc


ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / ".copilot-space" / "workflow.yaml"
DEFAULT_ARTIFACTS = ROOT / "audit_artifacts"
DEFAULT_REPORTS = ROOT / "reports"
STATUS_TEMPLATE = ROOT / "templates" / "audit" / "status_update_report.md.j2"
VERSION = "1.1.0"


def load_yaml(p: Path) -> Dict[str, Any]:
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _build_id_score_map(scored_payload: Dict[str, Any]) -> Dict[str, float]:
    mp: Dict[str, float] = {}
    for c in scored_payload.get("capabilities", []):
        mp[c["id"]] = float(c.get("score", 0.0))
    return mp


def compute_deltas(
    curr: Dict[str, float], base: Dict[str, float]
) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
    """Return (top_improvements, top_regressions) sorted by magnitude."""
    changes: List[Tuple[str, float]] = []
    for cid, new in curr.items():
        old = base.get(cid)
        if old is None:
            continue
        delta = new - old
        changes.append((cid, delta))
    # improvements: delta > 0 desc; regressions: delta < 0 asc
    improvements = sorted(
        [(cid, d) for cid, d in changes if d > 0], key=lambda x: x[1], reverse=True
    )
    regressions = sorted([(cid, d) for cid, d in changes if d < 0], key=lambda x: x[1])
    # cap with top 10 each for concise report
    return improvements[:10], regressions[:10]


def ensure_dirs(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate Codex Status Update Audit Report")
    ap.add_argument(
        "--base", help="Path to baseline capabilities_scored.json for delta comparison", default=""
    )
    ap.add_argument(
        "--artifacts",
        help="Artifacts directory (default from workflow.yaml or audit_artifacts/)",
        default="",
    )
    ap.add_argument(
        "--reports", help="Reports directory (default from workflow.yaml or reports/)", default=""
    )
    args = ap.parse_args()

    cfg = load_yaml(CFG_PATH)
    artifacts_dir = (
        Path(args.artifacts)
        if args.artifacts
        else ROOT / cfg.get("output", {}).get("artifacts_dir", DEFAULT_ARTIFACTS)
    )
    reports_dir = (
        Path(args.reports)
        if args.reports
        else ROOT / cfg.get("output", {}).get("reports_dir", DEFAULT_REPORTS)
    )
    ensure_dirs(reports_dir)

    scored_path = artifacts_dir / "capabilities_scored.json"
    if not scored_path.exists():
        print("capabilities_scored.json not found. Run S4 first.", file=sys.stderr)
        raise SystemExit(2)

    # Load inputs
    scored = load_json(scored_path)
    if not isinstance(scored, dict):
        print("Invalid capabilities_scored.json structure.", file=sys.stderr)
        raise SystemExit(3)
    gaps = load_json(artifacts_dir / "gaps.json")
    manifest = load_json(ROOT / "audit_run_manifest.json")
    thresholds = (cfg.get("scoring", {}) or {}).get("thresholds", {}) or {"low": 0.70}
    low_threshold = float(thresholds.get("low", 0.70))

    caps: List[Dict[str, Any]] = scored.get("capabilities", [])  # type: ignore[assignment]
    total_caps = len(caps)
    avg_score = (
        round(sum(float(c.get("score", 0.0)) for c in caps) / total_caps, 4) if total_caps else 0.0
    )

    low_list: List[Dict[str, Any]] = []
    if isinstance(gaps, dict) and "low_maturity" in gaps:
        low_list = list(gaps["low_maturity"])  # type: ignore[assignment]
    else:
        # compute low maturity set if gaps.json missing
        low_list = [c for c in caps if float(c.get("score", 0.0)) < low_threshold]

    # sort low maturity by ascending score for readability
    low_sorted = sorted(low_list, key=lambda c: float(c.get("score", 0.0)))

    # Deltas vs base
    improvements: List[Tuple[str, float]] = []
    regressions: List[Tuple[str, float]] = []
    if args.base:
        base_path = Path(args.base)
        if base_path.exists():
            base = load_json(base_path)
            curr_map = _build_id_score_map(scored)
            base_map = _build_id_score_map(base if isinstance(base, dict) else {})
            improvements, regressions = compute_deltas(curr_map, base_map)

    weights = scored.get("weights") or cfg.get("weights", {})
    warnings = scored.get("warnings", [])
    if not warnings and isinstance(manifest, dict):
        warnings = manifest.get("warnings", [])

    integrity = {
        "repo_root_sha": manifest.get("repo_root_sha", "") if isinstance(manifest, dict) else "",
        "template_hash": manifest.get("template_hash", "") if isinstance(manifest, dict) else "",
    }

    # Render template
    tpl_dir = STATUS_TEMPLATE.parent
    env = Environment(
        loader=FileSystemLoader(str(tpl_dir)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(STATUS_TEMPLATE.name)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC")

    context = {
        "timestamp": timestamp,
        "version": VERSION,
        "summary": {
            "total_capabilities": total_caps,
            "average_score": avg_score,
            "low_count": len(low_sorted),
            "low_threshold": low_threshold,
        },
        "weights": weights,
        "warnings": warnings,
        "integrity": integrity,
        "low_maturity": [
            {
                "id": c["id"],
                "score": float(c.get("score", 0.0)),
                "primary_deficit": c.get("primary_deficit", ""),
            }
            for c in low_sorted[:25]  # cap list length for compactness
        ],
        "deltas": {
            "improvements": [{"id": cid, "delta": round(d, 4)} for cid, d in improvements],
            "regressions": [{"id": cid, "delta": round(d, 4)} for cid, d in regressions],
        },
    }

    out_path = reports_dir / f"codex_status_update_{time.strftime('%Y%m%d_%H%M%S')}.md"
    out_path.write_text(template.render(**context), encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
