#!/usr/bin/env python3
"""
Generate Performance Report
Phase 4D Planset 007 - Performance monitoring report generation

Generates reports in multiple formats:
- Markdown for PR comments
- JSON for storage
- HTML for dashboards
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def load_json_safe(path: Path) -> dict[str, Any]:
    """Load JSON file with error handling"""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}", file=sys.stderr)
        return {}


def generate_markdown_report(
    metrics: dict[str, Any],
    regressions: dict[str, Any],
) -> str:
    """Generate markdown performance report"""
    lines = [
        "# ⚡ Performance Monitoring Report",
        "",
        f"**Report Date**: {datetime.now().isoformat()}",
        "",
    ]
    
    # Metrics summary
    if metrics.get("system"):
        lines.append("## System Metrics")
        lines.append("")
        system = metrics["system"]
        lines.append(f"- **Timestamp**: {system.get('timestamp', 'N/A')}")
        lines.append(f"- **Hostname**: {system.get('hostname', 'N/A')}")
        
        if "memory" in system:
            memory = system["memory"]
            total_gb = memory["total_bytes"] / (1024**3)
            used_gb = memory["used_bytes"] / (1024**3)
            lines.append(f"- **Memory**: {used_gb:.2f} GB / {total_gb:.2f} GB")
        lines.append("")
    
    # Repository metrics
    if metrics.get("repository"):
        lines.append("## Repository Metrics")
        lines.append("")
        repo = metrics["repository"]
        lines.append(f"- **Size**: {repo.get('repo_size', 'N/A')}")
        lines.append(f"- **Python Files**: {repo.get('python_files', 'N/A')}")
        lines.append("")
    
    # Test metrics
    if metrics.get("metrics", {}).get("tests"):
        lines.append("## Test Metrics")
        lines.append("")
        tests = metrics["metrics"]["tests"]
        lines.append(f"- **Test Files**: {tests.get('test_files', 0)}")
        lines.append(f"- **Total Tests**: {tests.get('total_tests', 0)}")
        lines.append("")
    
    # Regressions
    if regressions.get("regressions"):
        lines.append("## Performance Regressions")
        lines.append("")
        lines.append("| Metric | Change | Severity |")
        lines.append("|--------|--------|----------|")
        
        for regression in regressions["regressions"]:
            metric = regression.get("metric", "N/A")
            change = regression.get("percent_change", 0)
            severity = regression.get("severity", "UNKNOWN")
            lines.append(f"| {metric} | {change:+.1%} | {severity} |")
        lines.append("")
    else:
        lines.append("## Performance Status")
        lines.append("")
        lines.append("✅ No performance regressions detected")
        lines.append("")
    
    return "\n".join(lines)


def generate_json_report(
    metrics: dict[str, Any],
    regressions: dict[str, Any],
) -> dict[str, Any]:
    """Generate JSON performance report"""
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "regressions": regressions,
        "summary": {
            "total_regressions": regressions.get("regressions_detected", 0),
            "metrics_analyzed": regressions.get("total_metrics_analyzed", 0),
        },
    }


def main() -> int:
    """Generate performance report"""
    parser = argparse.ArgumentParser(
        description="Generate performance report"
    )
    parser.add_argument(
        "--metrics",
        type=Path,
        required=True,
        help="Metrics JSON file",
    )
    parser.add_argument(
        "--regressions",
        type=Path,
        required=True,
        help="Regression report JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output file",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "html"],
        default="markdown",
        help="Output format",
    )
    
    args = parser.parse_args()
    
    # Load data
    metrics = load_json_safe(args.metrics)
    regressions = load_json_safe(args.regressions)
    
    # Generate report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    if args.format == "markdown":
        content = generate_markdown_report(metrics, regressions)
        with open(args.output, "w") as f:
            f.write(content)
    
    elif args.format == "json":
        content = generate_json_report(metrics, regressions)
        with open(args.output, "w") as f:
            json.dump(content, f, indent=2)
    
    elif args.format == "html":
        # Simple HTML wrapper
        markdown_report = generate_markdown_report(metrics, regressions)
        html = f"""
        <html>
        <head>
            <title>Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                pre {{ background-color: #f0f0f0; padding: 10px; }}
            </style>
        </head>
        <body>
            <pre>{markdown_report}</pre>
        </body>
        </html>
        """
        with open(args.output, "w") as f:
            f.write(html)
    
    print(f"✅ Report generated: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
