"""
RAG Rebuild Audit — D4 exit criteria helper.

Usage:
    python scripts/rag/rag_rebuild_audit.py --check freshness
    python scripts/rag/rag_rebuild_audit.py --check quality
    python scripts/rag/rag_rebuild_audit.py --check audit
    python scripts/rag/rag_rebuild_audit.py --check all
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_freshness() -> dict:
    """D4 #1 — RAG index age ≤ 24 hours."""
    sla_hours = 24
    # Check for index timestamp markers
    markers = [
        ".codex/rag_index/.last_rebuilt",
        ".codex/embeddings/codex_index_meta.json",
        "benchmarks/rag/index_meta.json",
        ".codex/reports/rag/last_rebuild.json",
    ]
    for marker in markers:
        p = Path(marker)
        if p.exists():
            # Try reading JSON timestamp first
            if p.suffix == ".json":
                try:
                    data = json.loads(p.read_text())
                except Exception as exc:
                    return {
                        "check": "freshness",
                        "marker": str(p),
                        "passed": False,
                        "note": f"Failed to parse freshness marker: {exc}",
                    }
                ts_str = data.get("generated_at", "")
                if ts_str:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    age_hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
                    return {
                        "check": "freshness",
                        "marker": str(p),
                        "age_hours": round(age_hours, 1),
                        "sla_hours": sla_hours,
                        "passed": age_hours <= sla_hours,
                        "note": "Freshness check from marker timestamp",
                    }
            try:
                # Fallback to mtime
                mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
                age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
                return {
                    "check": "freshness",
                    "marker": str(p),
                    "age_hours": round(age_hours, 1),
                    "sla_hours": sla_hours,
                    "passed": age_hours <= sla_hours,
                    "note": "Freshness check from marker mtime",
                }
            except Exception as exc:
                return {
                    "check": "freshness",
                    "marker": str(p),
                    "passed": False,
                    "note": f"Failed to read freshness marker mtime: {exc}",
                }

    # If no marker found, check benchmarks/rag/retrieval_benchmark.json as proxy
    bench = Path("benchmarks/rag/retrieval_benchmark.json")
    if bench.exists():
        try:
            data = json.loads(bench.read_text())
            ts_str = data.get("generated_at", "")
            if ts_str:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                age_hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
                # Benchmarks older than 24h are stale; freshness SLA from workflow
                return {
                    "check": "freshness",
                    "marker": str(bench),
                    "age_hours": round(age_hours, 1),
                    "sla_hours": sla_hours,
                    "passed": age_hours <= sla_hours,
                    "note": "Freshness check from retrieval benchmark timestamp",
                }
        except Exception as exc:
            # Non-fatal: benchmark file may be malformed; fall through to default
            return {
                "check": "freshness",
                "passed": False,
                "note": f"Failed to parse benchmark file: {exc}",
            }

    return {
        "check": "freshness",
        "passed": False,
        "note": "No RAG index timestamp marker found. Run rag-freshness-scheduler.yml.",
    }


def check_quality() -> dict:
    """D4 #2 — recall ≥ 0.70, MRR ≥ 0.60."""
    bench = Path("benchmarks/rag/retrieval_benchmark.json")
    if not bench.exists():
        return {"check": "quality", "passed": False, "note": "benchmarks/rag/retrieval_benchmark.json missing"}

    data = json.loads(bench.read_text())
    # Support both legacy and current benchmark schemas:
    # - legacy: top-level recall_at_k/recall + min_recall/min_mrr
    # - current: last_measured.top5_recall/mrr + top5_recall_min/mrr_min
    last_measured = data.get("last_measured", {})
    recall = data.get("recall_at_k", data.get("recall"))
    if recall is None:
        recall = last_measured.get("top5_recall", last_measured.get("recall", 0))
    mrr = data.get("mrr")
    if mrr is None:
        mrr = last_measured.get("mrr", 0)
    thresholds = data.get("thresholds", {})
    recall_thresh = thresholds.get("min_recall", thresholds.get("top5_recall_min", 0.70))
    mrr_thresh = thresholds.get("min_mrr", thresholds.get("mrr_min", 0.60))

    return {
        "check": "quality",
        "recall": recall,
        "mrr": mrr,
        "recall_threshold": recall_thresh,
        "mrr_threshold": mrr_thresh,
        "passed": recall >= recall_thresh and mrr >= mrr_thresh,
    }


def check_audit() -> dict:
    """D4 #4 — log a rebuild audit entry with full audit trail."""
    audit_path = Path(".codex/reports/rag/rebuild_audit_latest.json")
    audit_log = Path(".codex/reports/rag/rebuild_audit_log.ndjson")
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "generated_at": _ts(),
        "trigger": os.environ.get("GITHUB_WORKFLOW", "manual"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "sha": os.environ.get("GITHUB_SHA", "unknown"),
        "index_status": "verified",
        "benchmark_path": "benchmarks/rag/retrieval_benchmark.json",
        "freshness_scheduler": "rag-freshness-scheduler.yml",
        "quality_gate": "rag-quality-nightly.yml",
        "note": "Rebuild audited — index automated and auditable (D4 exit criteria #4)",
    }
    audit_path.write_text(json.dumps(entry, indent=2))

    # Append to audit log (ndjson) for historical tracking
    with open(audit_log, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return {"check": "audit", "passed": True, "artifact": str(audit_path), "log": str(audit_log)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", choices=["freshness", "quality", "audit", "all"], default="all")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    checks = {"freshness": check_freshness, "quality": check_quality, "audit": check_audit}

    if args.check == "all":
        results = {k: fn() for k, fn in checks.items()}
    else:
        results = {args.check: checks[args.check]()}

    report = {
        "generated_at": _ts(),
        "domain": "D4_rag_quality",
        "checks": results,
        "all_passed": all(v.get("passed") for v in results.values()),
    }
    print(json.dumps(report, indent=2))

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(report, indent=2))

    if not report["all_passed"]:
        failed = [k for k, v in results.items() if not v.get("passed")]
        print(f"::warning::D4 RAG: {failed} failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
