"""
Test Workflow Validation

Test module for workflow validation.
"""

#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate local CI tooling presence (pre-commit); avoid enabling GH Actions.

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
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


def test_rag_workflow_coverage_records_runtime_implementation(tmp_path):
    pytest.importorskip("coverage")
    workflow = _load_workflow("test-rag.yml")
    script = next(
        step["run"]
        for job in workflow["jobs"].values()
        for step in job.get("steps", [])
        if step.get("name") == "Run RAG tests with coverage"
    )
    match = re.search(r"--cov=(\S+)", script)
    assert match is not None
    script = """
import runpy
import sys
from coverage import Coverage

source, config, implementation, destination = sys.argv[1:]
collector = Coverage(config_file=config, data_file=None, source=[source])
collector.start()
try:
    namespace = runpy.run_path(implementation)
    assert namespace["OutputProcessor"].scrub_output(" answer ") == "answer"
finally:
    collector.stop()
assert implementation in collector.get_data().measured_files()
collector.xml_report(outfile=destination)
"""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            match.group(1),
            str(REPO_ROOT / "tests/rag/.coveragerc"),
            str(REPO_ROOT / "src/aries_serpent_core/rag/postprocess.py"),
            str(tmp_path / "coverage.xml"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "coverage.xml").is_file()


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
    assert (
        top_perms != "write-all"
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


def test_container_scan_runs_all_trivy_configurations_for_every_pr() -> None:
    workflow = _load_workflow("container-scan.yml")

    assert "paths" not in workflow["on"]["pull_request"]
    assert workflow["jobs"]["trivy-scan"]["strategy"]["matrix"]["dockerfile"] == [
        ".config/Dockerfile",
        "docker/Dockerfile.cpu",
        "docker/Dockerfile.gpu",
    ]


def test_cognitive_preflight_is_read_only_and_never_pushes_docs() -> None:
    workflow = _load_workflow("agent-auth-delegation.yml")
    job = workflow["jobs"]["cognitive-preflight"]
    assert job["permissions"] == {
        "actions": "read",
        "contents": "read",
        "issues": "write",
        "pull-requests": "write",
    }

    commands = "\n".join(step.get("run", "") for step in job["steps"])
    assert "git push" not in commands
    assert "git commit" not in commands
    assert "git pull --rebase" not in commands
    assert "session_wrapup_autofix.py" in commands


def test_workflow_analyzer_reports_omit_secret_identifiers() -> None:
    analyzer_path = REPO_ROOT / ".github" / "scripts" / "workflow_analyzer.py"
    spec = importlib.util.spec_from_file_location("workflow_analyzer_for_test", analyzer_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    analyzer = module.WorkflowAnalyzer()
    analyzer.workflows = {
        "sample.yml": {
            "path": "sample.yml",
            "name": "sample",
            "guarded": False,
            "triggers": ["push"],
            "jobs": ["test"],
            "secrets": ["SUPER_SECRET_SENTINEL"],
            "runners": ["ubuntu-latest"],
            "actions_used": [],
            "has_docker": False,
            "has_uv": False,
            "has_nox": False,
            "has_pytest": True,
        }
    }

    json_report = analyzer.generate_json_report()
    markdown_report = analyzer.generate_markdown_report()

    assert "SUPER_SECRET_SENTINEL" not in json_report
    assert "SUPER_SECRET_SENTINEL" not in markdown_report
    assert json.loads(json_report)["workflows"]["sample.yml"]["secret_count"] == 1


def test_cognitive_preflight_documentation_checks_bind_to_head_commit() -> None:
    workflow = _load_workflow("agent-auth-delegation.yml")
    steps = workflow["jobs"]["cognitive-preflight"]["steps"]
    commands = {
        step["name"]: step.get("run", "")
        for step in steps
        if step.get("name")
        in {
            "Verify Accountability Report updated in last commit",
            "Verify CHANGELOG.md updated in last commit",
        }
    }

    assert set(commands) == {
        "Verify Accountability Report updated in last commit",
        "Verify CHANGELOG.md updated in last commit",
    }
    assert (
        "git rev-list --first-parent --no-merges"
        in commands["Verify Accountability Report updated in last commit"]
    )
    assert (
        "git diff-tree --no-commit-id --name-only -r"
        in commands["Verify CHANGELOG.md updated in last commit"]
    )
    assert "2026-11-25" not in "\n".join(commands.values())


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
    target_index = next(
        i for i, step in enumerate(steps) if step.get("with", {}).get("path") == "_manifest_target"
    )
    target_checkout = steps[target_index]
    assert target_checkout["uses"].startswith("actions/checkout@")
    assert target_checkout["with"]["ref"] == "${{ steps.resolve-target.outputs.branch }}"
    assert target_checkout["with"]["token"] == "${{ github.token }}"
    assert target_checkout["with"]["persist-credentials"] is False
    generation_index = next(i for i, step in enumerate(steps) if step.get("id") == "refresh")
    assert resolve_index < target_index < generation_index
    # Main remains at the workspace root. Never load a target composite action.
    assert "path" not in steps[0]["with"]
    assert not job.get("defaults")
    assert all("working-directory" not in step for step in steps)
    assert all(not step.get("uses", "").startswith("./") for step in steps[target_index + 1 :])
    setup_index = next(
        i
        for i, step in enumerate(steps)
        if step.get("uses") == "./.github/actions/setup-python-cached"
    )
    assert setup_index < target_index
    generation = steps[generation_index]
    assert generation["env"] == {"TARGET_ROOT": "${{ github.workspace }}/_manifest_target"}
    assert generation["run"].splitlines() == [
        'python -I scripts/ci/generate_manifest.py --repo-root "$TARGET_ROOT"',
        'python -I scripts/ci/sync_tracked_files.py --repo-root "$TARGET_ROOT" --fix --manifest-only --quiet',
        'python -I scripts/ci/generate_manifest.py --repo-root "$TARGET_ROOT" --verify-integrity',
    ]

    publish = steps[-1]
    assert steps[target_index + 1 :] == [generation, publish]
    assert publish["env"]["TARGET_REF"] == target_checkout["with"]["ref"]
    assert publish["env"]["GH_TOKEN"] == (
        "${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}"
    )
    commands = publish["run"]
    assert publish["env"]["TARGET_ROOT"] == generation["env"]["TARGET_ROOT"]
    assert 'git -C "$TARGET_ROOT" push origin "HEAD:${TARGET_REF}"' in commands
    assert (
        'git -C "$TARGET_ROOT" add -- \\\n  CODEX_MANIFEST.json \\\n  .secrets.baseline' in commands
    )
    for forbidden in ("python", "scripts/", "CHANGELOG.md", "AGENT_ACCOUNTABILITY_REPORT.md"):
        assert forbidden not in commands
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
            '#!/bin/sh\n[ "$1" = -C ] && [ "$2" = "$TARGET_ROOT" ] || exit 9\nshift 2\n'
            'printf "git %s\\n" "$*" >> "$TRACE"\n'
            '[ "$1" != diff ] || exit 1\n'
            'if [ "$1" = push ] && [ "$PUSH_FAIL" = true ]; then exit 1; fi\n'
        ),
        "gh": (
            '#!/bin/sh\nprintf "gh %s\\n" "$*" >> "$TRACE"\n'
            'if [ "$1" = api ]; then printf "%s\\n" "$PR_COUNT"; fi\n'
        ),
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
            "TARGET_ROOT": str(tmp_path / "target-data"),
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


@pytest.mark.parametrize("script", ["generate_manifest.py", "sync_tracked_files.py"])
def test_manifest_tool_default_root_still_matches_script_repository(script: str) -> None:
    spec = importlib.util.spec_from_file_location(
        "manifest_tool", REPO_ROOT / "scripts/ci" / script
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.REPO_ROOT == REPO_ROOT


def test_manifest_sync_reports_missing_scanner_without_scanning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Optional no-scan reporting is distinct from exercising the real adapter."""
    spec = importlib.util.spec_from_file_location(
        "manifest_sync", REPO_ROOT / "scripts/ci/sync_tracked_files.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._set_repo_root(tmp_path)
    module.MANIFEST_PATH.write_text('{"integrity_sha256": "fixture"}', encoding="utf-8")
    module.SECRETS_BASELINE.write_text('{"results": {}}', encoding="utf-8")
    module.AGENT_CONTEXT_PATH.parent.mkdir()
    module.AGENT_CONTEXT_PATH.write_text("{}", encoding="utf-8")
    module.AGENT_AUTH_SESSION_PATH.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(module, "_detect_secrets_available", lambda: False)

    def unexpected_scan(_path: Path) -> None:
        pytest.fail("No scanner adapter should run when the optional dependency is absent")

    monkeypatch.setattr(module, "_scan_baseline_file", unexpected_scan)
    result = module.SyncResult()
    module.check_secrets_baseline(result, fix=True)
    module.check_agent_context_baseline(result, fix=True)
    module.check_agent_auth_session_baseline(result, fix=True)
    assert len(result.checks) == 3
    assert all(
        check["message"] == "detect-secrets unavailable in this env; baseline comparison skipped"
        and not check["fixed"]
        for check in result.checks
    )
    assert json.loads(module.SECRETS_BASELINE.read_text()) == {"results": {}}


def test_manifest_trusted_tools_process_poisoned_target_as_data_only(tmp_path: Path) -> None:
    """Target Python/plugins/actions are inert even with a poisoned import path."""
    pytest.importorskip(
        "detect_secrets",
        reason="Real scanner isolation exercise requires the optional detect-secrets package",
        exc_type=ModuleNotFoundError,
    )
    target = tmp_path / "target"
    registry = target / ".github/agents/AGENT_REGISTRY.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text("agents:\n  - id: data-only-agent\n", encoding="utf-8")
    workflows = target / ".github/workflows"
    workflows.mkdir()
    (workflows / "staging-only.yml").write_text("name: staging data\n", encoding="utf-8")
    context = target / ".codex/agent_context.json"
    context.parent.mkdir()
    context.write_text(
        json.dumps({"hash": hashlib.sha256(b"fixture").hexdigest()}), encoding="utf-8"
    )
    (target / ".codex/agent_auth_session.json").write_text(context.read_text(), encoding="utf-8")
    (target / ".secrets.baseline").write_text(
        json.dumps(
            {"results": {}, "plugins_used": [{"name": "TargetPlugin", "path": "target_plugin.py"}]}
        ),
        encoding="utf-8",
    )
    marker = tmp_path / "target-code-executed"
    poison = (
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n"
        "raise RuntimeError('target code must never execute')\n"
    )
    for relative in (
        "sitecustomize.py",
        "yaml.py",
        "detect_secrets/__main__.py",
        "detect_secrets/__init__.py",
        "target_plugin.py",
        "scripts/ci/generate_manifest.py",
        "scripts/ci/sync_tracked_files.py",
        ".github/actions/setup-python-cached/action.yml",
    ):
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(poison, encoding="utf-8")

    def run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-I",
                str(REPO_ROOT / "scripts/ci" / script),
                "--repo-root",
                str(target),
                *args,
            ],
            cwd=target,
            env={"PATH": os.defpath, "PYTHONPATH": str(target)},
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )

    run("generate_manifest.py")
    run("sync_tracked_files.py", "--fix", "--manifest-only")
    run("sync_tracked_files.py", "--check", "--manifest-only")
    run("generate_manifest.py", "--verify-integrity")
    assert not marker.exists()
    manifest = json.loads((target / "CODEX_MANIFEST.json").read_text())
    assert manifest["agents"][0]["name"] == "data-only-agent"
    assert [item["name"] for item in manifest["workflows"]] == ["staging-only"]
    baseline = json.loads((target / ".secrets.baseline").read_text())
    for relative in (
        "CODEX_MANIFEST.json",
        ".codex/agent_context.json",
        ".codex/agent_auth_session.json",
    ):
        entries = baseline["results"][relative]
        assert entries
        assert all(entry["filename"] == relative for entry in entries)


@pytest.mark.parametrize("script", ["generate_manifest.py", "sync_tracked_files.py"])
def test_manifest_data_root_rejects_output_symlink_escape(tmp_path: Path, script: str) -> None:
    target = tmp_path / "target"
    target.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("untouched", encoding="utf-8")
    (target / "CODEX_MANIFEST.json").symlink_to(outside)
    args = ["--check", "--manifest-only"] if script == "sync_tracked_files.py" else []
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            str(REPO_ROOT / "scripts/ci" / script),
            "--repo-root",
            str(target),
            *args,
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "escapes --repo-root" in result.stderr
    assert outside.read_text() == "untouched"


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--manifest-only", "--pre-push"],
        ["--manifest-only", "--post-to-discussion", "3673"],
    ],
)
def test_manifest_external_sync_root_disallows_execution_modes(
    tmp_path: Path, args: list[str]
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            str(REPO_ROOT / "scripts/ci/sync_tracked_files.py"),
            "--repo-root",
            str(tmp_path),
            *args,
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "--repo-root requires --manifest-only" in result.stderr
