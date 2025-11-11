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


def test_bestk_keep_last_trim():
    """Test that keep_last=True doesn't leak checkpoints beyond k (P1 fix)"""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        index = td / "index.json"
        
        # Save k=3 checkpoints with metrics [1.0, 2.0, 3.0] (lower is better)
        for step in range(3):
            ckpt = td / f"checkpoint_{step}.pt"
            _fake_save(ckpt)
            update_and_prune(ckpt, metric=float(step + 1), k=3, index_path=index)
        
        # Now save a worse checkpoint (metric=10.0) with keep_last=True
        # This should force it into kept list but then trim back to k=3
        ckpt_worst = td / "checkpoint_worst.pt"
        _fake_save(ckpt_worst)
        res = update_and_prune(ckpt_worst, metric=10.0, k=3, index_path=index, keep_last=True)
        
        # Verify kept list has exactly k=3 entries, not k+1
        assert len(res["kept"]) == 3, f"Expected 3 kept checkpoints, got {len(res['kept'])}"
        
        # Verify the worst checkpoint is kept (keep_last=True)
        kept_paths = {e["path"] for e in res["kept"]}
        assert str(ckpt_worst) in kept_paths, "keep_last should retain the latest checkpoint"
        
        # Verify index file has exactly k entries
        data = json.loads(index.read_text())
        assert len(data["entries"]) == 3, f"Index should have 3 entries, got {len(data['entries'])}"
        
        # Verify one of the previous checkpoints was pruned
        assert len(res["pruned"]) == 1, "Should have pruned exactly 1 checkpoint"