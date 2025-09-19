import json

import pytest

pytest.importorskip("torch")

from torch import nn, optim

from codex_ml.utils.provenance import environment_summary
from src.codex_ml.utils.checkpointing import save_checkpoint


def test_checkpoint_includes_commit_and_system(tmp_path):
    m = nn.Linear(2, 2)
    opt = optim.SGD(m.parameters(), lr=0.1)
    sch = optim.lr_scheduler.StepLR(opt, 1)
    p = tmp_path / "ckpt.pt"
    save_checkpoint(str(p), m, opt, sch, epoch=7)
    meta = json.loads(p.with_suffix(".meta.json").read_text())
    assert meta["epoch"] == 7
    commit = environment_summary().get("git_commit")
    if commit:
        assert meta["git_commit"] == commit
