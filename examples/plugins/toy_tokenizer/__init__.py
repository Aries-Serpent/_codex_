"""Toy tokenizer plugin illustrating registry extension."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import List


@dataclass
class ToyTokenizer:
    vocab: dict[str, int]

    def encode(self, text: str) -> list[int]:
        return [self.vocab.setdefault(ch, len(self.vocab)) for ch in text]

    def decode(self, ids: Iterable[int]) -> str:
        inv = {v: k for k, v in self.vocab.items()}
        return "".join(inv.get(i, "?") for i in ids)


def build(**kwargs):
    vocab = dict(kwargs.get("vocab", {}))
    return ToyTokenizer(vocab=vocab)


__all__ = ["ToyTokenizer", "build"]
