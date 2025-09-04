#!/usr/bin/env python3
"""Edge-case tests for SentencePieceAdapter using a vendored tiny model."""

# ruff: noqa: INP001
from pathlib import Path

import pytest

from src.tokenization.sentencepiece_adapter import SentencePieceAdapter

spm = pytest.importorskip("sentencepiece")


def test_padding_truncation_roundtrip() -> None:
    """Verify encoding/decoding with vendored tiny model."""
    # tiny toy model vendored in tests/assets
    model = Path(__file__).resolve().parents[1] / "assets" / "spm_tiny.model"
    if not model.exists():
        pytest.skip("Missing spm_tiny.model; run tools/gen_tiny_spm.py to create artifacts.")

    tok = SentencePieceAdapter(model_path=model)
    ids = tok.encode("hello world", padding="max_length", truncation="only_first", max_length=8)
    assert len(ids) == 8  # noqa: PLR2004,S101
    text = tok.decode(ids)
    assert isinstance(text, str)  # noqa: S101
