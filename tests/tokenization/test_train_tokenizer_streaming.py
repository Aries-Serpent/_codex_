from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from tokenization import train_tokenizer


def test_iter_text_uses_chunk_size(monkeypatch):
    calls: list[int | None] = []

    def fake_ingest(path, *, encoding, chunk_size):  # pragma: no cover - stub
        assert encoding == "auto"
        calls.append(chunk_size)
        yield f"chunk:{path}\n"

    monkeypatch.setattr(train_tokenizer, "ingest", fake_ingest)
    files = ["one.txt", "two.txt"]
    cfg = train_tokenizer.TrainTokenizerConfig(
        corpus_glob=[], streaming=True, stream_chunk_size=128
    )
    pieces = list(train_tokenizer._iter_text(files, cfg))
    assert calls == [128, 128]
    assert pieces == ["chunk:one.txt", "chunk:two.txt"]


def test_sentencepiece_streaming_iterator(monkeypatch, tmp_path):
    pytest.importorskip("tokenizers")
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("alpha\nbeta\n", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_train(**kwargs):
        captured.update(kwargs)
        model_prefix = Path(kwargs["model_prefix"])
        model_prefix.with_suffix(".model").write_text("m", encoding="utf-8")
        model_prefix.with_suffix(".vocab").write_text("v", encoding="utf-8")

    class _DummyProcessor:
        def Load(self, path: str) -> None:  # pragma: no cover - stub
            self.path = path

    fake_spm = types.SimpleNamespace(
        SentencePieceTrainer=types.SimpleNamespace(Train=fake_train),
        SentencePieceProcessor=lambda: _DummyProcessor(),
    )
    monkeypatch.setattr(train_tokenizer, "spm", fake_spm)
    monkeypatch.setattr(train_tokenizer, "_SPM_ERROR", RuntimeError("missing"))

    class DummyTokenizer:
        def __init__(self, model_path: str) -> None:
            self.model_path = model_path

        @staticmethod
        def from_spm(model_path: str) -> "DummyTokenizer":
            return DummyTokenizer(model_path)

        def save(self, output: str) -> None:
            Path(output).write_text("{}", encoding="utf-8")

    monkeypatch.setattr(train_tokenizer, "SentencePieceUnigramTokenizer", DummyTokenizer)

    cfg = train_tokenizer.TrainTokenizerConfig(
        corpus_glob=str(corpus),
        vocab_size=32,
        out_dir=str(tmp_path / "artifacts"),
        name="tok",
        streaming=True,
        stream_chunk_size=3,
        workers=1,
        seed=0,
    )

    out_dir = train_tokenizer.train(cfg)
    shard_input = captured.get("input")
    assert shard_input is not None
    shards = [Path(part) for part in str(shard_input).split(",")]
    assert shards
    assert all("shard-" in shard.name for shard in shards)

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["config"]["stream_chunk_size"] == 3
    assert manifest["config"]["streaming"] is True
