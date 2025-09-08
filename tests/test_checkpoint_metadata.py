import subprocess
from pathlib import Path

import torch

from codex_ml.utils.checkpointing import save_checkpoint


def test_checkpoint_saves_env_metadata(tmp_path):
    model = torch.nn.Linear(1, 1)
    path = tmp_path / "ckpt.pt"
    save_checkpoint(str(path), model, None, None, epoch=0)
    ckpt = torch.load(path)
    env = ckpt["extra"]["env"]
    repo_root = Path(__file__).resolve().parent.parent
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    assert env["git_commit"] == commit
    assert env["python"]
    assert env["platform"]
