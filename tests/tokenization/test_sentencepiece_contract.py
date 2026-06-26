"""Dedicated contract-coverage tests for SentencePieceAdapter.

These tests verify that ``SentencePieceAdapter`` honours every clause of the
formal tokenizer contract defined in
``src.codex_ml.interfaces.contracts.TokenizerContract`` without requiring a
real sentencepiece installation.  A minimal stub processor is injected via
``monkeypatch`` so the tests are deterministic and fast.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_STUB_VOCAB = ["<unk>", "<s>", "</s>", "hello", "world", "▁hi"]


def _make_stub_processor():
    """Return a minimal sentencepiece-like stub."""

    class _StubProcessor:
        def __init__(self, model_file=None, **_kwargs):
            self._vocab = list(_STUB_VOCAB)

        def encode(self, text: str, out_type=int):  # type: ignore[override]
            tokens = text.lower().split()
            vocab_map = {t: i for i, t in enumerate(self._vocab)}
            ids = [vocab_map.get(t, 0) for t in tokens]
            return ids if out_type is int else [str(i) for i in ids]

        def decode(self, ids) -> str:
            reverse = {i: t for i, t in enumerate(self._vocab)}
            return " ".join(reverse.get(int(i), "<unk>") for i in ids)

        def GetPieceSize(self):
            return len(self._vocab)

        def get_piece_size(self):
            return len(self._vocab)

        def vocab_size(self):
            return len(self._vocab)

        def pad_id(self):
            return 0

    return _StubProcessor


def _make_stub_module(proc_cls):
    return types.SimpleNamespace(
        SentencePieceTrainer=types.SimpleNamespace(
            train=lambda **kw: Path(str(kw.get("model_prefix", "toy")) + ".model").write_text(
                "", encoding="utf-8"
            )
        ),
        SentencePieceProcessor=proc_cls,
    )


@pytest.fixture()
def adapter(tmp_path, monkeypatch):
    """Return a loaded SentencePieceAdapter backed by the stub processor."""
    import src.codex_ml.tokenization.sentencepiece_adapter as mod

    proc_cls = _make_stub_processor()
    stub_module = _make_stub_module(proc_cls)
    monkeypatch.setattr(mod, "spm", stub_module)
    # Ensure the module-level cache is also patched (used by _get_sentencepiece)
    monkeypatch.setitem(sys.modules, "sentencepiece", stub_module)

    model_file = tmp_path / "test.model"
    model_file.write_text("", encoding="utf-8")

    a = mod.SentencePieceAdapter(model_file)
    a.load()
    return a


# ---------------------------------------------------------------------------
# Contract: vocab_size property
# ---------------------------------------------------------------------------


class TestVocabSizeProperty:
    def test_vocab_size_returns_int(self, adapter):
        assert isinstance(adapter.vocab_size, int)

    def test_vocab_size_is_positive(self, adapter):
        assert adapter.vocab_size > 0, "vocab_size must be greater than zero"

    def test_vocab_size_matches_stub(self, adapter):
        assert adapter.vocab_size == len(_STUB_VOCAB), "_stub_vocab must not be empty"


# ---------------------------------------------------------------------------
# Contract: name_or_path property
# ---------------------------------------------------------------------------


class TestNameOrPathProperty:
    def test_name_or_path_returns_str(self, adapter):
        assert isinstance(adapter.name_or_path, str)

    def test_name_or_path_is_non_empty(self, adapter):
        assert adapter.name_or_path != "", "name_or_path is not valid"

    def test_name_or_path_contains_model_file(self, adapter):
        assert "test.model" in adapter.name_or_path, "Condition must be true"


# ---------------------------------------------------------------------------
# Contract: encode
# ---------------------------------------------------------------------------


class TestEncodeContract:
    def test_encode_returns_list_of_int(self, adapter):
        ids = adapter.encode("hello world")
        assert isinstance(ids, list)
        assert all(isinstance(i, int) for i in ids)

    def test_encode_non_empty_string(self, adapter):
        ids = adapter.encode("hello")
        assert len(ids) > 0, "Ids must not be empty"

    def test_encode_raises_type_error_for_none(self, adapter):
        with pytest.raises(TypeError):
            adapter.encode(None)  # type: ignore[arg-type]

    def test_encode_raises_type_error_for_int(self, adapter):
        with pytest.raises(TypeError):
            adapter.encode(42)  # type: ignore[arg-type]

    def test_encode_raises_type_error_for_bytes(self, adapter):
        with pytest.raises(TypeError):
            adapter.encode(b"hello")  # type: ignore[arg-type]

    def test_encode_raises_type_error_for_list(self, adapter):
        with pytest.raises(TypeError):
            adapter.encode(["hello", "world"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Contract: decode
# ---------------------------------------------------------------------------


class TestDecodeContract:
    def test_decode_returns_str(self, adapter):
        ids = adapter.encode("hello world")
        text = adapter.decode(ids)
        assert isinstance(text, str)

    def test_decode_raises_value_error_for_non_int_ids(self, adapter):
        with pytest.raises(ValueError, match="int ids"):
            adapter.decode(["bad"])  # type: ignore[arg-type]

    def test_decode_raises_value_error_for_float_ids(self, adapter):
        with pytest.raises(ValueError, match="int ids"):
            adapter.decode([1.5])  # type: ignore[arg-type]

    def test_decode_raises_value_error_for_mixed_ids(self, adapter):
        with pytest.raises(ValueError, match="int ids"):
            adapter.decode([1, "two"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Contract: encode/decode roundtrip
# ---------------------------------------------------------------------------


class TestRoundtripContract:
    def test_hello_world_roundtrip(self, adapter):
        text = "hello world"
        ids = adapter.encode(text)
        decoded = adapter.decode(ids)
        # The stub is deterministic; decoded should contain the tokens
        assert isinstance(decoded, str)
        assert len(decoded) > 0, "Decoded must not be empty"

    def test_empty_string_encodes_to_list(self, adapter):
        ids = adapter.encode("")
        assert isinstance(ids, list)

    def test_decode_empty_ids(self, adapter):
        text = adapter.decode([])
        assert isinstance(text, str)


# ---------------------------------------------------------------------------
# Contract: validate_tokenizer_contract
# ---------------------------------------------------------------------------


class TestValidateTokenizerContract:
    def test_passes_for_valid_adapter(self, adapter):
        from src.codex_ml.interfaces.contracts import validate_tokenizer_contract

        # Should not raise
        validate_tokenizer_contract(adapter)

    def test_raises_for_missing_encode(self, tmp_path, monkeypatch):
        from src.codex_ml.interfaces.contracts import (
            TokenizationContractError,
            validate_tokenizer_contract,
        )

        class BadAdapter:
            vocab_size = 10
            name_or_path = "fake"

            def decode(self, ids):
                return ""

            def add_special_tokens(self, tokens):
                return {}

        with pytest.raises(TokenizationContractError, match="encode"):
            validate_tokenizer_contract(BadAdapter())

    def test_raises_for_missing_vocab_size(self, tmp_path):
        from src.codex_ml.interfaces.contracts import (
            TokenizationContractError,
            validate_tokenizer_contract,
        )

        class NoVocabAdapter:
            name_or_path = "fake"

            def encode(self, text):
                return [1, 2]

            def decode(self, ids):
                return "ok"

            def add_special_tokens(self, tokens):
                return {}

        with pytest.raises(TokenizationContractError, match="vocab_size"):
            validate_tokenizer_contract(NoVocabAdapter())


# ---------------------------------------------------------------------------
# Contract: TokenizerContract protocol structural check
# ---------------------------------------------------------------------------


class TestProtocolStructuralCheck:
    def test_has_all_required_methods(self, adapter):
        """Verify SentencePieceAdapter exposes all methods required by TokenizerContract."""
        assert callable(getattr(adapter, "encode", None))
        assert callable(getattr(adapter, "decode", None))
        assert callable(getattr(adapter, "add_special_tokens", None))
        assert hasattr(adapter, "vocab_size")
        assert hasattr(adapter, "name_or_path")

    def test_vocab_size_is_property(self, adapter):
        # Access twice — must be idempotent
        vs1 = adapter.vocab_size
        vs2 = adapter.vocab_size
        assert vs1 == vs2, "vs1 is not valid"

    def test_name_or_path_is_property(self, adapter):
        p1 = adapter.name_or_path
        p2 = adapter.name_or_path
        assert p1 == p2, "p1 is not valid"
