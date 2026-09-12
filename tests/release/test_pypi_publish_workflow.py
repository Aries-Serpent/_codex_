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

    for job_name in ("publish-testpypi", "publish-pypi", "verify-installation"):
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

    assert build_job["permissions"]["attestations"] == "write"
    assert "Validate release artifacts" in step_names
    assert "Install built wheel in isolated virtualenv" in step_names
    assert "Attest release artifacts" in step_names
    assert "Verify build provenance" in step_names
    install_command = _step(
        build_job,
        "Install built wheel in isolated virtualenv",
    )["run"]
    assert '--import-name "$IMPORT_NAME"' in install_command


def test_publish_jobs_validate_tag_and_provenance_before_upload() -> None:
    workflow = _load_workflow()

    testpypi_job = workflow["jobs"]["publish-testpypi"]
    pypi_job = workflow["jobs"]["publish-pypi"]

    assert testpypi_job["permissions"]["attestations"] == "read"
    assert pypi_job["permissions"]["attestations"] == "read"
    assert "Validate downloaded artifacts" in _step_names(testpypi_job)
    assert "Verify artifact provenance" in _step_names(testpypi_job)
    assert "Validate downloaded artifacts" in _step_names(pypi_job)
    assert "Verify release tag matches built version" in _step_names(pypi_job)
    assert "Verify artifact provenance" in _step_names(pypi_job)
    for job in (testpypi_job, pypi_job):
        checkout_index = next(
            index
            for index, step in enumerate(job["steps"])
            if step.get("uses") == "actions/checkout@v7"
        )
        validation_index = _step_names(job).index("Validate downloaded artifacts")
        assert checkout_index < validation_index
        assert job["env"]["GH_TOKEN"] == "${{ github.token }}"
