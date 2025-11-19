import json
import subprocess
import sys
from pathlib import Path
import pytest

DECODE_SCRIPT = "scripts/space_traversal/decode_validate_and_extract.py"
EXTRACT_SCRIPT = "scripts/space_traversal/extract_validate_gaps.py"
FIXTURE = "tests/fixtures/pasted.txt"

@pytest.mark.skipif(not Path(FIXTURE).exists(), reason="pasted fixture missing")
def test_decode_and_extract(tmp_path: Path):
    out_dir = tmp_path / "extracted"
    cmd = [sys.executable, DECODE_SCRIPT, "--input", FIXTURE, "--out-dir", str(out_dir), "--stable-output"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert res.returncode == 0
    decoded = out_dir / "validate_decoded.json"
    gaps = out_dir / "gaps_extracted.json"
    summary = out_dir / "gaps_summary.md"
    assert decoded.exists()
    assert gaps.exists()
    assert summary.exists()
    with open(gaps, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, list)
