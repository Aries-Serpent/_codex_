"""
Test Checkpoint Json Event

Test module for checkpoint json event.
"""

import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("torch")

import torch
import torch.nn as nn
from codex_ml.utils.checkpointing import save_checkpoint

# PyTorch 2.x has an issubclass bug with Python 3.12 that prevents pickling
# tensors via legacy serialization (torch/serialization.py:persistent_id).
_TORCH_312_BUG = False
try:
    _TORCH_312_BUG = sys.version_info >= (3, 12) and torch.__version__.startswith("2.")
except AttributeError:
    _TORCH_312_BUG = False  # torch not installed; bug cannot apply


@pytest.mark.skipif(
    _TORCH_312_BUG,
    reason="PyTorch 2.x issubclass() bug with Python 3.12 prevents checkpoint pickling",
)
def test_checkpoint_emits_one_json_line(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("CODEX_EMIT_CHECKPOINT_JSON", "1")
    model = nn.Linear(4, 2)
    opt = torch.optim.SGD(model.parameters(), lr=0.01)
    ckpt = tmp_path / "ckpt.pt"

    save_checkpoint(str(ckpt), model, opt, None, epoch=0)

    out_lines = capsys.readouterr().out.strip().splitlines()
    assert out_lines, "no stdout produced"
    evt = json.loads(out_lines[-1])
    assert evt.get("event") == "checkpoint_saved", "Condition must be true"
    assert Path(evt["path"]).name == ckpt.name, "name is not valid"
    assert isinstance(evt.get("bytes"), int)
    sha = evt.get("sha256")
    assert isinstance(sha, str) and len(sha) == 64
    assert evt.get("epoch") == 0, "Condition must be true"
