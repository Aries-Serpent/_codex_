"""
Test Workflow Validation

Test module for workflow validation.
"""

#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate local CI tooling presence (pre-commit); avoid enabling GH Actions.

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PRE_COMMIT = REPO_ROOT / ".pre-commit-config.yaml"


@pytest.mark.smoke
def test_ci_precommit_config_present_and_valid_yaml():
    if not PRE_COMMIT.exists():
        pytest.skip(".pre-commit-config.yaml not present")
    data = yaml.safe_load(PRE_COMMIT.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    repos = data.get("repos", [])
    assert isinstance(repos, list)


# ---------------------------------------------------------------------------
# CodeQL alert remediation: actions/missing-workflow-permissions
# Alerts 13200-13207 — all four workflows must have restrictive top-level
# permissions (empty dict, NOT the broad "read-all" shorthand) so that
# principle-of-least-privilege is enforced via per-job permissions blocks.
# ---------------------------------------------------------------------------

#: Workflows that were flagged by CodeQL alerts 13200-13207
_FLAGGED_WORKFLOWS = [
    "rust_swarm_ci.yml",  # alerts 13200-13204 (five jobs)
    "status_gate.yml",  # alert 13205
    "template_lint.yml",  # alert 13206
    "test-rag.yml",  # alert 13207
]

WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"


def _load_workflow(filename: str) -> dict:
    path = WORKFLOWS_DIR / filename
    assert path.exists(), f"Workflow not found: {path}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("filename", _FLAGGED_WORKFLOWS)
def test_workflow_top_level_permissions_not_read_all(filename: str) -> None:
    """Top-level permissions must NOT be the broad 'read-all' shorthand.

    'permissions: read-all' grants every read scope by default, which violates
    the principle of least privilege and triggers CodeQL
    actions/missing-workflow-permissions alerts 13200-13207.
    The correct fix is 'permissions: {}' (deny-all at workflow level) with
    explicit per-job permissions.
    """
    data = _load_workflow(filename)
    top_perms = data.get("permissions")
    assert top_perms != "read-all", (
        f"{filename}: top-level 'permissions: read-all' is too broad. "
        "Use 'permissions: {}' instead and set explicit per-job permissions."
    )
    assert (top_perms != "write-all", "top_perms is not valid"
    ), f"{filename}: top-level 'permissions: write-all' is dangerously broad."


@pytest.mark.parametrize("filename", _FLAGGED_WORKFLOWS)
def test_workflow_jobs_all_have_explicit_permissions(filename: str) -> None:
    """Every job in a flagged workflow must declare explicit permissions.

    When the workflow-level permissions are '{}' (empty/deny-all), each job
    must declare its own permissions block to grant only what it needs.
    This satisfies CodeQL alerts 13200-13207 (actions/missing-workflow-permissions).
    """
    data = _load_workflow(filename)
    jobs: dict = data.get("jobs", {})
    assert jobs, f"{filename}: no jobs found"

    missing = [
        job_name
        for job_name, job_cfg in jobs.items()
        if job_cfg is None or "permissions" not in job_cfg
    ]
    assert not missing, (
        f"{filename}: the following jobs lack an explicit 'permissions:' block "
        f"(required when top-level permissions are restricted): {missing}"
    )


@pytest.mark.parametrize("filename", _FLAGGED_WORKFLOWS)
def test_workflow_top_level_permissions_is_empty_dict(filename: str) -> None:
    """Top-level permissions must be the empty dict '{}' for the four flagged workflows.

    Rationale: all jobs have their own explicit permissions, so the workflow-level
    default should be deny-all ('{}') to prevent future jobs from accidentally
    inheriting broad permissions.
    """
    data = _load_workflow(filename)
    top_perms = data.get("permissions")
    assert top_perms == {}, (
        f"{filename}: expected top-level 'permissions: {{}}' (empty dict), "
        f"got {top_perms!r}. "
        "Set 'permissions: {}' at workflow level and use per-job permissions."
    )
