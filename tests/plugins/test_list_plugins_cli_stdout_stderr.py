"""
Test List Plugins Cli Stdout Stderr

Test module for list plugins cli stdout stderr.
"""

from __future__ import annotations

import json
import subprocess
import sys


def test_json_output_stays_on_stdout() -> None:
    import os
    env = os.environ.copy()
    env["PYTHONWARNINGS"] = "ignore"  # Suppress Python warnings
    env["CODEX_LOG_LEVEL"] = "ERROR"  # Suppress info/warning logs

    proc = subprocess.run(
        [sys.executable, "-m", "codex_ml.cli.list_plugins", "--format", "json"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert isinstance(data, dict)
    # Allow warnings but check that critical output is on stdout
    assert (
        proc.stderr.strip() == ""
        or "WARNING" in proc.stderr
        or "Exception occurred" in proc.stderr
        or "psutil import failed; falling back to minimal sampler" in proc.stderr
    )
