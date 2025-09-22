"""Tokenizer registry and helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

from codex_ml.registry.base import Registry

tokenizer_registry = Registry("tokenizer", entry_point_group="codex_ml.tokenizers")


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
            f"Tokenizer assets for '{alias}' expected at {candidate}. Provide a valid path or use the generic 'hf' tokenizer "
            "with `local_files_only=false` to download resources."
        )

    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value).expanduser()
            if env_path.exists():
                return str(env_path)
            raise FileNotFoundError(
                f"Environment variable {specific_env} points to {env_path}, but no tokenizer files were found."
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
        f"Tokenizer assets for '{alias}' not found. Checked: {', '.join(checked) if checked else '<no candidates>'}. "
        "Provide `name_or_path` or set CODEX_ML_OFFLINE_MODELS_DIR / CODEX_ML_OFFLINE_TOKENIZERS_DIR."
    )


@tokenizer_registry.register("hf")
def _build_hf_tokenizer(**kwargs: Any):
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    name_or_path = kwargs.pop("name_or_path", None)
    return HFTokenizerAdapter.load(name_or_path, **kwargs)


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
