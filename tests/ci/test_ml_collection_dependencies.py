"""Ensure ML jobs install dependencies needed before pytest marker filtering."""

import ast
from pathlib import Path

import pytest
import yaml


@pytest.mark.parametrize("job_name", ["test-ml-components", "integration-shard", "coverage-shard"])
def test_ml_jobs_install_and_preflight_collection_dependencies(job_name):
    workflow_path = Path(__file__).resolve().parents[2] / ".github/workflows/ml-tests.yml"
    workflow = yaml.safe_load(workflow_path.read_text())
    job = workflow["jobs"][job_name]
    install = next(
        step["run"]
        for step in job["steps"]
        if step.get("name") == "Install project and ML runtime dependencies"
    )

    for requirement in (
        '"detect-secrets>=1.5.0"',
        '"hypothesis>=6.165.10,<7.0.0"',
        '"freezegun>=1.5.1"',
    ):
        assert requirement in install
    assert install.index("-m pip install") < install.index("import importlib")

    preflight = install.split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    tree = ast.parse(preflight)
    imports = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert {"detect_secrets", "hypothesis", "freezegun"} <= imports
    assert job["permissions"] == {"contents": "read"}
    assert (
        job["timeout-minutes"]
        == {
            "test-ml-components": 60,
            "integration-shard": 25,
            "coverage-shard": 40,
        }[job_name]
    )


def test_shards_preserve_scope_and_keep_coverage_out_of_integration():
    workflow_path = Path(__file__).resolve().parents[2] / ".github/workflows/ml-tests.yml"
    jobs = yaml.safe_load(workflow_path.read_text())["jobs"]
    integration = next(
        step
        for step in jobs["integration-shard"]["steps"]
        if step.get("name") == "Run integration tests"
    )
    coverage = next(
        step
        for step in jobs["coverage-shard"]["steps"]
        if step.get("name") == "Run non-integration coverage tests"
    )
    assert "tests/integration/" in integration["run"]
    assert '-m "integration"' in integration["run"]
    assert "--cov" not in integration["run"]
    assert "--junitxml=reports/junit.xml" in integration["run"]
    assert "-rfE" in integration["run"]
    assert "tests/" in coverage["run"]
    assert '-m "not slow and not integration"' in coverage["run"]
    assert "--cov=src" in coverage["run"] and "--cov=training" in coverage["run"]
    assert "--cov-fail-under=0" in coverage["run"]  # Partial shards are not the gate.
    # Test failures are gated by the aggregate against the quarantine manifest;
    # missing JUnit or non-test exit codes still fail the shard job.
    assert "--ml-quarantine .codex/baselines/ml_unit_quarantine.json" in coverage["run"]
    assert "set +e" in coverage["run"] and "rc=$?" in coverage["run"]
    assert "reports/pytest-exit-code" in coverage["run"]
    assert "[ ! -s reports/junit.xml ]" in coverage["run"]
    assert '*) echo "::error::pytest exited' in coverage["run"]
    summarize = next(
        step["run"]
        for step in jobs["coverage-shard"]["steps"]
        if step.get("name") == "Summarize coverage shard"
    )
    assert "--report-only" in summarize
    assert coverage["env"]["COVERAGE_FILE"] == ".coverage.unit-${{ matrix.shard }}"
    for name, count in (("integration-shard", 4), ("coverage-shard", 4)):
        job = jobs[name]
        assert job["strategy"]["fail-fast"] is False
        assert len(job["strategy"]["matrix"]["shard"]) == count
        assert job["needs"] == "test-ml-components"
        assert any(
            step.get("if") == "always()" and "Summarize" in step.get("name", "")
            for step in job["steps"]
        )
    aggregate = jobs["ml-slow-aggregate"]
    assert aggregate["name"] == "ml-slow-aggregate"
    assert aggregate["if"] == "always()"
    assert set(aggregate["needs"]) == {"test-ml-components", "integration-shard", "coverage-shard"}
    assert aggregate["permissions"] == {"contents": "read"}
    downloads = [
        step["with"]["pattern"]
        for step in aggregate["steps"]
        if "download-artifact@" in step.get("uses", "")
    ]
    assert downloads == ["int-junit-*", "unit-cov-*"]
    tooling = next(
        step["run"] for step in aggregate["steps"] if step.get("name") == "Install report tooling"
    )
    assert "defusedxml>=0.7.1" in tooling
    steps = {step.get("name"): step for step in aggregate["steps"]}
    gate = steps["Validate shards and enforce combined unit coverage"]["run"]
    assert "--fail-under" not in gate
    assert "--floor-file .codex/baselines/ml_unit_coverage_floor.json" in gate
    assert "--quarantine .codex/baselines/ml_unit_quarantine.json" in gate
    assert aggregate["steps"][0]["with"]["fetch-depth"] == 2
    ratchet = steps["Ratchet quarantine and coverage floor against PR base"]
    assert ratchet["if"] == "always() && github.event_name == 'pull_request'"
    assert "ratchet --base-ref HEAD^1" in ratchet["run"]
    assert (
        "contains(github.event.pull_request.labels.*.name, 'quarantine-approved')"
        in ratchet["env"]["ML_QUARANTINE_GROWTH_APPROVED"]
    )
    push_base = steps["Check out push base baselines"]
    assert "github.event_name == 'push'" in push_base["if"]
    assert "0000000000000000000000000000000000000000" in push_base["if"]
    assert push_base["with"]["ref"] == "${{ github.event.before }}"
    assert push_base["with"]["persist-credentials"] is False
    push_ratchet = steps["Ratchet quarantine and coverage floor against push base"]
    assert push_ratchet["if"] == "always() && github.event_name == 'push'"
    # Approval is never available on push; untrusted values reach the shell via env only.
    assert push_ratchet["env"] == {"PUSH_BEFORE": "${{ github.event.before }}"}
    assert "unset ML_QUARANTINE_GROWTH_APPROVED" in push_ratchet["run"]
    assert '--no-approval --base-ref "${PUSH_BEFORE}"' in push_ratchet["run"]
    assert "::notice::" in push_ratchet["run"]
    for step in aggregate["steps"]:
        assert "${{" not in step.get("run", "")
    assert (
        ".codex/baselines/ml_unit_*.json"
        in yaml.safe_load(workflow_path.read_text())["on"]["push"]["paths"]
    )
    for job in jobs.values():
        assert job["timeout-minutes"] <= 60
        for step in job["steps"]:
            uses = step.get("uses", "")
            assert not uses or uses.startswith("./") or len(uses.split("@", 1)[1]) == 40


def test_ml_repairs_can_be_validated_on_staging_sub_prs():
    workflow_path = Path(__file__).resolve().parents[2] / ".github/workflows/ml-tests.yml"
    workflow = yaml.safe_load(workflow_path.read_text())
    assert "0D_base_" in workflow["on"]["pull_request"]["branches"]
