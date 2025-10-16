from __future__ import annotations

from pathlib import Path

import pytest

from src.data import datasets


class DummyTokenizer:
    def batch_encode_plus(self, texts, padding, truncation, max_length, return_tensors):
        assert padding == "max_length"
        assert truncation is True
        assert max_length == 64 or max_length == 128
        encoded = [[len(text)] for text in texts]
        return {"input_ids": encoded, "labels": [idx for idx, _ in enumerate(texts)]}


def test_build_dataloaders(tmp_path: Path) -> None:
    data_path = tmp_path / "samples.tsv"
    data_path.write_text("hello\t0\nworld\t1\nthird\t0\n", encoding="utf-8")
    tokenizer = DummyTokenizer()
    train_loader, val_loader = datasets.build_dataloaders(
        data_path, tokenizer, batch_size=2, max_length=64
    )
    batches = list(iter(train_loader))
    assert batches
    if val_loader is not None:
        assert list(iter(val_loader))


def test_split_ratio_validation(tmp_path: Path) -> None:
    data_path = tmp_path / "samples.tsv"
    data_path.write_text("hello\t0\n", encoding="utf-8")
    with pytest.raises(ValueError):
        datasets.build_dataloaders(data_path, DummyTokenizer(), split_ratio=(0.5, 0.4))
