"""Extended tokenizer padding/truncation invariants."""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest


def _resolve_model_path() -> Path | None:
    root = Path(__file__).resolve().parents[1]
    candidate = root / "fixtures" / "spm_toy.model"
    if candidate.exists():
        os.environ.setdefault("CODEX_TOKENIZER_MODEL", str(candidate))
        return candidate
    existing = os.getenv("CODEX_TOKENIZER_MODEL")
    if existing:
        return Path(existing)
    return None


def _maybe_get_cli(monkeypatch: pytest.MonkeyPatch):
    """Import the tokenization CLI helpers if available, otherwise skip.

    Returns a ``(module, model_path)`` tuple so callers can pass the explicit
    ``model`` argument instead of depending on ambient environment variables.
    """

    try:
        mod = importlib.import_module("codex_ml.tokenization.cli")
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"tokenization CLI unavailable: {exc}")
        return None

    model = _resolve_model_path()
    if model is None:
        pytest.skip("tokenization model missing; run tools/make_spm_fixture.py")
        return None

    monkeypatch.setenv("CODEX_TOKENIZER_MODEL", str(model))
    return mod, model


@pytest.mark.parametrize("max_len", [8, 16, 32])
def test_padding_truncation_length_invariant(monkeypatch: pytest.MonkeyPatch, max_len: int):
    mod_model = _maybe_get_cli(monkeypatch)
    if mod_model is None:
        return
    mod, model = mod_model
    encode = getattr(mod, "encode", None)
    decode = getattr(mod, "decode", None)
    if not callable(encode) or not callable(decode):
        pytest.skip("encode/decode helpers not exposed; skipping")
        return
    sample = "hello codex"
    ids = encode(sample, model=model, max_len=max_len, pad=True, trunc=True)
    assert isinstance(ids, (list, tuple)) and all(isinstance(i, int) for i in ids)
    assert len(ids) == max_len
    text = decode(ids, model=model)
    assert isinstance(text, str) and text.strip()


def test_padding_equalizes_varied_lengths(monkeypatch: pytest.MonkeyPatch) -> None:
    mod_model = _maybe_get_cli(monkeypatch)
    if mod_model is None:
        return
    mod, model = mod_model
    encode = getattr(mod, "encode", None)
    decode = getattr(mod, "decode", None)
    if not callable(encode) or not callable(decode):
        pytest.skip("encode/decode helpers not exposed; skipping")
        return
    samples = ["hi", "hello", "hello codex", "hello codex tokenizer"]
    max_len = 24
    encoded = [
        encode(s, model=model, max_len=max_len, pad=True, trunc=True)
        for s in samples
    ]
    assert all(len(e) == max_len for e in encoded)
    for ids in encoded[:2]:
        assert isinstance(decode(ids, model=model), str)


@pytest.mark.parametrize("max_len", [4, 6])
def test_truncation_is_applied(monkeypatch: pytest.MonkeyPatch, max_len: int) -> None:
    mod_model = _maybe_get_cli(monkeypatch)
    if mod_model is None:
        return
    mod, model = mod_model
    encode = getattr(mod, "encode", None)
    if not callable(encode):
        pytest.skip("encode helper not exposed; skipping")
        return
    ids = encode(
        "this string should be truncated",
        model=model,
        max_len=max_len,
        pad=False,
        trunc=True,
    )
    assert len(ids) <= max_len
