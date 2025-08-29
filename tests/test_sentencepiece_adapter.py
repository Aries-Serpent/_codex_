# BEGIN: CODEX_TEST_SP_ADAPTER
import json
from types import SimpleNamespace
from pathlib import Path

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from codex_ml.tokenization.sentencepiece_adapter import SentencePieceAdapter


def _stub_sp(monkeypatch, model: Path, vocab_size: int = 5):
    class Trainer:
        def __init__(self):
            self.calls = []

        def train(self, **kwargs):  # pragma: no cover - trivial
            self.calls.append(kwargs)
            Path(kwargs["model_prefix"] + ".model").write_text("model", encoding="utf-8")

    class Processor:
        def __init__(self, model_file: str):
            self.model_file = model_file

        def vocab_size(self) -> int:  # pragma: no cover - trivial
            return vocab_size

    trainer = Trainer()
    sp_stub = SimpleNamespace(
        SentencePieceTrainer=trainer, SentencePieceProcessor=Processor
    )
    monkeypatch.setattr(
        "codex_ml.tokenization.sentencepiece_adapter.spm", sp_stub, raising=False
    )
    return trainer


def test_train_or_load_trains_and_loads(tmp_path, monkeypatch):
    model = tmp_path / "toy.model"
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello", encoding="utf-8")
    trainer = _stub_sp(monkeypatch, model)
    adapter = SentencePieceAdapter(model)
    adapter.model_prefix = model.with_suffix("")
    adapter.train_or_load(corpus, vocab_size=8)
    assert model.exists()
    assert trainer.calls  # training path
    assert adapter.sp.model_file == str(model)


def test_train_or_load_loads_existing_model(tmp_path, monkeypatch):
    model = tmp_path / "toy.model"
    model.write_text("model", encoding="utf-8")
    trainer = _stub_sp(monkeypatch, model)
    adapter = SentencePieceAdapter(model)
    adapter.model_prefix = model.with_suffix("")
    adapter.train_or_load(tmp_path / "corpus.txt")
    assert not trainer.calls  # load path
    assert adapter.sp.model_file == str(model)


def test_train_or_load_requires_sentencepiece(tmp_path, monkeypatch):
    model = tmp_path / "toy.model"
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("x", encoding="utf-8")
    monkeypatch.setattr(
        "codex_ml.tokenization.sentencepiece_adapter.spm", None, raising=False
    )
    adapter = SentencePieceAdapter(model)
    with pytest.raises(AttributeError):
        adapter.train_or_load(corpus)


def test_load_requires_sentencepiece(tmp_path, monkeypatch):
    model = tmp_path / "toy.model"
    model.write_text("model", encoding="utf-8")
    monkeypatch.setattr(
        "codex_ml.tokenization.sentencepiece_adapter.spm", None, raising=False
    )
    adapter = SentencePieceAdapter(model)
    with pytest.raises(AttributeError):
        adapter.load()


def test_add_special_tokens(tmp_path):
    model = tmp_path / "toy.model"
    adapter = SentencePieceAdapter(model)
    adapter.model_prefix = model.with_suffix("")
    adapter.add_special_tokens({"a": "<a>"})
    sidecar = json.loads(
        model.with_suffix(".special_tokens.json").read_text(encoding="utf-8")
    )
    assert sidecar == {"a": "<a>"}


def test_assert_vocab_size(tmp_path, monkeypatch):
    model = tmp_path / "toy.model"
    model.write_text("model", encoding="utf-8")
    _stub_sp(monkeypatch, model, vocab_size=7)
    adapter = SentencePieceAdapter(model)
    adapter.model_prefix = model.with_suffix("")
    adapter.train_or_load(tmp_path / "corpus.txt")
    adapter.assert_vocab_size(7)
    with pytest.raises(AssertionError):
        adapter.assert_vocab_size(10)
    adapter.sp = None
    with pytest.raises(RuntimeError):
        adapter.assert_vocab_size(7)
# END: CODEX_TEST_SP_ADAPTER
