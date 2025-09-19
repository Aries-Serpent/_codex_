import json

import pytest

pytest.importorskip("tokenizers")

from tokenizers import Tokenizer

from tokenization.train_tokenizer import TrainTokenizerConfig, train


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
    assert manifest_stream["config"]["stream_chunk_size"] == 4

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
    assert manifest_baseline["config"]["stream_chunk_size"] is None
    assert manifest_baseline["config"]["streaming"] is False

    sample = "hello world again"
    assert tok_stream.encode(sample).ids == tok_baseline.encode(sample).ids
    assert tok_stream.get_vocab() == tok_baseline.get_vocab()


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
    assert tok_stream.encode(text).ids == tok_baseline.encode(text).ids
    assert tok_stream.get_vocab() == tok_baseline.get_vocab()

    manifest_stream = json.loads((stream_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest_baseline = json.loads((baseline_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest_stream["config"]["streaming"] is True
    assert manifest_baseline["config"]["streaming"] is False
