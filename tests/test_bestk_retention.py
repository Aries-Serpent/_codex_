from __future__ import annotations

import json

import pytest

from codex_ml.utils.checkpoint import save_checkpoint

torch = pytest.importorskip("torch")


def test_bestk_retention_prunes_extras(tmp_path):
    model = torch.nn.Linear(2, 2)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    metrics = [0.9, 0.7, 0.5, 0.4]
    for idx, metric in enumerate(metrics, start=1):
        ckpt_dir = tmp_path / f"epoch-{idx}"
        save_checkpoint(
            model=model,
            optimizer=optimizer,
            scheduler=None,
            out_dir=ckpt_dir,
            metadata={"epoch": idx},
            metric_name="eval_loss",
            metric_value=metric,
            best_k=2,
        )

    index_path = tmp_path / "index.json"
    assert index_path.exists()
    index = json.loads(index_path.read_text())
    assert len(index) == 2

    kept_paths = {entry["path"] for entry in index}
    assert kept_paths == {"epoch-3", "epoch-4"}

    # Ensure only retained checkpoints remain on disk.
    existing = {p.name for p in tmp_path.iterdir() if p.is_dir()}
    assert existing == kept_paths
