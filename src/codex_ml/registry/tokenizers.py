"""Tokenizer registry and helpers."""

from __future__ import annotations

from typing import Any, Callable

from codex_ml.registry.base import Registry

tokenizer_registry = Registry("tokenizer", entry_point_group="codex_ml.tokenizers")


@tokenizer_registry.register("hf")
def _build_hf_tokenizer(**kwargs: Any):
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    name_or_path = kwargs.pop("name_or_path", None)
    return HFTokenizerAdapter.load(name_or_path, **kwargs)


def register_tokenizer(name: str, obj: Callable[..., Any] | None = None, *, override: bool = False):
    """Register a tokenizer factory under ``name``."""

    return tokenizer_registry.register(name, obj, override=override)


def get_tokenizer(name: str, **kwargs: Any):
    """Instantiate a tokenizer using the registered factory."""

    factory = tokenizer_registry.get(name)
    if callable(factory):
        return factory(**kwargs)
    if kwargs:
        raise TypeError(f"Tokenizer '{name}' does not accept keyword arguments")
    return factory


def list_tokenizers() -> list[str]:
    return tokenizer_registry.list()


__all__ = ["tokenizer_registry", "register_tokenizer", "get_tokenizer", "list_tokenizers"]
