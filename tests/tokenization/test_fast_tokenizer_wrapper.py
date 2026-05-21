"""Unit tests for :mod:`tokenizer.fast_tokenizer` thin wrapper."""

from __future__ import annotations

from uuid import uuid4

import pytest

from tokenizer.fast_tokenizer import FastTokenizerWrapper


@pytest.fixture()
def trained_tokenizer_json(tmp_path):
    pytest.importorskip("tokenizers")
    try:
        from tokenizers import Tokenizer  # type: ignore
        from tokenizers.models import WordLevel  # type: ignore
        from tokenizers.pre_tokenizers import Whitespace  # type: ignore
        from tokenizers.trainers import WordLevelTrainer  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency not fully available
        pytest.skip(f"tokenizers dependency incomplete: {exc}")

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
    assert wrapper.decode(ids).strip() == text


def test_padding_and_truncation(trained_tokenizer_json):
    wrapper = FastTokenizerWrapper(str(trained_tokenizer_json))
    padded = wrapper.encode("foo bar baz", padding="max_length", truncation=True, max_length=6)
    assert len(padded) == 6
    assert padded[-1] == 0
    truncated = wrapper.encode("foo bar baz", truncation=True, max_length=2)
    assert len(truncated) == 2
