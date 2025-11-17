from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

src_dir = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(src_dir))

spec = importlib.util.spec_from_file_location(
    "training.checkpointing", src_dir / "training" / "checkpointing.py"
)
assert spec and spec.loader
checkpointing = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checkpointing
spec.loader.exec_module(checkpointing)
save_checkpoint = checkpointing.save_checkpoint
load_checkpoint = checkpointing.load_checkpoint

pytest.importorskip("torch")
pytest.importorskip("peft")

from peft import (  # noqa: E402
    LoraConfig,
    TaskType,
    get_peft_model,
    get_peft_model_state_dict,
)

import torch  # noqa: E402  (import after skip checks)


def _make_model() -> torch.nn.Module:
    base = torch.nn.Linear(4, 4)
    cfg = LoraConfig(
        r=2,
        lora_alpha=4,
        lora_dropout=0.0,
        target_modules=["weight"],
        task_type=TaskType.FEATURE_EXTRACTION,
    )
    return get_peft_model(base, cfg)


def test_checkpoint_includes_lora_state(tmp_path: Path):
    model = _make_model()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    state_before = get_peft_model_state_dict(model)

    ckpt_dir = tmp_path / "ckpt"
    save_checkpoint(
        model,
        optimizer,
        epoch=1,
        val_metric=0.1,
        out_dir=ckpt_dir,
        mode="min",
    )
    ckpt_files = list(ckpt_dir.glob("epoch*-metric*.pt"))
    assert ckpt_files, "checkpoint was not written"
    payload = torch.load(ckpt_files[0], map_location="cpu")
    assert "peft_state" in payload
    assert payload["peft_state"], "peft_state payload should not be empty"

    restored = _make_model()
    for name, param in restored.named_parameters():
        if "lora" in name:
            param.data.zero_()
    load_checkpoint(ckpt_files[0], restored, optimizer=None, restore_rng=False)
    state_after = get_peft_model_state_dict(restored)
    assert set(state_before.keys()) == set(state_after.keys())
    for key in state_before:
        assert torch.allclose(state_before[key], state_after[key])
