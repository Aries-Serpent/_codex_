#!/usr/bin/env python3
"""
Collect failing check runs and artifacts for commits in PR #3248
Working around API rate limits by using a subset approach
"""
import json
import subprocess
import sys
import time
from typing import List, Dict, Any

def run_command(cmd: List[str]) -> tuple:
    """Run a command and return stdout, stderr, return code"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def get_pr_commits_git() -> List[str]:
    """Get commits from git log"""
    # Get the PR branch commits
    stdout, stderr, rc = run_command(['git', 'log', 'pr-3248', '--format=%H', '-n', '100'])
    if rc != 0:
        print(f"Error getting commits: {stderr}", file=sys.stderr)
        return []
    
    commits = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
    return commits

def get_check_runs_for_commit(sha: str) -> Dict[str, Any]:
    """Get check runs for a specific commit using gh api"""
    print(f"  Fetching check runs for {sha[:7]}...", file=sys.stderr)
    
    # Try to get check runs
    stdout, stderr, rc = run_command([
        'gh', 'api', 
        f'repos/Aries-Serpent/_codex_/commits/{sha}/check-runs',
        '--jq', '.'
    ])
    
    if rc != 0:
        print(f"    Error: {stderr.strip()}", file=sys.stderr)
        return None
    
    try:
        data = json.loads(stdout)
        return data
    except json.JSONDecodeError as e:
        print(f"    JSON Error: {e}", file=sys.stderr)
        return None

def get_workflow_runs_for_commit(sha: str) -> List[Dict[str, Any]]:
    """Get workflow runs for a specific commit"""
    print(f"  Fetching workflow runs for {sha[:7]}...", file=sys.stderr)
    
    stdout, stderr, rc = run_command([
        'gh', 'api',
        f'repos/Aries-Serpent/_codex_/actions/runs?head_sha={sha}',
        '--paginate',
        '--jq', '.workflow_runs'
    ])
    
    if rc != 0:
        print(f"    Error: {stderr.strip()}", file=sys.stderr)
        return []
    
    try:
        # Handle paginated results
        runs = []
        for line in stdout.strip().split('\n'):
            if line.strip():
                data = json.loads(line)
                if isinstance(data, list):
                    runs.extend(data)
                else:
                    runs.append(data)
        return runs
    except json.JSONDecodeError as e:
        print(f"    JSON Error: {e}", file=sys.stderr)
        return []

def get_artifacts_for_run(run_id: int) -> List[Dict[str, Any]]:
    """Get artifacts for a workflow run"""
    stdout, stderr, rc = run_command([
        'gh', 'api',
        f'repos/Aries-Serpent/_codex_/actions/runs/{run_id}/artifacts',
        '--jq', '.artifacts'
    ])
    
    if rc != 0:
        return []
    
    try:
        data = json.loads(stdout)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

def is_failing_check(check_run: Dict[str, Any]) -> bool:
    """Determine if a check run is failing"""
    status = check_run.get('status')
    conclusion = check_run.get('conclusion')
    
    # Check if not completed
    if status != 'completed':
        return True
    
    # Check if conclusion indicates failure
    failing_conclusions = ['failure', 'timed_out', 'cancelled', 'action_required']
    if conclusion in failing_conclusions:
        return True
    
    return False

def process_commit(sha: str) -> Dict[str, Any]:
    """Process a single commit"""
    commit_data = {
        'sha': sha,
        'failing_checks': [],
        'artifacts': []
    }
    
    # Get check runs
    check_data = get_check_runs_for_commit(sha)
    if check_data and 'check_runs' in check_data:
        for check in check_data['check_runs']:
            if is_failing_check(check):
                commit_data['failing_checks'].append({
                    'name': check.get('name'),
                    'status': check.get('status'),
                    'conclusion': check.get('conclusion'),
                    'html_url': check.get('html_url')
                })
    
    # Get workflow runs and artifacts
    workflow_runs = get_workflow_runs_for_commit(sha)
    for run in workflow_runs:
        run_id = run.get('id')
        if run_id:
            artifacts = get_artifacts_for_run(run_id)
            for artifact in artifacts:
                commit_data['artifacts'].append({
                    'name': artifact.get('name'),
                    'size_in_bytes': artifact.get('size_in_bytes'),
                    'archive_download_url': artifact.get('archive_download_url'),
                    'workflow_run_id': run_id,
                    'workflow_name': run.get('name')
                })
    
    # Add a small delay to avoid rate limiting
    time.sleep(0.5)
    
    # Only return if has failing checks or artifacts
    if commit_data['failing_checks'] or commit_data['artifacts']:
        return commit_data
    
    return None

def main():
    owner = "Aries-Serpent"
    repo = "_codex_"
    pr_number = 3248
    
    print(f"Collecting data for PR #{pr_number}...", file=sys.stderr)
    
    # Get commits from git
    commits = get_pr_commits_git()
    print(f"Found {len(commits)} commits in local git history", file=sys.stderr)
    
    # Process only the most recent commits to avoid rate limiting
    # Let's process up to 10 commits
    max_commits = min(10, len(commits))
    commits_to_process = commits[:max_commits]
    
    print(f"Processing {len(commits_to_process)} commits...", file=sys.stderr)
    
    results = []
    for i, sha in enumerate(commits_to_process, 1):
        print(f"\n[{i}/{len(commits_to_process)}] Processing {sha[:7]}...", file=sys.stderr)
        commit_data = process_commit(sha)
        if commit_data:
            results.append(commit_data)
            print(f"  -> Found {len(commit_data['failing_checks'])} failing checks, {len(commit_data['artifacts'])} artifacts", file=sys.stderr)
    
    # Output results
    output = {
        'pr_number': pr_number,
        'repository': f"{owner}/{repo}",
        'total_commits_in_pr': len(commits),
        'commits_processed': len(commits_to_process),
        'commits_with_failures_or_artifacts': len(results),
        'commits': results
    }
    
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
