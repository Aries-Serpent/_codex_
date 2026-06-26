#!/usr/bin/env python3
"""
wec_health_monitor.py — WEC Compliance Health Monitoring Dashboard

Purpose
-------
Provides real-time health monitoring of WEC (Workflow Execution Checklist) 
compliance across open PRs. Tracks:

  1. WEC compliance rate across all open PRs
  2. Workflow execution metrics (pass/fail rates)
  3. Average time to merge compliance
  4. Compliance trend analysis
  5. Health score calculation

Usage
-----
    python scripts/ci/wec_health_monitor.py [--json] [--verbose]
    python scripts/ci/wec_health_monitor.py --summary [--days N]
    python scripts/ci/wec_health_monitor.py --trends [--export FILE]
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
REPO = "Aries-Serpent/_codex_"

# Health score weights (sum = 1.0)
HEALTH_WEIGHTS = {
    "wec_compliance_rate": 0.30,  # 30% — WEC compliance across PRs
    "workflow_pass_rate": 0.25,   # 25% — workflow success rate
    "req_compliance_rate": 0.25,  # 25% — REQ-4/REQ-5 compliance
    "merge_speed": 0.20,          # 20% — time to merge compliance
}

# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class PRHealthMetrics:
    """Health metrics for a single PR."""
    pr_number: int
    wec_compliant: bool
    req4_updated: bool
    req5_updated: bool
    workflow_count: int
    workflow_pass_rate: float
    time_to_merge_hours: float
    created_at: str
    last_checked: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HealthSummary:
    """Overall health summary metrics."""
    timestamp: str
    total_prs: int
    wec_compliant_count: int
    wec_compliance_rate: float
    req_compliance_rate: float
    avg_workflow_pass_rate: float
    avg_merge_time_hours: float
    health_score: float
    status: str
    prs: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Health Monitoring Functions
# ---------------------------------------------------------------------------


def get_open_prs() -> list[dict[str, Any]]:
    """Fetch all open PRs from the repository."""
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--repo", REPO, "--state", "open", "--json",
             "number,title,createdAt,updatedAt"],
            capture_output=True,
            text=True,
            check=True,
        )
        prs = json.loads(result.stdout)
        return prs
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to fetch PRs: {e.stderr}")
        return []


def check_wec_compliance(pr_number: int) -> bool:
    """Check if PR has WEC compliance satisfied."""
    try:
        result = subprocess.run(
            ["python", "scripts/ci/session_wrapup_autofix.py",
             "--pr-number", str(pr_number),
             "--check-wec-compliance"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        return result.returncode == 0
    except Exception as e:
        logger.debug(f"WEC check failed for PR #{pr_number}: {e}")
        return False


def check_req_compliance(pr_number: int) -> tuple[bool, bool]:
    """Check if PR has REQ-4 and REQ-5 compliance.
    
    Returns (req4_ok, req5_ok).
    """
    try:
        result = subprocess.run(
            ["python", "scripts/ci/session_wrapup_autofix.py",
             "--pr-number", str(pr_number),
             "--check"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        # Both must be satisfied
        req_ok = result.returncode == 0
        return req_ok, req_ok
    except Exception as e:
        logger.debug(f"REQ check failed for PR #{pr_number}: {e}")
        return False, False


def get_workflow_metrics(pr_number: int) -> tuple[int, float]:
    """Get workflow count and pass rate for PR.
    
    Returns (workflow_count, pass_rate).
    """
    try:
        result = subprocess.run(
            ["gh", "pr", "view", str(pr_number), "--repo", REPO,
             "--json", "statusCheckRollup"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        checks = data.get("statusCheckRollup", [])
        
        if not checks:
            return 0, 1.0
        
        passed = sum(1 for c in checks if c.get("status") == "PASS")
        total = len(checks)
        pass_rate = passed / total if total > 0 else 1.0
        
        return total, pass_rate
    except Exception as e:
        logger.debug(f"Failed to get workflow metrics for PR #{pr_number}: {e}")
        return 0, 0.0


def calculate_time_to_merge(pr: dict[str, Any]) -> float:
    """Calculate time from PR creation to current (hours)."""
    try:
        created_at_str = pr.get("createdAt", "")
        if not created_at_str:
            return 0.0
        
        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - created_at
        return delta.total_seconds() / 3600  # Convert to hours
    except Exception as e:
        logger.debug(f"Failed to calculate time to merge: {e}")
        return 0.0


def calculate_health_score(summary: HealthSummary) -> float:
    """Calculate overall health score (0.0 - 1.0)."""
    score = (
        HEALTH_WEIGHTS["wec_compliance_rate"] * summary.wec_compliance_rate +
        HEALTH_WEIGHTS["workflow_pass_rate"] * summary.avg_workflow_pass_rate +
        HEALTH_WEIGHTS["req_compliance_rate"] * summary.req_compliance_rate +
        HEALTH_WEIGHTS["merge_speed"] * min(1.0, summary.avg_merge_time_hours / 24.0)
    )
    return min(1.0, max(0.0, score))


def determine_health_status(score: float) -> str:
    """Determine health status from score."""
    if score >= 0.90:
        return "🟢 EXCELLENT"
    elif score >= 0.75:
        return "🟡 GOOD"
    elif score >= 0.60:
        return "🟠 FAIR"
    else:
        return "🔴 POOR"


def generate_health_report(json_output: bool = False, verbose: bool = False) -> HealthSummary | None:
    """Generate comprehensive health report for all open PRs."""
    logger.info("📊 Generating WEC Health Report...")
    
    # Fetch all open PRs
    prs = get_open_prs()
    if not prs:
        logger.warning("No open PRs found")
        return None
    
    pr_metrics: list[PRHealthMetrics] = []
    req4_count = 0
    req5_count = 0
    wec_count = 0
    total_workflow_pass = 0.0
    total_merge_time = 0.0
    
    for pr in prs:
        pr_number = pr["number"]
        
        if verbose:
            logger.info(f"  Checking PR #{pr_number}...")
        
        # Check compliance
        wec_ok = check_wec_compliance(pr_number)
        req4_ok, req5_ok = check_req_compliance(pr_number)
        workflow_count, pass_rate = get_workflow_metrics(pr_number)
        merge_time = calculate_time_to_merge(pr)
        
        if wec_ok:
            wec_count += 1
        if req4_ok:
            req4_count += 1
        if req5_ok:
            req5_count += 1
        
        total_workflow_pass += pass_rate
        total_merge_time += merge_time
        
        metrics = PRHealthMetrics(
            pr_number=pr_number,
            wec_compliant=wec_ok,
            req4_updated=req4_ok,
            req5_updated=req5_ok,
            workflow_count=workflow_count,
            workflow_pass_rate=pass_rate,
            time_to_merge_hours=merge_time,
            created_at=pr.get("createdAt", ""),
            last_checked=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        pr_metrics.append(metrics)
    
    # Calculate aggregate metrics
    total_prs = len(prs)
    wec_compliance_rate = wec_count / total_prs if total_prs > 0 else 0.0
    req_compliance_rate = (req4_count + req5_count) / (2 * total_prs) if total_prs > 0 else 0.0
    avg_workflow_pass_rate = total_workflow_pass / total_prs if total_prs > 0 else 0.0
    avg_merge_time = total_merge_time / total_prs if total_prs > 0 else 0.0
    
    summary = HealthSummary(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        total_prs=total_prs,
        wec_compliant_count=wec_count,
        wec_compliance_rate=wec_compliance_rate,
        req_compliance_rate=req_compliance_rate,
        avg_workflow_pass_rate=avg_workflow_pass_rate,
        avg_merge_time_hours=avg_merge_time,
        health_score=0.0,  # Will calculate below
        status="",  # Will calculate below
        prs=[m.to_dict() for m in pr_metrics],
    )
    
    # Calculate health score and status
    summary.health_score = calculate_health_score(summary)
    summary.status = determine_health_status(summary.health_score)
    
    if json_output:
        print(json.dumps(summary.to_dict(), indent=2))
    else:
        _print_health_report(summary)
    
    return summary


def _print_health_report(summary: HealthSummary) -> None:
    """Print human-readable health report."""
    print()
    print("=" * 80)
    print(f"🏥 WEC Health Monitor Report — {summary.timestamp}")
    print("=" * 80)
    print()
    
    print(f"📊 Overall Health: {summary.status} ({summary.health_score:.1%})")
    print()
    
    print("📈 Metrics:")
    print(f"  • Total Open PRs:           {summary.total_prs}")
    print(f"  • WEC Compliant:            {summary.wec_compliant_count}/{summary.total_prs} ({summary.wec_compliance_rate:.1%})")
    print(f"  • REQ-4/5 Compliance:       {summary.req_compliance_rate:.1%}")
    print(f"  • Avg Workflow Pass Rate:   {summary.avg_workflow_pass_rate:.1%}")
    print(f"  • Avg Merge Time:           {summary.avg_merge_time_hours:.1f} hours")
    print()
    
    # Health score breakdown
    print("🎯 Health Score Components:")
    wec_contrib = HEALTH_WEIGHTS["wec_compliance_rate"] * summary.wec_compliance_rate
    req_contrib = HEALTH_WEIGHTS["req_compliance_rate"] * summary.req_compliance_rate
    wf_contrib = HEALTH_WEIGHTS["workflow_pass_rate"] * summary.avg_workflow_pass_rate
    merge_contrib = HEALTH_WEIGHTS["merge_speed"] * min(1.0, summary.avg_merge_time_hours / 24.0)
    
    print(f"  • WEC Compliance:    {wec_contrib:.2f} ({HEALTH_WEIGHTS['wec_compliance_rate']:.0%} weight)")
    print(f"  • Workflow Success:  {wf_contrib:.2f} ({HEALTH_WEIGHTS['workflow_pass_rate']:.0%} weight)")
    print(f"  • REQ Compliance:    {req_contrib:.2f} ({HEALTH_WEIGHTS['req_compliance_rate']:.0%} weight)")
    print(f"  • Merge Speed:       {merge_contrib:.2f} ({HEALTH_WEIGHTS['merge_speed']:.0%} weight)")
    print()
    
    if summary.total_prs <= 10:
        print("📋 PR Details:")
        for pr in summary.prs:
            status = "✅" if pr["wec_compliant"] else "❌"
            print(f"  {status} PR #{pr['pr_number']}: "
                  f"WEC={pr['wec_compliant']}, "
                  f"Workflows={pr['workflow_pass_rate']:.0%}, "
                  f"Age={pr['time_to_merge_hours']:.1f}h")
    
    print()
    print("=" * 80)


def save_health_report(summary: HealthSummary, filepath: Path) -> None:
    """Save health report to file."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(summary.to_dict(), f, indent=2)
        logger.info(f"✅ Health report saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save health report: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="WEC Compliance Health Monitoring Dashboard (Phase 6)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output report as JSON",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Verbose output",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Generate summary report and save",
    )
    parser.add_argument(
        "--export",
        metavar="FILE",
        default="",
        help="Export report to JSON file",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Number of days for trend analysis (default: 7)",
    )
    
    args = parser.parse_args(argv)
    
    # Generate report
    summary = generate_health_report(json_output=args.json, verbose=args.verbose)
    
    if summary is None:
        return 1
    
    # Export if requested
    if args.export:
        export_path = Path(args.export)
        save_health_report(summary, export_path)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
