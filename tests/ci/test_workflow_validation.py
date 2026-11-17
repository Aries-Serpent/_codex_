"""
Test Workflow Validation

Test module for workflow validation.
"""

#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate local CI tooling presence (pre-commit); avoid enabling GH Actions.

from __future__ import annotations

import os
import subprocess
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


def test_manifest_pr_validation_runs_for_new_head_pushes() -> None:
    workflow = _load_workflow("codex-manifest-refresh.yml")
    assert workflow["on"]["pull_request"]["types"] == [
        "opened",
        "reopened",
        "synchronize",
    ]


def test_manifest_pr_validation_is_secret_free_and_read_only() -> None:
    workflow = _load_workflow("codex-manifest-refresh.yml")
    assert workflow["permissions"] == {}
    assert "pull_request_target" not in workflow["on"]
    job = workflow["jobs"]["validate-pr-manifest"]
    assert job["if"] == "github.event_name == 'pull_request'"
    assert job["permissions"] == {"contents": "read"}
    assert job["timeout-minutes"] == 30
    assert "secrets." not in yaml.safe_dump(job)

    checkout = job["steps"][0]["with"]
    assert checkout["token"] == "${{ github.token }}"
    assert checkout["persist-credentials"] is False
    assert checkout["repository"] == "${{ github.event.pull_request.head.repo.full_name }}"
    assert checkout["ref"] == "${{ github.event.pull_request.head.sha }}"

    commands = "\n".join(step.get("run", "") for step in job["steps"])
    assert "python scripts/ci/generate_manifest.py\n" in commands
    assert "python scripts/ci/generate_manifest.py --verify-integrity" in commands
    for forbidden in ("git push", "git commit", "gh ", "session_wrapup_autofix.py"):
        assert forbidden not in commands


def test_manifest_publication_generates_from_resolved_target() -> None:
    workflow = _load_workflow("codex-manifest-refresh.yml")
    job = workflow["jobs"]["refresh-manifest"]
    assert "github.event_name != 'pull_request'" in job["if"]
    assert "github.actor != 'github-actions[bot]'" in job["if"]
    assert job["permissions"] == {
        "contents": "write",
        "pull-requests": "read",
        "actions": "write",
    }

    steps = job["steps"]
    resolve_index = next(i for i, step in enumerate(steps) if step.get("id") == "resolve-target")
    resolve = steps[resolve_index]
    assert resolve["uses"] == "./.github/actions/resolve-push-target"
    assert resolve["with"]["ensure-exists"] == "true"
    assert steps[0]["with"]["ref"] == "main"
    target_checkout = steps[resolve_index + 1]
    assert target_checkout["uses"].startswith("actions/checkout@")
    assert target_checkout["with"]["ref"] == "${{ steps.resolve-target.outputs.branch }}"
    assert target_checkout["with"]["token"] == "${{ github.token }}"
    assert target_checkout["with"]["persist-credentials"] is False
    generation_index = next(i for i, step in enumerate(steps) if step.get("id") == "refresh")
    assert resolve_index + 1 < generation_index

    publish = steps[-1]
    assert publish["env"]["TARGET_REF"] == target_checkout["with"]["ref"]
    assert publish["env"]["GH_TOKEN"] == (
        "${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}"
    )
    commands = publish["run"]
    assert 'git push origin "HEAD:${TARGET_REF}"' in commands
    for forbidden in ("git pull", "git rebase", "--force", "HEAD_REF"):
        assert forbidden not in commands
    # Keep the existing downstream approval request; it grants no approval itself.
    assert "-f approval_source=workflow-execution-gate" in commands
    assert "-f approval_intent=auto_approve_action_required" in commands


def test_manifest_rescue_preserves_same_repo_guard_without_dependabot_writes() -> None:
    job = _load_workflow("codex-manifest-refresh.yml")["jobs"]["rescue-comment"]
    assert job["needs"] == "validate-pr-manifest"
    assert "failure()" in job["if"]
    assert "github.event_name == 'pull_request'" in job["if"]
    assert "github.actor != 'dependabot[bot]'" in job["if"]
    assert "github.event.pull_request.head.repo.full_name == github.repository" in job["if"]
    assert job["permissions"] == {
        "contents": "read",
        "pull-requests": "write",
        "issues": "write",
    }
    assert "secrets." not in yaml.safe_dump(job)
    assert job["steps"][0]["with"]["token"] == "${{ github.token }}"
    assert job["steps"][0]["with"]["ref"] == "main"
    assert job["steps"][0]["with"]["persist-credentials"] is False
    assert job["steps"][1]["env"]["GH_TOKEN"] == "${{ github.token }}"


@pytest.mark.parametrize(
    ("target", "open_prs", "push_fails", "expected_push", "expected_dispatch"),
    [
        ("0D_base_", "1", False, False, False),
        ("main", "1", False, False, False),
        ("0D_base_", "0", False, True, False),
        ("main", "0", False, True, True),
        ("main", "0", True, True, False),
        ("copilot/staging-tip", "0", False, True, False),
    ],
)
def test_manifest_publication_guard_and_fast_forward_failure(
    tmp_path: Path,
    target: str,
    open_prs: str,
    push_fails: bool,
    expected_push: bool,
    expected_dispatch: bool,
) -> None:
    """Execute the actual publish shell with local stubs; never contact GitHub."""
    job = _load_workflow("codex-manifest-refresh.yml")["jobs"]["refresh-manifest"]
    script = job["steps"][-1]["run"]
    script = script.replace("${{ github.repository }}", "example/repository")
    script = script.replace("${{ github.event.pull_request.number }}", "")
    assert "${{" not in script
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stubs = {
        "git": (
            '#!/bin/sh\nprintf "git %s\\n" "$*" >> "$TRACE"\n'
            '[ "$1" != diff ] || exit 1\n'
            'if [ "$1" = push ] && [ "$PUSH_FAIL" = true ]; then exit 1; fi\n'
        ),
        "gh": (
            '#!/bin/sh\nprintf "gh %s\\n" "$*" >> "$TRACE"\n'
            'if [ "$1" = api ]; then printf "%s\\n" "$PR_COUNT"; fi\n'
        ),
        "python": "#!/bin/sh\nexit 1\n",
    }
    for name, body in stubs.items():
        path = bin_dir / name
        path.write_text(body, encoding="utf-8")
        path.chmod(0o700)
    trace = tmp_path / "trace"
    result = subprocess.run(
        ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", script],
        cwd=tmp_path,
        env={
            "PATH": str(bin_dir) + os.pathsep + os.defpath,
            "TRACE": str(trace),
            "TARGET_REF": target,
            "GH_TOKEN": "local-test-placeholder",
            "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
            "PUSH_FAIL": str(push_fails).lower(),
            "PR_COUNT": open_prs,
        },
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert (result.returncode != 0) == push_fails, result.stderr
    calls = trace.read_text(encoding="utf-8")
    assert (f"git push origin HEAD:{target}\n" in calls) == expected_push
    assert ("gh workflow run " in calls) == expected_dispatch
    for forbidden in ("git pull ", "git rebase ", "--force"):
        assert forbidden not in calls
