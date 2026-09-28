"""
Test Semgrep Rules

Test module for semgrep rules.
"""

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "semgrep_rules"


BAD_CODE = """
import subprocess, pickle, yaml, requests, ast
subprocess.run('ls', shell=True)
eval('1+1')
requests.get('http://example.com')
requests.get('http://example.com', verify=False)
yaml.load('a: b')
pickle.load(open('a','rb'))
"""


def test_semgrep_rules(tmp_path: Path) -> None:
    if shutil.which("semgrep") is None:
        import pytest

        pytest.skip("semgrep not installed")
    bad = tmp_path / "bad.py"
    bad.write_text(BAD_CODE)
    env = os.environ.copy()
    # The repo test runner injects src/ into PYTHONPATH to support local imports,
    # but Semgrep is an external CLI that should not inherit that shadowing when it
    # resolves third-party packages like ``mcp.server.auth``. Strip the project path
    # so the scanner uses the active environment's installed dependencies instead of
    # repo-local partial packages.
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env.setdefault("SEMGREP_COLOR", "never")
    env.setdefault("SEMGREP_DISABLE_LIVE_PROGRESS", "1")
    res = subprocess.run(
        ["semgrep", "--config", str(CONFIG_DIR), str(bad)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    output = f"{res.stdout}\n{res.stderr}" if res.stdout or res.stderr else ""
    assert "semgrep_rules.python.python.requests.no-timeout" in output, "Condition must be true"
    assert "semgrep_rules.py-requests-verify-disabled" in output, "Condition must be true"
    assert "semgrep_rules.py-subprocess-shell-true" in output, "Condition must be true"
    assert "semgrep_rules.py-pickle-load" in output, "Condition must be true"
