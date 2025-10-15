from __future__ import annotations

import subprocess
import sys


def test_eval_override_failure_sets_nonzero_exit() -> None:
    script = (
        "import os, sys;"
        "os.environ['CODEX_EVAL_ENTRY'] = 'nonexistent_mod:missing';"
        "import codex_ml.cli.entrypoints as entry;"
        "sys.exit(entry.eval_main())"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "env override failed" in (proc.stderr or "")
    assert "override_failed" in (proc.stderr or "")
