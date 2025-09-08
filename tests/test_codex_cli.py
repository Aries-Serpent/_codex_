import os
import subprocess
import sys

import pytest


def _run(args: list[str]) -> int:
    env = os.environ.copy()
    env["CODEX_CLI_SKIP_PRECOMMIT"] = "1"
    env["CODEX_CLI_SKIP_TESTS"] = "1"
    result = subprocess.run(
        [sys.executable, "tools/codex_cli.py", *args],
        env=env,
        check=False,
    )
    return result.returncode


@pytest.mark.skip(reason="codex_cli tooling unavailable in tests")
def test_cli_lint_smoke():
    assert _run(["lint"]) == 0


@pytest.mark.skip(reason="codex_cli tooling unavailable in tests")
def test_cli_test_smoke():
    assert _run(["test"]) == 0


@pytest.mark.skip(reason="codex_cli tooling unavailable in tests")
def test_cli_audit_smoke():
    assert _run(["audit"]) == 0
