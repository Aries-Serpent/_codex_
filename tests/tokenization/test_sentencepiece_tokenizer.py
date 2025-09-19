#!/usr/bin/env python3
"""Tests for the SentencePieceTokenizer adapter."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

if "transformers" not in sys.modules:

    class _TokenizerStub:
        pad_token_id = 0
        eos_token_id = 0
        pad_token = "<pad>"
        eos_token = "<eos>"
        vocab_size = 1
        name_or_path = "stub-tokenizer"

        def encode(self, text, **kwargs):
            max_length = kwargs.get("max_length") or 1
            tokens = [0] * min(len(text.split()), max_length)
            if kwargs.get("padding") in {True, "max_length"} and max_length:
                tokens = tokens + [0] * max(0, max_length - len(tokens))
            return tokens or [0]

        def decode(self, ids, **kwargs):
            return " ".join("token" for _ in ids)

        def add_special_tokens(self, *args, **kwargs):
            return None

        def save_pretrained(self, *args, **kwargs):
            return None

        def batch_encode_plus(self, texts, **kwargs):
            items = list(texts)
            max_length = kwargs.get("max_length") or 1
            return {"input_ids": [[0] * max_length for _ in items]}

        def convert_tokens_to_ids(self, token):
            return 0

        def __call__(self, inputs, **kwargs):
            max_length = kwargs.get("max_length") or 1
            return {"input_ids": [[0] * max_length for _ in inputs]}

    class _AutoTokenizer:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            return _TokenizerStub()

    sys.modules["transformers"] = SimpleNamespace(
        AutoTokenizer=_AutoTokenizer,
        PreTrainedTokenizerBase=_TokenizerStub,
        IS_CODEX_STUB=True,
    )

from codex_ml.tokenization.adapter import SentencePieceTokenizer, TokenizerAdapter

spm = pytest.importorskip("sentencepiece")


def _train_sentencepiece_model(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(
        "\n".join(
            [
                "hello world",
                "hello there",
                "general kenobi",
                "tokenization adapter",
                "sentence piece tokenizer",
                "batch encode decode",
            ]
        ),
        encoding="utf-8",
    )
    model_prefix = tmp_path / "spm_test"
    spm.SentencePieceTrainer.train(
        input=str(corpus),
        model_prefix=str(model_prefix),
        vocab_size=32,
        character_coverage=1.0,
        model_type="unigram",
        pad_id=0,
        unk_id=1,
        bos_id=2,
        eos_id=3,
        hard_vocab_limit=False,
    )
    return model_prefix.with_suffix(".model")


def test_sentencepiece_tokenizer_roundtrip(tmp_path: Path) -> None:
    model_file = _train_sentencepiece_model(tmp_path)
    tokenizer = SentencePieceTokenizer(model_file)
    text = "hello world"
    ids = tokenizer.encode(text)
    assert isinstance(ids, list) and ids  # noqa: S101
    decoded = tokenizer.decode(ids)
    assert decoded.replace(" ", "").lower().startswith("hello")


def test_sentencepiece_tokenizer_batch_and_truncation(tmp_path: Path) -> None:
    model_file = _train_sentencepiece_model(tmp_path)
    tokenizer = SentencePieceTokenizer(model_file)
    text = "alpha beta gamma delta"
    full_ids = tokenizer.encode(text)
    truncated = tokenizer.encode(text, truncation="only_first", max_length=3)
    assert len(truncated) == 3
    assert tokenizer.decode(truncated) == tokenizer.decode(full_ids[:3])
    batch = tokenizer.batch_encode(
        ["alpha beta", "gamma delta"], truncation="only_first", max_length=2
    )
    assert all(len(seq) <= 2 for seq in batch)


def test_sentencepiece_tokenizer_save_and_reload(tmp_path: Path) -> None:
    model_file = _train_sentencepiece_model(tmp_path)
    tokenizer = SentencePieceTokenizer(model_file, special_tokens=["<extra>"])
    save_dir = tmp_path / "saved"
    tokenizer.save_pretrained(str(save_dir))
    reloaded = SentencePieceTokenizer.from_pretrained(save_dir)
    text = "general kenobi"
    original = tokenizer.encode(text)
    restored = reloaded.encode(text)
    assert original == restored
    assert reloaded.special_tokens == ["<extra>"]


def test_tokenizer_adapter_from_config(tmp_path: Path) -> None:
    model_file = _train_sentencepiece_model(tmp_path)
    cfg = {"type": "sentencepiece", "model_path": str(model_file)}
    tokenizer = TokenizerAdapter.from_config(cfg)
    assert isinstance(tokenizer, SentencePieceTokenizer)
    text = "adapter config"
    ids = tokenizer.encode(text, truncation="longest_first", max_length=4)
    assert ids == tokenizer.encode(text)[:4]
