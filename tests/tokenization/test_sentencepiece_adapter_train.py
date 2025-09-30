from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path


def _reload_adapter():
    module_name = "src.tokenization.sentencepiece_adapter"
    if module_name in sys.modules:
        return importlib.reload(sys.modules[module_name])
    return importlib.import_module(module_name)


def _install_stub(monkeypatch, tmp_path: Path):
    calls: dict[str, object] = {}

    class _Processor:
        def __init__(self, model_file: str | None = None):
            self._model_file = model_file

        def Load(self, model_file: str) -> None:  # noqa: N802 - external API
            self._model_file = model_file

        def encode(self, text: str, out_type=int):
            data = [ord(ch) for ch in text]
            if out_type is int:
                return data
            return [out_type(x) for x in data]

        def decode(self, ids):
            return "".join(chr(i) for i in ids)

        def pad_id(self) -> int:
            return 0

    def _train(**kwargs):
        calls["kwargs"] = kwargs
        model_path = Path(kwargs["model_prefix"]).with_suffix(".model")
        model_path.write_text("stub", encoding="utf-8")

    trainer = types.SimpleNamespace(Train=_train, train=_train)
    stub = types.SimpleNamespace(
        SentencePieceProcessor=_Processor,
        SentencePieceTrainer=trainer,
    )
    monkeypatch.setitem(sys.modules, "sentencepiece", stub)
    return calls


def test_train_or_load_stubs(tmp_path, monkeypatch):
    calls = _install_stub(monkeypatch, tmp_path)
    mod = _reload_adapter()

    model_path = tmp_path / "toy.model"
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello world", encoding="utf-8")

    adapter = mod.SentencePieceAdapter(model_path)
    adapter.train_or_load(corpus, vocab_size=16, character_coverage=0.99)

    assert "kwargs" in calls
    params = calls["kwargs"]
    assert params["model_prefix"].endswith("toy")
    assert Path(params["model_prefix"]).with_suffix(".model").exists()

    encoded = adapter.encode("stub")
    assert encoded
    padded = adapter.encode("stub", padding="max_length", max_length=6)
    assert len(padded) == 6
    decoded = adapter.decode(encoded)
    assert decoded == "stub"


def test_load_requires_model(tmp_path, monkeypatch):
    _install_stub(monkeypatch, tmp_path)
    mod = _reload_adapter()

    adapter = mod.SentencePieceAdapter(tmp_path / "missing.model")
    try:
        adapter.load()
    except FileNotFoundError:
        pass
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected FileNotFoundError for missing model")
