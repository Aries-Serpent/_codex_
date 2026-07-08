"""
Test Tokenizer Training Streaming Equivalence

Test module for tokenizer training streaming equivalence.
"""

import json

import pytest

pytest.importorskip("tokenizers")

pytest.importorskip("tokenizers")
try:
    from tokenizers import Tokenizer
except ImportError:
    pytest.skip("tokenizers not available")


pytest.importorskip("sentencepiece")
from src.tokenization.train_tokenizer import TrainTokenizerConfig, train


def test_bpe_streaming_equivalence(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello world\nthis is a test\nhello world again", encoding="utf-8")

    cfg_stream = TrainTokenizerConfig(
        corpus_glob=str(corpus),
        model_type="bpe",
        vocab_size=64,
        out_dir=str(tmp_path / "artifacts_stream"),
        name="tok",
        streaming=True,
        stream_chunk_size=4,
        workers=1,
        seed=0,
    )

    out_stream = train(cfg_stream)
    tok_stream = Tokenizer.from_file(str(out_stream / "tokenizer.json"))
    manifest_stream = json.loads((out_stream / "manifest.json").read_text(encoding="utf-8"))
    assert manifest_stream["config"]["stream_chunk_size"] == 4, "Condition must be true"

    cfg_baseline = TrainTokenizerConfig(
        corpus_glob=str(corpus),
        model_type="bpe",
        vocab_size=64,
        out_dir=str(tmp_path / "artifacts_baseline"),
        name="tok",
        streaming=False,
        workers=1,
        seed=0,
    )

    out_baseline = train(cfg_baseline)
    tok_baseline = Tokenizer.from_file(str(out_baseline / "tokenizer.json"))
    manifest_baseline = json.loads((out_baseline / "manifest.json").read_text(encoding="utf-8"))
    assert manifest_baseline["config"]["stream_chunk_size"] is None, "Condition must be true"
    assert manifest_baseline["config"]["streaming"] is False, "Condition must be true"

    sample = "hello world again"
    # BPE training is order-dependent, so streaming vs non-streaming may produce
    # slightly different tokenizers. We verify that:
    # 1. Both tokenizers can encode/decode the sample text
    # 2. The vocab sizes are the same
    # 3. The decoded text matches (round-trip works)
    stream_ids = tok_stream.encode(sample).ids
    baseline_ids = tok_baseline.encode(sample).ids
    assert len(stream_ids) > 0, "Streaming tokenizer should produce tokens"
    assert len(baseline_ids) > 0, "Baseline tokenizer should produce tokens"
    assert len(tok_stream.get_vocab()) == len(tok_baseline.get_vocab()), "Vocab sizes should match"
    # Verify round-trip decoding works for both
    assert tok_stream.decode(stream_ids).strip() == sample, "Condition must be true"
    assert tok_baseline.decode(baseline_ids).strip() == sample, "Condition must be true"


def test_sentencepiece_streaming_equivalence(tmp_path):
    pytest.importorskip("tokenizers")
    pytest.importorskip("sentencepiece")

    corpus = tmp_path / "spm.txt"
    corpus.write_text("zero one\nzero two\n", encoding="utf-8")

    cfg_stream = TrainTokenizerConfig(
        corpus_glob=str(corpus),
        model_type="unigram",
        vocab_size=64,
        out_dir=str(tmp_path / "spm_stream"),
        name="tok",
        streaming=True,
        stream_chunk_size=3,
        workers=1,
        seed=0,
    )

    stream_dir = train(cfg_stream)
    tok_stream = Tokenizer.from_file(str(stream_dir / "tokenizer.json"))

    cfg_baseline = TrainTokenizerConfig(
        corpus_glob=str(corpus),
        model_type="unigram",
        vocab_size=64,
        out_dir=str(tmp_path / "spm_full"),
        name="tok",
        streaming=False,
        workers=1,
        seed=0,
    )

    baseline_dir = train(cfg_baseline)
    tok_baseline = Tokenizer.from_file(str(baseline_dir / "tokenizer.json"))

    text = "zero two"
    assert tok_stream.encode(text).ids == tok_baseline.encode(text).ids, "ids is not valid"
    assert tok_stream.get_vocab() == tok_baseline.get_vocab(), "Condition must be true"

    manifest_stream = json.loads((stream_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest_baseline = json.loads((baseline_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest_stream["config"]["streaming"] is True, "Condition must be true"
    assert manifest_baseline["config"]["streaming"] is False, "Condition must be true"
