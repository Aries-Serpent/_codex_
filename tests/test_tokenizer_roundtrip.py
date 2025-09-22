from __future__ import annotations

from typing import Iterable, Sequence

from codex_ml.interfaces.tokenizer import HFTokenizer, WhitespaceTokenizer


def _safe_tokenizer() -> HFTokenizer | WhitespaceTokenizer:
    """Return an HF tokenizer when available, otherwise fall back to whitespace."""

    try:
        return HFTokenizer(
            "hf-internal-testing/tiny-random-bert",
            padding=True,
            truncation=True,
            max_length=16,
        )
    except Exception:
        return WhitespaceTokenizer()


def _non_empty(ids: Iterable[int]) -> bool:
    return any(int(x) != 0 for x in ids)


def test_roundtrip_encode_decode() -> None:
    tokenizer = _safe_tokenizer()
    text = "hello world"

    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)

    assert isinstance(encoded, list)
    assert _non_empty(encoded)
    assert isinstance(decoded, str)
    assert decoded.strip() != ""


def test_batch_encode_shapes_stable() -> None:
    tokenizer = _safe_tokenizer()
    items: Sequence[str] = (
        "one two three",
        "alpha beta gamma",
        "delta epsilon",
    )
    batch = tokenizer.batch_encode(items)
    assert isinstance(batch, list)
    assert len(batch) == len(items)
    assert all(isinstance(row, list) for row in batch)

    as_mapping = tokenizer.batch_encode(items, return_dict=True)
    if isinstance(as_mapping, dict):
        assert "input_ids" in as_mapping
        input_ids = as_mapping.get("input_ids")
        if isinstance(input_ids, Sequence):
            assert len(input_ids) == len(items)
