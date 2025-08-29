from typing import Any, Dict, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

try:  # optional PEFT
    from peft import LoraConfig, PeftModel, get_peft_model
except Exception:  # pragma: no cover - optional
    LoraConfig = None
    PeftModel = None
    get_peft_model = None


def load_model_and_tokenizer(
    model_name: str,
    *,
    dtype: str = "auto",
    device_map: str = "auto",
    lora: Optional[Dict[str, Any]] = None,
):
    torch_dtype = {
        "auto": None,
        "fp32": torch.float32,
        "fp16": torch.float16,
        "bf16": torch.bfloat16,
    }[dtype]
    tok = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch_dtype, device_map=device_map
    )
    if lora:
        # Apply LoRA adapters when `peft` is available. Missing optional
        # dependencies simply result in the base model being returned.
        if get_peft_model and LoraConfig:
            base_cfg = {
                "r": 8,
                "lora_alpha": 16,
                "lora_dropout": 0.0,
                "bias": "none",
                "task_type": "CAUSAL_LM",
            }
            base_cfg.update(lora)
            cfg = LoraConfig(**base_cfg)
            model = get_peft_model(model, cfg)
        # else: PEFT not installed; silently skip
    return model, tok
