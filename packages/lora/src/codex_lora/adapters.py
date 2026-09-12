"""Lazy adapters for PEFT and the existing Codex ML LoRA implementation."""

from __future__ import annotations

from importlib import import_module

from .contracts import LoraConfig


class OptionalDependencyError(ImportError):
    """Raised when a requested adapter backend is not installed."""


class PeftBackend:
    """PEFT backend whose heavy dependency is imported only on use."""

    @staticmethod
    def _module():
        try:
            return import_module("peft")
        except (ImportError, AttributeError) as exc:
            raise OptionalDependencyError(
                "PEFT support requires the 'peft' extra: pip install codex-ml-lora[peft]"
            ) from exc

    def apply(
        self,
        model: object,
        config: LoraConfig,
        *,
        adapter_name: str | None = None,
    ) -> object:
        peft = self._module()
        peft_config = peft.LoraConfig(**config.as_backend_kwargs())
        if adapter_name is None:
            return peft.get_peft_model(model, peft_config)
        return peft.get_peft_model(model, peft_config, adapter_name=adapter_name)

    def load(self, model: object, path: str, *, adapter_name: str | None = None) -> object:
        peft = self._module()
        kwargs = {} if adapter_name is None else {"adapter_name": adapter_name}
        return peft.PeftModel.from_pretrained(model, path, **kwargs)


class CodexMlLoraAdapter:
    """Migration adapter around ``codex_ml.peft.peft_adapter.apply_lora``."""

    def apply(
        self,
        model: object,
        config: LoraConfig,
        *,
        adapter_name: str | None = None,
    ) -> object:
        if adapter_name is not None:
            raise ValueError("the legacy Codex ML adapter does not support adapter_name")
        module = import_module("codex_ml.peft.peft_adapter")
        return module.apply_lora(model, config.as_backend_kwargs())

    def load(self, model: object, path: str, *, adapter_name: str | None = None) -> object:
        raise NotImplementedError("the legacy Codex ML adapter does not expose adapter loading")


__all__ = ["CodexMlLoraAdapter", "OptionalDependencyError", "PeftBackend"]
