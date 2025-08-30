from __future__ import annotations

from codex_ml.interfaces.tokenizer import HFTokenizer

MODEL = "hf-internal-testing/tiny-random-bert"


def test_encode_decode_roundtrip() -> None:
    tk = HFTokenizer(MODEL, padding=False, truncation=True, max_length=32)
    ids = tk.encode("hello world")
    assert isinstance(ids, list) and ids
    out = tk.decode(ids)
    assert "hello" in out.lower()


def test_padding_and_truncation() -> None:
    tk = HFTokenizer(MODEL, padding="max_length", truncation=True, max_length=5)
    ids = tk.encode("a b c d e f")
    assert len(ids) == 5


def test_batch_encode_decode() -> None:
    tk = HFTokenizer(MODEL, padding=True, truncation=True, max_length=8)
    batch = tk.batch_encode(["hi", "there"])
    assert len(batch) == 2 and all(isinstance(x, list) for x in batch)
    texts = tk.batch_decode(batch)
    assert len(texts) == 2
