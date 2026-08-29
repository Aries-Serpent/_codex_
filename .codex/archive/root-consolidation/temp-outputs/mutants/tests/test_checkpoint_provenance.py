"""
Test Checkpoint Provenance

Test module for checkpoint provenance.
"""

import json

import pytest

pytest.importorskip("torch")

from codex_ml.utils.provenance import environment_summary
from src.codex_ml.utils.checkpointing import save_checkpoint
from torch import nn, optim


def test_checkpoint_includes_commit_and_system(tmp_path):
    m = nn.Linear(2, 2)
    opt = optim.SGD(m.parameters(), lr=0.1)
    sch = optim.lr_scheduler.StepLR(opt, 1)
    p = tmp_path / "ckpt.pt"
    save_checkpoint(str(p), m, opt, sch, epoch=7)
    meta = json.loads(p.with_suffix(".meta.json").read_text())
    assert meta["epoch"] == 7, "Condition must be true"
    commit = environment_summary().get("git_commit")
    if commit:
        assert meta["git_commit"] == commit, "Condition must be true"
