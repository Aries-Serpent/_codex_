from pathlib import Path

import pytest

from codex_ml.utils.checkpointing import CheckpointManager

torch = pytest.importorskip(
    "torch", reason="PyTorch not installed; skipping checkpoint resume tests"
)
pytest.importorskip("torch.nn", reason="torch.nn not available; skipping checkpoint resume tests")


class Tiny(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.l = torch.nn.Linear(4, 3)


def test_resume_roundtrip(tmp_path: Path) -> None:
    model = Tiny()
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    sch = torch.optim.lr_scheduler.StepLR(opt, step_size=1, gamma=0.5)

    ckpt_root = tmp_path / "output" / "checkpoints"
    mgr = CheckpointManager(ckpt_root, keep_last=2, keep_best=1)

    out1 = mgr.save(
        1,
        model=model,
        optimizer=opt,
        scheduler=sch,
        config={"exp": "test"},
        metrics={"val_loss": 0.9},
    )
    assert (out1 / "state.pt").exists()
    assert (ckpt_root / "last").exists()

    # train to change weights
    for _ in range(2):
        x = torch.randn(5, 4)
        y = torch.randint(0, 3, (5,))
        opt.zero_grad()
        loss = torch.nn.CrossEntropyLoss()(model.l(x), y)
        loss.backward()
        opt.step()
        sch.step()

    out2 = mgr.save(2, model=model, optimizer=opt, scheduler=sch, metrics={"val_loss": 0.5})
    assert (out2 / "state.pt").exists()

    fresh = Tiny()
    opt2 = torch.optim.SGD(fresh.parameters(), lr=0.1)
    sch2 = torch.optim.lr_scheduler.StepLR(opt2, step_size=1, gamma=0.5)
    info = mgr.resume_from(out2, model=fresh, optimizer=opt2, scheduler=sch2)
    assert info["state"] is True
    assert info["meta"]["epoch"] == 2


def test_retention_policy(tmp_path: Path) -> None:
    model = Tiny()
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    mgr = CheckpointManager(tmp_path / "output" / "checkpoints", keep_last=2, keep_best=1)
    for e in range(1, 6):
        mgr.save(e, model, opt, metrics={"val_loss": 10 - e})
    epochs = sorted(p.name for p in (tmp_path / "output" / "checkpoints").glob("epoch-*"))
    assert "epoch-5" in epochs and "epoch-4" in epochs
    assert "epoch-3" not in epochs
