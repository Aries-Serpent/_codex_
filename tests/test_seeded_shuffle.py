from ingestion.utils import seeded_shuffle


def test_seeded_shuffle_deterministic():
    data = list(range(10))
    a = seeded_shuffle(data, seed=42)
    b = seeded_shuffle(data, seed=42)
    assert a == b
    assert sorted(a) == data
