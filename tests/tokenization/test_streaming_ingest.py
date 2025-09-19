from __future__ import annotations

import pytest

from tokenization import train_tokenizer as module


def test_iter_text_uses_configured_chunk_size(monkeypatch):
    calls: list[tuple[str, str, int | None]] = []

    def fake_ingest(path, *, encoding, chunk_size):
        calls.append((path, encoding, chunk_size))
        # Return chunks that straddle newline boundaries to exercise buffering.
        return iter((f"{path}-line-1\n", f"{path}-line-2\n"))

    monkeypatch.setattr(module, "ingest", fake_ingest)

    cfg = module.TrainTokenizerConfig(corpus_glob=[], streaming=True, stream_chunk_size=128)
    output = list(module._iter_text(["foo.txt", "bar.txt"], cfg))

    assert calls == [
        ("foo.txt", "auto", 128),
        ("bar.txt", "auto", 128),
    ]
    assert output == [
        "foo.txt-line-1",
        "foo.txt-line-2",
        "bar.txt-line-1",
        "bar.txt-line-2",
    ]


def test_iter_text_uses_default_chunk_size_when_streaming(monkeypatch):
    seen: list[int | None] = []

    def fake_ingest(path, *, encoding, chunk_size):
        seen.append(chunk_size)
        return "full\ntext"

    monkeypatch.setattr(module, "ingest", fake_ingest)

    cfg = module.TrainTokenizerConfig(corpus_glob=[], streaming=True)
    output = list(module._iter_text(["only.txt"], cfg))

    assert seen == [module.DEFAULT_STREAM_CHUNK_SIZE]
    assert output == ["full", "text"]


def test_iter_text_reads_entire_file_when_streaming_disabled(monkeypatch):
    seen: list[int | None] = []

    def fake_ingest(path, *, encoding, chunk_size):
        seen.append(chunk_size)
        return "all-at-once"

    monkeypatch.setattr(module, "ingest", fake_ingest)

    cfg = module.TrainTokenizerConfig(corpus_glob=[], streaming=False)
    output = list(module._iter_text(["file.txt"], cfg))

    assert seen == [None]
    assert output == ["all-at-once"]


def test_iter_text_streams_progressively(monkeypatch):
    yielded: list[int] = []

    def fake_ingest(path, *, encoding, chunk_size):
        def _generator():
            buffer = ["line-0\n", "line-1\n", "tail"]
            for idx, chunk in enumerate(buffer):
                yielded.append(idx)
                yield chunk

        return _generator()

    monkeypatch.setattr(module, "ingest", fake_ingest)

    cfg = module.TrainTokenizerConfig(corpus_glob=[], streaming=True, stream_chunk_size=64)
    iterator = module._iter_text(["stream.txt"], cfg)
    gen = iter(iterator)

    assert next(gen) == "line-0"
    assert yielded == [0]
    assert next(gen) == "line-1"
    assert yielded == [0, 1]


def test_iter_text_rejects_non_positive_chunk_size():
    cfg = module.TrainTokenizerConfig(corpus_glob=[], stream_chunk_size=0)
    with pytest.raises(ValueError):
        list(module._iter_text(["foo.txt"], cfg))
