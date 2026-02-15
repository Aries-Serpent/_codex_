#!/usr/bin/env python3
"""
Collect failing workflow runs data using MCP GitHub server data
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
    workflow_runs = load_workflow_runs('/tmp/1771139172923-copilot-tool-output-vzbrum.txt')
    pr_commits = load_commits('/tmp/pr3248_commits.txt')
    
    print(f"Loaded {len(workflow_runs)} workflow runs", file=sys.stderr)
    print(f"Loaded {len(pr_commits)} PR commits", file=sys.stderr)
    
    # Create a set of PR commit SHAs for fast lookup
    pr_commit_set = set(pr_commits)
    
    # Group runs by commit SHA
    commit_data = {}
    
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
                'workflow_runs': [],
                'artifacts': []
            }
        
        # Check if this run is failing
        if is_failing_run(run):
            commit_data[head_sha]['failing_checks'].append({
                'name': run.get('name'),
                'status': run.get('status'),
                'conclusion': run.get('conclusion'),
                'html_url': run.get('html_url'),
                'run_id': run.get('id')
            })
        
        # Add to workflow runs list
        commit_data[head_sha]['workflow_runs'].append({
            'id': run.get('id'),
            'name': run.get('name'),
            'status': run.get('status'),
            'conclusion': run.get('conclusion')
        })
    
    # Filter to only commits with failures
    filtered_commits = []
    for sha in pr_commits:  # Maintain order
        if sha in commit_data and commit_data[sha]['failing_checks']:
            filtered_commits.append(commit_data[sha])
    
    # Create output
    output = {
        'pr_number': 3248,
        'repository': 'Aries-Serpent/_codex_',
        'total_commits': len(pr_commits),
        'commits_with_failures_or_artifacts': len(filtered_commits),
        'commits': filtered_commits,
        'note': 'Artifacts information requires additional API calls per workflow run. This report includes failing checks from workflow runs.',
        'collection_method': 'GitHub MCP Server (partial data)'
    }
    
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
