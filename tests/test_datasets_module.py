"""
Test Datasets Module

Test module for datasets module.
"""

from __future__ import annotations

import pytest

# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")
try:
    import torch
except (ImportError, AttributeError) as exc:  # pragma: no cover - runtime guard
    pytest.skip(f"PyTorch runtime not available: {exc}", allow_module_level=True)

from data.datasets import (
    DataLoaderConfig,
    build_text_classification_dataloaders,
    load_text_classification_dataset,
)


class StubTokenizer:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], dict[str, object]]] = []

    def batch_encode_plus(self, texts, **kwargs):
        self.calls.append((list(texts), kwargs))
        length = kwargs["max_length"]
        batch_size = len(texts)
        return {
            "input_ids": torch.ones((batch_size, length), dtype=torch.long),
            "attention_mask": torch.ones((batch_size, length), dtype=torch.long),
        }


def test_build_text_classification_dataloaders(tmp_path):
    dataset_path = tmp_path / "dataset.tsv"
    dataset_path.write_text("hello\t0\nworld\t1\nfoo\t0\nbar\t1\n", encoding="utf-8")

    tokenizer = StubTokenizer()
    config = DataLoaderConfig(
        file_path=str(dataset_path),
        batch_size=2,
        max_length=32,
        validation_split=0.5,
        seed=1,
    )

    train_loader, val_loader = build_text_classification_dataloaders(tokenizer, config)

    # Create iterator explicitly for Python 3.12+ compatibility
    train_iter = iter(train_loader)
    batch = next(train_iter)
    assert set(batch.keys()) == {"input_ids", "attention_mask", "labels"}
    assert batch["input_ids"].shape == (2, 32)
    assert batch["labels"].dtype == torch.long, "dtype is not valid"
    assert val_loader is not None, "val_loader must be initialized"


def test_load_text_classification_dataset_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_text_classification_dataset(tmp_path / "missing.tsv")
