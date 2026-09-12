"""Lazy adapters for PEFT and the existing Codex ML LoRA implementation."""

from __future__ import annotations

from collections.abc import Mapping
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
        load_adapter = getattr(model, "load_adapter", None)
        if callable(load_adapter):
            kwargs = {} if adapter_name is None else {"adapter_name": adapter_name}
            load_adapter(path, **kwargs)
            return model
        peft = self._module()
        kwargs = {} if adapter_name is None else {"adapter_name": adapter_name}
        return peft.PeftModel.from_pretrained(model, path, **kwargs)

    def save(self, model: object, path: str, *, adapter_name: str | None = None) -> object:
        """Save all or one PEFT adapter without importing PEFT at package import."""

        save_pretrained = getattr(model, "save_pretrained", None)
        if not callable(save_pretrained):
            raise TypeError("model does not support PEFT adapter persistence")
        kwargs = {} if adapter_name is None else {"selected_adapters": [adapter_name]}
        return save_pretrained(path, **kwargs)

    def activate(self, model: object, adapter_name: str) -> object:
        set_adapter = getattr(model, "set_adapter", None)
        if not callable(set_adapter):
            raise TypeError("model does not support selecting a PEFT adapter")
        set_adapter(adapter_name)
        return model

    def disable(self, model: object) -> object:
        disable_layers = getattr(model, "disable_adapter_layers", None)
        if not callable(disable_layers):
            raise TypeError("model does not support disabling PEFT adapter layers")
        disable_layers()
        return model

    def delete(self, model: object, adapter_name: str) -> object:
        delete_adapter = getattr(model, "delete_adapter", None)
        if not callable(delete_adapter):
            raise TypeError("model does not support deleting a PEFT adapter")
        delete_adapter(adapter_name)
        return model

    def prepare_for_training(
        self,
        model: object,
        *,
        gradient_checkpointing: bool = False,
        gradient_checkpointing_kwargs: Mapping[str, object] | None = None,
    ) -> object:
        """Apply PEFT's quantized-training preparation hook lazily."""

        peft = self._module()
        kwargs = dict(gradient_checkpointing_kwargs or {})
        if "use_gradient_checkpointing" in kwargs:
            raise ValueError(
                "gradient_checkpointing_kwargs must not contain "
                "'use_gradient_checkpointing'; use gradient_checkpointing instead"
            )
        return peft.prepare_model_for_kbit_training(
            model,
            use_gradient_checkpointing=gradient_checkpointing,
            **kwargs,
        )


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
