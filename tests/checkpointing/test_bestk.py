import tempfile, json
from pathlib import Path
import torch
from codex_ml.checkpointing.bestk import update_and_prune

def _fake_save(path: Path):
    torch.save({"state": 1}, path)

def test_bestk_basic():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        index = td / "index.json"
        kept = []
        for step in range(5):
            ckpt = td / f"checkpoint_{step}.pt"
            _fake_save(ckpt)
            res = update_and_prune(ckpt, metric=float(step), k=3, index_path=index)
            kept = res["kept"]
        assert len(kept) <= 3
        # Ensure index reflects ≤ k entries
        data = json.loads(index.read_text())
        assert len(data["entries"]) <= 3

def test_bestk_dry_run():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        index = td / "index.json"
        ckpt = td / "checkpoint_1.pt"
        _fake_save(ckpt)
        res = update_and_prune(ckpt, metric=0.1, k=1, index_path=index, dry_run=True)
        # Index not written
        assert not index.exists()
        assert res["dry_run"] is True