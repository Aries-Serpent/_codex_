"""Operation-level GitHub write permission plan for azimuth verification."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class WritePermissionProbe:
    """Describe one permission surface without executing a hosted mutation."""

    capability: str
    permission_family: str
    operation: str
    risk: str
    preflight: str
    live_probe: str
    rollback: str
    execution: str = "dry_run_only"
    blocked_by: tuple[str, ...] = ()


WRITE_PERMISSION_PROBES: tuple[WritePermissionProbe, ...] = (
    WritePermissionProbe(
        "contents.write",
        "contents",
        "create_dangling_blob",
        "low",
        "GET /repos/{repo}",
        "POST /repos/{repo}/git/blobs",
        "Unreferenced Git object has no branch/ref or visible repository effect",
    ),
    WritePermissionProbe(
        "pull_requests.write",
        "pull_requests",
        "create_and_close_task_pr",
        "medium",
        "GET /repos/{repo}; verify push and branch protection",
        "Create task branch commit and draft PR; update the same PR",
        "Close PR and preserve branch/commit evidence",
        blocked_by=("requires_task_owned_commit", "no_branch_deletion"),
    ),
    WritePermissionProbe(
        "issues.write",
        "issues",
        "create_close_probe_issue",
        "medium",
        "GET /repos/{repo}/issues?per_page=1",
        "Create labelled probe issue, then close it",
        "Close issue; history remains auditable",
        blocked_by=("creates_external_record",),
    ),
    WritePermissionProbe(
        "actions.write",
        "actions",
        "dispatch_noop_workflow",
        "high",
        "List workflow dispatch inputs and workflow permissions",
        "Dispatch a no-op workflow dedicated to permission verification",
        "Cancel immediately if needed; verify conclusion/logs",
        blocked_by=("requires_noop_workflow", "server_workflow_controls"),
    ),
    WritePermissionProbe(
        "checks.write",
        "checks",
        "create_complete_check_run",
        "high",
        "GET checks for task commit",
        "Create a neutral check run and complete it",
        "Completed check remains on task commit",
        blocked_by=("requires_github_app", "visible_check_record"),
    ),
    WritePermissionProbe(
        "statuses.write",
        "statuses",
        "set_commit_status",
        "medium",
        "Verify task commit SHA and existing contexts",
        "Create task-prefixed pending then success status",
        "Final success state remains auditable",
        blocked_by=("requires_task_owned_commit",),
    ),
    WritePermissionProbe(
        "releases.write",
        "releases",
        "create_delete_draft_release",
        "high",
        "GET releases and release/tag policy",
        "Create private draft release with task tag, then delete it",
        "Delete draft and verify 404",
        blocked_by=("owner_approval_for_release_surface",),
    ),
    WritePermissionProbe(
        "deployments.write",
        "deployments",
        "create_inactivate_deployment",
        "high",
        "GET deployments and environment protection",
        "Create a task deployment then mark inactive",
        "Mark inactive; deployment history remains",
        blocked_by=("environment_controls", "external_audit_record"),
    ),
    WritePermissionProbe(
        "discussions.write",
        "discussions",
        "create_delete_or_close_discussion",
        "high",
        "GET discussions/categories via GraphQL",
        "Create a private-safe task discussion then close it if supported",
        "Close discussion; history remains auditable",
        blocked_by=("requires_graphql_write", "creates_external_record"),
    ),
    WritePermissionProbe(
        "variables.write",
        "variables",
        "create_update_delete_variable",
        "medium",
        "GET actions variables metadata",
        "Create task-prefixed variable, update it, then delete it",
        "Delete variable and verify 404",
        blocked_by=("elevated_repository_token",),
    ),
    WritePermissionProbe(
        "secrets.write",
        "secrets",
        "create_delete_secret_without_readback",
        "critical",
        "GET public key and permitted secret names only",
        "Encrypt a random task marker, PUT secret, then DELETE",
        "Delete secret and verify absence by name metadata",
        blocked_by=("elevated_repository_token", "credential_rotation_boundary"),
    ),
    WritePermissionProbe(
        "webhooks.write",
        "webhooks",
        "create_delete_loopback_hook",
        "critical",
        "GET webhooks; verify no secret-bearing configuration is returned",
        "Create disabled/no-delivery hook if API permits, then delete it",
        "Delete hook and verify 404",
        blocked_by=("administrative_permission", "hosted_security_control"),
    ),
    WritePermissionProbe(
        "security_events.write",
        "security_events",
        "dismiss_reopen_only_owned_test_alert",
        "critical",
        "GET CodeQL/secret scanning alerts and ownership",
        "No synthetic security-alert write; consume existing task-owned alert only",
        "Restore original alert state if changed",
        blocked_by=("no_test_alert_available", "security_owner_gate"),
    ),
    WritePermissionProbe(
        "administration.write",
        "administration",
        "no_op_repository_setting",
        "critical",
        "GET repository settings and branch/ruleset state",
        "PATCH a setting to its exact current value only after review",
        "Restore captured value and verify unchanged",
        blocked_by=("server_admin_boundary", "owner_approval_for_admin_probe"),
    ),
)


def azimuth_write_plan() -> dict[str, Any]:
    """Return the 360-degree operation map with execution and rollback evidence."""
    probes = [asdict(probe) for probe in WRITE_PERMISSION_PROBES]
    return {
        "mode": "azimuth",
        "execution_default": "dry_run_only",
        "live_write_enabled": False,
        "probe_count": len(probes),
        "probes": probes,
        "decision_rule": (
            "A domain is write-verified only after a task-scoped live probe, "
            "successful reconciliation, and rollback/terminal-state evidence."
        ),
        "forbidden_fallbacks": [
            "weaken checks or protections",
            "forge reviews or results",
            "bypass branch/environment controls",
            "rotate or expose secrets",
            "delete unrelated branches",
            "claim permission from repository role metadata alone",
        ],
    }


__all__ = ["WRITE_PERMISSION_PROBES", "WritePermissionProbe", "azimuth_write_plan"]
