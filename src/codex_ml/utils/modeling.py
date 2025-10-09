from typing import Any, Dict, Optional, Tuple

from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import

torch, _HAS_TORCH = optional_import("torch")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")
if _HAS_TRANSFORMERS and transformers is not None:
    AutoModelForCausalLM = getattr(transformers, "AutoModelForCausalLM", None)
    AutoTokenizer = getattr(transformers, "AutoTokenizer", None)
    if AutoModelForCausalLM is None or AutoTokenizer is None:  # pragma: no cover - stubbed install
        _HAS_TRANSFORMERS = False
        AutoModelForCausalLM = None  # type: ignore[assignment]
        AutoTokenizer = None  # type: ignore[assignment]
else:  # pragma: no cover - optional dependency
    AutoModelForCausalLM = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]

try:  # optional PEFT
    from peft import LoraConfig, PeftModel, get_peft_model
except Exception:  # pragma: no cover - optional
    LoraConfig = None
    PeftModel = None
    get_peft_model = None


def _get_registry_factory(name: str):
    try:
        from codex_ml.models.loader_registry import get_model

        return get_model(name)
    except Exception:
        return None


def _invoke_registry(
    factory,
    *,
    dtype: str,
    device_map: Optional[str],
    lora: Optional[Dict[str, Any]],
) -> Tuple[Any, Any]:
    result = factory(
        dtype=dtype,
        device_map=device_map,
        lora=lora,
        include_tokenizer=True,
    )
    if isinstance(result, tuple) and len(result) == 2:
        return result
    if isinstance(result, dict):
        model = result.get("model")
        tokenizer = result.get("tokenizer")
        if model is not None and tokenizer is not None:
            return model, tokenizer
    model = getattr(result, "model", None)
    tokenizer = getattr(result, "tokenizer", None)
    if model is not None and tokenizer is not None:
        return model, tokenizer
    raise TypeError(
        "Registry factory must return (model, tokenizer) tuple, mapping, or object with 'model'/'tokenizer'."
    )


def load_model_and_tokenizer(
    model_name: str,
    *,
    dtype: str = "auto",
    device_map: str = "auto",
    lora: Optional[Dict[str, Any]] = None,
):
    factory = _get_registry_factory(model_name)
    if factory is not None:
        return _invoke_registry(factory, dtype=dtype, device_map=device_map, lora=lora)

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
