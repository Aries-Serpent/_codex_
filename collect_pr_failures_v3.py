#!/usr/bin/env python3
"""
Collect failing check runs info for PR #3248 HEAD commit
Since we have API access limitations, we'll focus on the HEAD commit
"""
import json
import sys

def main():
    owner = "Aries-Serpent"
    repo = "_codex_"
    pr_number = 3248
    
    # The HEAD SHA from the PR
    head_sha = "95bcc8abc008d588e86e8283e2eba669dee556cf"
    
    # Manual data collection based on what we know
    # The user is asking for data that requires GitHub API access
    # which we don't have in this environment due to rate limiting
    
    output = {
        'pr_number': pr_number,
        'repository': f"{owner}/{repo}",
        'head_sha': head_sha,
        'note': 'Due to API rate limiting and authentication issues, automated collection is not possible. Please use the GitHub UI or authenticated gh CLI to collect this data.',
        'manual_instructions': {
            'step_1': f'Get commits: gh api repos/{owner}/{repo}/pulls/{pr_number}/commits',
            'step_2': f'For each commit SHA, get check runs: gh api repos/{owner}/{repo}/commits/SHA/check-runs',
            'step_3': f'For each commit SHA, get workflow runs: gh api repos/{owner}/{repo}/actions/runs?head_sha=SHA',
            'step_4': f'For each workflow run ID, get artifacts: gh api repos/{owner}/{repo}/actions/runs/RUN_ID/artifacts'
        },
        'alternative_approach': 'Use GitHub UI: Navigate to the PR page, click on "Checks" tab to see all failing checks',
        'commits': []
    }
    
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
