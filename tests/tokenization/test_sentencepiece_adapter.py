from __future__ import annotations

import importlib
import json
import types
from pathlib import Path

import pytest


def test_import_error(no_sentencepiece):
    mod = importlib.import_module("codex_ml.tokenization.sentencepiece_adapter")
    assert getattr(mod, "spm") is None


def test_train_roundtrip(tmp_path, monkeypatch):
    mod = importlib.import_module("codex_ml.tokenization.sentencepiece_adapter")
    sp_stub = types.SimpleNamespace(
        SentencePieceTrainer=types.SimpleNamespace(
            train=lambda **kw: Path(kw["model_prefix"] + ".model").write_text("m", encoding="utf-8")
        ),
        SentencePieceProcessor=type(
            "P",
            (),
            {
                "__init__": lambda self, model_file: None,
                "encode": lambda self, text, out_type=int: [1, 2, 3],
                "decode": lambda self, ids: "ok",
                "vocab_size": lambda self: 3,
            },
        ),
    )
    monkeypatch.setattr(mod, "spm", sp_stub)
    monkeypatch.setattr(
        mod.SentencePieceAdapter,
        "model_prefix",
        property(lambda self: self.model_path.with_suffix("")),
        raising=False,
    )
    corpus = tmp_path / "c.txt"
    corpus.write_text("hi", encoding="utf-8")
    adapter = mod.SentencePieceAdapter(tmp_path / "toy.model")
    adapter.train_or_load(corpus)
    adapter.add_special_tokens({"pad": "<pad>"})
    ids = adapter.encode("hello")
    text = adapter.decode(ids)
    assert ids and text == "ok"
    adapter.assert_vocab_size(2)
    with pytest.raises(AssertionError):
        adapter.assert_vocab_size(10)
    sidecar = json.loads((tmp_path / "toy.special_tokens.json").read_text(encoding="utf-8"))
    assert sidecar["pad"] == "<pad>"
