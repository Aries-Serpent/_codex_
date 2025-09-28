import importlib
import os
import pathlib

import pytest

pytestmark = pytest.mark.requires_sentencepiece


def _maybe_get_cli():
    """
    Try to import the tokenization CLI helpers the repo already exposes.
    Tests skip cleanly if optional deps (e.g., sentencepiece) are absent.
    """

    try:
        mod = importlib.import_module("codex_ml.tokenization.cli")
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"tokenization CLI unavailable: {exc}")
        return None
    if importlib.util.find_spec("sentencepiece") is None:
        pytest.skip("sentencepiece not installed; skipping tokenization CLI tests")
    root = pathlib.Path(__file__).resolve().parents[1]
    model = root / "fixtures" / "spm_toy.model"
    if not model.exists():
        pytest.skip("missing tests/fixtures/spm_toy.model; run: tools/make_spm_fixture.py")
    os.environ.setdefault("CODEX_TOKENIZER_MODEL", str(model))
    return mod


@pytest.mark.parametrize("max_len", [8, 16, 32])
def test_padding_truncation_length_invariant(max_len):
    mod = _maybe_get_cli()
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
    # When pad and trunc are both True, IDs should be exactly max_len long.
    assert len(ids) == max_len
    # Decoding should yield a non-empty string (round-trip len invariant, not content strict)
    text = decode(ids)
    assert isinstance(text, str) and text.strip()


def test_padding_equalizes_varied_lengths():
    mod = _maybe_get_cli()
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
    # Spot-check decode sanity without asserting exact text (special tokens/normalization may differ)
    for ids in encoded[:2]:
        assert isinstance(decode(ids), str)


@pytest.mark.parametrize("max_len", [4, 6])
def test_truncation_is_applied(max_len):
    mod = _maybe_get_cli()
    if mod is None:
        return
    encode = getattr(mod, "encode", None)
    if not callable(encode):
        pytest.skip("encode helper not exposed; skipping")
        return
    # Use a string that will be longer than max_len in token space for typical SP/BPE settings
    ids = encode("this string should be truncated", max_len=max_len, pad=False, trunc=True)
    assert len(ids) <= max_len


# WHY: Enforce padding/truncation invariants independent of model specifics.
# RISK: None (skip-safe if helpers/deps absent).
# ROLLBACK: delete this file.
# TESTS: 'pytest -q tests/tokenization/test_padding_truncation_ext.py'
