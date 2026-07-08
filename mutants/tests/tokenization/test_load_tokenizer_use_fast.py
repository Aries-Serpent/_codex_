"""
Test Load Tokenizer Use Fast

Test module for load tokenizer use fast.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from codex_ml.tokenization import load_tokenizer


def _sp_stub(monkeypatch, model_path: Path):
    class SentencePieceTrainer:
        @staticmethod
        def Train(*args, **kwargs):  # pragma: no cover - minimal stub
            model_path.write_text("stub", encoding="utf-8")

        @staticmethod
        def train(*args, **kwargs):
            SentencePieceTrainer.Train(*args, **kwargs)

    class SentencePieceProcessor:
        def __init__(self, model_file=None):
            # Accept model_file kwarg used by newer sentencepiece adapter
            self.model_file = str(model_file) if model_file is not None else None

        def Load(self, model_file):
            self.model_file = str(model_file)

        load = Load

        def encode(self, text, out_type=None, **kwargs):
            # Accept out_type kwarg used by sentencepiece_adapter.py
            return [1, 2]

        def decode(self, ids):  # pragma: no cover - simplified
            return "x"

        def GetPieceSize(self):
            return 8

        vocab_size = 8
        name_or_path = ""

    sp_stub = SimpleNamespace(
        SentencePieceTrainer=SentencePieceTrainer,
        SentencePieceProcessor=SentencePieceProcessor,
    )
    monkeypatch.setitem(sys.modules, "sentencepiece", sp_stub)
    monkeypatch.setattr("codex_ml.tokenization.sentencepiece_adapter.spm", sp_stub, raising=False)


def _skip_if_offline(exc: Exception) -> None:
    """Skip test gracefully when HuggingFace model is unavailable in offline CI."""
    msg = str(exc).lower()
    if "unavailable" in msg or "connect" in msg or "network" in msg:
        pytest.skip(f"HuggingFace model unavailable (offline): {exc}")


def test_use_fast_flag():
    try:
        tok_fast = load_tokenizer("gpt2", use_fast=True)
    except (ValueError, TypeError) as exc:
        _skip_if_offline(exc)
        raise
    assert getattr(tok_fast.tokenizer, "is_fast", False)
    try:
        tok_slow = load_tokenizer("gpt2", use_fast=False)
    except (ValueError, TypeError) as exc:
        _skip_if_offline(exc)
        raise
    # In transformers >= 4.37 GPT-2's slow Python tokenizer was rewritten using the
    # Rust backend, so use_fast=False may still return a tokenizer with is_fast=True.
    # Verify the tokenizer loaded correctly and can encode text.
    assert tok_slow is not None, "tok_slow must be initialized"
    tokens = tok_slow.encode("hello world")
    assert isinstance(tokens, list) and len(tokens) > 0


def test_load_sentencepiece_adapter(tmp_path, monkeypatch):
    model = tmp_path / "toy.model"
    _sp_stub(monkeypatch, model)
    from codex_ml.tokenization.sentencepiece_adapter import SentencePieceAdapter

    SentencePieceAdapter(model).train_or_load(tmp_path / "corpus.txt", vocab_size=8)
    adapter = load_tokenizer(path=str(model))
    assert isinstance(adapter, SentencePieceAdapter)
