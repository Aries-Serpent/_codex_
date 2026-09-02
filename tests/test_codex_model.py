"""
Test Codex Model

Test module for codex model.
"""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("torch")

import torch

from codex_ml.codex_model import ModelConfig, build_codex_model


def test_build_codex_model_cpu(tmp_path: Path) -> None:
    model = torch.nn.Linear(2, 1)
    ckpt = tmp_path / "checkpoint.pt"
    torch.save(model.state_dict(), ckpt)

    cfg = ModelConfig(base_model_path=ckpt, dtype="float32", device="cpu")
    loaded = build_codex_model(cfg)

    assert next(loaded.parameters()).device.type == "cpu", "type is not valid"
    assert str(next(loaded.parameters()).dtype).endswith("float32"), "Condition must be true"


def test_build_codex_model_with_lora(tmp_path: Path) -> None:
    if importlib.util.find_spec("peft") is None:
        pytest.skip("peft not installed")

    model = torch.nn.Sequential(torch.nn.Linear(2, 2), torch.nn.Linear(2, 1))
    ckpt = tmp_path / "checkpoint.pt"
    torch.save(model.state_dict(), ckpt)

    cfg = ModelConfig(
        base_model_path=ckpt,
        dtype="float32",
        device="cpu",
        enable_lora=True,
        lora_target_modules=("0", "1"),
    )
    wrapped = build_codex_model(cfg)

    assert any("lora" in name.lower() for name, _ in wrapped.named_parameters())
