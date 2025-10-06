from __future__ import annotations

from typing import Iterable, List, Sequence

try:  # pragma: no cover - optional dependency
    from tokenizers import Tokenizer
except Exception:  # pragma: no cover - degrade gracefully
    Tokenizer = None  # type: ignore[assignment]


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
    ) -> List[List[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: List[List[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def decode(self, token_ids: Iterable[int]) -> str:
        return self.tokenizer.decode(list(token_ids))
