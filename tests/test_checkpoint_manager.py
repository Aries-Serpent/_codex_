import json
import random

import pytest

from codex_ml.utils.checkpointing import (
    CheckpointManager,
    dump_rng_state,
    load_rng_state,
    load_training_checkpoint,
    save_checkpoint,
    set_seed,
)

torch = pytest.importorskip("torch")
SGD = torch.optim.SGD


def test_save_and_resume(tmp_path):
    model = torch.nn.Linear(2, 2)
    opt = SGD(model.parameters(), lr=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda _: 1.0)
    mgr = CheckpointManager(tmp_path, keep_last=1, keep_best=1)
    mgr.save(1, model, opt, sched, config={"a": 1}, metrics={"val_loss": 1.0})
    ep2 = mgr.save(2, model, opt, sched, metrics={"val_loss": 0.5})
    assert (tmp_path / "last").read_text() == str(ep2)
    assert not (tmp_path / "epoch-1").exists()
    info = mgr.resume_from(ep2, model, opt, sched)
    assert info["meta"]["epoch"] == 2


def test_save_load_checkpoint(tmp_path):
    model = torch.nn.Linear(1, 1)
    opt = SGD(model.parameters(), lr=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda epoch: 1.0)
    path = tmp_path / "ckpt.pt"
    save_checkpoint(str(path), model, opt, sched, epoch=5, extra={"foo": "bar"})
    state = load_training_checkpoint(str(path), model, opt, sched)
    assert state.get("epoch") == 5
    extra = state.get("extra", {})
    assert extra.get("foo") == "bar"
    # Environment/provenance metadata should be present
    assert "system" in extra or "env" in extra or "git_commit" in extra


def test_rng_and_seed(tmp_path):
    state = dump_rng_state()
    a = random.random()
    random.random()
    load_rng_state(state)
    assert random.random() == a
    seeds = set_seed(123, tmp_path)
    assert seeds["python"] == 123 and (tmp_path / "seeds.json").exists()


def test_checkpoint_resume_restores_rng(tmp_path):
    torch.manual_seed(1234)
    model = torch.nn.Linear(2, 2)
    opt = SGD(model.parameters(), lr=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda _: 1.0)
    mgr = CheckpointManager(tmp_path, keep_last=2, keep_best=2)
    saved_path = mgr.save(1, model, opt, sched, metrics={"val_loss": 1.0})
    expected = torch.rand(1).item()
    torch.manual_seed(0)
    torch.rand(1)
    mgr.resume_from(saved_path, model, opt, sched)
    resumed = torch.rand(1).item()
    assert resumed == expected


def test_checkpoint_best_k_tracking(tmp_path):
    model = torch.nn.Linear(2, 2)
    opt = SGD(model.parameters(), lr=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda _: 1.0)
    mgr = CheckpointManager(tmp_path, keep_last=2, metric="val_loss", mode="min", best_k=2)
    values = [0.6, 0.4, 0.5, 0.3]
    for step, val in enumerate(values, 1):
        mgr.save(step, model, opt, sched, metrics={"val_loss": val})
    data = json.loads((tmp_path / "best.json").read_text(encoding="utf-8"))
    best_values = [item["value"] for item in data.get("items", [])]
    assert best_values == [0.3, 0.4]
    best_dir = tmp_path / "best_candidates"
    assert any(best_dir.iterdir())
    best_link = tmp_path / "best"
    assert best_link.exists()
