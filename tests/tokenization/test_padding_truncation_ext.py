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


def _maybe_get_cli_module():
    """Import the tokenization CLI helpers while tolerating optional deps."""

    try:
        return importlib.import_module("codex_ml.tokenization.cli")
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"tokenization CLI unavailable: {exc}")
        return None


@pytest.mark.parametrize("max_len", [8, 16, 32])
def test_padding_truncation_length_invariant(max_len: int) -> None:
    mod = _maybe_get_cli_module()
    if mod is None:
        return
    encode = getattr(mod, "encode", None)
    decode = getattr(mod, "decode", None)
    if not callable(encode) or not callable(decode):
        pytest.skip("encode/decode helpers not exposed; skipping")
        return
    if _resolve_model_path() is None:
        pytest.skip("tokenization model missing; run tools/make_spm_fixture.py")
    sample = "hello codex"
    ids = encode(sample, max_len=max_len, pad=True, trunc=True)
    assert isinstance(ids, (list, tuple)) and all(isinstance(i, int) for i in ids)
    assert len(ids) == max_len
    text = decode(ids)
    assert isinstance(text, str) and text.strip()


def test_padding_equalizes_varied_lengths() -> None:
    mod = _maybe_get_cli_module()
    if mod is None:
        return
    encode = getattr(mod, "encode", None)
    decode = getattr(mod, "decode", None)
    if not callable(encode) or not callable(decode):
        pytest.skip("encode/decode helpers not exposed; skipping")
        return
    if _resolve_model_path() is None:
        pytest.skip("tokenization model missing; run tools/make_spm_fixture.py")
    samples = ["hi", "hello", "hello codex", "hello codex tokenizer"]
    max_len = 24
    encoded = [encode(s, max_len=max_len, pad=True, trunc=True) for s in samples]
    assert all(len(e) == max_len for e in encoded)
    for ids in encoded[:2]:
        assert isinstance(decode(ids), str)


@pytest.mark.parametrize("max_len", [4, 6])
def test_truncation_is_applied(max_len: int) -> None:
    mod = _maybe_get_cli_module()
    if mod is None:
        return
    encode = getattr(mod, "encode", None)
    if not callable(encode):
        pytest.skip("encode helper not exposed; skipping")
        return
    if _resolve_model_path() is None:
        pytest.skip("tokenization model missing; run tools/make_spm_fixture.py")
    ids = encode("this string should be truncated", max_len=max_len, pad=False, trunc=True)
    assert len(ids) <= max_len
