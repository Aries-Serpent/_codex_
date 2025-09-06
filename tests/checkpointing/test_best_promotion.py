import json
import os

from training.checkpoint_manager import CheckpointManager


def test_best_promotion(tmp_path):
    mgr = CheckpointManager(tmp_path, keep_last=3, metric="eval_perplexity", mode="min")
    vals = [3.0, 2.5, 2.4]
    for step, val in enumerate(vals, start=1):
        mgr.save_now(step, b"x", {"eval_perplexity": val})
    best_link = tmp_path / "best"
    assert os.readlink(best_link) == "ckpt-3.pt"
    data = json.loads((tmp_path / "best.json").read_text())
    assert data["value"] == 2.4 and data["step"] == 3
