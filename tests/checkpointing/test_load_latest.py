from __future__ import annotations

from pathlib import Path

import pytest

from codex_ml.utils.checkpointing import CheckpointManager

torch = pytest.importorskip("torch", reason="PyTorch not installed; skipping load_latest tests")


class Tiny(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.layer = torch.nn.Linear(4, 2)


def _random_step(model: Tiny, optimizer: torch.optim.Optimizer) -> None:
    optimizer.zero_grad()
    x = torch.randn(8, 4)
    y = torch.randint(0, 2, (8,))
    loss = torch.nn.CrossEntropyLoss()(model.layer(x), y)
    loss.backward()
    optimizer.step()


def test_load_latest_restores_latest_epoch(tmp_path: Path) -> None:
    root = tmp_path / "ckpts"
    mgr = CheckpointManager(root, keep_last=3, keep_best=1)

    model = Tiny()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.5)

    mgr.save(1, model=model, optimizer=optimizer, scheduler=scheduler)
    _random_step(model, optimizer)
    scheduler.step()
    state_snapshot = {k: v.detach().clone() for k, v in model.state_dict().items()}
    ckpt_dir = mgr.save(2, model=model, optimizer=optimizer, scheduler=scheduler)

    fresh = Tiny()
    fresh_opt = torch.optim.SGD(fresh.parameters(), lr=0.1)
    fresh_sch = torch.optim.lr_scheduler.StepLR(fresh_opt, step_size=1, gamma=0.5)
    info = mgr.load_latest(model=fresh, optimizer=fresh_opt, scheduler=fresh_sch)

    assert info["meta"]["epoch"] == 2
    assert Path(info["path"]) == ckpt_dir
    for name, param in fresh.state_dict().items():
        assert torch.allclose(param, state_snapshot[name])


def test_load_latest_recovers_when_marker_invalid(tmp_path: Path) -> None:
    root = tmp_path / "ckpts"
    mgr = CheckpointManager(root, keep_last=3, keep_best=1)

    model = Tiny()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

    mgr.save(1, model=model, optimizer=optimizer, scheduler=None)
    _random_step(model, optimizer)
    mgr.save(2, model=model, optimizer=optimizer, scheduler=None)

    # Corrupt the marker so discovery must fall back to epoch globbing
    (root / "last").write_text(str(root / "missing"), encoding="utf-8")

    fresh = Tiny()
    fresh_opt = torch.optim.SGD(fresh.parameters(), lr=0.1)
    info = mgr.load_latest(model=fresh, optimizer=fresh_opt, scheduler=None)
    assert info["meta"]["epoch"] == 2
    assert Path(info["path"]).name == "epoch-2"


def test_load_latest_non_strict_returns_empty(tmp_path: Path) -> None:
    mgr = CheckpointManager(tmp_path / "empty")
    result = mgr.load_latest(strict=False)
    assert result == {"meta": {}, "state": False, "path": None}
