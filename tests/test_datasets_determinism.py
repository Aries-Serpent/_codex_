import pytest

pytestmark = pytest.mark.requires_torch

datasets = pytest.importorskip("src.data.datasets", reason="torch required")
torch = pytest.importorskip("torch", reason="torch required")


def test_deterministic_split_same_seed_repeats():
    dataset = datasets.tiny_tensor_dataset(n=20, d_in=4, n_classes=3)
    split1 = datasets.deterministic_split(dataset, [0.5, 0.5], seed=123)
    split2 = datasets.deterministic_split(dataset, [0.5, 0.5], seed=123)
    assert len(split1) == len(split2) == 2
    assert set(split1[0].indices) == set(split2[0].indices)
    assert set(split1[1].indices) == set(split2[1].indices)


def test_deterministic_split_diff_seed_changes():
    dataset = datasets.tiny_tensor_dataset(n=20, d_in=4, n_classes=3)
    split1 = datasets.deterministic_split(dataset, [0.5, 0.5], seed=1)
    split2 = datasets.deterministic_split(dataset, [0.5, 0.5], seed=2)
    assert set(split1[0].indices) != set(split2[0].indices) or set(split1[1].indices) != set(
        split2[1].indices
    )
