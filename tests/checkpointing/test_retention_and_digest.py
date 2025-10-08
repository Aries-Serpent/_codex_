from __future__ import annotations

import hashlib
import json
from pathlib import Path

from codex_ml.utils import checkpoint_core


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_retention_keeps_last_epochs(tmp_path) -> None:
    root = tmp_path / "checkpoints"
    for epoch in range(4):
        out_dir = root / f"epoch-{epoch}"
        checkpoint_core.save_checkpoint(
            out_dir,
            payload={"model_state": {"epoch": epoch}},
            metadata={"metrics": {"val_loss": float(epoch)}},
            keep_last=2,
        )
    remaining = sorted(p.name for p in root.iterdir() if p.is_dir())
    assert remaining == ["epoch-2", "epoch-3"]

    latest = root / "epoch-3"
    state_file = latest / "state.pt"
    meta = json.loads((latest / "metadata.json").read_text(encoding="utf-8"))
    digest_file = (latest / "state.sha256").read_text(encoding="utf-8").strip()
    assert meta["digest_sha256"] == _file_sha256(state_file) == digest_file
