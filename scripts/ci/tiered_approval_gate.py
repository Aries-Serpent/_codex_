#!/usr/bin/env python3
import sys
import json
import subprocess
from typing import List, Tuple

def run_gh_command(cmd: List[str]) -> Tuple[bool, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr or e.stdout

def get_pr_files(pr_number: int) -> List[str]:
    success, output = run_gh_command(['gh', 'pr', 'view', str(pr_number), '--json', 'files'])
    if not success:
        return []
    try:
        data = json.loads(output)
        return [f['path'] for f in data.get('files', [])]
    except Exception:
        return []

def determine_risk_tier(files: List[str]) -> str:
    high_risk_prefixes = ['src/core/', 'src/api/', 'codex_ml/core/']
    medium_risk_prefixes = ['src/', 'scripts/', '.github/workflows/']

    tier = 'low'
    for f in files:
        if any(f.startswith(prefix) for prefix in high_risk_prefixes):
            return 'high'
        elif any(f.startswith(prefix) for prefix in medium_risk_prefixes):
            tier = 'medium'

    return tier

def get_approvals(pr_number: int) -> int:
    success, output = run_gh_command(['gh', 'pr', 'reviews', str(pr_number), '--json', 'state'])
    if not success:
        return 0
    try:
        reviews = json.loads(output)
        return sum(1 for r in reviews if r.get('state') == 'APPROVED')
    except Exception:
        return 0

def check_manager_override(pr_number: int) -> bool:
    # Check if PR has manager override label
    success, output = run_gh_command(['gh', 'pr', 'view', str(pr_number), '--json', 'labels'])
    if success:
        try:
            data = json.loads(output)
            labels = [lbl['name'] for lbl in data.get('labels', [])]
            if 'manager-override' in labels or 'hotfix' in labels:
                return True
        except Exception:
            pass
    return False

def check_auto_approve_label(pr_number: int) -> bool:
    # Auto-approval is opt-in: require the permanent label to be active on the PR.
    # The single-session override can still be used only when explicitly present and
    # still within its TTL window.
    success, output = run_gh_command(['gh', 'pr', 'view', str(pr_number), '--json', 'labels', 'createdAt'])
    if success:
        try:
            data = json.loads(output)
            labels = [lbl['name'] for lbl in data.get('labels', [])]
            if 'wec:auto-approve' in labels:
                return True
            if 'wec:auto-approve-once' in labels:
                created = data.get('createdAt')
                if not created:
                    return False
                import datetime
                created_dt = datetime.datetime.fromisoformat(created.replace('Z', '+00:00'))
                age_hours = (datetime.datetime.now(datetime.timezone.utc) - created_dt).total_seconds() / 3600
                return age_hours <= 1
        except Exception:
            pass
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: tiered_approval_gate.py <pr_number>")
        sys.exit(1)

    pr_number = int(sys.argv[1])
    files = get_pr_files(pr_number)
    risk_tier = determine_risk_tier(files)
    approvals = get_approvals(pr_number)
    is_hotfix = check_manager_override(pr_number)

    required_approvals = {'low': 1, 'medium': 2, 'high': 3}[risk_tier]

    print(f"PR {pr_number} files changed: {len(files)}")
    print(f"Risk Tier: {risk_tier.upper()}")
    print(f"Current Approvals: {approvals}")
    print(f"Required Approvals: {required_approvals}")

    if is_hotfix:
        if not check_auto_approve_label(pr_number):
            print("HOTFIX/MANAGER OVERRIDE requires the 'wec:auto-approve' or 'wec:auto-approve-once' label — skipping bot approval.")
            sys.exit(1)
        print("HOTFIX/MANAGER OVERRIDE ACTIVE. Approval allowed only with 'wec:auto-approve' or 'wec:auto-approve-once' label.")
        run_gh_command(['gh', 'pr', 'review', str(pr_number), '--approve', '--body', 'Auto-approved via manager hotfix override'])
        sys.exit(0)

    if approvals >= required_approvals:
        print("Requirements met.")
        sys.exit(0)

    if risk_tier == 'low' and approvals == 0:
        if not check_auto_approve_label(pr_number):
            print("Low-risk changes, but 'wec:auto-approve' label is not active — skipping bot auto-approve.")
            sys.exit(1)
        print("Low risk changes detected and 'wec:auto-approve' label active. Bot auto-approving trivial changes.")
        run_gh_command(['gh', 'pr', 'review', str(pr_number), '--approve', '--body', 'Auto-approved low-risk changes'])
        sys.exit(0)

    print(f"Pending approvals. Need {required_approvals}, have {approvals}.")
    sys.exit(1)

if __name__ == '__main__':
    main()
