from __future__ import annotations

import subprocess
import sys


def test_names_only_emits_marker_when_empty() -> None:
    cmd = [
        sys.executable,
        "-m",
        "codex_ml.cli.list_plugins",
        "--no-discover",
        "--names-only",
        "--format",
        "text",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    output = proc.stdout.strip()
    assert output == "(none)" or "\n" in output or output == ""
