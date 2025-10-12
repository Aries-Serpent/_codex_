from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import torch
    from torch import Tensor
except Exception:  # pragma: no cover - guard for optional deps
    torch = None  # type: ignore
    Tensor = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception:  # pragma: no cover
    AutoModelForCausalLM = None  # type: ignore
    AutoTokenizer = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from peft import LoraConfig, get_peft_model
except Exception:  # pragma: no cover
    LoraConfig = None  # type: ignore
    get_peft_model = None  # type: ignore


@dataclass
class HFModelBundle:
    model: "torch.nn.Module"
    tokenizer: "AutoTokenizer"


def _resolve_dtype(dtype: str):
    if torch is None:
        return None
    dtype_lower = dtype.lower()
    if dtype_lower in {"float16", "fp16"}:
        return torch.float16
    if dtype_lower in {"bfloat16", "bf16"}:
        return torch.bfloat16
    return torch.float32


def load_hf_llm(
    pretrained: str,
    tokenizer_name: Optional[str] = None,
    dtype: str = "float32",
    trust_remote_code: bool = False,
    low_cpu_mem_usage: bool = True,
) -> HFModelBundle:
    """Load a Hugging Face causal LM and tokenizer with conservative defaults."""

    assert AutoModelForCausalLM is not None and AutoTokenizer is not None, "transformers missing"

    tok_name = tokenizer_name or pretrained
    tokenizer = AutoTokenizer.from_pretrained(
        tok_name,
        use_fast=True,
        trust_remote_code=trust_remote_code,
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    torch_dtype = _resolve_dtype(dtype)
    model = AutoModelForCausalLM.from_pretrained(
        pretrained,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=low_cpu_mem_usage,
        trust_remote_code=trust_remote_code,
    )
    return HFModelBundle(model=model, tokenizer=tokenizer)


def freeze_base_weights(model: "torch.nn.Module", trainable_substrings: Optional[List[str]] = None) -> int:
    """Freeze all parameters except those matching provided substrings."""

    if trainable_substrings is None:
        trainable_substrings = ["lora_", "adapter", "grafted"]

    total_params = 0
    trainable_params = 0
    for name, param in model.named_parameters():
        total_params += int(param.numel())
        should_train = any(substr in name for substr in trainable_substrings)
        param.requires_grad = should_train
        if should_train:
            trainable_params += int(param.numel())
    if total_params:
        logger.info(
            "Parameters: total=%s trainable=%s (%.4f%%)",
            total_params,
            trainable_params,
            100 * trainable_params / max(total_params, 1),
        )
    return trainable_params


def apply_lora(
    model: "torch.nn.Module",
    r: int = 8,
    alpha: int = 16,
    dropout: float = 0.05,
    target_modules: Optional[List[str]] = None,
):
    """Apply LoRA adapters to a causal language model."""

    assert LoraConfig is not None and get_peft_model is not None, "peft missing"

    if target_modules is None:
        target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]

    config = LoraConfig(
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        target_modules=target_modules,
        task_type="CAUSAL_LM",
        bias="none",
    )
    peft_model = get_peft_model(model, config)
    try:  # pragma: no cover - optional diagnostic
        peft_model.print_trainable_parameters()
    except Exception:  # pragma: no cover - defensive
        pass
    return peft_model


def tokenize_for_causal_lm(tokenizer, texts: List[str], max_length: int = 128) -> Tuple[dict, "Tensor"]:
    """Tokenize text for causal language modelling with labels mirroring inputs."""

    encoding = tokenizer(
        texts,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors="pt",
    )
    labels = encoding["input_ids"].clone()
    return encoding, labels
