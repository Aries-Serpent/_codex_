from __future__ import annotations

from pathlib import Path

from omegaconf import OmegaConf
import pytest


def test_eval_guard(tmp_path, monkeypatch):
    try:
        import hhg_logistics.eval.harness as harness
    except Exception:
        pytest.skip("lm-eval or transformers missing")

    cfg = OmegaConf.create(
        {
            "eval": {
                "enable": False,
                "output_json": str(tmp_path / "eval.json"),
                "tasks": ["hellaswag:10"],
                "model_args": {"use_accelerate": True, "dtype": "float32"},
                "batch_size": "auto",
                "num_fewshot": None,
                "limit": 5,
            },
            "model": {"pretrained": "sshleifer/tiny-gpt2"},
        }
    )
    result = harness.main.__wrapped__(cfg)  # type: ignore[attr-defined]
    assert result == {}
    assert not Path(cfg.eval.output_json).exists()
