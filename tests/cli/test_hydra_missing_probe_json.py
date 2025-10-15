from __future__ import annotations

import json
import subprocess
import sys

SCRIPT = """
import sys
sys.modules['hydra'] = None
sys.modules['omegaconf'] = None
import codex_ml.cli.hydra_main as hydra_main
result = hydra_main.main(['--probe-json'])
code = result if isinstance(result, int) else 0
sys.exit(code)
"""


def test_probe_json_with_hydra_missing() -> None:
    proc = subprocess.run(
        [sys.executable, "-c", SCRIPT],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload.get("component") == "codex-train"
    assert payload.get("ok") in {True, False}
    assert "Traceback" not in (proc.stderr or "")
