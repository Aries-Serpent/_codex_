import subprocess
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from codex_ml.utils.checkpointing import save_checkpoint


def test_checkpoint_records_git_commit(tmp_path):
    class Toy(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.l = torch.nn.Linear(2, 2)

    model = Toy()
    path = tmp_path / "ckpt.pt"
    save_checkpoint(str(path), model, None, None, epoch=0)
    ckpt = torch.load(str(path), weights_only=False)
    extra = ckpt["extra"]
    repo_root = Path(__file__).resolve().parent.parent
    commit = subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True).strip()
    assert extra["git_commit"] == commit
    assert "system" in extra
