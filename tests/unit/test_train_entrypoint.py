from __future__ import annotations

from omegaconf import OmegaConf
import pytest


def test_train_guard_noop(tmp_path):
    try:
        import hhg_logistics.train as train_module
    except Exception:
        pytest.skip("imports failed due to optional deps")

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
    result = train_module.main.__wrapped__(cfg)  # type: ignore[attr-defined]
    assert result == {}
