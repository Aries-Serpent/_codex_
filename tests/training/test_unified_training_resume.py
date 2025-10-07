from __future__ import annotations

from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training
from codex_ml.utils.checkpoint_core import save_checkpoint


def test_resume_flag(tmp_path):
    ckpt_dir = tmp_path / "epoch-0"
    save_checkpoint(ckpt_dir, payload={}, metadata={"epoch": 0})
    cfg = UnifiedTrainingConfig(
        model_name="dummy",
        epochs=0,
        output_dir=str(tmp_path / "run2"),
        resume_from=str(ckpt_dir),
    )
    result = run_unified_training(cfg)
    assert result["resume_from"] == str(ckpt_dir)
