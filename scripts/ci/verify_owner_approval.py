#!/usr/bin/env python3
"""Verify protected environment configuration before token delegation.

The administrator must separately verify that the marker exists only as an
environment-scoped secret. This check never creates secrets or approves deployments.
"""

from __future__ import annotations

import os
import sys
from typing import Any

if __package__:
    from .approve_pending_runs import _gh as package_request

    _gh = package_request
else:
    from approve_pending_runs import _gh as script_request

    _gh = script_request


def _valid_reviewer(entry: object) -> bool:
    if not isinstance(entry, dict) or entry.get("type") not in {"User", "Team"}:
        return False
    reviewer = entry.get("reviewer")
    return isinstance(reviewer, dict) and type(reviewer.get("id")) is int and reviewer["id"] > 0


def protection_error(environment: dict[str, Any], marker: str) -> str | None:
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
    if (
        not isinstance(policy, dict)
        or type(policy.get("protected_branches")) is not bool
        or type(policy.get("custom_branch_policies")) is not bool
        or policy["protected_branches"] == policy["custom_branch_policies"]
    ):
        return "unrestricted-environment-deployment-branches"
    return None


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
    error = protection_error(environment, marker)
    if error:
        print(f"::error::Protected owner approval denied: {error}. Administrator action required.")
        return 1
    print(
        "Verified owner-approval protection and runtime marker; platform review remains required."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
