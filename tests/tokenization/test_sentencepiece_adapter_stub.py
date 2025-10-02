"""Unit tests for the lightweight SentencePieceAdapter without real deps."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable

import pytest

MODULE_NAME = "src.tokenization.sentencepiece_adapter"


class _StubProcessor:
    """Minimal stub mimicking a subset of ``SentencePieceProcessor``."""

    def __init__(self, pad_id: int = 0, piece_size: int = 0) -> None:
        self._pad_id = pad_id
        self._piece_size = piece_size
        self.model_file: str | None = None

    # The adapter prefers ``Load`` but some environments expose ``load`` instead.
    def Load(self, model_file: str) -> None:  # noqa: N802 - mimic third-party casing
        self.model_file = model_file

    def load(self, model_file: str) -> None:
        self.Load(model_file)

    def pad_id(self) -> int:
        return self._pad_id

    def vocab_size(self) -> int:
        return self._piece_size

    def get_piece_size(self) -> int:
        return self._piece_size

    def piece_size(self) -> int:
        return self._piece_size

    def encode(self, text: str, out_type=int) -> Iterable[int]:  # type: ignore[override]
        return [out_type(ord(ch)) for ch in text]

    def EncodeAsIds(self, text: str) -> list[int]:  # noqa: N802 - third-party casing
        return [ord(ch) for ch in text]

    def decode(self, ids: Iterable[int]) -> str:
        return "".join(chr(int(i)) for i in ids)

    def DecodeIds(self, ids: Iterable[int]) -> str:  # noqa: N802
        return self.decode(ids)


def _install_stub(monkeypatch: pytest.MonkeyPatch, pad_id: int = 0, piece_size: int = 0) -> None:
    stub = SimpleNamespace(
        SentencePieceProcessor=lambda: _StubProcessor(pad_id, piece_size),
    )
    monkeypatch.setitem(sys.modules, "sentencepiece", stub)


def _reload_adapter(monkeypatch: pytest.MonkeyPatch, pad_id: int = 0, piece_size: int = 0):
    _install_stub(monkeypatch, pad_id=pad_id, piece_size=piece_size)
    sys.modules.pop(MODULE_NAME, None)
    return importlib.import_module(MODULE_NAME)


def test_encode_decode_roundtrip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _reload_adapter(monkeypatch, pad_id=7)
    SentencePieceAdapter = module.SentencePieceAdapter

    model = tmp_path / "toy.model"
    model.write_text("stub", encoding="utf-8")

    adapter = SentencePieceAdapter(model)

    ids = adapter.encode("hello", padding="max_length", truncation="only_first", max_length=6)
    assert len(ids) == 6
    # pad id propagated from stub
    assert ids[-1] == 7

    decoded = adapter.decode(ids[:5])
    assert decoded == "hello"

    # round-trip via batch_encode helpers
    batch = adapter.batch_encode(["hi", "codex"], padding="max_length", max_length=5)
    assert batch[0][-1] == 7
    assert adapter.decode(batch[1][:5]) == "codex"


def test_load_allows_reuse(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _reload_adapter(monkeypatch)
    SentencePieceAdapter = module.SentencePieceAdapter

    model = tmp_path / "toy.model"
    model.write_text("stub", encoding="utf-8")

    adapter = SentencePieceAdapter(model)
    # drop processor to ensure load() repopulates
    adapter.sp = None
    adapter.load()
    assert adapter.sp is not None
    assert getattr(adapter.sp, "model_file", None) == str(model)


def test_pad_id_fallbacks_to_zero(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _reload_adapter(monkeypatch, pad_id=-1)
    SentencePieceAdapter = module.SentencePieceAdapter

    model = tmp_path / "toy.model"
    model.write_text("stub", encoding="utf-8")

    adapter = SentencePieceAdapter(model)

    ids = adapter.encode("ok", padding="max_length", max_length=5)
    assert ids[-1] == 0


def test_decode_accepts_iterable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _reload_adapter(monkeypatch, pad_id=3)
    SentencePieceAdapter = module.SentencePieceAdapter

    model = tmp_path / "toy.model"
    model.write_text("stub", encoding="utf-8")

    adapter = SentencePieceAdapter(model)

    ids = adapter.encode("iterable", padding="max_length", max_length=9)
    # convert to generator to ensure the helper eagerly realises values
    decoded = adapter.decode(i for i in ids[:8])
    assert decoded == "iterable"


def test_add_special_tokens_persists_map(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _reload_adapter(monkeypatch, pad_id=5, piece_size=13)
    SentencePieceAdapter = module.SentencePieceAdapter

    model = tmp_path / "toy.model"
    model.write_text("stub", encoding="utf-8")

    adapter = SentencePieceAdapter(model)

    mapping = adapter.add_special_tokens(["<pad>", "<bos>"])
    assert mapping["<pad>"] == 13
    assert mapping["<bos>"] == 14

    sidecar = model.with_suffix(".special_tokens.json")
    assert sidecar.exists()
    persisted = json.loads(sidecar.read_text(encoding="utf-8"))
    assert persisted == mapping

    adapter_again = SentencePieceAdapter(model)
    updated = adapter_again.add_special_tokens(["<bos>", "<eos>"])
    assert updated["<pad>"] == 13
    assert updated["<bos>"] == 14
    assert updated["<eos>"] == 15
