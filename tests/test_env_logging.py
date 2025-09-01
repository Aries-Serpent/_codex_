import json

from codex_utils.repro import log_env_info
from functional_training import run_functional_training


def test_log_env_info(tmp_path):
    path = tmp_path / "env.json"
    log_env_info(path)
    data = json.loads(path.read_text())
    assert data.get("git_commit")
    assert "packages" in data and data["packages"]


def test_functional_training_logs_env(tmp_path):
    run_functional_training(
        ["hi"],
        [{"prompt": "p", "completion": "c"}],
        [("p", "c", "x", 1)],
        checkpoint_dir=str(tmp_path),
    )
    assert (tmp_path / "env.json").exists()
