from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import validate as validate_schema

from scripts.ci import agent_resource_profile, agent_setup_readiness, prepare_agent_context
from scripts.ci.environment_preflight import _build_config, _detect_missing_runtime_dependencies
from scripts.ci.validate_copilot_bootstrap import validate_retained_workflow

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/copilot-setup-steps.yml"


def test_retained_workflow_reports_legacy_findings_and_deferred_cloud_contract():
    report = validate_retained_workflow(WORKFLOW)
    assert report.errors == ()
    assert len(report.legacy_findings) == 1
    assert "filtered environment output" in report.legacy_findings[0]
    assert report.deferred_cloud_setup_checks == (
        "agent context preparation and delivery",
        "requested LFS fetch integration",
        "always-run setup readiness reporting",
    )


def test_retained_ordinary_workflow_schema():
    """Ordinary Actions schema acceptance is not hosted setup support."""
    data = yaml.safe_load(WORKFLOW.read_text())
    validate_schema(
        data["jobs"],
        {
            "type": "object",
            "required": ["resource-profile", "copilot-setup-steps", "rescue-comment"],
            "additionalProperties": False,
            "properties": {
                "resource-profile": {
                    "type": "object",
                    "required": ["runs-on", "permissions", "timeout-minutes", "steps"],
                    "properties": {
                        "runs-on": {"type": ["string", "array", "object"]},
                        "permissions": {"const": {"contents": "read"}},
                        "timeout-minutes": {"type": "integer", "minimum": 1, "maximum": 59},
                        "steps": {"type": "array", "minItems": 1},
                    },
                },
                "copilot-setup-steps": {
                    "type": "object",
                    "required": ["runs-on", "permissions", "timeout-minutes", "steps"],
                    "properties": {
                        "runs-on": {"type": ["string", "array", "object"]},
                        "permissions": {
                            "const": {
                                "contents": "read",
                                "actions": "write",
                                "issues": "write",
                                "pull-requests": "write",
                            }
                        },
                        "timeout-minutes": {"type": "integer", "minimum": 1, "maximum": 59},
                        "steps": {"type": "array", "minItems": 1},
                    },
                },
                "rescue-comment": {
                    "type": "object",
                    "required": ["runs-on", "permissions", "timeout-minutes", "steps"],
                    "properties": {
                        "runs-on": {"type": ["string", "array", "object"]},
                        "permissions": {"const": {"pull-requests": "write", "issues": "write"}},
                        "timeout-minutes": {"type": "integer", "minimum": 1, "maximum": 59},
                        "steps": {"type": "array", "minItems": 1},
                    },
                },
            },
        },
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "extra_job",
        "runner",
        "timeout",
        "permissions",
        "export",
        "env_sort",
        "printenv",
        "baseline_env_sort",
        "malformed_checkout",
    ],
)
def test_baseline_guard_rejects_compatibility_and_dump_regressions(tmp_path, mutation):
    data = yaml.safe_load(WORKFLOW.read_text())
    job = data["jobs"]["copilot-setup-steps"]
    if mutation == "extra_job":
        data["jobs"]["unexpected"] = {"runs-on": "ubuntu-latest", "steps": []}
    elif mutation == "runner":
        data["jobs"]["resource-profile"]["runs-on"] = "ubuntu-latest"
    elif mutation == "timeout":
        job["timeout-minutes"] = 60
    elif mutation == "permissions":
        job["permissions"]["actions"] = "read"
    elif mutation == "export":
        profile_step = data["jobs"]["resource-profile"]["steps"][1]
        profile_step["run"] = profile_step["run"].replace("--github-output", "--unused")
    elif mutation == "baseline_env_sort":
        environment_step = next(
            step for step in job["steps"] if step.get("name") == "✅ Validate Environment Setup"
        )
        environment_step["run"] = environment_step["run"].replace(
            'env | grep -E "^(CODEX|PYTHON|RAG|CI|GITHUB|COPILOT)" | sort || true',
            "env | sort",
        )
    elif mutation == "malformed_checkout":
        checkout_step = next(
            step
            for step in job["steps"]
            if str(step.get("uses", "")).startswith("actions/checkout@")
        )
        checkout_step["with"] = "invalid"
    else:
        job["steps"].append(
            {
                "name": "Unexecuted unsafe mutation",
                "run": "printenv" if mutation == "printenv" else "env | sort",
            }
        )
    path = tmp_path / "workflow.yml"
    path.write_text(yaml.safe_dump(data))
    report = validate_retained_workflow(path)
    assert report.errors
    if mutation in {"env_sort", "printenv", "baseline_env_sort"}:
        assert any("environment output" in error for error in report.errors)
    if mutation == "malformed_checkout":
        assert "checkout options must be a mapping" in report.errors


@pytest.mark.parametrize("contents", ["[]", "jobs: []", "jobs: ["])
def test_validator_reports_malformed_workflow_structure(tmp_path, contents):
    path = tmp_path / "malformed.yml"
    path.write_text(contents)
    report = validate_retained_workflow(path)
    assert report.errors


def test_validator_reports_malformed_yaml_without_raising(tmp_path):
    path = tmp_path / "malformed.yml"
    path.write_text("jobs: [")
    report = validate_retained_workflow(path)
    assert report.errors[0].startswith("unable to read valid workflow YAML:")


def test_resource_main_exports_real_tool_consumers(tmp_path, monkeypatch):
    output, env, summary = (tmp_path / name for name in ("out", "env", "summary"))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "profile",
            "--github-output",
            str(output),
            "--github-env",
            str(env),
            "--summary",
            str(summary),
            "--current-runner-profile",
            "ubuntu-latest",
            "--high-headroom-runner-profile",
            "not-verified-label",
        ],
    )
    monkeypatch.setattr(
        agent_resource_profile,
        "probe_capacity",
        lambda: agent_resource_profile.ResourceCapacity(3072, 2, 64),
    )
    assert agent_resource_profile.main() == 0
    assert "COPILOT_AGENT_WORKERS=1\n" in env.read_text()
    assert "node_heap_mib=1536\n" in output.read_text()
    assert not any(line.startswith("NODE_OPTIONS=") for line in env.read_text().splitlines())
    assert "recommendation only" in summary.read_text()
    assert "Already selected runner label: `ubuntu-latest`" in summary.read_text()


def test_ml_classification_does_not_authorize_assets(tmp_path):
    config = _build_config("ml-heavy", "test", tmp_path)
    assert config["lfs_mode"] == "none"
    assert config["lfs_include_paths"] == []
    assert "runner_profile" not in config["runtime"]


def test_explicit_environment_overrides_task_heuristics(tmp_path, monkeypatch):
    from scripts.ci import environment_preflight

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "preflight",
            "--repo-root",
            str(tmp_path),
            "--task-context",
            "torch rag",
            "--environment-type",
            "documentation",
        ],
    )
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    assert environment_preflight.main() == 0
    config = yaml.safe_load((tmp_path / ".codex/agent_environment_config.yaml").read_text())
    assert config["environment_type"] == "documentation"
    assert config["lfs_include_paths"] == []


def test_sklearn_import_mapping(monkeypatch):
    seen = []
    monkeypatch.setattr("importlib.util.find_spec", lambda name: seen.append(name))
    assert _detect_missing_runtime_dependencies(["scikit-learn>=1"])
    assert seen == ["sklearn"]


def test_failed_setup_cannot_be_reported_ready(tmp_path):
    result = agent_setup_readiness.report(
        tmp_path,
        {
            "ASSET_OUTCOME": "failure",
            "PYTHON_OUTCOME": "skipped",
            "INTENT_OUTCOME": "success",
        },
    )
    assert result["status"] == "not-ready"


def test_optional_context_absence_is_partial_not_fake_ready(tmp_path):
    status = tmp_path / ".codex/lfs_assets_status.json"
    status.parent.mkdir()
    status.write_text(json.dumps({"status": "not-requested"}))
    result = agent_setup_readiness.report(
        tmp_path,
        {
            "ASSET_OUTCOME": "success",
            "PYTHON_OUTCOME": "success",
            "INTENT_OUTCOME": "success",
        },
    )
    assert result["status"] == "partial"
    assert result["platform_access"] == "unverified"


def test_optional_scorer_failure_invalidates_stale_output(tmp_path, monkeypatch):
    stale = tmp_path / "patterns.json"
    stale.write_text('{"selected_patterns": [{"name": "stale"}]}')
    monkeypatch.setattr(
        prepare_agent_context.subprocess,
        "run",
        lambda *_a, **_k: type("R", (), {"returncode": 2})(),
    )
    status = prepare_agent_context.prepare(tmp_path, 1)
    assert status["status"] == "unavailable"
    assert not stale.exists()
    assert "no platform prompt attachment" in status["delivery"]


def test_real_scorer_parser_and_artifact(tmp_path):
    result = prepare_agent_context.prepare(tmp_path, 10)
    assert result["status"] == "available"
    assert len((tmp_path / "context.md").read_text()) <= 6001
    assert "not instructions or authorization" in (tmp_path / "context.md").read_text()


def test_optional_context_opt_out_does_not_invoke_scorer(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_CONTEXT_ENABLED", "false")
    monkeypatch.setattr(
        prepare_agent_context.subprocess, "run", lambda *_a, **_k: pytest.fail("disabled")
    )
    assert prepare_agent_context.prepare(tmp_path, 1)["status"] == "disabled"


def test_historical_flags_are_not_platform_bootstrap_requirements(tmp_path, monkeypatch):
    from scripts.ci import promotion_readiness_gate

    snapshot = tmp_path / ".codex/agent_context.json"
    snapshot.parent.mkdir()
    snapshot.write_text(
        json.dumps(
            {
                "COPILOT_AGENT_CCA_VERSION_LOCK": "historical-experimental",
                "COPILOT_AGENT_DEDUPLICATION_ENABLED": False,
            }
        )
    )
    monkeypatch.setattr(promotion_readiness_gate, "REPO_ROOT", tmp_path)
    assert all(item["pass"] for item in promotion_readiness_gate.check_governance_vars())
