from training.data_utils import split_texts


def test_split_seed_reproducibility() -> None:
    texts = ["a", "b", "c", "d", "e"]
    t1, v1 = split_texts(texts, seed=123)
    t2, v2 = split_texts(texts, seed=123)
    t3, v3 = split_texts(texts, seed=321)
    assert t1 == t2 and v1 == v2
    assert (t1, v1) != (t3, v3)
