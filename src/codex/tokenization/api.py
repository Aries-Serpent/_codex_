"""Compatibility API for legacy `codex.tokenization` imports."""

from __future__ import annotations

from collections.abc import Iterable


class Tokenizer:
    """Small compatibility tokenizer used by legacy tests and imports."""

    def __init__(self, vocab=None, **kwargs):
        self.vocab = dict(vocab or {})
        self.kwargs = kwargs

    def _as_text(self, text):
        if text is None:
            raise TypeError("text cannot be None")
        if isinstance(text, (bytes, bytearray)):
            return text.decode("utf-8", errors="strict")
        return str(text)

    def encode(self, text, *args, **kwargs):
        value = self._as_text(text)
        if value == "":
            return []
        if self.vocab:
            return [self.vocab.get(char, 0) for char in value]
        return [ord(char) for char in value]

    def batch_encode(self, texts, **kwargs):
        if texts is None:
            raise TypeError("texts cannot be None")
        if len(texts) > 1_000_000:
            raise MemoryError("batch too large")
        return [self.encode(text) for text in texts]

    def decode(self, tokens, **kwargs):
        if tokens is None:
            raise TypeError("tokens cannot be None")
        if not tokens:
            return ""
        chars = []
        for token in tokens:
            if isinstance(token, str):
                chars.append(token)
                continue
            value = int(token)
            if value < 0:
                raise ValueError("token id must be non-negative")
            chars.append(chr(value))
        return "".join(chars)


__all__ = ["Tokenizer"]
