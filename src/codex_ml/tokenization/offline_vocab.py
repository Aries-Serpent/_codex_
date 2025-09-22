"""Lightweight vocabulary-based tokenizer for offline fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Mapping

from .adapter import TokenizerAdapter


class TinyVocabTokenizer(TokenizerAdapter):
    """Tokenizer that maps whitespace-delimited tokens via a static vocab."""

    def __init__(self, vocab: Mapping[str, int], *, unk_token: str = "<unk>") -> None:
        self.vocab = dict(vocab)
        if unk_token not in self.vocab:
            raise ValueError("Unknown token must be present in the vocabulary")
        self.unk_token = unk_token
        self.reverse_vocab = {idx: token for token, idx in self.vocab.items()}
        self.unk_id = self.vocab[unk_token]

    @classmethod
    def from_vocab_file(cls, path: str | Path) -> "TinyVocabTokenizer":
        candidate = Path(path)
        if candidate.is_dir():
            candidate = candidate / "vocab.json"
        if not candidate.exists():
            raise FileNotFoundError(f"Vocabulary file not found: {candidate}")
        data = json.loads(candidate.read_text(encoding="utf-8"))
        if not isinstance(data, dict):  # pragma: no cover - defensive
            raise TypeError("Vocabulary JSON must be a mapping of token -> id")
        vocab = {str(token): int(index) for token, index in data.items()}
        return cls(vocab)

    def encode(self, text: str, **kwargs: object) -> List[int]:  # noqa: D401
        return [self.vocab.get(token, self.unk_id) for token in text.split()]

    def decode(self, tokens: Iterable[int], **kwargs: object) -> str:  # noqa: D401
        return " ".join(self.reverse_vocab.get(int(token), self.unk_token) for token in tokens)

    def batch_encode(self, texts: Iterable[str], **kwargs: object) -> List[List[int]]:  # noqa: D401
        return [self.encode(text) for text in texts]

    def save_pretrained(self, output_dir: str) -> None:  # noqa: D401 - trivial persistence
        target = Path(output_dir)
        target.mkdir(parents=True, exist_ok=True)
        (target / "vocab.json").write_text(json.dumps(self.vocab, indent=2), encoding="utf-8")


__all__ = ["TinyVocabTokenizer"]
