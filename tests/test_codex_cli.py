import os
import subprocess
import sys
from pathlib import Path


def _run(args: list[str]) -> int:
    env = os.environ.copy()
    env["CODEX_CLI_SKIP_PRECOMMIT"] = "1"
    env["CODEX_CLI_SKIP_TESTS"] = "1"
    script = Path(__file__).resolve().parents[1] / "tools" / "codex_cli.py"
    result = subprocess.run([sys.executable, str(script), *args], env=env, check=False)
    return result.returncode


def test_cli_lint_smoke():
    assert _run(["lint"]) == 0


def test_cli_test_smoke():
    assert _run(["test"]) == 0


def test_cli_audit_smoke():
    assert _run(["audit"]) == 0
