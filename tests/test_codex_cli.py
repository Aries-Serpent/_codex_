import os
import subprocess
import sys

import pytest

pytestmark = pytest.mark.skip(reason="codex_cli tool not available in test env")


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


# individual smoke tests skipped via module-level marker
