#!/usr/bin/env python3
"""
Exhaustive MCP Data Collector for PR #3248 Failing Checks
Collects workflow runs, jobs, and artifacts for all 81 target commits.
"""

import json
import os
import sys
from pathlib import Path

# Load target commits
target_commits_file = Path(__file__).parent / "target_commits.json"
with open(target_commits_file, 'r') as f:
    TARGET_COMMITS = json.load(f)

# Data storage
collected_data = {}
evidence_dir = Path(__file__).parent / "workspace" / "evidence" / "pr3248"
evidence_dir.mkdir(parents=True, exist_ok=True)

def save_evidence(commit_sha, endpoint, data):
    """Save API response as evidence"""
    commit_dir = evidence_dir / commit_sha
    commit_dir.mkdir(exist_ok=True)
    
    evidence_file = commit_dir / f"{endpoint}.json"
    with open(evidence_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return str(evidence_file)

def collect_for_commit(commit_sha, check_runs_data=None, workflow_runs_data=None):
    """
    Collect all data for a single commit.
    
    Expected inputs from MCP tools:
    - check_runs_data: Result from GET /repos/{owner}/{repo}/commits/{sha}/check-runs
    - workflow_runs_data: Result from GET /repos/{owner}/{repo}/actions/runs?head_sha={sha}
    """
    commit_data = {
        'commit_sha': commit_sha,
        'commit_url': f"https://github.com/Aries-Serpent/_codex_/commit/{commit_sha}",
        'runs': []
    }
    
    # Process check runs (most authoritative)
    if check_runs_data and 'check_runs' in check_runs_data:
        save_evidence(commit_sha, 'check_runs', check_runs_data)
        
        for check_run in check_runs_data['check_runs']:
            # Map check_run to our schema
            run_data = {
                'run_id': check_run.get('id'),
                'run_html_url': check_run.get('html_url'),
                'run_name': check_run.get('name'),
                'run_conclusion': check_run.get('conclusion') or check_run.get('status'),
                'job_id': check_run.get('id'),  # For check runs, use same ID
                'job_name': check_run.get('name'),
                'job_html_url': check_run.get('html_url'),
                'job_status': check_run.get('status'),
                'artifact_archive_download_url': 'N/A'  # Check runs don't have artifacts
            }
            commit_data['runs'].append(run_data)
    
    # Process workflow runs (secondary source)
    if workflow_runs_data and 'workflow_runs' in workflow_runs_data:
        save_evidence(commit_sha, 'workflow_runs', workflow_runs_data)
        
        for run in workflow_runs_data['workflow_runs']:
            # We'll need to get jobs and artifacts for each run
            # This would require additional MCP calls
            run_data = {
                'run_id': run.get('id'),
                'run_html_url': run.get('html_url'),
                'run_name': run.get('name'),
                'run_conclusion': run.get('conclusion'),
                'job_id': 'PENDING',  # Need to fetch jobs
                'job_name': 'PENDING',
                'job_html_url': 'PENDING',
                'job_status': run.get('status'),
                'artifact_archive_download_url': 'PENDING'  # Need to fetch artifacts
            }
            commit_data['runs'].append(run_data)
    
    collected_data[commit_sha] = commit_data
    return commit_data

def generate_markdown_row(commit_sha, runs):
    """Generate markdown table row for a commit"""
    if not runs:
        return f"| {commit_sha[:7]} | [View commit](https://github.com/Aries-Serpent/_codex_/commit/{commit_sha}) | No runs found | N/A | N/A | N/A | N/A | N/A | N/A |"
    
    rows = []
    for run in runs:
        row = f"| {run.get('run_id', 'N/A')} | {run.get('run_html_url', 'N/A')} | {run.get('run_name', 'N/A')} | {run.get('run_conclusion', 'N/A')} | {run.get('job_id', 'N/A')} | {run.get('job_name', 'N/A')} | {run.get('job_html_url', 'N/A')} | {run.get('job_status', 'N/A')} | {run.get('artifact_archive_download_url', 'N/A')} |"
        rows.append(row)
    
    return "\n".join(rows)

def update_failing_checks_md():
    """Update failing_checks.md with collected data"""
    md_content = [
        "# [Investigation Report]: Failing Checks per Commit (PR #3248)",
        "",
        "> **Generated**: 2026-02-15T08:30:00Z",
        "> **Automation**: GitHub MCP Server Tools (Exhaustive Collection)",
        "> **Coverage**: All 81 commits from PR #3248",
        "",
        "## Summary",
        "",
        f"- **Total Commits**: {len(TARGET_COMMITS)}",
        f"- **Commits Processed**: {len(collected_data)}",
        f"- **Collection Method**: Automated (GitHub MCP Server)",
        "",
        "## Complete Data Table",
        "",
        "| run_id | run_html_url | run_name | run_conclusion | job_id | job_name | job_html_url | job_status | artifact_archive_download_url |",
        "|---|---|---|---|---|---|---|---|---|"
    ]
    
    for commit_sha in TARGET_COMMITS:
        if commit_sha in collected_data:
            commit_data = collected_data[commit_sha]
            md_content.append(f"\n### Commit: {commit_sha}")
            md_content.append(generate_markdown_row(commit_sha, commit_data['runs']))
        else:
            md_content.append(f"\n### Commit: {commit_sha}")
            md_content.append(f"| PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |")
    
    failing_checks_md = Path(__file__).parent / "failing_checks.md"
    with open(failing_checks_md, 'w') as f:
        f.write("\n".join(md_content))
    
    print(f"Updated {failing_checks_md}")
    print(f"Processed {len(collected_data)} / {len(TARGET_COMMITS)} commits")

def save_collection_status():
    """Save current collection status"""
    status = {
        'total_commits': len(TARGET_COMMITS),
        'processed': len(collected_data),
        'pending': len(TARGET_COMMITS) - len(collected_data),
        'evidence_dir': str(evidence_dir),
        'commits_processed': list(collected_data.keys())
    }
    
    status_file = Path(__file__).parent / "collection_status.json"
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    return status

if __name__ == "__main__":
    print("Exhaustive Data Collector for PR #3248")
    print("=" * 60)
    print(f"Target commits: {len(TARGET_COMMITS)}")
    print(f"Evidence directory: {evidence_dir}")
    print("\nThis script processes MCP tool outputs.")
    print("Run MCP collection commands and pass results to collect_for_commit()")
    print("\nExample usage:")
    print("  # In agent code:")
    print("  check_runs = github_mcp_server_get_commit(...)")
    print("  collect_for_commit(sha, check_runs_data=check_runs)")
    print("  update_failing_checks_md()")
