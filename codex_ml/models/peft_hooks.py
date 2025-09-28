from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

try:
    from peft import LoraConfig, get_peft_model  # type: ignore
except Exception:  # ImportError and others
    LoraConfig = None  # type: ignore
    get_peft_model = None  # type: ignore


@dataclass
class LoraBuildCfg:
    r: int = 8
    alpha: int = 16
    dropout: float = 0.0
    target_modules: Optional[list[str]] = None  # e.g., ["q_proj", "v_proj"]
    bias: str = "none"
    task_type: str = "SEQ_CLS"  # kept generic for toy tests


def build_lora(model: Any, cfg: Optional[LoraBuildCfg] = None) -> Any:
    """
    Optionally wrap a model with LoRA adapters.
    If PEFT is not installed, returns the model unchanged.
    """
    if LoraConfig is None or get_peft_model is None:
        return model
    cfg = cfg or LoraBuildCfg()
    lcfg = LoraConfig(
        r=cfg.r,
        lora_alpha=cfg.alpha,
        lora_dropout=cfg.dropout,
        target_modules=cfg.target_modules,
        bias=cfg.bias,
        task_type=cfg.task_type,
    )
    return get_peft_model(model, lcfg)

