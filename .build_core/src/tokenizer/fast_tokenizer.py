"""
Fast Tokenizer Module

This module provides functionality for fast tokenizer.

Usage:
    from tokenizer.fast_tokenizer import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
from collections.abc import Iterable, Sequence
from pathlib import Path

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    from tokenizers import Tokenizer
except (ImportError, AttributeError):  # pragma: no cover - degrade gracefully
    Tokenizer = None

try:  # pragma: no cover - optional dependency
    from transformers import AutoTokenizer
except (IOError, OSError):  # pragma: no cover - transformers missing is acceptable
    AutoTokenizer = None  # type: ignore[misc,assignment]


class FastTokenizerWrapper:
    """Thin wrapper around HuggingFace ``tokenizers`` with padding helpers."""

    def __init__(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError("tokenizers library not installed")
        if not tokenizer_file:
            raise ValueError("tokenizer_file must be provided")
        self.tokenizer = Tokenizer.from_file(tokenizer_file)

    def encode_batch(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def decode(self, token_ids: Iterable[int]) -> str:
        return self.tokenizer.decode(list(token_ids))

    def encode(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    @property
    def vocab_size(self) -> int:
        """Expose the underlying vocabulary size."""

        return int(self.tokenizer.get_vocab_size())

    def convert_ids_to_tokens(self, token_ids: Iterable[int] | int) -> list[str] | str:
        """Convert ids to tokens mimicking Hugging Face API."""

        if isinstance(token_ids, int):
            return self.tokenizer.id_to_token(int(token_ids))
        return [self.tokenizer.id_to_token(int(idx)) for idx in token_ids]

    def __call__(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=max_length is not None,
            max_length=max_length,
        )
        return {"input_ids": ids}


def build_tokenizer(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = AutoTokenizer.from_pretrained(  # nosec B615
                    str(target), use_fast=True, trust_remote_code=False
                )
                # Ensure pad_token is set; many decoder-only models omit it.
                if tokenizer.pad_token is None and tokenizer.eos_token is not None:  # type: ignore[attr-defined]
                    tokenizer.pad_token = tokenizer.eos_token  # type: ignore[attr-defined]
            except (IOError, OSError) as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except (IOError, OSError) as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise
