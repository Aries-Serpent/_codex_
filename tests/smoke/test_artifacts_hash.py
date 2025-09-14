from pathlib import Path

import pytest

from codex_ml.utils.artifacts import compute_sha256, write_hash_sidecar, write_metadata

pytestmark = pytest.mark.smoke


def test_write_hash_and_meta(tmp_path: Path):
    p = tmp_path / "tiny.txt"
    p.write_text("hello world\n", encoding="utf-8")
    digest = compute_sha256(p)
    out_hash = write_hash_sidecar(p)
    meta_path = write_metadata(p, extra={"kind": "test"})
    assert out_hash == digest
    assert (p.with_suffix(".txt.sha256")).exists()
    assert meta_path.exists()
