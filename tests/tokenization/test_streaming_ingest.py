import pytest

from tokenization import train_tokenizer as module


def test_iter_text_uses_configured_chunk_size(monkeypatch):
    calls = []

    def fake_ingest(path, *, encoding, chunk_size):
        calls.append((path, encoding, chunk_size))
        return iter((f"{path}-chunk-0", f"{path}-chunk-1"))

    monkeypatch.setattr(module, "ingest", fake_ingest)

    cfg = module.TrainTokenizerConfig(corpus_glob=[], stream_chunk_size=128)
    output = list(module._iter_text(["foo.txt", "bar.txt"], cfg))

    assert calls == [
        ("foo.txt", "auto", 128),
        ("bar.txt", "auto", 128),
    ]
    assert output == [
        "foo.txt-chunk-0",
        "foo.txt-chunk-1",
        "bar.txt-chunk-0",
        "bar.txt-chunk-1",
    ]


def test_iter_text_uses_default_chunk_size_when_unset(monkeypatch):
    seen = []

    def fake_ingest(path, *, encoding, chunk_size):
        seen.append(chunk_size)
        return "full-text"

    monkeypatch.setattr(module, "ingest", fake_ingest)

    cfg = module.TrainTokenizerConfig(corpus_glob=[])
    output = list(module._iter_text(["only.txt"], cfg))

    assert seen == [module.DEFAULT_STREAM_CHUNK_SIZE]
    assert output == ["full-text"]


def test_iter_text_streams_progressively(monkeypatch):
    yielded = []

    def fake_ingest(path, *, encoding, chunk_size):
        def _generator():
            for idx in range(3):
                yielded.append(idx)
                yield f"chunk-{idx}"

        return _generator()

    monkeypatch.setattr(module, "ingest", fake_ingest)

    cfg = module.TrainTokenizerConfig(corpus_glob=[], stream_chunk_size=64)
    iterator = module._iter_text(["stream.txt"], cfg)
    gen = iter(iterator)

    assert next(gen) == "chunk-0"
    assert yielded == [0]
    assert next(gen) == "chunk-1"
    assert yielded == [0, 1]


def test_iter_text_rejects_non_positive_chunk_size():
    cfg = module.TrainTokenizerConfig(corpus_glob=[], stream_chunk_size=0)
    with pytest.raises(ValueError):
        list(module._iter_text(["foo.txt"], cfg))
