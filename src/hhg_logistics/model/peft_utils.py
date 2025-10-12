from __future__ import annotations

import logging
from contextlib import suppress
from dataclasses import dataclass

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
    model: torch.nn.Module
    tokenizer: AutoTokenizer


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
    tokenizer_name: str | None = None,
    dtype: str = "float32",
    use_fast: bool | None = None,
    trust_remote_code: bool = False,
    low_cpu_mem_usage: bool = True,
) -> HFModelBundle:
    """Load a Hugging Face causal LM and tokenizer with conservative defaults."""

    if AutoModelForCausalLM is None or AutoTokenizer is None:
        msg = "transformers missing"
        raise ImportError(msg)

    tok_name = tokenizer_name or pretrained
    if use_fast is None:
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                tok_name,
                use_fast=True,
                trust_remote_code=trust_remote_code,
            )
        except ValueError as err:
            logger.info(
                "Falling back to slow tokenizer for %s because fast tokenizer is unavailable: %s",
                tok_name,
                err,
            )
            tokenizer = AutoTokenizer.from_pretrained(
                tok_name,
                use_fast=False,
                trust_remote_code=trust_remote_code,
            )
    else:
        tokenizer = AutoTokenizer.from_pretrained(
            tok_name,
            use_fast=use_fast,
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


def freeze_base_weights(
    model: torch.nn.Module, trainable_substrings: list[str] | None = None
) -> int:
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


def _infer_default_lora_targets(model: torch.nn.Module) -> list[str]:
    """Infer LoRA target modules for a given model.

    The heuristic first consults ``model.config.model_type`` when available so
    we can prioritise architecture-specific conventions (e.g. GPT-2's
    ``c_attn``/``c_proj`` blocks). If that does not resolve a match we fall back
    to scanning the module suffixes for common projection names. A ``ValueError``
    is raised if no suitable targets are discovered so callers can surface a
    helpful error rather than silently training nothing.
    """

    config = getattr(model, "config", None)
    model_type = getattr(config, "model_type", None)

    def _suffixes() -> set[str]:
        return {name.rsplit(".", maxsplit=1)[-1] for name, _ in model.named_modules()}

    suffixes = _suffixes()

    architecture_defaults: dict[str, list[str]] = {
        "gpt2": ["c_attn", "c_proj"],
        "gpt_bigcode": ["c_attn", "c_proj"],
        "llama": ["q_proj", "k_proj", "v_proj", "o_proj"],
        "mistral": ["q_proj", "k_proj", "v_proj", "o_proj"],
        "gpt_neox": ["query_key_value", "dense"],
        "falcon": ["query_key_value", "dense"],
    }

    if isinstance(model_type, str):
        preferred = architecture_defaults.get(model_type.lower())
        if preferred and set(preferred).issubset(suffixes):
            return preferred

    common_candidates: list[list[str]] = [
        ["c_attn", "c_proj"],
        ["q_proj", "k_proj", "v_proj", "o_proj"],
        ["query_key_value", "dense"],
    ]
    for candidate in common_candidates:
        if set(candidate).issubset(suffixes):
            return candidate

    msg = "Unable to infer LoRA target modules for model"
    raise ValueError(msg)


def apply_lora(
    model: torch.nn.Module,
    r: int = 8,
    alpha: int = 16,
    dropout: float = 0.05,
    target_modules: list[str] | None = None,
):
    """Apply LoRA adapters to a causal language model."""

    if LoraConfig is None or get_peft_model is None:
        msg = "peft missing"
        raise ImportError(msg)

    if target_modules is None:
        target_modules = _infer_default_lora_targets(model)

    config = LoraConfig(
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        target_modules=target_modules,
        task_type="CAUSAL_LM",
        bias="none",
    )
    peft_model = get_peft_model(model, config)
    with suppress(Exception):  # pragma: no cover - optional diagnostic
        peft_model.print_trainable_parameters()
    return peft_model


def tokenize_for_causal_lm(
    tokenizer, texts: list[str], max_length: int = 128
) -> tuple[dict, Tensor]:
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
