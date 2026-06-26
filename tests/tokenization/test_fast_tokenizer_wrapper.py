"""Unit tests for :mod:`tokenizer.fast_tokenizer` thin wrapper."""

from __future__ import annotations

from uuid import uuid4

import pytest

from tokenizer.fast_tokenizer import FastTokenizerWrapper


@pytest.fixture()
def trained_tokenizer_json(tmp_path):
    Tokenizer = pytest.importorskip("tokenizers").Tokenizer
    WordLevel = pytest.importorskip("tokenizers.models").WordLevel
    Whitespace = pytest.importorskip("tokenizers.pre_tokenizers").Whitespace
    WordLevelTrainer = pytest.importorskip("tokenizers.trainers").WordLevelTrainer

    corpus = ["hello world", "foo bar baz", "chatbot"]
    tok = Tokenizer(WordLevel(unk_token="[UNK]"))
    tok.pre_tokenizer = Whitespace()
    trainer = WordLevelTrainer(special_tokens=["[UNK]"])
    tok.train_from_iterator(corpus, trainer=trainer)
    target = tmp_path / f"tokenizer-{uuid4().hex}.json"
    tok.save(str(target))
    return target


def test_round_trip(trained_tokenizer_json):
    wrapper = FastTokenizerWrapper(str(trained_tokenizer_json))
    text = "hello world"
    ids = wrapper.encode(text)
    assert wrapper.decode(ids).strip() == text, "Condition must be true"


def test_padding_and_truncation(trained_tokenizer_json):
    wrapper = FastTokenizerWrapper(str(trained_tokenizer_json))
    padded = wrapper.encode("foo bar baz", padding="max_length", truncation=True, max_length=6)
    assert len(padded) == 6, "Padded must not be empty"
    assert padded[-1] == 0, "Condition must be true"
    truncated = wrapper.encode("foo bar baz", truncation=True, max_length=2)
    assert len(truncated) == 2, "Truncated must not be empty"
