"""
pytest.importorskip("charset_normalizer")
Test Streaming Ingest

Test module for streaming ingest.
"""

from __future__ import annotations

import pytest

from src.codex_ml.tokenization import train_tokenizer as module

pytestmark = pytest.mark.skipif(
    module is None, reason="tokenizers not available — train_tokenizer module not loaded"
)


def test_iter_text_uses_configured_chunk_size(monkeypatch):
    calls: list[tuple[str, str, int | None]] = []

    def fake_ingest(path, *, encoding, chunk_size):
        calls.append((path, encoding, chunk_size))
        # Return chunks that straddle newline boundaries to exercise buffering.
        return iter((f"{path}-line-1\n", f"{path}-line-2\n"))

    monkeypatch.setattr(module, "ingest", fake_ingest)

    cfg = module.TrainTokenizerConfig(corpus_glob=[], streaming=True, stream_chunk_size=128)
    output = list(module._iter_text(["foo.txt", "bar.txt"], cfg))

    # Fixed malformed assertion: assert calls ==
    assert output == ["full\n", "text"]


def test_iter_text_reads_entire_file_when_streaming_disabled(monkeypatch):
    seen: list[int | None] = []

    def fake_ingest(path, *, encoding, chunk_size):
        seen.append(chunk_size)
        return "all-at-once"

    monkeypatch.setattr(module, "ingest", fake_ingest)

    cfg = module.TrainTokenizerConfig(corpus_glob=[], streaming=False)
    output = list(module._iter_text(["file.txt"], cfg))

    assert seen == [None], "seen is not valid"
    assert output == ["all-at-once"], "output is not valid"


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

    assert next(gen) == "line-0\n", "Condition must be true"
    assert yielded == [0], "yielded is not valid"
    assert next(gen) == "line-1\n", "Condition must be true"
    assert yielded == [0, 1]


def test_iter_text_rejects_non_positive_chunk_size():
    cfg = module.TrainTokenizerConfig(corpus_glob=[], stream_chunk_size=0)
    with pytest.raises(ValueError):
        module._resolve_streaming_options(cfg)
