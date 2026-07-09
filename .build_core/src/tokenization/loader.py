"""
Loader Module

This module provides functionality for loader.

Usage:
    from tokenization.loader import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from tokenizers import Tokenizer

from transformers import AutoTokenizer, PreTrainedTokenizerFast


def _ensure_special_tokens(
    tokenizer: PreTrainedTokenizerFast,
) -> PreTrainedTokenizerFast:
    """Ensure the tokenizer has padding and EOS tokens configured."""

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token or tokenizer.unk_token or "[PAD]"
    if tokenizer.eos_token is None:
        tokenizer.eos_token = tokenizer.pad_token
    if tokenizer.pad_token_id is None:
        tokenizer.add_special_tokens({"pad_token": tokenizer.pad_token})
    return tokenizer


def _load_from_file(tokenizer_file: Path) -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer.from_file(str(tokenizer_file))
    tokenizer = PreTrainedTokenizerFast(tokenizer_object=tokenizer_obj)
    tokenizer.model_max_length = 512
    return _ensure_special_tokens(tokenizer)


def _load_from_model_name(
    model_name_or_path: str, cache_dir: Path, allow_remote: bool
) -> PreTrainedTokenizerFast:
    from codex_ml.utils.hf_pinning import load_from_pretrained

    tokenizer = load_from_pretrained(  # Uses revision pinning for security
        AutoTokenizer,
        model_name_or_path,
        cache_dir=str(cache_dir),
        local_files_only=not allow_remote,
    )
    return _ensure_special_tokens(tokenizer)


def load_tokenizer(
    config: Mapping[str, Any] | None = None,
    *,
    cache_dir: str | Path = "artifacts/tokenizer_cache",
    allow_remote: bool = False,
) -> PreTrainedTokenizerFast:
    """Load a HuggingFace tokenizer respecting offline defaults.

    Args:
        config: Optional configuration mapping. Recognized keys:
            - ``model_name`` / ``model_name_or_path``: HuggingFace model id or path.
            - ``tokenizer_file`` / ``vocab_file``: Local tokenizer json/vocab path.
        cache_dir: Directory to cache tokenizer assets.
        allow_remote: When ``True``, allow remote downloads; otherwise enforce
            ``local_files_only`` and raise if files are missing.

    Returns:
        A :class:`PreTrainedTokenizerFast` instance with padding and EOS tokens
        ensured.
    """

    cfg: Mapping[str, Any] = config or {}
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)

    tokenizer_file = cfg.get("tokenizer_file") or cfg.get("vocab_file")
    model_name_or_path = cfg.get("model_name") or cfg.get("model_name_or_path")

    if tokenizer_file:
        candidate = Path(tokenizer_file)
        if not candidate.exists():
            raise FileNotFoundError(f"tokenizer file not found: {candidate}")
        return _load_from_file(candidate)

    if model_name_or_path:
        return _load_from_model_name(model_name_or_path, cache_path, allow_remote)

    raise ValueError(
        "Tokenizer configuration must provide 'model_name_or_path' or 'tokenizer_file'."
    )


__all__ = ["load_tokenizer"]
