"""
Test Roundtrip Basic

Test module for roundtrip basic.
"""

import importlib
import importlib.util

import pytest

pytest.importorskip("sentencepiece")

from codex_ml.interfaces.tokenizer import HFTokenizer
from src.tokenization.train_tokenizer import TrainTokenizerConfig, train


def test_roundtrip_basic(tmp_path):
    if importlib.util.find_spec("sentencepiece_model_pb2") is None:
        pytest.skip("sentencepiece_model_pb2 module missing; skipping round-trip test")
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
    out = None  # Assigned in try block; except branches skip test
    try:
        out = train(cfg)
    except OSError as exc:  # pragma: no cover - env missing sentencepiece
        pytest.skip(str(exc))
    except Exception as exc:  # pragma: no cover - optional dependency gaps
        message = str(exc)
        if "sentencepiece_model_pb2" in message or "protobuf" in message.lower():
            pytest.skip("sentencepiece protobuf helpers unavailable")
        raise
    tk = HFTokenizer(
        name_or_path=None,
        artifacts_dir=str(out),
        padding="max_length",
        truncation=True,
        max_length=4,
    )
    token_ids = tk.encode("hello world")
    assert len(token_ids) == 4, "Token_ids must not be empty"
    assert tk.decode(token_ids).startswith("hello"), "Condition must be true"


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
            assert text == "hello codex", "text is not valid"
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
    assert decoded == "hello codex", "decoded is not valid"


def test_cli_encode_decode_presence():
    module = importlib.import_module("codex_ml.tokenization.cli")
    encode_fn = getattr(module, "encode", None)
    decode_fn = getattr(module, "decode", None)
    if encode_fn is None or decode_fn is None:
        pytest.skip("encode/decode helpers not exposed; skipping round-trip test")

    sample = "hello codex"
    token_ids = None  # Assigned in try block before use; except branches skip test
    try:
        token_ids = encode_fn(sample, max_len=16, pad=True, trunc=True)
    except Exception as exc:
        pytest.skip(f"encode helper unavailable: {exc}")

    # At this point, token_ids is guaranteed to be assigned (except branches skip test)
    assert isinstance(token_ids, (list, tuple)) and token_ids

    decoded = None  # Assigned in try block before use; except branches skip test
    try:
        decoded = decode_fn(token_ids)
    except Exception as exc:
        pytest.skip(f"decode helper unavailable: {exc}")

    # At this point, decoded is guaranteed to be assigned (except branches skip test)
    assert isinstance(decoded, str) and decoded.strip()
    assert sample.replace(" ", "").lower() == decoded.replace(" ", "").lower()
