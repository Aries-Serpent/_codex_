"""Ensure ML jobs install dependencies needed before pytest marker filtering."""

import ast
import subprocess
import sys
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
    assert ".[runtime,test-ml-integrations]" in install
    assert "-m pip check" in install
    setup = next(step for step in job["steps"] if step.get("id") == "setup-python")
    assert setup["with"]["extras"] == "runtime,test-ml-integrations"

    preflight = install.split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    tree = ast.parse(preflight)
    imports = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert {
        "detect_secrets",
        "hypothesis",
        "freezegun",
        "sqlparse",
        "nox",
        "mypy",
        "ruff",
        "black",
        "isort",
        "pymysql",
        "imageio",
        "skimage",
        "pywt",
        "cv2",
        "ray",
    } <= imports
    assert job["permissions"] == {"contents": "read"}
    assert (
        job["timeout-minutes"]
        == {
            "test-ml-components": 60,
            "integration-shard": 25,
            "coverage-shard": 40,
        }[job_name]
    )


@pytest.mark.parametrize("job_name", ["test-ml-components", "integration-shard", "coverage-shard"])
def test_ml_preflight_rejects_repo_torch_stub(tmp_path, job_name):
    workflow_path = Path(__file__).resolve().parents[2] / ".github/workflows/ml-tests.yml"
    job = yaml.safe_load(workflow_path.read_text())["jobs"][job_name]
    install = next(
        step["run"]
        for step in job["steps"]
        if step.get("name") == "Install project and ML runtime dependencies"
    )
    preflight = install.split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    script = tmp_path / "preflight.py"
    script.write_text(
        "import importlib\nfrom types import SimpleNamespace\n"
        "importlib.import_module = lambda name: SimpleNamespace(IS_CODEX_STUB=True)\n" + preflight
    )
    process = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert process.returncode == 1
    assert "Real CPU PyTorch is required" in process.stderr


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


def test_ml_repairs_can_be_validated_on_staging_sub_prs():
    workflow_path = Path(__file__).resolve().parents[2] / ".github/workflows/ml-tests.yml"
    workflow = yaml.safe_load(workflow_path.read_text())
    assert "0D_base_" in workflow["on"]["pull_request"]["branches"]
