"""Convenience wrapper for HuggingFace causal language models."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module, util
from typing import Any, Mapping

_VALID_DTYPES = {"fp32", "fp16", "bf16"}


def _resolve_device(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def _dtype_map(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def _encoding_to_inputs(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(batch)!r}")


@dataclass
class ChatModelConfig:
    """Configuration describing how to instantiate :class:`ChatModel`."""

    model_name: str = "sshleifer/tiny-gpt2"
    tokenizer_name: str | None = None
    dtype: str = "fp32"
    device: str = "auto"
    use_lora: bool = False
    lora_r: int | None = None
    lora_alpha: float | None = None
    lora_dropout: float | None = None
    lora_target_modules: tuple[str, ...] | None = None
    generation_kwargs: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        errors: list[str] = []
        if self.dtype not in _VALID_DTYPES:
            errors.append(f"dtype must be one of {sorted(_VALID_DTYPES)}")
        if self.use_lora and self.lora_r is not None and self.lora_r <= 0:
            errors.append("lora_r must be positive when use_lora is enabled")
        if errors:
            raise ValueError("; ".join(errors))

    def resolved_tokenizer_name(self) -> str:
        return self.tokenizer_name or self.model_name


class ChatModel:
    """High-level helper that owns a model, tokenizer and generation defaults."""

    def __init__(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def _apply_lora(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    @property
    def device(self) -> str:
        return self._device

    @property
    def dtype(self) -> Any:
        return self._dtype

    def generate(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)


__all__ = ["ChatModel", "ChatModelConfig"]
