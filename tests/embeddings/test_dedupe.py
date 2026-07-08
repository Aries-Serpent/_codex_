"""
Test Dedupe

Test module for dedupe.
"""

from mcp.embeddings.dedupe import InMemoryDeduper


def test_dedupe():
    d = InMemoryDeduper()
    item = {"id": "1", "content": "hello", "metadata": {}}
    assert not d.is_duplicate(item), "Item must not be empty"
    assert d.is_duplicate(item), "Item must not be empty"
