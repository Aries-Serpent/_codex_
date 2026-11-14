#!/usr/bin/env python3
"""Verify protected environment configuration before token delegation.

The administrator must separately verify that the marker exists only as an
environment-scoped secret. This check never creates secrets or approves deployments.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

if __package__:
    from .approve_pending_runs import _gh as package_request

    _gh = package_request
else:
    # Script mode (`python3 scripts/ci/verify_owner_approval.py`): the sibling
    # module imports `scripts.ci`, so the repository root must be importable.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.ci.approve_pending_runs import _gh as script_request

    _gh = script_request

REQUIRED_DEPLOYMENT_BRANCHES = frozenset({"main", "0D_base_"})


def _valid_reviewer(entry: object) -> bool:
    if not isinstance(entry, dict) or entry.get("type") not in {"User", "Team"}:
        return False
    reviewer = entry.get("reviewer")
    return isinstance(reviewer, dict) and type(reviewer.get("id")) is int and reviewer["id"] > 0


def protection_error(
    environment: dict[str, Any], marker: str, branch_policies: object = None
) -> str | None:
    if marker != "true":
        return "missing-or-invalid-environment-marker"
    rules = environment.get("protection_rules")
    if not isinstance(rules, list):
        return "unknown-environment-protection"
    reviewers = [
        rule
        for rule in rules
        if isinstance(rule, dict) and rule.get("type") == "required_reviewers"
    ]
    if (
        len(reviewers) != 1
        or reviewers[0].get("prevent_self_review") is not True
        or not isinstance(reviewers[0].get("reviewers"), list)
        or not reviewers[0]["reviewers"]
    ):
        return "missing-independent-environment-review"
    if any(not _valid_reviewer(entry) for entry in reviewers[0]["reviewers"]):
        return "invalid-environment-reviewer"
    if environment.get("can_admins_bypass") is not False:
        return "environment-allows-administrator-bypass"
    policy = environment.get("deployment_branch_policy")
    # Only custom branch policies can restrict deployment to the required
    # branches; `protected_branches` admits every protected branch.
    if (
        not isinstance(policy, dict)
        or policy.get("protected_branches") is not False
        or policy.get("custom_branch_policies") is not True
    ):
        return "unrestricted-environment-deployment-branches"
    if branch_policy_names(branch_policies) != REQUIRED_DEPLOYMENT_BRANCHES:
        return "unexpected-environment-deployment-branches"
    return None


def branch_policy_names(payload: object) -> frozenset[str] | None:
    """Return exact branch names, or None when the listing is unverifiable."""
    if not isinstance(payload, dict):
        return None
    policies = payload.get("branch_policies")
    total = payload.get("total_count")
    if not isinstance(policies, list) or type(total) is not int or total != len(policies):
        return None
    names: set[str] = set()
    for entry in policies:
        if not isinstance(entry, dict) or entry.get("type", "branch") != "branch":
            return None
        name = entry.get("name")
        if not isinstance(name, str) or any(char in name for char in "*?[]"):
            return None
        names.add(name)
    return frozenset(names) if len(names) == len(policies) else None


def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    marker = os.environ.get("OWNER_APPROVAL_PROTECTED", "")
    if not repo or not token:
        print("::error::Cannot verify owner-approval environment without repository access.")
        return 1
    try:
        status, environment = _gh("GET", f"/repos/{repo}/environments/owner-approval", token)
    except (OSError, ValueError):
        print("::error::Owner-approval environment inspection failed.")
        return 1
    if status != 200 or not isinstance(environment, dict):
        print(f"::error::Owner-approval environment inspection denied (HTTP {status}).")
        return 1
    try:
        status, branch_policies = _gh(
            "GET",
            f"/repos/{repo}/environments/owner-approval/deployment-branch-policies?per_page=100",
            token,
        )
    except (OSError, ValueError):
        print("::error::Owner-approval branch policy inspection failed.")
        return 1
    if status != 200:
        branch_policies = None
    error = protection_error(environment, marker, branch_policies)
    if error:
        print(f"::error::Protected owner approval denied: {error}. Administrator action required.")
        return 1
    print(
        "Verified owner-approval protection and runtime marker; platform review remains required."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
