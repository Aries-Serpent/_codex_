import json
from pathlib import Path
import pytest

torch = pytest.importorskip("torch", reason="Torch required for resume / optimizer tests")

from codex_ml.train_loop import run_training  # noqa: E402


@pytest.fixture()
def ckpt_tmp(tmp_path):
    return tmp_path / "ckpts"


def test_resume_basic(ckpt_tmp):
    # Initial run: 1 epoch
    result1 = run_training(
        epochs=1,
        checkpoint_dir=str(ckpt_tmp),
        resume=False,
        model_name=None,
        steps_per_epoch=2,
    )
    assert (ckpt_tmp / "epoch-0001").exists()
    latest = json.loads((ckpt_tmp / "latest.json").read_text())
    assert latest["epoch"] == 1
    assert not result1.get("resumed")

    # Second run: extend to 3 epochs with resume
    result2 = run_training(
        epochs=3,
        checkpoint_dir=str(ckpt_tmp),
        resume=True,
        model_name=None,
        steps_per_epoch=2,
    )
    assert result2["resumed"] is True
    assert result2["resumed_from_epoch"] == 1
    # Ensure new epochs created
    assert (ckpt_tmp / "epoch-0002").exists()
    assert (ckpt_tmp / "epoch-0003").exists()
    latest2 = json.loads((ckpt_tmp / "latest.json").read_text())
    assert latest2["epoch"] == 3


def test_resume_flag_without_checkpoint(tmp_path):
    ckpt_dir = tmp_path / "empty"
    ckpt_dir.mkdir()
    result = run_training(
        epochs=2,
        checkpoint_dir=str(ckpt_dir),
        resume=True,
        model_name=None,
        steps_per_epoch=2,
    )
    assert result["start_epoch"] == 1
    assert result["resumed"] is False
    assert (ckpt_dir / "epoch-0001").exists()
    assert (ckpt_dir / "epoch-0002").exists()


def test_optimizer_steps_and_metrics(tmp_path):
    # Build a tiny custom model for gradient updates
    class TinyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(4, 4, bias=False)

        def forward(self, x):
            return self.linear(x)

    model = TinyModel()
    ckpt_dir = tmp_path / "opt"
    ckpt_dir.mkdir()

    res = run_training(
        epochs=2,
        grad_accum=2,
        steps_per_epoch=5,
        model=model,
        checkpoint_dir=str(ckpt_dir),
        resume=False,
        return_state=True,
    )
    # Expected optimizer steps per epoch:
    # steps_per_epoch=5, grad_accum=2 -> full steps floor(5/2)=2 + final leftover step => 3 optimizer steps per epoch
    expected_per_epoch = 3
    assert res["optimizer_steps"] == expected_per_epoch * 2
    assert res["total_steps"] == 2 * 5
    assert res["steps_per_epoch"] == 5
    assert res["grad_accum"] == 2


def test_optimizer_resume_state(tmp_path):
    class TinyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(4, 4, bias=False)

        def forward(self, x):
            return self.linear(x)

    model = TinyModel()
    ckpt_dir = tmp_path / "resume_opt"
    ckpt_dir.mkdir()

    # First run to epoch 1
    res1 = run_training(
        epochs=1,
        steps_per_epoch=4,
        grad_accum=2,
        model=model,
        checkpoint_dir=str(ckpt_dir),
        resume=False,
        return_state=True,
    )
    w_before = model.linear.weight.detach().clone()

    # Resume to epoch 3
    res2 = run_training(
        epochs=3,
        steps_per_epoch=4,
        grad_accum=2,
        model=model,
        checkpoint_dir=str(ckpt_dir),
        resume=True,
        return_state=True,
    )
    w_after = model.linear.weight.detach().clone()

    assert res2["resumed"] is True
    assert res2["resumed_from_epoch"] == 1
    assert not torch.equal(w_before, w_after), "Weights should update after resumed training"
    # Ensure final epoch directory exists
    assert (ckpt_dir / "epoch-0003").exists()