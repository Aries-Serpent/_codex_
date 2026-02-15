#!/usr/bin/env python3
"""
Collect failing check runs and artifacts for all commits in PR #3248
"""
import json
import subprocess
import sys
from typing import List, Dict, Any

def run_gh_api(endpoint: str) -> Any:
    """Run gh api command and return JSON response"""
    try:
        result = subprocess.run(
            ['gh', 'api', endpoint],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error fetching {endpoint}: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Exception fetching {endpoint}: {e}", file=sys.stderr)
        return None

def get_pr_commits(owner: str, repo: str, pr_number: int) -> List[str]:
    """Get all commit SHAs from a PR"""
    commits = []
    page = 1
    per_page = 100
    
    while True:
        endpoint = f"repos/{owner}/{repo}/pulls/{pr_number}/commits?per_page={per_page}&page={page}"
        data = run_gh_api(endpoint)
        
        if not data or len(data) == 0:
            break
            
        for commit in data:
            commits.append(commit['sha'])
        
        if len(data) < per_page:
            break
        page += 1
    
    return commits

def get_check_runs(owner: str, repo: str, ref: str) -> List[Dict[str, Any]]:
    """Get check runs for a commit"""
    endpoint = f"repos/{owner}/{repo}/commits/{ref}/check-runs"
    data = run_gh_api(endpoint)
    
    if not data or 'check_runs' not in data:
        return []
    
    return data['check_runs']

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

def get_workflow_runs(owner: str, repo: str, ref: str) -> List[Dict[str, Any]]:
    """Get workflow runs for a commit"""
    endpoint = f"repos/{owner}/{repo}/actions/runs?head_sha={ref}"
    data = run_gh_api(endpoint)
    
    if not data or 'workflow_runs' not in data:
        return []
    
    return data['workflow_runs']

def get_workflow_artifacts(owner: str, repo: str, run_id: int) -> List[Dict[str, Any]]:
    """Get artifacts for a workflow run"""
    endpoint = f"repos/{owner}/{repo}/actions/runs/{run_id}/artifacts"
    data = run_gh_api(endpoint)
    
    if not data or 'artifacts' not in data:
        return []
    
    return data['artifacts']

def process_commit(owner: str, repo: str, sha: str) -> Dict[str, Any]:
    """Process a single commit and collect its failing checks and artifacts"""
    print(f"Processing commit {sha}...", file=sys.stderr)
    
    commit_data = {
        'sha': sha,
        'failing_checks': [],
        'artifacts': []
    }
    
    # Get check runs
    check_runs = get_check_runs(owner, repo, sha)
    for check in check_runs:
        if is_failing_check(check):
            commit_data['failing_checks'].append({
                'name': check.get('name'),
                'status': check.get('status'),
                'conclusion': check.get('conclusion'),
                'html_url': check.get('html_url')
            })
    
    # Get workflow runs and their artifacts
    workflow_runs = get_workflow_runs(owner, repo, sha)
    for run in workflow_runs:
        run_id = run.get('id')
        if run_id:
            artifacts = get_workflow_artifacts(owner, repo, run_id)
            for artifact in artifacts:
                commit_data['artifacts'].append({
                    'name': artifact.get('name'),
                    'size_in_bytes': artifact.get('size_in_bytes'),
                    'archive_download_url': artifact.get('archive_download_url'),
                    'workflow_run_id': run_id,
                    'workflow_name': run.get('name')
                })
    
    # Only return if has failing checks or artifacts
    if commit_data['failing_checks'] or commit_data['artifacts']:
        return commit_data
    
    return None

def main():
    owner = "Aries-Serpent"
    repo = "_codex_"
    pr_number = 3248
    
    print(f"Collecting data for PR #{pr_number}...", file=sys.stderr)
    
    # Get all commits
    commits = get_pr_commits(owner, repo, pr_number)
    print(f"Found {len(commits)} commits", file=sys.stderr)
    
    # Process each commit
    results = []
    for i, sha in enumerate(commits, 1):
        print(f"[{i}/{len(commits)}] ", end='', file=sys.stderr)
        commit_data = process_commit(owner, repo, sha)
        if commit_data:
            results.append(commit_data)
    
    # Output results
    output = {
        'pr_number': pr_number,
        'repository': f"{owner}/{repo}",
        'total_commits': len(commits),
        'commits_with_failures_or_artifacts': len(results),
        'commits': results
    }
    
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
