from __future__ import annotations

import subprocess
import sys

SCRIPT = """
import sys
sys.modules['hydra'] = None
sys.modules['omegaconf'] = None
import codex_ml.cli.hydra_main as hydra_main
sys.exit(hydra_main.main())
"""


def test_hydra_missing_exits_cleanly() -> None:
    proc = subprocess.run([sys.executable, "-c", SCRIPT], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr
    assert "hydra-core is required" in proc.stderr
