"""Workflow tests for PyPI publishing assurance."""

from __future__ import annotations

from pathlib import Path

import yaml

WORKFLOW_PATH = (
    Path(__file__).resolve().parents[2] / ".github" / "workflows" / "pypi-publish.yml"
)


def _load_workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _distribution_entries(job: dict) -> list[dict]:
    return job["strategy"]["matrix"]["distribution"]


def _step_names(job: dict) -> list[str]:
    return [step.get("name", "") for step in job["steps"]]


def _step(job: dict, name: str) -> dict:
    return next(step for step in job["steps"] if step.get("name") == name)


def test_workflow_dispatch_package_options_include_cognitive_sdk() -> None:
    workflow = _load_workflow()
    options = workflow["on"]["workflow_dispatch"]["inputs"]["package"]["options"]

    assert "codex-cognitive-sdk" in options


def test_all_release_jobs_include_cognitive_sdk_distribution() -> None:
    workflow = _load_workflow()

    build_entries = _distribution_entries(workflow["jobs"]["build"])
    assert any(
        entry["name"] == "codex-cognitive-sdk" and entry["path"] == "packages/cognitive_sdk"
        for entry in build_entries
    )

    for job_name in (
        "attest",
        "validate",
        "publish-testpypi",
        "publish-pypi",
        "verify-installation",
    ):
        entries = _distribution_entries(workflow["jobs"][job_name])
        assert any(entry["name"] == "codex-cognitive-sdk" for entry in entries)

    verify_entries = _distribution_entries(workflow["jobs"]["verify-installation"])
    assert any(
        entry["name"] == "codex-cognitive-sdk" and entry["import"] == "codex_cognitive_sdk"
        for entry in verify_entries
    )


def test_build_job_contains_phase5_assurance_steps() -> None:
    workflow = _load_workflow()
    build_job = workflow["jobs"]["build"]
    step_names = _step_names(build_job)

    assert "id-token" not in build_job["permissions"]
    assert "attestations" not in build_job["permissions"]
    assert "Validate release artifacts" in step_names
    assert "Install built wheel in isolated virtualenv" in step_names
    assert "Attest release artifacts" not in step_names
    assert "Verify build provenance" not in step_names
    assert "--require-hashes -r requirements/lock-release.txt" in _step(
        build_job, "Install build dependencies"
    )["run"]
    assert "python -m build --no-isolation" in _step(build_job, "Build package")["run"]
    install_command = _step(
        build_job,
        "Install built wheel in isolated virtualenv",
    )["run"]
    assert '--import-name "$IMPORT_NAME"' in install_command


def test_publish_jobs_validate_tag_and_provenance_before_upload() -> None:
    workflow = _load_workflow()

    attest_job = workflow["jobs"]["attest"]
    validation_job = workflow["jobs"]["validate"]
    testpypi_job = workflow["jobs"]["publish-testpypi"]
    pypi_job = workflow["jobs"]["publish-pypi"]

    assert attest_job["permissions"]["id-token"] == "write"
    assert attest_job["permissions"]["attestations"] == "write"
    assert all("run" not in step for step in attest_job["steps"])

    assert "id-token" not in validation_job["permissions"]
    assert validation_job["permissions"]["attestations"] == "read"
    assert "Validate downloaded artifacts" in _step_names(validation_job)
    assert "Verify release tag matches built version" in _step_names(validation_job)
    assert "Verify artifact provenance" in _step_names(validation_job)

    for job in (testpypi_job, pypi_job):
        assert job["permissions"]["id-token"] == "write"
        assert "attestations" not in job["permissions"]
        assert all("run" not in step for step in job["steps"])
        assert all(step.get("uses") != "actions/checkout@v7" for step in job["steps"])
        assert len(job["steps"]) == 2


def test_job_conditions_are_matrix_free_and_selection_guards_operational_steps() -> None:
    workflow = _load_workflow()
    jobs = workflow["jobs"]

    for job_name, job in jobs.items():
        assert "matrix." not in str(job.get("if", "")), (
            f"{job_name} job-level if cannot use matrix context"
        )

    guarded_steps = {
        "publish-testpypi": {"Download artifacts", "Publish to TestPyPI"},
        "publish-pypi": {"Download artifacts", "Publish to PyPI"},
    }
    for job_name, step_names in guarded_steps.items():
        job = jobs[job_name]
        assert "SELECTED_DISTRIBUTION" not in job.get("env", {})
        for step_name in step_names:
            condition = str(_step(job, step_name).get("if", ""))
            assert "matrix.distribution" in condition, (
                f"{job_name}/{step_name} must select its matrix distribution at step level"
            )

    verify_job = jobs["verify-installation"]
    assert "SELECTED_DISTRIBUTION" not in verify_job.get("env", {})
    for step in verify_job["steps"]:
        condition = str(step.get("if", ""))
        assert "matrix.distribution" in condition, (
            "verify-installation/"
            f"{step.get('name', step.get('uses', '<unnamed>'))} must select its matrix "
            "distribution at step level"
        )
