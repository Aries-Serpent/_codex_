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
        stream_chunk_size=512,
        workers=1,
        seed=0,
    )

    out_baseline = train(cfg_baseline)
    tok_baseline = Tokenizer.from_file(str(out_baseline / "tokenizer.json"))
    manifest_baseline = json.loads((out_baseline / "manifest.json").read_text(encoding="utf-8"))
    assert manifest_baseline["config"]["stream_chunk_size"] == 512

    sample = "hello world again"
    assert tok_stream.encode(sample).ids == tok_baseline.encode(sample).ids
    assert tok_stream.get_vocab() == tok_baseline.get_vocab()
