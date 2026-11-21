import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


def test_github_scripts_compile():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required to validate github-script syntax")

    workflow = (
        Path(__file__).resolve().parents[2] / ".github/workflows/copilot-setup-validation.yml"
    )
    jobs = yaml.safe_load(workflow.read_text())["jobs"]
    scripts = [
        step["with"]["script"]
        for job in jobs.values()
        for step in job.get("steps", [])
        if step.get("uses", "").startswith("actions/github-script@")
    ]
    assert scripts
    for script in scripts:
        subprocess.run(
            [
                node,
                "-e",
                "new (Object.getPrototypeOf(async function(){}).constructor)(process.argv[1])",
                script,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
