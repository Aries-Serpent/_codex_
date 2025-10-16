from __future__ import annotations

import json
import subprocess
import sys


def test_json_output_stays_on_stdout() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "codex_ml.cli.list_plugins", "--format", "json"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert isinstance(data, dict)
    assert proc.stderr.strip() == ""
