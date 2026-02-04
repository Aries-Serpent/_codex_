"""High-level wrapper around causal language models.

The :class:`CodexModel` simplifies device placement, dtype selection and
optional LoRA adapter application.  It intentionally avoids heavy imports at
module import time by relying on optional imports for PyTorch, transformers and
peft.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from codex_ml.modeling.codex_model_loader import load_model_with_optional_lora
from codex_ml.utils.optional import optional_import

_transformers, _HAS_TRANSFORMERS = optional_import("transformers")
_torch, _HAS_TORCH = optional_import("torch")
_peft, _HAS_PEFT = optional_import("peft")

AutoTokenizer = getattr(_transformers, "AutoTokenizer", None)
TokenizerBase = getattr(_transformers, "PreTrainedTokenizerBase", object)
LoraConfig = getattr(_peft, "LoraConfig", None)
get_peft_model: Callable[..., Any] | None = getattr(_peft, "get_peft_model", None)


@dataclass
class LoraOptions:
    """Configuration for LoRA adapter application."""

    r: int = 8
    alpha: float = 16.0
    dropout: float = 0.05
    target_modules: Iterable[str] | None = None
    adapter_path: str | None = None


class CodexModel:
    """Convenience wrapper around Hugging Face causal language models."""

    def __init__(
        self,
        model_name: str,
        *,
        tokenizer_name: str | None = None,
        dtype: str | None = None,
        device: str | None = None,
        tokenizer_kwargs: Mapping[str, Any] | None = None,
        model_kwargs: Mapping[str, Any] | None = None,
        lora: LoraOptions | Mapping[str, Any] | None = None,
        tokenizer: Any | None = None,
        model: Any | None = None,
    ) -> None:
        if not _HAS_TRANSFORMERS:
            raise ImportError("transformers is required to use CodexModel")

        self.model_name = model_name
        self.tokenizer_name = tokenizer_name or model_name
        self._dtype_name = dtype
        self._device_name = device or self._default_device()
        self._tokenizer_kwargs = dict(tokenizer_kwargs or {})
        self._model_kwargs = dict(model_kwargs or {})
        self._lora_cfg = self._normalise_lora(lora)

        self.tokenizer = tokenizer
        self.model = model

    @staticmethod
    def _default_device() -> str:
        if (
            _HAS_TORCH
            and _torch is not None
            and getattr(_torch.cuda, "is_available", lambda: False)()
        ):
            return "cuda"
        return "cpu"

    @staticmethod
    def _normalise_lora(options: LoraOptions | Mapping[str, Any] | None) -> LoraOptions | None:
        if options is None:
            return None
        if isinstance(options, LoraOptions):
            return options
        cfg = dict(options)
        return LoraOptions(
            r=int(cfg.get("r", 8)),
            alpha=float(cfg.get("alpha", cfg.get("lora_alpha", 16.0))),
            dropout=float(cfg.get("dropout", cfg.get("lora_dropout", 0.05))),
            target_modules=cfg.get("target_modules"),
            adapter_path=cfg.get("adapter_path"),
        )

    def init_model(self) -> Any:
        """Initialise the tokenizer and underlying model if needed."""

        if self.model is not None and self.tokenizer is not None:
            return self.model

        if AutoTokenizer is None:
            raise ImportError(
                "AutoTokenizer is unavailable; install transformers with tokenizer support"
            )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.tokenizer_name, **self._tokenizer_kwargs
        )

        lora_enabled = self._lora_cfg is not None and bool(
            self._lora_cfg.adapter_path or get_peft_model
        )
        model_kwargs = dict(self._model_kwargs)
        model_kwargs.setdefault("device_map", None)

        self.model = load_model_with_optional_lora(
            self.model_name,
            dtype=self._dtype_name,
            lora_enabled=lora_enabled,
            lora_path=self._lora_cfg.adapter_path if self._lora_cfg else None,
            lora_r=self._lora_cfg.r if self._lora_cfg else 8,
            lora_alpha=self._lora_cfg.alpha if self._lora_cfg else 16,
            lora_dropout=self._lora_cfg.dropout if self._lora_cfg else 0.05,
            lora_target_modules=(
                list(self._lora_cfg.target_modules)
                if self._lora_cfg and self._lora_cfg.target_modules
                else None
            ),
            **model_kwargs,
        )

        if _HAS_TORCH and _torch is not None:
            self.model = self.model.to(self._device_name)
        return self.model

    def apply_lora(self, **overrides: Any) -> Any:
        """Attach LoRA adapters to the underlying model."""

        if self.model is None:
            self.init_model()
        if not _HAS_PEFT or LoraConfig is None or get_peft_model is None:
            raise ImportError("peft is required to apply LoRA adapters")

        cfg = LoraOptions(**{**(self._lora_cfg.__dict__ if self._lora_cfg else {}), **overrides})
        lora_config = LoraConfig(
            r=cfg.r,
            lora_alpha=cfg.alpha,
            lora_dropout=cfg.dropout,
            target_modules=list(cfg.target_modules) if cfg.target_modules is not None else None,
            task_type="CAUSAL_LM",
        )
        self.model = get_peft_model(self.model, lora_config)
        return self.model

    def prepare_for_inference(self) -> Any:
        """Switch the model to evaluation mode and move it to the target device."""

        if self.model is None:
            self.init_model()
        if self.model is None:
            raise RuntimeError("Model failed to initialise")
        if _HAS_TORCH and _torch is not None:
            self.model = self.model.to(self._device_name)
            self.model.eval()
        return self.model

    def generate(
        self, prompt: str, *, max_tokens: int = 20, temperature: float = 0.8, **kwargs: Any
    ) -> str:
        """Generate text from ``prompt`` using the wrapped model."""

        if not _HAS_TORCH or _torch is None:
            raise ImportError("PyTorch is required for text generation")

        self.prepare_for_inference()
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer failed to initialise")

        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = self._to_device(inputs)
        no_grad = getattr(_torch, "no_grad", None)
        if callable(no_grad):
            with no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                )
        else:  # pragma: no cover - safety fallback for minimal torch builds
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def _to_device(self, inputs: Any) -> Any:
        if hasattr(inputs, "to"):
            return inputs.to(self._device_name)
        if isinstance(inputs, Mapping):
            return {key: self._to_device(value) for key, value in inputs.items()}
        return inputs


__all__ = ["CodexModel", "LoraOptions"]
