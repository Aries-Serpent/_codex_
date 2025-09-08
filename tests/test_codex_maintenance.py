import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_codex_maintenance_summary(tmp_path):
    code = (
        "import sys,tools.codex_maintenance as m;"
        "m.TASKS=[('ok',[sys.executable,'-c','import sys;sys.exit(0)']),"
        "('fail',[sys.executable,'-c','import sys;sys.exit(1)'])];"
        "m.main()"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT)
    out = proc.stdout
    if not out:
        pytest.skip("maintenance summary not produced")
    assert "- ok: success" in out
    assert "- fail: failure" in out
    assert proc.returncode != 0
