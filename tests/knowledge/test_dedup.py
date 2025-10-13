from __future__ import annotations

from codex.knowledge.dedup import dedup_records, hamming, simhash


def test_simhash_stability_for_similar_text() -> None:
    a = simhash("Hello world")
    b = simhash("Hello world!")
    c = simhash("Entirely different sentence")
    assert hamming(a, b) <= 3
    assert hamming(a, c) > 3


def test_dedup_records_filters_near_duplicates() -> None:
    texts = [
        "alpha beta gamma",
        "alpha beta gamma!",
        "unrelated content",
        "alpha beta gamma",  # identical to first
    ]
    keep = dedup_records(texts, threshold=3)
    assert len(keep) == 2
    assert 0 in keep  # first entry kept
    assert 2 in keep  # unrelated entry kept
