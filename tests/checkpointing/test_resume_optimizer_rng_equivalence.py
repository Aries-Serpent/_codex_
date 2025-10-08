from __future__ import annotations

import random

from codex_ml.utils import checkpoint_core


def test_resume_optimizer_rng_equivalence(tmp_path) -> None:
    random.seed(1337)
    ckpt_dir = tmp_path / "epoch-1"
    payload = {
        "model_state": {"linear.weight": [1.0, 2.0]},
        "optimizer_state": {"lr": 0.001, "momentum": 0.9},
    }
    metadata = {"metrics": {"val_loss": 0.5}}
    checkpoint_core.save_checkpoint(ckpt_dir, payload=payload, metadata=metadata)

    sequence_after_save = [random.random() for _ in range(4)]
    loaded = checkpoint_core.load_checkpoint(ckpt_dir)
    assert loaded["optimizer_state"] == payload["optimizer_state"]

    rng_payload = loaded.get("_rng")
    assert rng_payload is not None
    checkpoint_core.restore_rng_state(rng_payload)
    sequence_after_restore = [random.random() for _ in range(4)]
    assert sequence_after_restore == sequence_after_save
