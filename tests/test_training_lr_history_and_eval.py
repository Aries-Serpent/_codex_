import pytest

torch = pytest.importorskip("torch", reason="Requires torch for optimizer / scheduler tests")

from codex_ml.train_loop import run_training  # noqa


def dummy_eval_fn(epoch: int, state):
    # Return simple metric referencing epoch
    return {"epoch_eval_score": epoch * 0.1}


def test_learning_rate_history_and_eval(tmp_path):
    ckpt_dir = tmp_path / "ck"
    ckpt_dir.mkdir()
    res = run_training(
        epochs=3,
        steps_per_epoch=2,
        grad_accum=2,
        checkpoint_dir=str(ckpt_dir),
        scheduler_cfg={"type": "linear", "final_lr_scale": 0.5},
        eval_fn=dummy_eval_fn,
        return_state=True,
    )
    lr_hist = res["learning_rate_history"]
    assert len(lr_hist) == 3
    # Each entry should be a list (param groups)
    assert all(isinstance(entry, list) for entry in lr_hist)
    # Evaluation callback results stored in state epoch_history
    state = res["state"]
    history = state.get("epoch_history")
    assert history and len(history) == 3
    # Ensure eval metric present
    assert "eval" in history[-1]
    assert "epoch_eval_score" in history[-1]["eval"]