import os
import subprocess
import sys


def _run(args: list[str]) -> int:
    env = os.environ.copy()
    env["CODEX_CLI_SKIP"] = "1"
    return subprocess.run([sys.executable, "tools/codex_cli.py", *args], env=env, check=False).returncode


def test_cli_lint_smoke() -> None:
    assert _run(["lint"]) == 0


def test_cli_test_smoke() -> None:
    assert _run(["test"]) == 0


def test_cli_audit_smoke() -> None:
    assert _run(["audit"]) == 0

