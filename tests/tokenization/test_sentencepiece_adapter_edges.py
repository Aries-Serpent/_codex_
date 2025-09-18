#!/usr/bin/env python3
"""Edge-case tests for SentencePieceAdapter using a vendored tiny model."""

# ruff: noqa: INP001
from pathlib import Path

import pytest

from src.tokenization.sentencepiece_adapter import SentencePieceAdapter

spm = pytest.importorskip("sentencepiece")


def _load_tiny_adapter() -> SentencePieceAdapter:
    model = Path(__file__).resolve().parents[1] / "assets" / "spm_tiny.model"
    if not model.exists():
        pytest.skip("Missing spm_tiny.model; run tools/gen_tiny_spm.py to create artifacts.")
    assert model.exists(), "Missing spm_tiny.model; run tools/gen_tiny_spm.py to create artifacts."
    return SentencePieceAdapter(model_path=model)


def test_padding_truncation_roundtrip() -> None:
    """Verify encoding/decoding with vendored tiny model."""
    tok = _load_tiny_adapter()
    ids = tok.encode("hello world", padding="max_length", truncation="only_first", max_length=8)
    assert len(ids) == 8  # noqa: PLR2004,S101
    text = tok.decode(ids)
    assert isinstance(text, str)  # noqa: S101


@pytest.mark.parametrize("truncation", ["only_first", "longest_first"])
def test_single_sequence_truncation_preserves_prefix(truncation: str) -> None:
    tok = _load_tiny_adapter()
    text = "hello world again"
    full_ids = tok.encode(text)
    ids = tok.encode(text, truncation=truncation, max_length=2)
    assert len(ids) == 2  # noqa: PLR2004,S101
    assert ids == full_ids[:2]


def test_only_first_truncation_matches_prefix_roundtrip() -> None:
    tok = _load_tiny_adapter()
    text = "hello world again"
    full_ids = tok.encode(text)
    ids = tok.encode(text, truncation="only_first", max_length=3)
    expected = tok.decode(full_ids[:3])
    decoded = tok.decode(ids)
    assert decoded == expected
