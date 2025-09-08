from __future__ import annotations

import json
import os

import yaml

from codex_ml.interfaces import apply_config


def test_apply_config_sets_env(monkeypatch, tmp_path):
    cfg = {
        "tokenizer": "pkg.tokenizer:Tok",
        "reward_model": {"path": "pkg.reward:RM", "kwargs": {"alpha": 1}},
    }
    path = tmp_path / "cfg.yaml"
    path.write_text(yaml.safe_dump(cfg))

    # ensure env vars are clear
    for key in [
        "CODEX_TOKENIZER_PATH",
        "CODEX_REWARD_PATH",
        "CODEX_REWARD_KWARGS",
    ]:
        monkeypatch.delenv(key, raising=False)

    apply_config(str(path))

    assert os.getenv("CODEX_TOKENIZER_PATH") == "pkg.tokenizer:Tok"
    assert os.getenv("CODEX_REWARD_PATH") == "pkg.reward:RM"
    assert json.loads(os.environ["CODEX_REWARD_KWARGS"]) == {"alpha": 1}
