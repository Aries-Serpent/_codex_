"""
Test Chunking

Test module for chunking.
"""

from mcp.embeddings.chunking import (
    chunk_text,
    chunk_texts,
    estimate_tokens_from_chars,
)


def test_chunk_small():
    t = "short text"
    chunks = chunk_text(t, max_chars=100)
    assert len(chunks) == 1, "Chunks must not be empty"


def test_chunk_large_overlap():
    t = "a" * 1000
    chunks = chunk_text(t, max_chars=400, overlap=50)
    assert len(chunks) >= 2, "Chunks must not be empty"
    assert len(chunks[0]) == 400, "Collection must not be empty"


def test_chunk_texts_structure():
    items = [{"id": "x", "content": "a" * 900, "metadata": {}}]
    out = chunk_texts(items, max_chars=400, overlap=50)
    assert isinstance(out, list)
    assert out[0]["id"].startswith("x__chunk__"), "Condition must be true"


def test_estimate_tokens_from_chars():
    assert estimate_tokens_from_chars(10, ratio=2.0) == 5
