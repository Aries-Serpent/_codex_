from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence
from typing import Iterable, Sequence

try:  # pragma: no cover - optional dependency
    from tokenizers import Tokenizer
except Exception:  # pragma: no cover - degrade gracefully
    Tokenizer = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from transformers import AutoTokenizer  # type: ignore
except Exception:  # pragma: no cover - transformers missing is acceptable
    AutoTokenizer = None  # type: ignore[assignment]


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

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if padding == "max_length" and max_length is not None:
            if len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
            else:
                ids = ids[:max_length]
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
                tokenizer = AutoTokenizer.from_pretrained(
                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise
