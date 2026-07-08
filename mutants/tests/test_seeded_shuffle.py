import pytest

pytest.importorskip("charset_normalizer")
"""
Test Seeded Shuffle

Test module for seeded shuffle.
"""

from ingestion.utils import deterministic_shuffle


def test_seeded_shuffle_deterministic():
    data = list(range(10))
    a = deterministic_shuffle(data, seed=42)
    b = deterministic_shuffle(data, seed=42)
    assert a == b, "a is not valid"
    assert sorted(a) == data, "Data must not be empty"
