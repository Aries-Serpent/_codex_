#!/usr/bin/env python3
"""
Collect artifacts for all workflow runs in the PR
"""
import json
import sys

def load_workflow_runs(file_path):
    """Load workflow runs"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data.get('workflow_runs', [])

def main():
    runs = load_workflow_runs('/tmp/1771139202224-copilot-tool-output-n51cg0.txt')
    
    # Get unique run IDs
    run_ids = [run['id'] for run in runs]
    
    print(f"Found {len(run_ids)} workflow runs", file=sys.stderr)
    print("Run IDs to query for artifacts:")
    for run_id in run_ids[:10]:  # First 10
        print(run_id)

if __name__ == '__main__':
    main()
