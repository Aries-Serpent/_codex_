"""Smoke tests for tokenizer.fast_tokenizer utilities."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from tokenizer import fast_tokenizer


class _DummyEncoding:
    def __init__(self, ids: Iterable[int]):
        self.ids = list(ids)


class _DummyTokenizer:
    def __init__(self, path: str):
        self.path = path

    @classmethod
    def from_file(cls, path: str):
        return cls(path)

    def encode_batch(self, texts: list[str]):
        return [_DummyEncoding(range(len(text))) for text in texts]

    def encode(self, text: str):
        return _DummyEncoding(range(len(text)))

    def decode(self, token_ids: Iterable[int]):
        return "decoded"

    def get_vocab_size(self) -> int:  # pragma: no cover - trivial
        return 10

    def id_to_token(self, idx: int) -> str:  # pragma: no cover - trivial
        return f"tok{idx}"


def test_build_tokenizer_missing_file(tmp_path: Path):
    missing = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        fast_tokenizer.build_tokenizer(missing)


def test_fast_tokenizer_wrapper(tmp_path: Path):
    tokenizer_file = tmp_path / "tokenizer.json"
    tokenizer_file.write_text("{}", encoding="utf-8")

    dummy_module = SimpleNamespace(Tokenizer=_DummyTokenizer)

    with (
        patch.dict("sys.modules", {"tokenizers": dummy_module}, clear=False),
        patch.object(fast_tokenizer, "AutoTokenizer", None),
        patch.object(fast_tokenizer, "Tokenizer", _DummyTokenizer),
    ):
        wrapper = fast_tokenizer.build_tokenizer(tokenizer_file)

    assert hasattr(wrapper, "encode")
    encoded = wrapper.encode("hello", padding="max_length", truncation=True, max_length=4)
    assert isinstance(encoded, list)
    assert len(encoded) == 4, "Encoded must not be empty"
