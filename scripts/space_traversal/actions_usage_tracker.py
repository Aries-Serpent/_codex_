"""
import logging
logger = logging.getLogger(__name__)
GitHub Actions Usage Tracker for Audit Pipeline v1.5.x

Tracks GitHub Actions usage, costs, and provides analytics for
monitoring CI/CD resource consumption.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class WorkflowRun:
    """Single workflow run record."""

    workflow_name: str
    run_id: str
    run_number: int
    trigger: str
    status: str
    started_at: str
    completed_at: str | None
    duration_minutes: float
    runner_type: str
    estimated_cost_usd: float


@dataclass
class UsageSummary:
    """Usage summary for a period."""

    period_start: str
    period_end: str
    total_runs: int
    total_minutes: float
    total_cost_usd: float
    runs_by_workflow: dict[str, int]
    runs_by_trigger: dict[str, int]
    average_duration_minutes: float


# GitHub Actions pricing (as of 2024)
PRICING = {
    "ubuntu-latest": 0.008,  # $/minute
    "ubuntu-22.04": 0.008,
    "ubuntu-20.04": 0.008,
    "macos-latest": 0.08,
    "macos-14": 0.08,
    "macos-13": 0.08,
    "windows-latest": 0.016,
    "windows-2022": 0.016,
    "windows-2019": 0.016,
}


class UsageTracker:
    """Track and analyze GitHub Actions usage."""

    def __init__(self, data_path: Path | str = "audit_artifacts/actions_usage.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.runs: list[WorkflowRun] = []
        self._load()

    def _load(self) -> None:
        """Load existing usage data."""
        if self.data_path.exists():
            try:
                data = json.loads(self.data_path.read_text())
                self.runs = [WorkflowRun(**r) for r in data.get("runs", [])]
            except (json.JSONDecodeError, KeyError):
                self.runs = []

    def _save(self) -> None:
        """Save usage data."""
        data = {"runs": [asdict(r) for r in self.runs], "updated_at": datetime.now().isoformat()}
        self.data_path.write_text(json.dumps(data, indent=2))

    def record_run(
        self,
        workflow_name: str,
        run_id: str,
        run_number: int,
        trigger: str,
        status: str,
        started_at: str,
        completed_at: str | None = None,
        duration_minutes: float = 0,
        runner_type: str = "ubuntu-latest",
    ) -> WorkflowRun:
        """Record a workflow run."""
        cost_per_min = PRICING.get(runner_type, 0.008)
        estimated_cost = duration_minutes * cost_per_min

        run = WorkflowRun(
            workflow_name=workflow_name,
            run_id=run_id,
            run_number=run_number,
            trigger=trigger,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            duration_minutes=duration_minutes,
            runner_type=runner_type,
            estimated_cost_usd=estimated_cost,
        )

        self.runs.append(run)
        self._save()
        return run

    def get_summary(self, days: int = 30) -> UsageSummary:
        """Get usage summary for the last N days."""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        recent_runs = [r for r in self.runs if r.started_at >= cutoff_str]

        total_minutes = sum(r.duration_minutes for r in recent_runs)
        total_cost = sum(r.estimated_cost_usd for r in recent_runs)

        runs_by_workflow: dict[str, int] = {}
        runs_by_trigger: dict[str, int] = {}

        for run in recent_runs:
            runs_by_workflow[run.workflow_name] = runs_by_workflow.get(run.workflow_name, 0) + 1
            runs_by_trigger[run.trigger] = runs_by_trigger.get(run.trigger, 0) + 1

        return UsageSummary(
            period_start=cutoff_str,
            period_end=datetime.now().isoformat(),
            total_runs=len(recent_runs),
            total_minutes=total_minutes,
            total_cost_usd=total_cost,
            runs_by_workflow=runs_by_workflow,
            runs_by_trigger=runs_by_trigger,
            average_duration_minutes=total_minutes / len(recent_runs) if recent_runs else 0,
        )

    def get_cost_report(self, days: int = 30) -> str:
        """Generate a cost report."""
        summary = self.get_summary(days)

        lines = [
            "# GitHub Actions Usage Report",
            "",
            f"**Period:** {summary.period_start[:10]} to {summary.period_end[:10]}",
            "",
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Runs | {summary.total_runs} |",
            f"| Total Minutes | {summary.total_minutes:.1f} |",
            f"| Estimated Cost | ${summary.total_cost_usd:.2f} |",
            f"| Avg Duration | {summary.average_duration_minutes:.1f} min |",
            "",
            "## Runs by Workflow",
            "",
            "| Workflow | Runs |",
            "|----------|------|",
        ]

        for wf, count in sorted(summary.runs_by_workflow.items(), key=lambda x: -x[1]):
            lines.append(f"| {wf} | {count} |")

        lines.extend(
            [
                "",
                "## Runs by Trigger",
                "",
                "| Trigger | Runs |",
                "|---------|------|",
            ]
        )

        for trigger, count in sorted(summary.runs_by_trigger.items(), key=lambda x: -x[1]):
            lines.append(f"| {trigger} | {count} |")

        lines.extend(
            [
                "",
                "## Cost Breakdown by Runner",
                "",
                "| Runner | Cost/Min | Notes |",
                "|--------|----------|-------|",
                "| ubuntu-latest | $0.008 | Default Linux |",
                "| macos-latest | $0.08 | 10x Linux cost |",
                "| windows-latest | $0.016 | 2x Linux cost |",
                "",
                "---",
                f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            ]
        )

        return "\n".join(lines)

    def export_csv(self, output_path: Path) -> None:
        """Export usage data to CSV."""
        import csv

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "workflow_name",
                    "run_id",
                    "run_number",
                    "trigger",
                    "status",
                    "started_at",
                    "completed_at",
                    "duration_minutes",
                    "runner_type",
                    "estimated_cost_usd",
                ],
            )
            writer.writeheader()
            for run in self.runs:
                writer.writerow(asdict(run))


def generate_usage_dashboard_html(tracker: UsageTracker, output_path: Path) -> None:
    """Generate an HTML dashboard for usage tracking."""
    summary = tracker.get_summary(30)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Actions Usage Dashboard</title>
    <style>
        :root {{
            --bg: #0d1117;
            --card: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --accent: #58a6ff;
            --success: #3fb950;
            --warning: #d29922;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: var(--accent); margin: 0; }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent);
        }}
        .metric-label {{ color: #8b949e; margin-top: 5px; }}
        .chart-container {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{ color: #8b949e; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 GitHub Actions Usage</h1>
            <p>Last 30 days • Updated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{summary.total_runs}</div>
                <div class="metric-label">Total Runs</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary.total_minutes:.0f}</div>
                <div class="metric-label">Total Minutes</div>
            </div>
            <div class="metric">
                <div class="metric-value">${summary.total_cost_usd:.2f}</div>
                <div class="metric-label">Estimated Cost</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary.average_duration_minutes:.1f}</div>
                <div class="metric-label">Avg Duration (min)</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>Runs by Workflow</h3>
            <table>
                <thead>
                    <tr><th>Workflow</th><th>Runs</th><th>%</th></tr>
                </thead>
                <tbody>
                    {"".join(f'<tr><td>{wf}</td><td>{c}</td><td>{c/max(summary.total_runs,1)*100:.1f}%</td></tr>' for wf, c in sorted(summary.runs_by_workflow.items(), key=lambda x: -x[1]))}
                </tbody>
            </table>
        </div>
        
        <div class="chart-container">
            <h3>Runs by Trigger</h3>
            <table>
                <thead>
                    <tr><th>Trigger</th><th>Runs</th><th>%</th></tr>
                </thead>
                <tbody>
                    {"".join(f'<tr><td>{t}</td><td>{c}</td><td>{c/max(summary.total_runs,1)*100:.1f}%</td></tr>' for t, c in sorted(summary.runs_by_trigger.items(), key=lambda x: -x[1]))}
                </tbody>
            </table>
        </div>
        
        <div class="chart-container">
            <h3>Cost Reference</h3>
            <table>
                <thead>
                    <tr><th>Runner</th><th>Cost/Minute</th><th>Monthly (100 runs @ 5min)</th></tr>
                </thead>
                <tbody>
                    <tr><td>ubuntu-latest</td><td>$0.008</td><td>$4.00</td></tr>
                    <tr><td>macos-latest</td><td>$0.08</td><td>$40.00</td></tr>
                    <tr><td>windows-latest</td><td>$0.016</td><td>$8.00</td></tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)


if __name__ == "__main__":
    import sys

    tracker = UsageTracker()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "report":
            print(tracker.get_cost_report())
        elif cmd == "dashboard":
            output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("usage_dashboard.html")
            generate_usage_dashboard_html(tracker, output)
            print(f"Generated: {output}")
        elif cmd == "csv":
            output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("usage_export.csv")
            tracker.export_csv(output)
            print(f"Exported: {output}")
    else:
        print("Usage: python actions_usage_tracker.py [report|dashboard|csv] [output_path]")
