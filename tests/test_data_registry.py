from __future__ import annotations

import itertools

import pytest

from src.data import registry


def test_register_and_get_roundtrip():
    name = "example_dataset"

    @registry.register(name)
    def _builder(**kwargs):
        return kwargs

    assert name in registry.list_datasets()
    result = registry.build(name, value=5)
    assert result["value"] == 5

    with pytest.raises(registry.DatasetRegistryError):
        registry.register(name)(_builder)  # type: ignore[misc]


def test_synthetic_dataset_builder_available():
    torch = pytest.importorskip("torch")
    if getattr(torch, "__version__", "").endswith("stub"):
        pytest.skip("real torch runtime is not available")
    if not hasattr(torch, "utils") or not hasattr(torch.utils, "data"):
        pytest.skip("torch.utils.data unavailable")

    train_loader, val_loader = registry.build(
        "synthetic_classification",
        num_samples=12,
        input_dim=4,
        num_classes=2,
        batch_size=4,
        seed=11,
        val_split=0.5,
    )
    batch = next(iter(train_loader))
    features, labels = batch
    assert features.shape[-1] == 4
    assert labels.dtype == torch.long
    if val_loader is not None:
        val_batch = next(iter(val_loader))
        assert isinstance(val_batch, tuple)
        assert len(val_batch) == 2
        assert all(len(b) <= 4 for b in val_batch)

    # Exhaust the loader to ensure it yields finite batches
    assert sum(1 for _ in itertools.islice(train_loader, 10)) >= 1
