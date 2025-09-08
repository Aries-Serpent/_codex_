import torch

from codex_ml.utils.checkpointing import save_checkpoint


def test_checkpoint_records_git_and_env(tmp_path):
    model = torch.nn.Linear(1, 1)
    opt = torch.optim.SGD(model.parameters(), 0.1)
    path = tmp_path / "ckpt.pt"
    save_checkpoint(str(path), model, opt, None, epoch=0)
    data = torch.load(path)
    extra = data.get("extra", {})
    assert extra.get("git_hash")
    env = extra.get("env")
    assert env and "python" in env
