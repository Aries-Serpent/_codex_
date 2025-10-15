"""Model initialization utilities with optional PEFT integration."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils.error_logging import append_error

try:  # pragma: no cover - optional dependency
    from peft import LoraConfig, get_peft_model
except Exception:  # pragma: no cover - runtime guard for lean installs
    LoraConfig = None  # type: ignore[assignment]
    get_peft_model = None  # type: ignore[assignment]

_DTYPE_MAP = {
    "fp32": torch.float32,
    "float32": torch.float32,
    "fp16": torch.float16,
    "float16": torch.float16,
    "bf16": torch.bfloat16,
    "bfloat16": torch.bfloat16,
}


@dataclass(slots=True)
class LoRASettings:
    """Configuration for parameter-efficient fine-tuning."""

    enabled: bool = False
    r: int = 8
    alpha: int = 16
    dropout: float = 0.0
    target_modules: Sequence[str] = field(default_factory=lambda: ("q_proj", "v_proj"))
    bias: str = "none"
    task_type: str = "CAUSAL_LM"


@dataclass(slots=True)
class ModelConfig:
    """Configuration inputs for ``load_model`` and ``load_tokenizer``."""

    model_name: str
    tokenizer_name: str | None = None
    device: str = "auto"
    dtype: str = "float32"
    low_cpu_mem_usage: bool = True
    lora: LoRASettings = field(default_factory=LoRASettings)

    def resolved_tokenizer(self) -> str:
        return self.tokenizer_name or self.model_name


def _resolve_device(device: str) -> str:
    if device.lower() == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def _resolve_dtype(dtype: str) -> torch.dtype:
    dt = _DTYPE_MAP.get(dtype.lower())
    if dt is None:
        append_error(
            "3.1", "resolve dtype", f"Unsupported dtype '{dtype}'", "Falling back to float32"
        )
        return torch.float32
    return dt


def _apply_lora(model: torch.nn.Module, config: LoRASettings) -> torch.nn.Module:
    if not config.enabled:
        return model
    if LoraConfig is None or get_peft_model is None:
        append_error(
            "3.1", "load LoRA", "peft is not installed", "Cannot enable LoRA without the peft extra"
        )
        raise RuntimeError("peft is required for LoRA fine-tuning")
    try:
        lora_cfg = LoraConfig(
            r=config.r,
            lora_alpha=config.alpha,
            lora_dropout=config.dropout,
            target_modules=list(config.target_modules),
            bias=config.bias,
            task_type=config.task_type,
        )
        return get_peft_model(model, lora_cfg)
    except Exception as exc:  # pragma: no cover - defensive guard
        append_error("3.1", "apply LoRA", str(exc), f"target_modules={config.target_modules}")
        raise


def load_model(cfg: ModelConfig) -> torch.nn.Module:
    """Load a Hugging Face model according to ``cfg``.

    The loader respects the requested dtype/device and applies LoRA adapters
    when ``cfg.lora.enabled`` is true.
    """

    torch_dtype = _resolve_dtype(cfg.dtype)
    device = _resolve_device(cfg.device)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            cfg.model_name,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=cfg.low_cpu_mem_usage,
        )
    except Exception as exc:
        append_error("3.1", "load model", str(exc), f"model_name={cfg.model_name}")
        raise
    model = model.to(device)
    model = _apply_lora(model, cfg.lora)
    return model


def load_tokenizer(cfg: ModelConfig) -> AutoTokenizer:
    """Load the tokenizer that pairs with ``cfg``."""

    tokenizer_name = cfg.resolved_tokenizer()
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    except Exception as exc:
        append_error("3.1", "load tokenizer", str(exc), f"tokenizer_name={tokenizer_name}")
        raise
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def load_model_and_tokenizer(cfg: ModelConfig) -> tuple[torch.nn.Module, AutoTokenizer]:
    """Convenience helper returning both model and tokenizer."""

    model = load_model(cfg)
    tokenizer = load_tokenizer(cfg)
    return model, tokenizer
