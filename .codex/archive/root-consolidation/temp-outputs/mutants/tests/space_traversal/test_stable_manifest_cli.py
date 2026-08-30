"""
Test Stable Manifest Cli

Test module for stable manifest cli.
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = "scripts/space_traversal/stable_manifest.py"


def test_stable_manifest_cli_normalizes(tmp_path: Path):
    a = tmp_path / "out_a"
    b = tmp_path / "out_b"
    a.mkdir()
    b.mkdir()
    (a / "report_20251119_120000").write_text("x")
    (a / "report_20251119_120000.log").write_text("x")
    (b / "report_20251119_120001").write_text("x")
    (b / "report_20251119_120001.log").write_text("x")
    out_a = tmp_path / "man_a.json"
    out_b = tmp_path / "man_b.json"
    cmd_a = [sys.executable, SCRIPT, "--dir", str(a), "--out", str(out_a)]
    cmd_b = [sys.executable, SCRIPT, "--dir", str(b), "--out", str(out_b)]
    res_a = subprocess.run(cmd_a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    res_b = subprocess.run(cmd_b, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert res_a.returncode == 0 and res_b.returncode == 0, "returncode is not valid"
    with open(out_a, "r", encoding="utf-8") as fh:
        ma = json.load(fh)
    with open(out_b, "r", encoding="utf-8") as fh:
        mb = json.load(fh)
    assert ma == mb, "ma is not valid"
