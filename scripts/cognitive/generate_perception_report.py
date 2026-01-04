#!/usr/bin/env python3
"""
Cognitive Brain - Perception Report Generator
Generates human-readable reports from perception data
"""
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def generate_perception_report(input_dir: str, output_path: str) -> str:
    """
    Generate a comprehensive perception report in Markdown format.
    
    Args:
        input_dir: Directory containing perception data
        output_path: Path to save Markdown report
    
    Returns:
        Generated report as string
    """
    input_path = Path(input_dir)
    
    # Load all perception data
    git_data = {}
    pr_data = {}
    ci_data = {}
    patterns = {}
    anomalies = {}
    
    for filename, data_var in [
        ("git_data.json", "git_data"),
        ("pr_metrics.json", "pr_data"),
        ("ci_data.json", "ci_data"),
        ("patterns.json", "patterns"),
        ("anomalies.json", "anomalies")
    ]:
        file_path = input_path / filename
        if file_path.exists():
            with open(file_path) as f:
                locals()[data_var] = json.load(f)
    
    # Generate report
    report_lines = [
        "# Cognitive Brain - Perception Report",
        f"> Generated: {datetime.now().isoformat()}",
        "",
        "## Executive Summary",
        ""
    ]
    
    # Git Summary
    if git_data:
        total_commits = git_data.get("total_commits", 0)
        total_additions = git_data.get("total_additions", 0)
        total_deletions = git_data.get("total_deletions", 0)
        unique_authors = git_data.get("unique_authors", 0)
        
        report_lines.extend([
            f"**Repository Activity ({git_data.get('since_date', 'recent')}):**",
            f"- **{total_commits}** commits from **{unique_authors}** authors",
            f"- **+{total_additions}** additions, **-{total_deletions}** deletions",
            f"- Net change: **{total_additions - total_deletions:+}** lines",
            ""
        ])
    
    # PR Summary
    if pr_data.get("metrics"):
        metrics = pr_data["metrics"]
        report_lines.extend([
            f"**Pull Request Activity:**",
            f"- **{metrics.get('total_prs', 0)}** PRs ({metrics.get('merged_prs', 0)} merged, {metrics.get('open_prs', 0)} open)",
            f"- Success rate: **{metrics.get('merged_prs', 0) / max(metrics.get('total_prs', 1), 1) * 100:.1f}%**",
            f"- Average merge time: **{metrics.get('avg_merge_time_hours', 0):.1f} hours**",
            ""
        ])
    
    # CI Summary
    if ci_data.get("metrics"):
        metrics = ci_data["metrics"]
        report_lines.extend([
            f"**CI/CD Performance:**",
            f"- **{metrics.get('total_runs', 0)}** workflow runs",
            f"- Success rate: **{metrics.get('success_rate_percent', 0):.1f}%**",
            f"- Average duration: **{metrics.get('avg_duration_minutes', 0):.1f} minutes**",
            ""
        ])
    
    # Patterns Section
    if patterns.get("patterns_detected"):
        report_lines.extend([
            "## 🔍 Detected Patterns",
            "",
            f"Found **{len(patterns['patterns_detected'])}** significant patterns:",
            ""
        ])
        
        for i, pattern in enumerate(patterns["patterns_detected"], 1):
            report_lines.extend([
                f"### {i}. {pattern['pattern_type'].replace('_', ' ').title()}",
                f"**Confidence:** {pattern['confidence'] * 100:.0f}%",
                "",
                pattern['description'],
                ""
            ])
            
            # Add pattern-specific data
            if pattern['pattern_type'] == 'high_activity_files':
                report_lines.append("Top files by change frequency:")
                for file_data in pattern['data'][:5]:
                    report_lines.append(f"- `{file_data['file']}`: {file_data['change_count']} changes")
                report_lines.append("")
    
    # Anomalies Section
    if anomalies.get("anomalies_detected"):
        report_lines.extend([
            "## ⚠️ Detected Anomalies",
            "",
            f"Found **{len(anomalies['anomalies_detected'])}** anomalies:",
            ""
        ])
        
        # Group by severity
        high_severity = [a for a in anomalies["anomalies_detected"] if a["severity"] == "high"]
        medium_severity = [a for a in anomalies["anomalies_detected"] if a["severity"] == "medium"]
        low_severity = [a for a in anomalies["anomalies_detected"] if a["severity"] == "low"]
        
        if high_severity:
            report_lines.extend(["### 🔴 High Severity", ""])
            for anomaly in high_severity:
                report_lines.extend([
                    f"**{anomaly['anomaly_type'].replace('_', ' ').title()}**",
                    f"{anomaly['description']}",
                    f"*Recommendation:* {anomaly['recommendation']}",
                    ""
                ])
        
        if medium_severity:
            report_lines.extend(["### 🟡 Medium Severity", ""])
            for anomaly in medium_severity:
                report_lines.extend([
                    f"**{anomaly['anomaly_type'].replace('_', ' ').title()}**",
                    f"{anomaly['description']}",
                    f"*Recommendation:* {anomaly['recommendation']}",
                    ""
                ])
    
    # Recommendations
    report_lines.extend([
        "## 💡 Recommendations",
        ""
    ])
    
    if anomalies.get("anomalies_detected"):
        report_lines.append("Based on detected anomalies:")
        for anomaly in anomalies["anomalies_detected"]:
            report_lines.append(f"- {anomaly['recommendation']}")
        report_lines.append("")
    else:
        report_lines.append("- No immediate actions required. System operating normally.")
        report_lines.append("")
    
    # Footer
    report_lines.extend([
        "---",
        "*Generated by Cognitive Brain Perception Layer*",
        f"*Agent 1 Integration: {'Enabled' if patterns.get('agent1_integration_enabled') else 'Disabled'}*",
        f"*Agent 5 Integration: {'Enabled' if anomalies.get('agent5_integration_enabled') else 'Disabled'}*"
    ])
    
    report_text = "\n".join(report_lines)
    
    # Save report
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    print(f"✅ Generated perception report")
    print(f"   Saved to: {output_path}")
    
    return report_text


def main():
    parser = argparse.ArgumentParser(
        description="Generate perception report for cognitive brain"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input directory with perception data"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output Markdown file path"
    )
    
    args = parser.parse_args()
    
    generate_perception_report(args.input, args.output)


if __name__ == "__main__":
    main()
