import subprocess
from pathlib import Path

import torch

from codex_ml.utils.checkpointing import save_checkpoint


def test_checkpoint_records_git_and_env(tmp_path):
    model = torch.nn.Linear(1, 1)
    opt = torch.optim.SGD(model.parameters(), 0.1)
    path = tmp_path / "ckpt.pt"
    save_checkpoint(str(path), model, opt, None, epoch=0)
    data = torch.load(path)
    extra = data.get("extra", {})
    # Expect modern keys saved by provenance utilities
    repo_root = Path(__file__).resolve().parents[1]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    assert extra.get("git_commit") == commit or extra.get("git_hash")
    env = extra.get("system") or extra.get("env") or {}
    assert isinstance(env, dict) and "python" in env and "platform" in env
