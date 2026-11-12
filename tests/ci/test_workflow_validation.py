"""
Test Workflow Validation

Test module for workflow validation.
"""

#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate local CI tooling presence (pre-commit); avoid enabling GH Actions.

from __future__ import annotations

from fnmatch import fnmatchcase
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


@pytest.mark.parametrize("event", ["push", "pull_request"])
def test_rust_swarm_ignores_only_metadata_codex_changes(event: str) -> None:
    """Metadata-only .codex updates must not consume the Rust CI matrix."""

    workflow = _load_workflow("rust_swarm_ci.yml")
    event_config = workflow["on"][event]
    ignored_paths = event_config["paths-ignore"]

    assert ".codex/**" in ignored_paths, "Condition must be true"
    for metadata_path in (
        ".codex/campaign_metrics.jsonl",
        ".codex/cascade_detector_state.json",
        ".codex/evidence/archive_ops.jsonl",
    ):
        assert any(fnmatchcase(metadata_path, pattern) for pattern in ignored_paths)

    for trigger_path in (
        "Cargo.toml",
        "Cargo.lock",
        "rust_swarm/src/lib.rs",
        "src/aries_serpent_core/cli.py",
        ".github/workflows/rust_swarm_ci.yml",
    ):
        assert not any(fnmatchcase(trigger_path, pattern) for pattern in ignored_paths)


@pytest.mark.parametrize(
    ("event_name", "head_repository", "publishes_check"),
    [
        ("pull_request", "Aries-Serpent/_codex_", True),
        ("pull_request", "contributor/_codex_", False),
        ("push", None, True),
    ],
)
def test_rust_swarm_audit_selects_trusted_or_fork_path(
    event_name: str, head_repository: str | None, publishes_check: bool
) -> None:
    workflow = _load_workflow("rust_swarm_ci.yml")
    job = workflow["jobs"]["security_audit"]
    steps = job["steps"]
    publisher = next(s for s in steps if s.get("uses", "").startswith("rustsec/audit-check@"))
    installer = next(s for s in steps if s.get("run") == "cargo install cargo-audit --locked")
    auditor = next(s for s in steps if s.get("run") == "cargo audit")
    trusted_condition = (
        "github.event_name != 'pull_request' || "
        "github.event.pull_request.head.repo.full_name == github.repository"
    )
    fork_condition = (
        "github.event_name == 'pull_request' && "
        "github.event.pull_request.head.repo.full_name != github.repository"
    )
    predicates = {
        "github.event_name != 'pull_request'": event_name != "pull_request",
        "github.event_name == 'pull_request'": event_name == "pull_request",
        "github.event.pull_request.head.repo.full_name == github.repository": (
            head_repository == "Aries-Serpent/_codex_"
        ),
        "github.event.pull_request.head.repo.full_name != github.repository": (
            head_repository != "Aries-Serpent/_codex_"
        ),
    }
    selected = []
    for step, expected_condition in (
        (publisher, trusted_condition),
        (installer, fork_condition),
        (auditor, fork_condition),
    ):
        condition = " ".join(step["if"].removeprefix("${{").removesuffix("}}").split())
        assert condition == expected_condition
        selected.append(
            any(
                all(predicates[atom.strip()] for atom in branch.split("&&"))
                for branch in condition.split("||")
            )
        )
    assert selected == [publishes_check, not publishes_check, not publishes_check]
    assert publisher["with"]["token"] == "${{ github.token }}"
    assert job["permissions"] == {"contents": "read", "checks": "write"}
    assert "with" not in installer and "with" not in auditor
    assert "env" not in installer and "env" not in auditor


def test_docker_approval_requires_protected_environment() -> None:
    workflow = _load_workflow("docker-build-push.yml")
    dispatch_inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    assert "approval_duration" not in dispatch_inputs
    assert "approval_until" not in dispatch_inputs
    assert workflow["env"]["OWNER_APPROVED_DURATION"] == "${{ vars.OWNER_APPROVED_DURATION }}"
    assert workflow["env"]["OWNER_APPROVED_UNTIL"] == "${{ vars.OWNER_APPROVED_UNTIL }}"

    for job_name in ("approval-check", "build-and-smoke", "push"):
        job = workflow["jobs"][job_name]
        assert job["environment"] == "owner-approval"
        guard = next(
            step
            for step in job["steps"]
            if step.get("run") == "bash scripts/ci/owner_approval_guard.sh"
        )
        assert guard["env"]["OWNER_APPROVAL_PROTECTED"] == "${{ secrets.OWNER_APPROVAL_PROTECTED }}"


_PERMISSION_LEVELS = {"none": 0, "read": 1, "write": 2}


def _permission_grants(permissions: object) -> dict[str, int] | None:
    """Normalize a permissions block; return ``None`` for write on every scope.

    An omitted block (``None``) falls back to the repository's default token
    permissions, which may be read-only, so it guarantees no grant.
    """
    if permissions == "write-all":
        return None
    if permissions is None:
        return {}
    if permissions == "read-all":
        return {"*": _PERMISSION_LEVELS["read"]}
    assert isinstance(permissions, dict), f"Unexpected permissions: {permissions!r}"
    return {scope: _PERMISSION_LEVELS[level] for scope, level in permissions.items()}


def _granted_level(grants: dict[str, int] | None, scope: str) -> int:
    if grants is None:
        return _PERMISSION_LEVELS["write"]
    return grants.get(scope, grants.get("*", 0))


def test_cost_gate_callers_grant_called_workflow_permissions() -> None:
    """Callers must grant everything cost-gate.yml requests.

    A reusable workflow cannot exceed its caller's grant; GitHub rejects the
    run at startup with zero jobs instead of failing an individual job.
    """
    called = _load_workflow("cost-gate.yml")
    required: dict[str, int] = {}
    blocks = [called.get("permissions")] + [
        job.get("permissions") for job in called["jobs"].values()
    ]
    for block in blocks:
        for scope, level in (_permission_grants(block) or {}).items():
            required[scope] = max(required.get(scope, 0), level)
    assert required.get("issues") == _PERMISSION_LEVELS["write"]

    callers = []
    for path in sorted(WORKFLOWS_DIR.glob("*.y*ml")):
        workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(workflow, dict):
            continue
        for job_name, job in (workflow.get("jobs") or {}).items():
            if isinstance(job, dict) and str(job.get("uses", "")).endswith("/cost-gate.yml"):
                block = job.get("permissions", workflow.get("permissions"))
                grants = _permission_grants(block)
                missing = {
                    scope: level
                    for scope, level in required.items()
                    if _granted_level(grants, scope) < level
                }
                assert not missing, f"{path.name}:{job_name} lacks {missing}"
                callers.append(path.name)
    assert "data-quality-suite.yml" in callers


def test_agent_delegation_requires_protected_environment() -> None:
    workflow = _load_workflow("agent-auth-delegation.yml")
    activation = workflow["jobs"]["activate-delegation"]
    assert activation["environment"] == "owner-approval"
    provenance_check = next(
        step
        for step in activation["steps"]
        if step.get("name") == "Verify protected owner approval"
    )
    assert (
        provenance_check["env"]["OWNER_APPROVAL_PROTECTED"]
        == "${{ secrets.OWNER_APPROVAL_PROTECTED }}"
    )
