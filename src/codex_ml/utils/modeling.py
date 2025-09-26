from typing import Any, Dict, Optional

from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import

torch, _HAS_TORCH = optional_import("torch")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")
if _HAS_TRANSFORMERS:
    AutoModelForCausalLM = transformers.AutoModelForCausalLM  # type: ignore[attr-defined]
    AutoTokenizer = transformers.AutoTokenizer  # type: ignore[attr-defined]
else:  # pragma: no cover - optional dependency
    AutoModelForCausalLM = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]

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
    if not (_HAS_TORCH and _HAS_TRANSFORMERS):
        raise ImportError("torch and transformers are required for model loading")
    torch_dtype = {
        "auto": None,
        "fp32": torch.float32,
        "fp16": torch.float16,
        "bf16": torch.bfloat16,
    }[dtype]
    tok = load_from_pretrained(
        AutoTokenizer,
        model_name,
        use_fast=True,
        revision=get_hf_revision(),
    )
    model = load_from_pretrained(
        AutoModelForCausalLM,
        model_name,
        torch_dtype=torch_dtype,
        device_map=device_map,
        revision=get_hf_revision(),
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
