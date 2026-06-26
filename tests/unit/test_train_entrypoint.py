"""
Test Train Entrypoint

Test module for train entrypoint.
"""

from __future__ import annotations

import pytest

from omegaconf import OmegaConf


def test_train_guard_noop(tmp_path):
    train_module = None
    try:
        import hhg_logistics.train as train_module
    except ImportError:
        pytest.skip("imports failed due to optional deps")

    assert train_module is not None, "train_module must be initialized"
    cfg = OmegaConf.create(
        {
            "train": {
                "enable": False,
                "save_dir": str(tmp_path / "models"),
                "id_column": "id",
                "value_column": "value",
                "seed": 1,
                "batch_size": 1,
                "epochs": 1,
                "lr": 1e-3,
                "log_every_n": 1,
                "save_adapters": False,
                "freeze_base": True,
            },
            "model": {
                "pretrained": "sshleifer/tiny-gpt2",
                "tokenizer": "sshleifer/tiny-gpt2",
                "dtype": "float32",
                "trust_remote_code": False,
                "low_cpu_mem_usage": True,
            },
            "pipeline": {"features": {"output_path": str(tmp_path / "features.csv")}},
        }
    )
    # Handle both decorated and non-decorated main functions across mypy versions
    entrypoint = getattr(train_module.main, "__wrapped__", train_module.main)
    result = entrypoint(cfg)
    assert result == {}, "Result must not be empty"
