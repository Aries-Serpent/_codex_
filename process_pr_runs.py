#!/usr/bin/env python3
"""
Process workflow runs for PR #3248 branch
"""
import json
import sys

def load_workflow_runs(file_path):
    """Load workflow runs from the MCP output file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data.get('workflow_runs', [])
    except Exception as e:
        print(f"Error loading workflow runs: {e}", file=sys.stderr)
        return []

def load_commits(file_path):
    """Load commit list"""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error loading commits: {e}", file=sys.stderr)
        return []

def is_failing_run(run):
    """Check if a workflow run is failing"""
    status = run.get('status')
    conclusion = run.get('conclusion')
    
    # Not completed
    if status != 'completed':
        return True
    
    # Failed conclusion
    failing_conclusions = ['failure', 'timed_out', 'cancelled', 'action_required']
    if conclusion in failing_conclusions:
        return True
    
    return False

def main():
    # Load data
    workflow_runs = load_workflow_runs('/tmp/1771139202224-copilot-tool-output-n51cg0.txt')
    pr_commits = load_commits('/tmp/pr3248_commits.txt')
    
    print(f"Loaded {len(workflow_runs)} workflow runs from PR branch", file=sys.stderr)
    print(f"Loaded {len(pr_commits)} PR commits", file=sys.stderr)
    
    # Create a set of PR commit SHAs for fast lookup
    pr_commit_set = set(pr_commits)
    
    # Group runs by commit SHA
    commit_data = {}
    failing_count = 0
    
    for run in workflow_runs:
        head_sha = run.get('head_sha')
        
        # Only process runs for commits in our PR
        if head_sha not in pr_commit_set:
            continue
        
        # Initialize commit data if needed
        if head_sha not in commit_data:
            commit_data[head_sha] = {
                'sha': head_sha,
                'failing_checks': [],
                'workflow_runs_summary': {
                    'total': 0,
                    'passing': 0,
                    'failing': 0
                }
            }
        
        commit_data[head_sha]['workflow_runs_summary']['total'] += 1
        
        # Check if this run is failing
        if is_failing_run(run):
            failing_count += 1
            commit_data[head_sha]['workflow_runs_summary']['failing'] += 1
            commit_data[head_sha]['failing_checks'].append({
                'name': run.get('name'),
                'status': run.get('status'),
                'conclusion': run.get('conclusion'),
                'html_url': run.get('html_url'),
                'run_id': run.get('id'),
                'event': run.get('event'),
                'created_at': run.get('created_at'),
                'updated_at': run.get('updated_at')
            })
        else:
            commit_data[head_sha]['workflow_runs_summary']['passing'] += 1
    
    print(f"Found {failing_count} failing workflow runs", file=sys.stderr)
    
    # Convert to list, maintaining commit order from PR
    commits_list = []
    for sha in pr_commits:
        if sha in commit_data:
            # Only include if has failing checks or we want all
            if commit_data[sha]['failing_checks']:
                commits_list.append(commit_data[sha])
    
    print(f"Commits with failures: {len(commits_list)}", file=sys.stderr)
    
    # Create output
    output = {
        'pr_number': 3248,
        'repository': 'Aries-Serpent/_codex_',
        'total_commits': len(pr_commits),
        'commits_with_failures_or_artifacts': len(commits_list),
        'total_failing_checks': failing_count,
        'commits': commits_list,
        'notes': [
            'This report includes failing workflow runs as check runs',
            'Artifacts require additional API calls per workflow run and are not included',
            'Data collected from GitHub MCP Server for branch: 0D_base_',
            'Failing criteria: status != completed OR conclusion in [failure, timed_out, cancelled, action_required]'
        ]
    }
    
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
