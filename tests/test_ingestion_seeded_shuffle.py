from ingestion.utils import deterministic_shuffle


def test_seeded_shuffle_deterministic():
    data = list(range(5))
    assert deterministic_shuffle(data, 0) == deterministic_shuffle(data, 0)
    assert deterministic_shuffle(data, 1) != deterministic_shuffle(data, 0)
