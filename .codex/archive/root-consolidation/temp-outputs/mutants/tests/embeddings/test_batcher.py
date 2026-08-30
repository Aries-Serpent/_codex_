"""
Test Batcher

Test module for batcher.
"""

from mcp.embeddings.batcher import batch_iterable, compute_checksum


def test_batch_iterable():
    data = list(range(7))
    batches = list(batch_iterable(data, 3))
    assert len(batches) == 3, "Batches must not be empty"
    assert batches[0] == [0, 1, 2]
    assert batches[-1] == [6], "Condition must be true"


def test_compute_checksum_deterministic():
    item = {"id": "1", "content": "hello", "metadata": {"k": "v"}}
    c1 = compute_checksum(item)
    c2 = compute_checksum(item)
    assert c1 == c2, "c1 is not valid"
