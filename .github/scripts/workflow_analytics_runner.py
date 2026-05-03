#!/usr/bin/env python3
"""
Workflow Analytics Runner

Analyzes GitHub Actions workflow runs to identify patterns, failures,
and improvement opportunities. Designed to be triggered manually or
automatically via GitHub Actions.

Usage:
    python workflow_analytics_runner.py \
        --analysis-period 50 \
        --status-filter failure \
        --output-dir .codex/reports
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Error pattern detection regexes
ERROR_PATTERNS = {
    "import_error": r"(?:ModuleNotFoundError|ImportError|NameError):\s*(.+)",
    "syntax_error": r"(?:SyntaxError|yaml\.scanner\.ScannerError):\s*(.+)",
    "test_failure": r"(?:FAILED|AssertionError|pytest\.fail):\s*(.+)",
    "timeout": r"(?:TimeoutError|Timeout|timed out):\s*(.+)",
    "permission": r"(?:PermissionError|403|Permission denied):\s*(.+)",
    "dependency": r"(?:pip resolver|incompatible|version conflict):\s*(.+)",
    "type_error": r"(?:TypeError|AttributeError):\s*(.+)",
    "file_not_found": r"(?:FileNotFoundError|No such file):\s*(.+)",
    "disk_full": r"(?:No space left|disk.*full|OSError.*28)",
    "artifact_missing": r"(?:Artifact.*not found|Unable to find.*artifact)",
    "env_setup": r"(?:command not found|tool.*not.*found|could not find)",
}


def run_gh_command(command: List[str]) -> str:
    """Run GitHub CLI command and return output."""
    try:
        result = subprocess.run(
            ["gh"] + command,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub CLI error: {e.stderr}", file=sys.stderr)
        return ""
    except FileNotFoundError:
        print("❌ GitHub CLI not found. Please install gh.", file=sys.stderr)
        sys.exit(1)


def get_workflow_runs(
    limit: int = 50,
    workflow: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch workflow runs from GitHub API."""
    command = [
        "run",
        "list",
        "--limit",
        str(limit),
        "--json",
        "databaseId,name,displayTitle,status,conclusion,createdAt,updatedAt,headBranch,event,workflowName",
    ]

    if workflow:
        command.extend(["--workflow", workflow])

    if status and status != "all":
        command.extend(["--status", status])

    output = run_gh_command(command)
    if not output:
        return []

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        print("❌ Failed to parse workflow runs JSON", file=sys.stderr)
        return []


def get_workflow_logs(run_id: int) -> str:
    """Get logs for a specific workflow run."""
    return run_gh_command(["run", "view", str(run_id), "--log"])


def analyze_log_for_patterns(log_content: str) -> Dict[str, List[str]]:
    """Analyze log content for known error patterns."""
    results = defaultdict(list)

    for category, pattern in ERROR_PATTERNS.items():
        matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
        if matches:
            # Keep only unique matches
            unique_matches = list(set(matches))[:5]  # Limit to top 5
            results[category].extend(unique_matches)

    return dict(results)


def calculate_statistics(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics from workflow runs."""
    total = len(runs)
    if total == 0:
        return {
            "total_runs": 0,
            "conclusion_distribution": {},
            "success_rate": 0.0,
            "health_status": "UNKNOWN",
        }

    # Count conclusions
    conclusions = Counter(run.get("conclusion") or "in_progress" for run in runs)

    # Calculate success rate (completed successfully / completed runs)
    completed_runs = [r for r in runs if r.get("conclusion")]
    successful_runs = [r for r in completed_runs if r.get("conclusion") == "success"]

    success_rate = (
        (len(successful_runs) / len(completed_runs) * 100)
        if completed_runs
        else 0.0
    )

    # Determine health status
    failure_count = conclusions.get("failure", 0)
    if failure_count == 0:
        health_status = "HEALTHY"
    elif failure_count < total * 0.05:  # Less than 5% failures
        health_status = "GOOD"
    elif failure_count < total * 0.15:  # Less than 15% failures
        health_status = "WARNING"
    else:
        health_status = "CRITICAL"

    return {
        "total_runs": total,
        "conclusion_distribution": dict(conclusions),
        "success_rate": round(success_rate, 2),
        "health_status": health_status,
        "completed_runs": len(completed_runs),
        "successful_runs": len(successful_runs),
        "failed_runs": conclusions.get("failure", 0),
    }


def generate_report(
    runs: List[Dict[str, Any]],
    statistics: Dict[str, Any],
    error_patterns: Dict[int, Dict[str, List[str]]],
    args: argparse.Namespace,
) -> tuple[Dict[str, Any], str]:
    """Generate JSON and Markdown reports."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

    # Build JSON report
    json_report = {
        "report_metadata": {
            "generated_at": timestamp,
            "report_type": "workflow_analytics",
            "agent": "workflow-analytics-agent",
            "analysis_period": f"Last {args.analysis_period} workflow runs",
            "version": "1.0.0",
            "run_id": args.run_id,
            "filters": {
                "workflow": args.workflow_filter or "all",
                "status": args.status_filter,
            },
        },
        "summary": statistics,
        "error_patterns_detected": len(error_patterns),
        "workflow_runs_analyzed": [
            {
                "id": run["databaseId"],
                "name": run["name"],
                "conclusion": run.get("conclusion"),
                "created_at": run["createdAt"],
                "branch": run.get("headBranch"),
            }
            for run in runs[:10]  # Include top 10 for sample
        ],
        "detected_patterns": error_patterns,
    }

    # Build Markdown report
    md_lines = [
        "# Workflow Analytics Report",
        "",
        f"**Generated**: {timestamp}",
        f"**Run ID**: {args.run_id}",
        f"**Analysis Period**: {args.analysis_period} runs",
        f"**Workflow Filter**: {args.workflow_filter or 'All workflows'}",
        f"**Status Filter**: {args.status_filter}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"{'✅' if statistics['health_status'] == 'HEALTHY' else '⚠️'} **CI/CD Health Status: {statistics['health_status']}**",
        "",
        "### Key Metrics",
        "",
        "| Metric | Value | Status |",
        "|--------|-------|--------|",
        f"| Total Runs Analyzed | {statistics['total_runs']} | ✅ |",
        f"| Success Rate | {statistics['success_rate']}% | {'✅' if statistics['success_rate'] >= 95 else '⚠️'} |",
        f"| Failed Runs | {statistics.get('failed_runs', 0)} | {'✅' if statistics.get('failed_runs', 0) == 0 else '❌'} |",
        f"| Patterns Detected | {len(error_patterns)} | {'✅' if len(error_patterns) == 0 else '⚠️'} |",
        "",
        "---",
        "",
        "## Workflow Run Distribution",
        "",
        "### Conclusion Breakdown",
        "",
        "| Conclusion | Count | Percentage |",
        "|------------|-------|------------|",
    ]

    for conclusion, count in sorted(
        statistics["conclusion_distribution"].items(), key=lambda x: -x[1]
    ):
        percentage = (count / statistics["total_runs"] * 100) if statistics["total_runs"] > 0 else 0
        md_lines.append(f"| {conclusion} | {count} | {percentage:.1f}% |")

    md_lines.extend([
        "",
        "---",
        "",
        "## Error Pattern Analysis",
        "",
    ])

    if error_patterns:
        md_lines.append(f"**Patterns Detected**: {len(error_patterns)} run(s) with errors")
        md_lines.append("")

        for run_id, patterns in error_patterns.items():
            md_lines.append(f"### Run #{run_id}")
            md_lines.append("")
            for category, errors in patterns.items():
                md_lines.append(f"**{category}**: {len(errors)} occurrence(s)")
                for error in errors[:3]:  # Show top 3
                    md_lines.append(f"- `{error[:100]}`")
            md_lines.append("")
    else:
        md_lines.extend([
            "✅ **No error patterns detected**",
            "",
            "All analyzed workflows completed successfully or were skipped as expected.",
            "",
        ])

    md_lines.extend([
        "---",
        "",
        "## Recommendations",
        "",
    ])

    if statistics["health_status"] == "HEALTHY":
        md_lines.extend([
            "✅ **Continue current practices** - CI/CD pipeline is healthy",
            "",
            "- Monitor for any emerging patterns",
            "- Maintain current testing and quality standards",
            "- Review this report monthly for trends",
        ])
    else:
        md_lines.extend([
            "⚠️ **Action Required** - CI/CD pipeline needs attention",
            "",
            "1. Review error patterns detected above",
            "2. Consult Error Pattern Database (`.codex/reports/ERROR_PATTERN_DATABASE.md`)",
            "3. Engage CI Testing Agent for remediation",
            "4. Monitor success rate until it returns to >95%",
        ])

    md_lines.extend([
        "",
        "---",
        "",
        "## Related Resources",
        "",
        "- **Error Pattern Database**: `.codex/reports/ERROR_PATTERN_DATABASE.md`",
        "- **Workflow Analytics Agent**: `.github/agents/workflow-analytics-agent.md`",
        "- **CI Testing Agent**: `.github/agents/ci-testing-agent.md`",
        "",
        "---",
        "",
        "**Generated by**: Workflow Analytics Agent v1.0.0",
        f"**Next Review**: {(datetime.now(timezone.utc).replace(day=28) if datetime.now(timezone.utc).day < 28 else datetime.now(timezone.utc).replace(month=datetime.now(timezone.utc).month + 1, day=28)).strftime('%Y-%m-%d')}",
    ])

    markdown_report = "\n".join(md_lines)

    return json_report, markdown_report


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Analyze GitHub Actions workflow runs"
    )
    parser.add_argument(
        "--analysis-period",
        type=int,
        default=50,
        help="Number of recent workflow runs to analyze",
    )
    parser.add_argument(
        "--workflow-filter",
        type=str,
        default="",
        help="Filter by specific workflow name",
    )
    parser.add_argument(
        "--status-filter",
        type=str,
        default="all",
        choices=["all", "failure", "success", "action_required", "cancelled"],
        help="Filter by workflow status",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".codex/reports"),
        help="Output directory for reports",
    )
    parser.add_argument(
        "--create-report",
        type=str,
        default="true",
        help="Generate detailed reports",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="manual",
        help="GitHub Actions run ID",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("🔍 Workflow Analytics Agent")
    print(f"📊 Analyzing last {args.analysis_period} workflow runs...")

    # Fetch workflow runs
    runs = get_workflow_runs(
        limit=args.analysis_period,
        workflow=args.workflow_filter if args.workflow_filter else None,
        status=args.status_filter if args.status_filter != "all" else None,
    )

    if not runs:
        print("⚠️ No workflow runs found")
        sys.exit(0)

    print(f"✅ Found {len(runs)} workflow runs")

    # Analyze runs for patterns
    error_patterns = {}
    failed_runs = [r for r in runs if r.get("conclusion") == "failure"]

    if failed_runs:
        print(f"🔬 Analyzing {len(failed_runs)} failed runs for error patterns...")
        for run in failed_runs[:10]:  # Analyze up to 10 failed runs
            run_id = run["databaseId"]
            print(f"   - Analyzing run #{run_id}...")
            logs = get_workflow_logs(run_id)
            if logs:
                patterns = analyze_log_for_patterns(logs)
                if patterns:
                    error_patterns[run_id] = patterns

    # Calculate statistics
    statistics = calculate_statistics(runs)

    print("\n📈 Statistics:")
    print(f"   Health Status: {statistics['health_status']}")
    print(f"   Success Rate: {statistics['success_rate']}%")
    print(f"   Failed Runs: {statistics.get('failed_runs', 0)}")
    print(f"   Patterns Detected: {len(error_patterns)}")

    # Generate reports if requested
    if args.create_report.lower() == "true":
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

        json_report, md_report = generate_report(runs, statistics, error_patterns, args)

        # Save reports
        json_file = args.output_dir / f"workflow_analytics_report_{timestamp}.json"
        md_file = args.output_dir / f"workflow_analytics_report_{timestamp}.md"

        json_file.write_text(json.dumps(json_report, indent=2))
        md_file.write_text(md_report)

        print("\n📝 Reports generated:")
        print(f"   - {json_file}")
        print(f"   - {md_file}")

    # Set outputs for GitHub Actions
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"patterns_detected={'true' if error_patterns else 'false'}\n")
            f.write(f"has_suggestions={'true' if statistics['health_status'] != 'HEALTHY' else 'false'}\n")
            f.write(f"health_status={statistics['health_status']}\n")

    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
