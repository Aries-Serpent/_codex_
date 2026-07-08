"""
Test Eval Wrapper

Test module for eval wrapper.
"""
from __future__ import annotations
    harness = pytest.importorskip("hhg_logistics.eval.harness")
from pathlib import Path
from omegaconf import OmegaConf






def test_eval_guard(tmp_path, monkeypatch):

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
    assert result == {}, "Result must not be empty"
    assert not Path(cfg.eval.output_json).exists(), "Condition must be true"
