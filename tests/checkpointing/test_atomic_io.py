from __future__ import annotations

from pathlib import Path

from codex_ml.checkpointing.atomic_io import atomic_write_bytes, file_sha256


def test_atomic_bytes_and_sha256(tmp_path: Path) -> None:
    target = tmp_path / "ckpts" / "ep1.pt"
    data = b"hello-world"
    path = atomic_write_bytes(target, data)
    assert path.exists()
    assert path.read_bytes() == data
    digest = file_sha256(path)
    assert len(digest) == 64
