import importlib

import pytest

pytest.importorskip("sentencepiece")

from codex_ml.interfaces.tokenizer import HFTokenizer  # noqa: E402
from tokenization.train_tokenizer import TrainTokenizerConfig, train  # noqa: E402


def test_roundtrip_basic(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello world\n" * 2)
    cfg = TrainTokenizerConfig(
        corpus_glob=str(corpus),
        vocab_size=20,
        out_dir=str(tmp_path / "artifacts"),
        name="tok",
        seed=123,
        workers=1,
    )
    try:
        out = train(cfg)
    except OSError as exc:  # pragma: no cover - env missing sentencepiece
        pytest.skip(str(exc))
    tk = HFTokenizer(
        name_or_path=None,
        artifacts_dir=str(out),
        padding="max_length",
        truncation=True,
        max_length=4,
    )
    ids = tk.encode("hello world")
    assert len(ids) == 4
    assert tk.decode(ids).startswith("hello")


def test_cli_encode_decode_roundtrip(monkeypatch, tmp_path):
    module = importlib.import_module("codex_ml.tokenization.cli")
    encode_fn = getattr(module, "encode", None)
    decode_fn = getattr(module, "decode", None)
    if encode_fn is None or decode_fn is None:
        pytest.skip("encode/decode helpers not exposed; skipping round-trip test")

    class DummyAdapter:
        def __init__(self, model):
            self.model = model
            self.loaded = False

        def load(self):
            self.loaded = True
            return self

        def encode(self, text):
            assert text == "hello codex"
            return [1, 2, 3, 4]

        def decode(self, ids):
            assert list(ids) == [1, 2, 3, 4, 0, 0]
            return "hello codex"

    monkeypatch.setattr(module, "SentencePieceAdapter", DummyAdapter)
    monkeypatch.setenv("CODEX_TOKENIZER_MODEL", str(tmp_path / "toy.model"))

    ids = encode_fn("hello codex", max_len=6, pad=True, trunc=True)
    assert ids == [1, 2, 3, 4, 0, 0]

    decoded = decode_fn(ids)
    assert isinstance(decoded, str)
    assert decoded == "hello codex"
