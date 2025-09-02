import random

import torch
from torch.optim import SGD

from codex_ml.utils.checkpointing import (
    CheckpointManager,
    dump_rng_state,
    load_checkpoint,
    load_rng_state,
    save_checkpoint,
    set_seed,
)


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
    epoch, extra = load_checkpoint(str(path), model, opt, sched)
    assert epoch == 5 and extra == {"foo": "bar"}


def test_rng_and_seed(tmp_path):
    state = dump_rng_state()
    a = random.random()
    random.random()
    load_rng_state(state)
    assert random.random() == a
    seeds = set_seed(123, tmp_path)
    assert seeds["python"] == 123 and (tmp_path / "seeds.json").exists()
