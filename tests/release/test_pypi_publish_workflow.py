"""Workflow tests for PyPI publishing assurance."""

from __future__ import annotations

from pathlib import Path

import yaml

WORKFLOW_PATH = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "pypi-publish.yml"


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
    assert (
        "--require-hashes -r requirements/lock-release.txt"
        in _step(build_job, "Install build dependencies")["run"]
    )
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
        assert "id-token" not in job["permissions"]
        assert "attestations" not in job["permissions"]
        scripts = [step for step in job["steps"] if "run" in step]
        assert len(scripts) == 1
        assert scripts[0]["name"] == "Verify exact validated artifact checksums"
        assert "sha256sum --check SHA256SUMS" in scripts[0]["run"]
        assert all(step.get("uses") != "actions/checkout@v7" for step in job["steps"])
        assert len(job["steps"]) == 3


def test_job_conditions_are_matrix_free_and_selection_guards_operational_steps() -> None:
    workflow = _load_workflow()
    jobs = workflow["jobs"]

    for job_name, job in jobs.items():
        assert "matrix." not in str(
            job.get("if", "")
        ), f"{job_name} job-level if cannot use matrix context"

    guarded_steps = {
        "publish-testpypi": {"Download artifacts", "Publish to TestPyPI"},
        "publish-pypi": {"Download artifacts", "Publish to PyPI"},
    }
    for job_name, step_names in guarded_steps.items():
        job = jobs[job_name]
        assert "SELECTED_DISTRIBUTION" not in job.get("env", {})
        for step_name in step_names:
            condition = str(_step(job, step_name).get("if", ""))
            assert (
                "matrix.distribution" in condition
            ), f"{job_name}/{step_name} must select its matrix distribution at step level"

    verify_job = jobs["verify-installation"]
    assert "SELECTED_DISTRIBUTION" not in verify_job.get("env", {})
    for step in verify_job["steps"]:
        condition = str(step.get("if", ""))
        assert "matrix.distribution" in condition, (
            "verify-installation/"
            f"{step.get('name', step.get('uses', '<unnamed>'))} must select its matrix "
            "distribution at step level"
        )


def test_selected_distribution_values_are_github_expressions() -> None:
    workflow = _load_workflow()
    for name in ("build", "attest", "validate"):
        selection = workflow["jobs"][name]["env"]["SELECTED_DISTRIBUTION"].strip()
        assert selection.startswith("${{"), name
        assert selection.endswith("}}"), name


def test_post_publish_import_uses_the_verification_virtualenv() -> None:
    workflow = _load_workflow()
    step = _step(workflow["jobs"]["verify-installation"], "Test installed import")
    assert '"$RUNNER_TEMP/verify-${DISTRIBUTION_NAME}/bin/python"' in step["run"]
    assert 'os.environ["IMPORT_NAME"]' in step["run"]
    assert step["env"]["DISTRIBUTION_NAME"] == "${{ matrix.distribution.name }}"


def test_checksums_bind_build_validation_and_publication() -> None:
    jobs = _load_workflow()["jobs"]
    build = _step(jobs["build"], "Record validated artifact checksums")
    assert "sha256sum -- *.whl *.tar.gz > SHA256SUMS" in build["run"]
    assert (
        "sha256sum --check SHA256SUMS"
        in _step(jobs["validate"], "Validate downloaded artifacts")["run"]
    )
    provenance = _step(jobs["attest"], "Generate build provenance")["with"]["subject-path"]
    assert "*.whl" in provenance and "*.tar.gz" in provenance
    for name in ("publish-testpypi", "publish-pypi"):
        steps = _step_names(jobs[name])
        assert steps.index("Verify exact validated artifact checksums") < steps.index(
            "Publish to TestPyPI" if name == "publish-testpypi" else "Publish to PyPI"
        )


def test_exact_artifact_verification_has_no_unpinned_resolution_or_fallback() -> None:
    jobs = _load_workflow()["jobs"]
    job = jobs["verify-installation"]
    assert job["permissions"] == {"contents": "read"}
    download = _step(job, "Download retained validated artifacts")
    assert download["with"] == {
        "name": "python-package-${{ matrix.distribution.name }}",
        "path": "dist/",
    }
    assert (
        "sha256sum --check SHA256SUMS"
        in _step(job, "Create isolated verification environment")["run"]
    )
    for step_name, origin in (("Install from TestPyPI", "testpypi"), ("Install from PyPI", "pypi")):
        command = _step(job, step_name)["run"]
        assert "verify-published" in command
        assert f"--origin {origin}" in command
        assert '--source-sha "$GITHUB_SHA"' in command
        assert "--dist-dir dist" in command
        assert '--python-path "$RUNNER_TEMP/verify-${DISTRIBUTION_NAME}/bin/python"' in command
        assert "pip install" not in command
        assert "--extra-index-url" not in command
    smoke = _step(job, "Test installed import")["run"]
    assert 'cd "$RUNNER_TEMP"' in smoke
    assert 'assurance["verify_installed_artifact"]' in smoke
    assert 'source_sha=os.environ["GITHUB_SHA"]' in smoke
    assert 'origin=os.environ["TARGET_ORIGIN"]' in smoke


def test_all_six_packages_keep_independent_tags_and_flat_artifact_subjects() -> None:
    jobs = _load_workflow()["jobs"]
    expected = {
        "codex-ml": "v",
        "codex-cognitive-sdk": "codex-cognitive-sdk-v",
        "codex-contracts": "codex-contracts-v",
        "codex-ml-evaluation": "codex-ml-evaluation-v",
        "codex-ml-lora": "codex-ml-lora-v",
        "codex-ml-telemetry": "codex-ml-telemetry-v",
    }
    for job in jobs.values():
        assert {
            entry["name"]: entry["release_tag_prefix"] for entry in _distribution_entries(job)
        } == expected
        assert "uses" not in job, "nested workflows are not authorized"
    for name in ("attest", "validate", "publish-testpypi", "publish-pypi"):
        assert _step(jobs[name], "Download artifacts")["with"]["path"] == "dist/"
    subject = _step(jobs["attest"], "Generate build provenance")["with"]["subject-path"]
    assert subject.split() == ["dist/*.whl", "dist/*.tar.gz"]
    assert (
        _step(jobs["publish-testpypi"], "Publish to TestPyPI")["with"]["password"]
        == "${{ secrets.TEST_PYPI_API_TOKEN }}"
    )
    assert (
        _step(jobs["publish-pypi"], "Publish to PyPI")["with"]["password"]
        == "${{ secrets.PYPI_TOKEN }}"
    )


def test_build_checks_functional_wheel_and_sdist_with_explicit_tool_sourcing() -> None:
    jobs = _load_workflow()["jobs"]
    command = _step(jobs["build"], "Install built wheel in isolated virtualenv")["run"]
    assert "install-artifacts" in command
    assert "--build-requirements requirements/lock-release.txt" in command
    assert '--source-sha "$GITHUB_SHA" --origin "$TARGET_ORIGIN"' in command
    identity = _step(jobs["build"], "Record retained build identity")["run"]
    assert "record-build" in identity
    checksums = _step(jobs["build"], "Record validated artifact checksums")["run"]
    assert "sha256sum BUILD_IDENTITY.json >> SHA256SUMS" in checksums
    verify = _step(jobs["validate"], "Verify artifact provenance")["run"]
    assert '--source-digest "$GITHUB_SHA"' in verify
