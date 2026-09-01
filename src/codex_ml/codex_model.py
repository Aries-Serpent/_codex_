"""Lightweight model bootstrap helpers for offline training flows.

This module intentionally avoids remote model fetching and keeps the
initialisation path deterministic. It supports loading a local checkpoint,
optionally wrapping the model with a LoRA/PEFT adapter when the dependency is
available.
"""

from __future__ import annotations

import importlib
import importlib.util
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _require_torch() -> Any:
    import importlib

    if importlib.util.find_spec("torch") is None:
        raise ImportError("torch is required to build Codex models in offline mode")
    return importlib.import_module("torch")


def _optional_peft() -> Any | None:
    import importlib

    if importlib.util.find_spec("peft") is None:
        return None
    return importlib.import_module("peft")


def _to_dtype(torch_mod: Any, dtype: str | Any | None) -> Any | None:
    if dtype is None:
        return None
    if isinstance(dtype, getattr(torch_mod, "dtype", type(None))):
        return dtype
    mapping: Mapping[str, Any] = {
        "float16": torch_mod.float16,
        "float32": torch_mod.float32,
        "float64": torch_mod.float64,
        "bfloat16": getattr(torch_mod, "bfloat16", None),
    }
    key = str(dtype).lower()
    if key in mapping and mapping[key] is not None:
        return mapping[key]
    raise ValueError(f"Unsupported dtype: {dtype}")


@dataclass
class ModelConfig:
    """Configuration for building a Codex model instance."""

    base_model_path: str | Path | None
    dtype: str | Any | None = None
    device: str | None = None
    enable_lora: bool = False
    lora_r: int = 4
    lora_alpha: int = 8
    lora_dropout: float = 0.05
    lora_target_modules: tuple[str, ...] = field(default_factory=tuple)
    lora_task_type: str = "FEATURE_EXTRACTION"


def _instantiate_fallback(torch_mod: Any) -> Any:
    # Minimal model to support smoke tests without external checkpoints.
    import torch.nn as nn

    return nn.Sequential(nn.Linear(4, 4), nn.ReLU(), nn.Linear(4, 2))


def _load_checkpoint(torch_mod: Any, config: ModelConfig, map_location: str) -> Any:
    if config.base_model_path is None:
        return _instantiate_fallback(torch_mod)

    path = Path(config.base_model_path)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint not found at {path}")

    checkpoint = torch_mod.load(path, map_location=map_location)
    # Handle both full model objects (legacy) and state_dict (recommended)
    if isinstance(checkpoint, torch_mod.nn.Module):
        return checkpoint
    if isinstance(checkpoint, dict):
        state_dict = checkpoint.get("state_dict") or checkpoint
        model_meta = checkpoint.get("model_meta") or {}
        input_dim = int(model_meta.get("input_dim", 4))
        output_dim = int(model_meta.get("output_dim", 2))
        model = _instantiate_fallback(torch_mod)
        # Adjust final layer if metadata is provided
        if input_dim != 4 or output_dim != 2:
            import torch.nn as nn

            model = nn.Sequential(
                nn.Linear(input_dim, input_dim),
                nn.ReLU(),
                nn.Linear(input_dim, output_dim),
            )
        model.load_state_dict(state_dict, strict=False)
        return model
    raise TypeError(f"Unsupported checkpoint type: {type(checkpoint)}")


def build_codex_model(config: ModelConfig) -> Any:
    """Return a model on the requested device with optional LoRA applied."""

    torch_mod = _require_torch()
    map_location = config.device or "cpu"
    model = _load_checkpoint(torch_mod, config, map_location=map_location)

    target_dtype = _to_dtype(torch_mod, config.dtype)
    if target_dtype is not None:
        model = model.to(dtype=target_dtype)

    if config.device is not None:
        model = model.to(config.device)

    if config.enable_lora:
        peft_mod = _optional_peft()
        if peft_mod is None:
            raise RuntimeError("peft is required when enable_lora=True")
        task_type = getattr(
            peft_mod.TaskType,
            config.lora_task_type,
            peft_mod.TaskType.FEATURE_EXTRACTION,
        )
        lora_cfg = peft_mod.LoraConfig(
            task_type=task_type,
            r=int(config.lora_r),
            lora_alpha=int(config.lora_alpha),
            lora_dropout=float(config.lora_dropout),
            target_modules=list(config.lora_target_modules) or None,
        )
        model = peft_mod.get_peft_model(model, lora_cfg)
    return model
