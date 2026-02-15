#!/usr/bin/env python3
"""
Create comprehensive report for PR #3248 with all collected data
"""
import json
import sys

def load_workflow_runs(file_path):
    """Load workflow runs"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data.get('workflow_runs', [])

def load_commits(file_path):
    """Load commits"""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def is_failing_run(run):
    """Check if failing"""
    status = run.get('status')
    conclusion = run.get('conclusion')
    
    if status != 'completed':
        return True
    
    failing_conclusions = ['failure', 'timed_out', 'cancelled', 'action_required']
    return conclusion in failing_conclusions

def main():
    # Load all data
    workflow_runs = load_workflow_runs('/tmp/1771139202224-copilot-tool-output-n51cg0.txt')
    pr_commits = load_commits('/tmp/pr3248_commits.txt')
    pr_commit_set = set(pr_commits)
    
    # Process all workflow runs and group by commit
    commit_data = {}
    all_run_ids = []
    
    for run in workflow_runs:
        head_sha = run.get('head_sha')
        run_id = run.get('id')
        all_run_ids.append(run_id)
        
        if head_sha not in pr_commit_set:
            continue
        
        if head_sha not in commit_data:
            commit_data[head_sha] = {
                'sha': head_sha,
                'failing_checks': [],
                'all_workflow_runs': [],
                'artifacts_note': 'Artifacts require per-run API calls. Run IDs are provided for manual collection.'
            }
        
        # Add run info
        run_info = {
            'run_id': run_id,
            'name': run.get('name'),
            'status': run.get('status'),
            'conclusion': run.get('conclusion'),
            'html_url': run.get('html_url'),
            'event': run.get('event'),
            'created_at': run.get('created_at'),
            'artifacts_url': f"https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs/{run_id}/artifacts"
        }
        
        commit_data[head_sha]['all_workflow_runs'].append(run_info)
        
        if is_failing_run(run):
            commit_data[head_sha]['failing_checks'].append({
                'name': run.get('name'),
                'status': run.get('status'),
                'conclusion': run.get('conclusion'),
                'html_url': run.get('html_url'),
                'run_id': run_id
            })
    
    # Create commits list in order, only include those with failing checks
    commits_list = []
    for sha in pr_commits:
        if sha in commit_data and commit_data[sha]['failing_checks']:
            commits_list.append(commit_data[sha])
    
    # Create final output
    output = {
        'pr_number': 3248,
        'repository': 'Aries-Serpent/_codex_',
        'pr_url': 'https://github.com/Aries-Serpent/_codex_/pull/3248',
        'total_commits': len(pr_commits),
        'commits_with_failures_or_artifacts': len(commits_list),
        'commits': commits_list,
        'collection_info': {
            'method': 'GitHub MCP Server API',
            'branch': '0D_base_',
            'data_collected': 'Workflow runs and failing checks',
            'artifacts_status': 'Not collected - requires additional API calls per workflow run',
            'total_workflow_runs_analyzed': len(workflow_runs)
        },
        'manual_artifact_collection': {
            'instructions': 'Use gh CLI or GitHub API to collect artifacts',
            'command_template': 'gh api repos/Aries-Serpent/_codex_/actions/runs/{run_id}/artifacts',
            'all_run_ids': all_run_ids
        },
        'failing_criteria': {
            'status': 'status != "completed"',
            'conclusion': 'conclusion in ["failure", "timed_out", "cancelled", "action_required"]'
        }
    }
    
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
