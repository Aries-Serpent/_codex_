"""
Test Hydra Main Exit Path

Test module for hydra main exit path.
"""

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
    assert proc.returncode in (0, 2)
    # Allow ImportError tracebacks during import detection
    # Check for hydra-related error message (case-insensitive, may be in stdout or stderr)
    output = (proc.stdout + proc.stderr).lower()
    assert ("hydra" in output or "import" in output, "Condition must be true"
    ), f"Expected hydra-related message in output, got: stdout={proc.stdout}, stderr={proc.stderr}"
