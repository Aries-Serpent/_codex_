import sys
from pathlib import Path
from types import SimpleNamespace

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
        def __init__(self):
            self.model_file = None

        def Load(self, model_file):
            self.model_file = str(model_file)

        load = Load

        def encode(self, text):  # pragma: no cover - simplified
            return [1, 2]

        def decode(self, ids):  # pragma: no cover - simplified
            return "x"

    sp_stub = SimpleNamespace(
        SentencePieceTrainer=SentencePieceTrainer,
        SentencePieceProcessor=SentencePieceProcessor,
    )
    monkeypatch.setitem(sys.modules, "sentencepiece", sp_stub)
    monkeypatch.setattr("codex_ml.tokenization.sentencepiece_adapter.spm", sp_stub, raising=False)


def test_use_fast_flag():
    tok_fast = load_tokenizer("gpt2", use_fast=True)
    assert getattr(tok_fast.tokenizer, "is_fast", False)
    tok_slow = load_tokenizer("gpt2", use_fast=False)
    assert not getattr(tok_slow.tokenizer, "is_fast", False)


def test_load_sentencepiece_adapter(tmp_path, monkeypatch):
    model = tmp_path / "toy.model"
    _sp_stub(monkeypatch, model)
    from codex_ml.tokenization.sentencepiece_adapter import SentencePieceAdapter

    SentencePieceAdapter(model).train_or_load(tmp_path / "corpus.txt", vocab_size=8)
    adapter = load_tokenizer(path=str(model))
    assert isinstance(adapter, SentencePieceAdapter)
