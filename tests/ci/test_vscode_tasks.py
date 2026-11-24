"""Regression checks for validation-only workspace tasks."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_frontend_typecheck_requires_installed_typescript(tmp_path: Path) -> None:
    tasks = json.loads((REPO_ROOT / ".vscode/tasks.json").read_text())["tasks"]
    task = next(task for task in tasks if task["label"] == "Codex: frontend typecheck")
    assert task["type"] == "process"
    assert task["command"] == "node"
    assert task["args"] == [
        "${workspaceFolder}/cognitive_app/node_modules/typescript/bin/tsc",
        "--noEmit",
    ]
    assert task["options"]["cwd"] == "${workspaceFolder}/cognitive_app"
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is not installed")
    frontend = tmp_path / "cognitive_app"
    frontend.mkdir()
    args = [arg.replace("${workspaceFolder}", str(tmp_path)) for arg in task["args"]]
    result = subprocess.run([node, *args], cwd=frontend, capture_output=True, text=True, timeout=10)
    assert result.returncode != 0
    assert "MODULE_NOT_FOUND" in result.stderr
    assert not list(frontend.iterdir())


def test_rate_limit_and_auth_tasks_use_canonical_modules() -> None:
    tasks = json.loads((REPO_ROOT / ".vscode/tasks.json").read_text())["tasks"]
    status = next(task for task in tasks if task["label"] == "Codex: GitHub rate-limit status")
    preflight = next(task for task in tasks if task["label"] == "Codex: GitHub auth preflight")

    assert status["args"] == ["-m", "scripts.ci.rate_limit_status", "--json"]
    assert preflight["args"][:2] == ["-m", "scripts.ci.github_auth_preflight"]
    assert preflight["args"][-2:] == ["--branch", "main"]


def test_rust_advisory_task_never_fetches() -> None:
    tasks = json.loads((REPO_ROOT / ".vscode/tasks.json").read_text())["tasks"]
    task = next(task for task in tasks if task["label"].startswith("Codex: Rust advisory check"))
    assert task["type"] == "process"
    assert task["args"][:2] == ["deny", "--frozen"]
