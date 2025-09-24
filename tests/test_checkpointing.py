import pathlib
import tempfile

import pytest

pytest.importorskip("torch")

from src.codex_ml.utils.checkpointing import load_training_checkpoint, save_checkpoint
from torch import nn, optim


def test_checkpoint_roundtrip():
    m = nn.Linear(2, 2)
    opt = optim.SGD(m.parameters(), lr=0.1)
    sch = optim.lr_scheduler.StepLR(opt, 1)
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "ckpt.pt"
        save_checkpoint(str(p), m, opt, sch, epoch=3, extra={"note": "ok"})
        state = load_training_checkpoint(str(p), m, opt, sch)
        assert state.get("epoch") == 3
        assert state.get("extra", {}).get("note") == "ok"
