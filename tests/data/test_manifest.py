from __future__ import annotations

import json
from pathlib import Path

from codex_ml.data.checksums import _sha256_file, manifest_for_paths


def test_manifest_stable_and_changes_on_tamper(tmp_path: Path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.bin"
    a.write_text("hello codex\n")
    b.write_bytes(b"\x00\x01\x02\x03")
    out = tmp_path / "artifacts/data_manifest.jsonl"
    manifest_for_paths([a, b], out)
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 2
    rows = [json.loads(L) for L in lines]
    # sha matches helper
    for r in rows:
        p = Path(r["path"])
        assert r["sha256"] == _sha256_file(p)
        assert r["bytes"] == p.stat().st_size
    # tamper 'a' and see changed checksum
    a.write_text("HELLO CODEX!\n")
    manifest_for_paths([a], out)  # overwrite with just 'a'
    tampered = json.loads(out.read_text().strip())
    assert tampered["sha256"] == _sha256_file(a)

