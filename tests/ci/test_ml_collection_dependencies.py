"""Ensure ML jobs install dependencies needed before pytest marker filtering."""

import ast
from pathlib import Path

import pytest
import yaml


@pytest.mark.parametrize("job_name", ["test-ml-components", "test-integration-slow"])
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
    assert job["timeout-minutes"] == 60
