import json
import os

from training.checkpoint_manager import CheckpointManager


def test_best_promotion(tmp_path):
    mgr = CheckpointManager(tmp_path, keep_last=3, metric="eval_perplexity", mode="min")
    payload = b"x"
    vals = [3.0, 2.5, 2.4]
    for step, val in enumerate(vals, start=1):
        mgr.save_now(step, payload, {"eval_perplexity": val})
    best_link = os.readlink(tmp_path / "best")
    assert best_link == "ckpt-3.pt"
    meta = json.loads((tmp_path / "best.json").read_text())
    assert meta["value"] == 2.4 and meta["step"] == 3
