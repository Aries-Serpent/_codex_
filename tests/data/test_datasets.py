"""Smoke tests for :mod:`data.datasets`."""

from __future__ import annotations

from pathlib import Path

import pytest

from data.datasets import DataConfig, TextClassificationDataset


def test_text_classification_dataset_parses_rows(tmp_path: Path):
    data = tmp_path / "train.tsv"
    data.write_text("hello\t1\nworld\t0\n")
    ds = TextClassificationDataset(str(data))
    assert len(ds) == 2
    assert ds[0][0] == "hello"


def test_data_config_defaults():
    cfg = DataConfig(dataset_path="train.tsv")
    assert cfg.batch_size == 8
    assert cfg.seed == 42
