"""
Test Gh Api Wrapper

Test module for gh api wrapper.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_print_curl_redacts_token() -> None:
    env = os.environ.copy()
    env["GH_TOKEN"] = "example-value"
    repo_root = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [
            sys.executable,
            "tools/github/gh_api.py",
            "--method",
            "GET",
            "--path",
            "/repos/Aries-Serpent/_codex_/branches",
            "--print-curl",
        ],
        env=env,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert proc.returncode == 0, "returncode is not valid"
    output = proc.stdout.strip()
    assert "Authorization: token ***REDACTED***" in output, "Condition must be true"
    assert "curl -sS -X GET" in output, "Condition must be true"
    assert "/repos/Aries-Serpent/_codex_/branches" in output, "Condition must be true"
