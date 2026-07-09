"""
Tokenizers Module

This module provides functionality for tokenizers.

Usage:
    from registry.tokenizers import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import os  # noqa: E402
from collections.abc import Callable, Hashable, Mapping, Sequence  # noqa: E402  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from codex_ml.registry.base import Registry  # noqa: E402
from codex_ml.registry.token_cache import (  # noqa: E402
    GLOBAL_TOKEN_LRU,
    cache_key,
    is_cache_disabled,
)

tokenizer_registry = Registry("tokenizer")
_TOKENIZER_PLUGINS_LOADED = False


def _register_tokenizer_from_plugin(
    name: str,
    obj: Callable[..., Any] | None = None,
    *,
    override: bool = False,
):
    return tokenizer_registry.register(
        name,
        obj,
        override=override,
        source="entry_point",
    )


def init_tokenizer_plugins(*, force: bool = False) -> int:
    """Discover external tokenizers via entry points."""

    global _TOKENIZER_PLUGINS_LOADED

    if force:
        _TOKENIZER_PLUGINS_LOADED = False

    if _TOKENIZER_PLUGINS_LOADED:
        return 0

    try:
        from codex_ml.plugins import load_plugins
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        _TOKENIZER_PLUGINS_LOADED = True
        return 0

    try:
        return load_plugins("codex_ml.tokenizers", register=_register_tokenizer_from_plugin)
    finally:
        _TOKENIZER_PLUGINS_LOADED = True


def _ensure_tokenizer_plugins_loaded() -> None:
    if not _TOKENIZER_PLUGINS_LOADED:
        init_tokenizer_plugins()


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").is_file():
            return parent

    fallback_index = min(3, len(current.parents) - 1)
    return current.parents[fallback_index]


def _resolve_tokenizer_target(
    alias: str,
    kwargs: dict[str, Any],
    *,
    default_remote: str,
    default_subdir: str,
    specific_env: str | None = None,
) -> str:
    provided = kwargs.get("name_or_path")
    if provided:
        candidate = Path(str(provided)).expanduser()
        if candidate.exists():
            return str(candidate)
        raise FileNotFoundError(
            f"Tokenizer assets for '{alias}' expected at {candidate}. Provide a valid path or use the generic 'hf' tokenizer "  # noqa: E501
            "with `local_files_only=false` to download resources."
        )

    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value).expanduser()
            if env_path.exists():
                return str(env_path)
            raise FileNotFoundError(
                f"Environment variable {specific_env} points to {env_path}, but no tokenizer files were found."  # noqa: E501
            )

    offline_root = os.environ.get("CODEX_ML_OFFLINE_MODELS_DIR") or os.environ.get(
        "CODEX_ML_OFFLINE_TOKENIZERS_DIR"
    )
    candidates = []
    if offline_root:
        candidates.append(Path(offline_root).expanduser() / default_subdir)
    candidates.append(_repo_root() / "artifacts" / "models" / default_subdir)

    checked = []
    for candidate in candidates:
        checked.append(str(candidate))
        if candidate.exists():
            return str(candidate)

    raise FileNotFoundError(
        f"Tokenizer assets for '{alias}' not found. Checked: {', '.join(checked) if checked else '<no candidates>'}. "  # noqa: E501
        "Provide `name_or_path` or set CODEX_ML_OFFLINE_MODELS_DIR / CODEX_ML_OFFLINE_TOKENIZERS_DIR."  # noqa: E501
    )


@tokenizer_registry.register("hf")
def _build_hf_tokenizer(**kwargs: Any):
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    name_or_path = kwargs.pop("name_or_path", None)
    return HFTokenizerAdapter.load(name_or_path, **kwargs)


@tokenizer_registry.register("whitespace")
def _build_whitespace_tokenizer(**kwargs: Any):
    from codex_ml.tokenization.adapter import WhitespaceTokenizer

    if kwargs:
        raise TypeError("whitespace tokenizer does not accept configuration parameters")
    return WhitespaceTokenizer()


@tokenizer_registry.register("gpt2-offline")
def _build_offline_gpt2_tokenizer(**kwargs: Any):
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    resolved = _resolve_tokenizer_target(
        "gpt2-offline",
        kwargs,
        default_remote="gpt2",
        default_subdir="gpt2",
        specific_env="CODEX_ML_GPT2_TOKENIZER_PATH",
    )
    local_kwargs = dict(kwargs)
    local_kwargs["name_or_path"] = resolved
    return HFTokenizerAdapter.load(**local_kwargs)


@tokenizer_registry.register("tiny-vocab")
def _build_tiny_vocab_tokenizer(**kwargs: Any):
    from codex_ml.tokenization.offline_vocab import TinyVocabTokenizer

    vocab: Mapping[str, int] | None = kwargs.get("vocab")
    path = kwargs.get("path")
    if vocab:
        unk_token = kwargs.get("unk_token", "<unk>")
        return TinyVocabTokenizer(vocab, unk_token=unk_token)
    if path:
        return TinyVocabTokenizer.from_vocab_file(path)
    raise ValueError("Provide either `vocab` mapping or `path` to build tiny-vocab tokenizer")


@tokenizer_registry.register("tinyllama-offline")
def _build_offline_tinyllama_tokenizer(**kwargs: Any):
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    resolved = _resolve_tokenizer_target(
        "tinyllama-offline",
        kwargs,
        default_remote="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        default_subdir="tinyllama",
        specific_env="CODEX_ML_TINYLLAMA_TOKENIZER_PATH",
    )
    local_kwargs = dict(kwargs)
    local_kwargs["name_or_path"] = resolved
    return HFTokenizerAdapter.load(**local_kwargs)


def register_tokenizer(
    name: str,
    obj: Callable[..., Any] | None = None,
    *,
    override: bool = False,
):
    """Register a tokenizer factory under ``name``."""

    return tokenizer_registry.register(name, obj, override=override)


def get_tokenizer(name: str, **kwargs: Any):
    """Instantiate a tokenizer using the registered factory."""

    _ensure_tokenizer_plugins_loaded()
    factory = tokenizer_registry.get(name)
    if callable(factory):
        return factory(**kwargs)
    if kwargs:
        raise TypeError(f"Tokenizer '{name}' does not accept keyword arguments")
    return factory


def list_tokenizers() -> list[str]:
    _ensure_tokenizer_plugins_loaded()
    return tokenizer_registry.list()


def _normalize_sequence(value: Sequence[Any]) -> list[Any]:
    normalized: list[Any] = []
    for item in value:
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            normalized.append(_normalize_sequence(item))
            continue
        try:
            normalized.append(int(item))
        except (TypeError, ValueError):
            normalized.append(item)
    return normalized


def _freeze_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    frozen: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            frozen[key] = tuple(_normalize_sequence(value))
        else:
            frozen[key] = value
    return frozen


def _clone_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    cloned: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, tuple):
            cloned[key] = [item for item in value]
        else:
            cloned[key] = value
    return cloned


def _call_tokenizer(
    tokenizer: Any,
    text: str,
    *,
    padding: bool | str | None,
    truncation: bool | None,
    max_length: int | None,
    add_special_tokens: bool | None,
    return_tensors: str | None = None,
) -> Mapping[str, Any]:
    kwargs: dict[str, Any] = {}
    if padding is not None:
        kwargs["padding"] = padding
    if truncation is not None:
        kwargs["truncation"] = truncation
    if max_length is not None:
        kwargs["max_length"] = max_length
    if add_special_tokens is not None:
        kwargs["add_special_tokens"] = add_special_tokens
    if return_tensors is not None:
        kwargs["return_tensors"] = return_tensors
    kwargs.setdefault("return_attention_mask", True)
    try:
        encoding = tokenizer(text, **kwargs)
    except TypeError as e:
        type(e).__name__
        logger.debug("TypeError: <ERROR_TYPE>")
        logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
        encode_plus = getattr(tokenizer, "encode_plus", None)
        if callable(encode_plus):
            encoding = encode_plus(text, **kwargs)
        else:
            encode_fn = getattr(tokenizer, "encode", None)
            if callable(encode_fn):
                ids = encode_fn(
                    text,
                    **{k: v for k, v in kwargs.items() if k != "return_attention_mask"},
                )
                if not isinstance(ids, Sequence):
                    raise TypeError("tokenizer.encode must return a sequence of token ids") from e
                normalized_ids = _normalize_sequence(ids)
                attention_mask = [1] * len(normalized_ids)
                return {"input_ids": normalized_ids, "attention_mask": attention_mask}
            raise
    if isinstance(encoding, Mapping):
        return dict(encoding)
    raise TypeError("Tokenizer call must return a mapping of features")


def encode_cached(
    tokenizer: Any,
    text: str,
    *,
    padding: bool | str | None = False,
    truncation: bool | None = False,
    max_length: int | None = None,
    add_special_tokens: bool | None = True,
    return_tensors: str | None = None,
) -> dict[str, Any]:
    """LRU-cached wrapper around tokenizer encodings."""

    identifier: Hashable
    for attr in ("cache_identifier", "name_or_path", "_name_or_path", "identifier"):
        value = getattr(tokenizer, attr, None)
        if value is not None:
            identifier = value
            break
    else:
        identifier = id(tokenizer)
    key = (identifier,) + cache_key(text, padding, truncation, max_length, add_special_tokens)

    if not is_cache_disabled() and GLOBAL_TOKEN_LRU.maxsize > 0:
        cached = GLOBAL_TOKEN_LRU.get(key)
        if cached is not None:
            return _clone_mapping(cached)

    encoding = _call_tokenizer(
        tokenizer,
        text,
        padding=padding,
        truncation=truncation,
        max_length=max_length,
        add_special_tokens=add_special_tokens,
        return_tensors=return_tensors,
    )
    frozen = _freeze_mapping(encoding)

    if not is_cache_disabled() and GLOBAL_TOKEN_LRU.maxsize > 0:
        GLOBAL_TOKEN_LRU.put(key, frozen)
    return _clone_mapping(frozen)


# Public API wrapper for entry point
def build_hf_tokenizer(**kwargs: Any):
    """Public API wrapper for HuggingFace tokenizer builder.

    This is the stable public entry point for building HuggingFace tokenizers.

    Args:
        **kwargs: Configuration parameters passed to HFTokenizerAdapter.load()

    Returns:
        HFTokenizerAdapter instance configured with the provided parameters.
    """
    return _build_hf_tokenizer(**kwargs)


__all__ = [
    "build_hf_tokenizer",
    "encode_cached",
    "get_tokenizer",
    "init_tokenizer_plugins",
    "list_tokenizers",
    "register_tokenizer",
    "tokenizer_registry",
]
