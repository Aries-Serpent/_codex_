"""
Test Tokenization

Test module for tokenization.
"""

import json

import pytest
from click.testing import CliRunner

pytest.importorskip("transformers")
pytest.importorskip("sentencepiece")

from codex_ml.cli.codex_cli import tokenizer_train
from codex_ml.tokenization import (
    BOS_TOKEN,
    EOS_TOKEN,
    PAD_TOKEN,
    UNK_TOKEN,
    load_tokenizer,
    pad_sequences,
)


@pytest.fixture(scope="module")
def tok():
    return load_tokenizer("gpt2")


def test_round_trip(tok):
    text = "hello world"
    ids = tok.encode(text)
    assert tok.decode(ids).strip() == text


def test_special_token_ids(tok):
    ids = [tok.encode(t)[0] for t in [BOS_TOKEN, EOS_TOKEN, PAD_TOKEN, UNK_TOKEN]]
    assert len(ids) == 4
    assert len(set(ids)) == 4


def test_deterministic(tok, tmp_path):
    text = "determinism matters"
    ids1 = tok.encode(text)
    tok.save(tmp_path / "tok.json")
    tok2 = load_tokenizer(path=str(tmp_path / "tok.json"))
    ids2 = tok2.encode(text)
    assert ids1 == ids2


def test_pad_sequences_padding_and_truncation():
    padded, mask = pad_sequences(
        [[1, 2, 3], [4]], pad_id=0, max_length=4, return_attention_mask=True
    )
    assert padded == [[1, 2, 3, 0], [4, 0, 0, 0]]
    assert mask == [[1, 1, 1, 0], [1, 0, 0, 0]]


def test_pad_sequences_validates_lengths():
    with pytest.raises(ValueError):
        pad_sequences([], pad_id=1)
    with pytest.raises(ValueError):
        pad_sequences([[1, 2, 3], [4, 5, 6, 7, 8]], max_length=3, truncate=False)


def test_tokenizer_train_dry_run_streaming(monkeypatch, tmp_path):
    calls = {}

    class DummyPipeline:
        class TokenizerPipelineError(Exception): ...

        def run_train(self, config, streaming=None, stream_chunk_size=None, dry_run=False):
            calls["config"] = config
            calls["streaming"] = streaming
            calls["stream_chunk_size"] = stream_chunk_size
            calls["dry_run"] = dry_run
            return tmp_path / "out"

    monkeypatch.setattr("codex_ml.cli.codex_cli._get_tokenizer_pipeline", lambda: DummyPipeline())
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(json.dumps({"dummy": True}), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        tokenizer_train,
        ["--config", str(cfg), "--streaming", "--stream-chunk-size", "2", "--dry-run"],
    )
    assert result.exit_code == 0
    assert calls == {
        "config": str(cfg),
        "streaming": True,
        "stream_chunk_size": 2,
        "dry_run": True,
    }
