from ingestion.utils import seeded_shuffle


def test_seeded_shuffle_deterministic():
    data = list(range(5))
    assert seeded_shuffle(data, 0) == seeded_shuffle(data, 0)
    assert seeded_shuffle(data, 1) != seeded_shuffle(data, 0)
