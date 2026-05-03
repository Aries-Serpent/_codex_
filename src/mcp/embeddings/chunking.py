"""
Chunking Module

This module provides functionality for chunking.

Usage:
    from embeddings.chunking import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# Simple heuristic chunker (character-based) with overlap to approximate token chunking.
from collections.abc import Iterable


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def chunk_texts(items: Iterable[dict], max_chars: int = 1000, overlap: int = 200):
    """
    Input: iterable of item dicts with 'id' and 'content'.
    Output: list of {id, chunk_index, content, metadata}
    """
    out = []
    for item in items:
        cid = item.get("id")
        content = item.get("content", "")
        metadata = item.get("metadata", {})
        chunks = chunk_text(content, max_chars=max_chars, overlap=overlap)
        for i, c in enumerate(chunks):
            out.append({"id": f"{cid}__chunk__{i}", "content": c, "metadata": metadata})
    return out


def estimate_tokens_from_chars(chars: int, ratio: float = 4.0) -> int:
    return max(1, int(chars / ratio))
