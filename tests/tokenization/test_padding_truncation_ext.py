from __future__ import annotations

import importlib
from pathlib import Path

import pytest

pytestmark = [pytest.mark.tokenizer, pytest.mark.requires_sentencepiece]


def _ensure_fixture(monkeypatch: pytest.MonkeyPatch) -> Path:
    root = Path(__file__).resolve().parents[1]
    model = root / "fixtures" / "spm_toy.model"
    if not model.exists():
        pytest.skip("missing tests/fixtures/spm_toy.model; run: python tools/make_spm_fixture.py")
    monkeypatch.setenv("CODEX_TOKENIZER_MODEL", str(model))
    return model


def _maybe_get_cli(monkeypatch: pytest.MonkeyPatch):
    """Import the tokenization CLI helpers if available, otherwise skip."""

    try:
        mod = importlib.import_module("codex_ml.tokenization.cli")
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"tokenization CLI unavailable: {exc}")
        return None
    _ensure_fixture(monkeypatch)
    return mod


@pytest.mark.parametrize("max_len", [8, 16, 32])
def test_padding_truncation_length_invariant(monkeypatch: pytest.MonkeyPatch, max_len: int):
    mod = _maybe_get_cli(monkeypatch)
    if mod is None:
        return
    encode = getattr(mod, "encode", None)
    decode = getattr(mod, "decode", None)
    if not callable(encode) or not callable(decode):
        pytest.skip("encode/decode helpers not exposed; skipping")
        return
    sample = "hello codex"
    ids = encode(sample, max_len=max_len, pad=True, trunc=True)
    assert isinstance(ids, (list, tuple)) and all(isinstance(i, int) for i in ids)
    assert len(ids) == max_len
    text = decode(ids)
    assert isinstance(text, str) and text.strip()


def test_padding_equalizes_varied_lengths(monkeypatch: pytest.MonkeyPatch):
    mod = _maybe_get_cli(monkeypatch)
    if mod is None:
        return
    encode = getattr(mod, "encode", None)
    decode = getattr(mod, "decode", None)
    if not callable(encode) or not callable(decode):
        pytest.skip("encode/decode helpers not exposed; skipping")
        return
    samples = ["hi", "hello", "hello codex", "hello codex tokenizer"]
    max_len = 24
    encoded = [encode(s, max_len=max_len, pad=True, trunc=True) for s in samples]
    assert all(len(e) == max_len for e in encoded)
    for ids in encoded[:2]:
        assert isinstance(decode(ids), str)


@pytest.mark.parametrize("max_len", [4, 6])
def test_truncation_is_applied(monkeypatch: pytest.MonkeyPatch, max_len: int):
    mod = _maybe_get_cli(monkeypatch)
    if mod is None:
        return
    encode = getattr(mod, "encode", None)
    if not callable(encode):
        pytest.skip("encode helper not exposed; skipping")
        return
    ids = encode("this string should be truncated", max_len=max_len, pad=False, trunc=True)
    assert len(ids) <= max_len
