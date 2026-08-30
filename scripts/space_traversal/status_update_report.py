#!/usr/bin/env python
"""
Status Update Report

Purpose:
    Updates status_report

Usage:
    python scripts/space_traversal/status_update_report.py [options]

    Examples:
    $ python scripts/space_traversal/status_update_report.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)



import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
    from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore
except Exception as exc:
    logger.debug(f"Exception: {exc}")
    print("Missing dependencies. Install via: pip install pyyaml jinja2", file=sys.stderr)
    raise SystemExit(1) from exc


ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / ".copilot-space" / "workflow.yaml"
DEFAULT_ARTIFACTS = ROOT / "audit_artifacts"
DEFAULT_REPORTS = ROOT / ".codex" / "reports"
STATUS_TEMPLATE = ROOT / "templates" / "audit" / "status_update_report.md.j2"
VERSION = "1.1.0"


def load_yaml(p: Path) -> dict[str, Any]:
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _build_id_score_map(scored_payload: dict[str, Any]) -> dict[str, float]:
    mp: dict[str, float] = {}
    for c in scored_payload.get("capabilities", []):
        mp[c["id"]] = float(c.get("score", 0.0))
    return mp


def compute_deltas(
    curr: dict[str, float], base: dict[str, float]
) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    """Return (top_improvements, top_regressions) sorted by magnitude."""
    changes: list[tuple[str, float]] = []
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
        "--reports", help="Reports directory (default from workflow.yaml or .codex/reports/)", default=""
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

    caps: list[dict[str, Any]] = scored.get("capabilities", [])  # type: ignore[assignment]
    total_caps = len(caps)
    avg_score = (
        round(sum(float(c.get("score", 0.0)) for c in caps) / total_caps, 4) if total_caps else 0.0
    )

    low_list: list[dict[str, Any]] = []
    if isinstance(gaps, dict) and "low_maturity" in gaps:
        low_list = list(gaps["low_maturity"])  # type: ignore[assignment]
    else:
        # compute low maturity set if gaps.json missing
        low_list = [c for c in caps if float(c.get("score", 0.0)) < low_threshold]

    # sort low maturity by ascending score for readability
    low_sorted = sorted(low_list, key=lambda c: float(c.get("score", 0.0)))

    # Deltas vs base
    improvements: list[tuple[str, float]] = []
    regressions: list[tuple[str, float]] = []
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
    # Security: Enable autoescape for HTML/XML templates to prevent XSS
    # If template contains user-generated content, autoescape should be True
    env = Environment(
        loader=FileSystemLoader(str(tpl_dir)),
        autoescape=select_autoescape(['html', 'xml', 'jinja2']),
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
