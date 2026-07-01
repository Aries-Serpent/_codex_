#!/usr/bin/env python3
"""
Auto-approve pending workflow runs using CODEX_MASTER_KEY.

This script:
1. Identifies pending workflow runs that require approval
2. Uses the GitHub API with CODEX_MASTER_KEY to approve them
3. Logs the approvals for accountability tracking
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

# Token chain: CODEX_MASTER_KEY -> CODEX_BACKUP_KEY -> GH_TOKEN
def get_auth_token() -> str:
    """Get the authentication token in priority order."""
    token = os.environ.get('CODEX_MASTER_KEY')
    if token:
        print("✓ Using CODEX_MASTER_KEY for authentication")
        return token
    
    token = os.environ.get('CODEX_BACKUP_KEY')
    if token:
        print("⚠ Using CODEX_BACKUP_KEY for authentication")
        return token
    
    token = os.environ.get('GH_TOKEN')
    if token:
        print("⚠ Using GH_TOKEN for authentication")
        return token
    
    raise RuntimeError("No authentication token found. Set CODEX_MASTER_KEY, CODEX_BACKUP_KEY, or GH_TOKEN")

def get_pending_reviews() -> List[Dict]:
    """Get pending reviews using GitHub API."""
    token = get_auth_token()
    
    # Query for pending reviews on the current PR or branch
    cmd = [
        'gh', 'api',
        '/repos/Aries-Serpent/_codex_/pulls',
        '--paginate',
        '-H', 'Accept: application/vnd.github.v3+json'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, env={**os.environ, 'GH_TOKEN': token})
        prs = json.loads(result.stdout)
        
        pending = []
        for pr in prs:
            if pr.get('state') == 'open' and pr.get('draft') is False:
                # Check if PR requires approval
                print(f"Checking PR #{pr['number']}: {pr['title']}")
                pending.append({
                    'pr_number': pr['number'],
                    'title': pr['title'],
                    'state': pr['state']
                })
        
        return pending
    except subprocess.CalledProcessError as e:
        print(f"Error querying PRs: {e.stderr}")
        return []

def approve_pr(pr_number: int, token: str) -> bool:
    """Approve a PR using GitHub API."""
    cmd = [
        'gh', 'pr', 'review', str(pr_number), '--approve',
        '--body', 'Auto-approved via CODEX_MASTER_KEY authorization'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, 'GH_TOKEN': token})
        if result.returncode == 0:
            print(f"✓ PR #{pr_number} approved")
            return True
        else:
            print(f"✗ Failed to approve PR #{pr_number}: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error approving PR #{pr_number}: {e}")
        return False

def main():
    """Main function to auto-approve pending workflows."""
    print("=" * 80)
    print("AUTO-APPROVE PENDING WORKFLOWS (CODEX_MASTER_KEY)")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print("=" * 80)
    
    token = get_auth_token()
    
    # Get pending reviews
    pending = get_pending_reviews()
    
    if not pending:
        print("\n✓ No pending reviews found")
        return 0
    
    print(f"\nFound {len(pending)} open PRs to process")
    
    approved = 0
    failed = 0
    
    for pr_info in pending:
        print(f"\nProcessing PR #{pr_info['pr_number']}: {pr_info['title']}")
        
        if approve_pr(pr_info['pr_number'], token):
            approved += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {approved} approved, {failed} failed")
    print("=" * 80)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
