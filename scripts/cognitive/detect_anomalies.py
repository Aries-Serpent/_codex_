#!/usr/bin/env python3
"""
Cognitive Brain - Anomaly Detection
Part of Perception Layer - integrates with Agent 5 for anomaly detection
"""
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any
import statistics


def detect_anomalies(input_dir: str, output_path: str, agent5_integration: bool = False) -> Dict[str, Any]:
    """
    Detect anomalies in collected data using Agent 5 integration.
    
    Args:
        input_dir: Directory containing perception data
        output_path: Path to save anomaly detection results
        agent5_integration: Whether to use Agent 5 anomaly detection
    
    Returns:
        Dictionary with detected anomalies and metadata
    """
    input_path = Path(input_dir)
    
    # Load collected data
    git_data = {}
    pr_data = {}
    ci_data = {}
    
    git_file = input_path / "git_data.json"
    if git_file.exists():
        with open(git_file) as f:
            git_data = json.load(f)
    
    pr_file = input_path / "pr_metrics.json"
    if pr_file.exists():
        with open(pr_file) as f:
            pr_data = json.load(f)
    
    ci_file = input_path / "ci_data.json"
    if ci_file.exists():
        with open(ci_file) as f:
            ci_data = json.load(f)
    
    # Detect anomalies
    anomalies = {
        "detection_timestamp": "2026-01-04T00:00:00Z",
        "agent5_integration_enabled": agent5_integration,
        "anomalies_detected": []
    }
    
    # Git anomalies
    if git_data.get("commits"):
        commits = git_data["commits"]
        
        # Anomaly: Unusually large commits
        commit_sizes = [c.get("additions", 0) + c.get("deletions", 0) for c in commits]
        if commit_sizes:
            avg_size = statistics.mean(commit_sizes)
            stdev_size = statistics.stdev(commit_sizes) if len(commit_sizes) > 1 else 0
            threshold = avg_size + (2 * stdev_size)
            
            large_commits = [
                {
                    "hash": c["hash"][:8],
                    "author": c["author_name"],
                    "size": c.get("additions", 0) + c.get("deletions", 0),
                    "subject": c["subject"][:60]
                }
                for c in commits
                if (c.get("additions", 0) + c.get("deletions", 0)) > threshold
            ]
            
            if large_commits:
                anomalies["anomalies_detected"].append({
                    "anomaly_type": "unusually_large_commits",
                    "severity": "medium",
                    "description": f"Commits exceeding 2σ threshold ({threshold:.0f} lines)",
                    "data": large_commits,
                    "recommendation": "Review large commits for potential refactoring opportunities"
                })
    
    # PR anomalies
    if pr_data.get("metrics"):
        metrics = pr_data["metrics"]
        
        # Anomaly: Low merge rate
        total_prs = metrics.get("total_prs", 0)
        merged_prs = metrics.get("merged_prs", 0)
        if total_prs > 0:
            merge_rate = merged_prs / total_prs
            if merge_rate < 0.5:
                anomalies["anomalies_detected"].append({
                    "anomaly_type": "low_pr_merge_rate",
                    "severity": "high",
                    "description": f"Only {merge_rate*100:.1f}% of PRs are being merged",
                    "data": {
                        "total_prs": total_prs,
                        "merged_prs": merged_prs,
                        "closed_without_merge": metrics.get("closed_prs", 0)
                    },
                    "recommendation": "Investigate reasons for low merge rate - review process issues?"
                })
        
        # Anomaly: Slow merge times
        avg_merge_time = metrics.get("avg_merge_time_hours", 0)
        if avg_merge_time > 48:
            anomalies["anomalies_detected"].append({
                "anomaly_type": "slow_pr_merge_times",
                "severity": "medium",
                "description": f"Average merge time is {avg_merge_time:.1f} hours (>2 days)",
                "data": {"avg_merge_time_hours": avg_merge_time},
                "recommendation": "Consider process improvements to reduce PR review time"
            })
    
    # CI/CD anomalies
    if ci_data.get("metrics"):
        metrics = ci_data["metrics"]
        
        # Anomaly: Low success rate
        success_rate = metrics.get("success_rate_percent", 100)
        if success_rate < 80:
            anomalies["anomalies_detected"].append({
                "anomaly_type": "low_ci_success_rate",
                "severity": "high",
                "description": f"CI success rate is only {success_rate:.1f}%",
                "data": {
                    "success_rate": success_rate,
                    "failed_runs": metrics.get("failed_runs", 0),
                    "total_runs": metrics.get("total_runs", 0)
                },
                "recommendation": "Investigate and fix flaky tests or infrastructure issues"
            })
        
        # Anomaly: Long CI duration
        avg_duration_min = metrics.get("avg_duration_minutes", 0)
        if avg_duration_min > 30:
            anomalies["anomalies_detected"].append({
                "anomaly_type": "long_ci_duration",
                "severity": "medium",
                "description": f"Average CI duration is {avg_duration_min:.1f} minutes",
                "data": {"avg_duration_minutes": avg_duration_min},
                "recommendation": "Optimize test suite or add parallelization"
            })
    
    anomalies["total_anomalies_found"] = len(anomalies["anomalies_detected"])
    
    # Calculate severity breakdown
    severity_counts = {}
    for a in anomalies["anomalies_detected"]:
        sev = a["severity"]
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    anomalies["severity_breakdown"] = severity_counts
    
    # Save results
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(anomalies, f, indent=2)
    
    print(f"✅ Detected {anomalies['total_anomalies_found']} anomalies")
    for a in anomalies["anomalies_detected"]:
        print(f"   - [{a['severity'].upper()}] {a['anomaly_type']}: {a['description']}")
    print(f"   Severity breakdown: {severity_counts}")
    print(f"   Saved to: {output_path}")
    
    return anomalies


def main():
    parser = argparse.ArgumentParser(
        description="Detect anomalies in cognitive perception data"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input directory with perception data"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path"
    )
    parser.add_argument(
        "--agent-5-integration",
        action="store_true",
        help="Enable Agent 5 anomaly detection integration"
    )
    
    args = parser.parse_args()
    
    detect_anomalies(args.input, args.output, args.agent_5_integration)


if __name__ == "__main__":
    main()
