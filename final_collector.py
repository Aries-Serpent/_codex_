#!/usr/bin/env python3
"""
Final attempt to collect PR #3248 data using available information
"""
import json
import sys

def create_empty_report():
    """Create a report with the expected structure but empty data"""
    
    # Load commit list
    try:
        with open('/tmp/pr3248_commits.txt', 'r') as f:
            commits = [line.strip() for line in f if line.strip()]
    except:
        commits = []
    
    output = {
        "pr_number": 3248,
        "repository": "Aries-Serpent/_codex_",
        "total_commits": len(commits),
        "commits_with_failures_or_artifacts": 0,
        "collection_status": "incomplete",
        "reason": "GitHub API authentication failed (HTTP 403). GITHUB_TOKEN is invalid or rate limited.",
        "all_commit_shas": commits,
        "commits": [],
        "instructions": {
            "manual_collection": "Use authenticated gh CLI or GitHub UI to collect check runs and artifacts",
            "api_endpoints": {
                "check_runs": "GET /repos/Aries-Serpent/_codex_/commits/{sha}/check-runs",
                "workflow_runs": "GET /repos/Aries-Serpent/_codex_/actions/runs?head_sha={sha}",
                "artifacts": "GET /repos/Aries-Serpent/_codex_/actions/runs/{run_id}/artifacts"
            },
            "failing_criteria": {
                "status": "status != 'completed' OR conclusion in ['failure', 'timed_out', 'cancelled', 'action_required']"
            }
        }
    }
    
    return output

def main():
    report = create_empty_report()
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
