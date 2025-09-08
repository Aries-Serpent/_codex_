import json
import subprocess
from pathlib import Path

import torch

from codex_ml.utils.checkpointing import save_checkpoint


class _M:
    def state_dict(self):
        return {"w": torch.tensor([1.0])}


class _O:
    def state_dict(self):
        return {"lr": 0.1}


def test_save_checkpoint_records_provenance(tmp_path):
    path = tmp_path / "ckpt.pt"
    save_checkpoint(str(path), _M(), _O(), scheduler=None, epoch=0, extra=None)
    prov_p = path.parent / "provenance.json"
    assert prov_p.exists()
    data = json.loads(prov_p.read_text())
    root = Path(__file__).resolve().parent.parent
    git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    assert data.get("git_commit") == git_commit
    assert isinstance(data.get("system"), dict)
