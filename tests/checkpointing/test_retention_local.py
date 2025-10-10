from __future__ import annotations

import json
from pathlib import Path

from codex_ml.utils.checkpoint_core import save_checkpoint


def test_bestk_and_keep_last(tmp_path: Path) -> None:
    root = tmp_path / "ckpts"
    for epoch in range(5):
        ckpt_dir = root / f"epoch-{epoch:04d}"
        payload = {"value": epoch}
        metadata = {
            "epoch": epoch,
            "metrics": {"val_loss": 1.0 - 0.1 * epoch},
        }
        save_checkpoint(
            ckpt_dir,
            payload=payload,
            metadata=metadata,
            include_rng=False,
            keep_last=2,
            best_k=2,
            best_metric="val_loss",
        )

    dirs = sorted(p.name for p in root.iterdir() if p.is_dir())
    assert dirs == ["epoch-0003", "epoch-0004"]

    index_path = root / "best_index.json"
    assert index_path.exists()
    best_index = json.loads(index_path.read_text(encoding="utf-8"))
    assert len(best_index) <= 2
    for entry in best_index:
        assert entry["path"] in {"epoch-0003", "epoch-0004"}
