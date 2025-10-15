from __future__ import annotations

import subprocess
import sys


def test_codex_eval_dry_run_succeeds() -> None:
    """Ensure eval CLI exits 0 when invoked with --dry-run."""
    code = (
        "import sys, codex_ml.cli.entrypoints as E; "
        "sys.argv=['codex-eval','--dry-run']; "
        "sys.exit(E.eval_main())"
    )
    proc = subprocess.run([sys.executable, "-c", code])
    assert proc.returncode == 0
