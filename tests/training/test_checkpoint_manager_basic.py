from types import SimpleNamespace

import torch
from torch.optim import SGD

from training.checkpoint_manager import CheckpointManager


def test_manager_basic(tmp_path):
    model = torch.nn.Linear(2, 2)
    opt = SGD(model.parameters(), lr=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda _: 1.0)

    mgr = CheckpointManager(tmp_path, save_steps=2, keep_last=1)
    cb = mgr.callback()
    state = SimpleNamespace(global_step=0, epoch=0)
    control = SimpleNamespace()

    cb.on_train_begin(None, state, control, model=model, optimizer=opt, lr_scheduler=sched)
    for step in range(1, 5):
        state.global_step = step
        cb.on_step_end(None, state, control)

    ckpts = list(tmp_path.glob("step-*.pt"))
    assert len(ckpts) == 1
    assert ckpts[0].name == "step-4.pt"
