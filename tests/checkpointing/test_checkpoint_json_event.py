import json
from pathlib import Path

import torch
import torch.nn as nn

from codex_ml.utils.checkpointing import save_checkpoint


def test_checkpoint_emits_one_json_line(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("CODEX_EMIT_CHECKPOINT_JSON", "1")
    model = nn.Linear(4, 2)
    opt = torch.optim.SGD(model.parameters(), lr=0.01)
    ckpt = tmp_path / "ckpt.pt"

    save_checkpoint(str(ckpt), model, opt, None, epoch=0)

    out_lines = capsys.readouterr().out.strip().splitlines()
    assert out_lines, "no stdout produced"
    evt = json.loads(out_lines[-1])
    assert evt.get("event") == "checkpoint_saved"
    assert Path(evt["path"]).name == ckpt.name
    assert isinstance(evt.get("bytes"), int)
    sha = evt.get("sha256")
    assert isinstance(sha, str) and len(sha) == 64
    assert evt.get("epoch") == 0
