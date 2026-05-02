#!/usr/bin/env python3
"""Cognitive brain trend analysis — track AAIS and health metrics over sessions.

Reads cognitive brain dashboard and PR session history to generate trend data.
Outputs JSON report for dashboard visualization.

Usage:
    python scripts/cognitive/trend_analysis.py [--json] [--output FILE]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = REPO_ROOT / ".codex" / "cognitive_brain" / "dashboard.md"
CHANGELOG = REPO_ROOT / ".codex" / "change_log.md"

# Known AAIS progression milestones
AAIS_HISTORY = [
    {"version": "V1.0", "score": 87.3, "session": 0, "date": "2026-01-15"},
    {"version": "V2.0", "score": 91.8, "session": 3, "date": "2026-01-28"},
    {"version": "V3.0", "score": 93.2, "session": 11, "date": "2026-02-11"},
    {"version": "V3.1", "score": 93.7, "session": 19, "date": "2026-02-12"},
    {"version": "V3.2", "score": 94.8, "session": 20, "date": "2026-02-12"},
    {"version": "V3.3", "score": 95.5, "session": 22, "date": "2026-02-12"},
    {"version": "V3.4", "score": 97.0, "session": 23, "date": "2026-02-12"},
]


def extract_dashboard_metrics() -> dict:
    """Extract current metrics from cognitive brain dashboard."""
    metrics = {
        "health_score": 0,
        "sessions": 0,
        "commits": 0,
        "patterns": 0,
        "aais_score": 0.0,
        "planset_completion": 0,
    }

    if not DASHBOARD.exists():
        return metrics

    content = DASHBOARD.read_text()

    # Extract health percentage
    match = re.search(r"Health[:\s]*(\d+)%", content)
    if match:
        metrics["health_score"] = int(match.group(1))

    # Extract session count
    match = re.search(r"Sessions?[:\s]*(\d+)", content)
    if match:
        metrics["sessions"] = int(match.group(1))

    # Extract commit count
    match = re.search(r"Commits?[:\s]*(\d+)", content)
    if match:
        metrics["commits"] = int(match.group(1))

    # Extract pattern count
    match = re.search(r"Patterns?[:\s]*(\d+)", content)
    if match:
        metrics["patterns"] = int(match.group(1))

    # Extract AAIS score
    match = re.search(r"AAIS[^:]*:\s*([\d.]+)", content)
    if match:
        metrics["aais_score"] = float(match.group(1))

    # Extract planset completion
    match = re.search(r"(\d+)/(\d+)\s*plansets?", content, re.IGNORECASE)
    if match:
        metrics["planset_completion"] = int(match.group(1))

    return metrics


def extract_session_history() -> list[dict]:
    """Extract session history from change log."""
    sessions = []

    if not CHANGELOG.exists():
        return sessions

    content = CHANGELOG.read_text()

    # Find session entries (## Session N or ## 2026-MM-DD)
    for match in re.finditer(
        r"##\s+(?:Session\s+(\d+)|(\d{4}-\d{2}-\d{2}))\s*[-—]?\s*(.*)",
        content,
    ):
        session_num = match.group(1) or "0"
        date = match.group(2) or ""
        description = match.group(3) or ""

        sessions.append(
            {
                "session": int(session_num) if session_num != "0" else len(sessions) + 1,
                "date": date,
                "description": description.strip(),
            }
        )

    return sessions


def generate_trend_report() -> dict:
    """Generate comprehensive trend analysis report."""
    metrics = extract_dashboard_metrics()
    sessions = extract_session_history()

    # AAIS progression targets
    aais_current = metrics["aais_score"]
    aais_target = 97.0
    aais_gap = max(0, aais_target - aais_current)

    # Calculate velocity from history
    deltas = []
    for i in range(1, len(AAIS_HISTORY)):
        prev = AAIS_HISTORY[i - 1]
        curr = AAIS_HISTORY[i]
        session_diff = max(1, curr["session"] - prev["session"])
        deltas.append({
            "from": prev["version"],
            "to": curr["version"],
            "delta": round(curr["score"] - prev["score"], 1),
            "sessions": session_diff,
            "velocity": round((curr["score"] - prev["score"]) / session_diff, 2),
        })
    avg_velocity = (
        round(sum(d["velocity"] for d in deltas) / len(deltas), 2) if deltas else 0
    )
    sessions_to_target = (
        round(aais_gap / avg_velocity) if avg_velocity > 0 else 0
    )

    return {
        "current_metrics": metrics,
        "session_history": sessions,
        "aais_progression": {
            "current": aais_current,
            "target": aais_target,
            "gap": round(aais_gap, 1),
            "grade": "A+" if aais_current >= 97.0 else "A" if aais_current >= 93.0 else "B+",
            "improvements_remaining": round(aais_gap / 0.7, 1),  # ~0.7 points per improvement
            "history": AAIS_HISTORY,
            "deltas": deltas,
            "avg_velocity_per_session": avg_velocity,
            "estimated_sessions_to_target": sessions_to_target,
        },
        "health_trend": {
            "current": metrics["health_score"],
            "target": 100,
            "status": "excellent" if metrics["health_score"] >= 95 else "good",
        },
        "planset_status": {
            "completed": metrics["planset_completion"],
            "total": 16,
            "percentage": round(metrics["planset_completion"] / 16 * 100, 1)
            if metrics["planset_completion"]
            else 0,
        },
    }



def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Cognitive brain trend analysis")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--output", type=str, help="Write report to file")
    args = parser.parse_args()

    report = generate_trend_report()

    if args.json or args.output:
        output = json.dumps(report, indent=2)
        if args.output:
            Path(args.output).write_text(output)
            print(f"Report written to {args.output}")
        else:
            print(output)
    else:
        # Human-readable output
        m = report["current_metrics"]
        ap = report["aais_progression"]
        print("═══ Cognitive Brain Trend Analysis ═══")
        print(f"  Health Score: {m['health_score']}%")
        print(f"  Sessions: {m['sessions']}")
        print(f"  Commits: {m['commits']}")
        print(f"  AAIS Score: {m['aais_score']}/100 ({ap['grade']})")
        print(f"  Target: {ap['target']}")
        print(f"  Gap: {ap['gap']} points")
        print(f"  Improvements remaining: ~{ap['improvements_remaining']}")
        print(f"  Avg velocity: {ap['avg_velocity_per_session']} pts/session")
        print(f"  Est. sessions to A+: ~{ap['estimated_sessions_to_target']}")
        ps = report["planset_status"]
        print(f"  Plansets: {ps['completed']}/{ps['total']} ({ps['percentage']}%)")
        print()
        print("  AAIS History:")
        for h in ap["history"]:
            print(f"    {h['version']}: {h['score']}")
        if ap.get("deltas"):
            print()
            print("  Session Deltas:")
            for d in ap["deltas"]:
                print(f"    {d['from']}→{d['to']}: +{d['delta']} ({d['velocity']} pts/session)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
