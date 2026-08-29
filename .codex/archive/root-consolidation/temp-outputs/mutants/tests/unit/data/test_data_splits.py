"""Unit tests for data split utilities and dataset parsing (Phase 23 Week 1)."""

import pytest

from data import datasets


def test_dataloader_config_validation_bounds():
    """Test DataLoaderConfig validates batch size and worker bounds."""
    from data.datasets import DataLoaderConfig

    # Valid config
    config = DataLoaderConfig(batch_size=32, num_workers=4)
    assert config.batch_size == 32, "batch_size is not valid"
    assert config.num_workers == 4, "num_workers is not valid"

    # Invalid batch size
    with pytest.raises(ValueError, match="batch_size must be positive"):
        DataLoaderConfig(batch_size=0)

    # Invalid workers
    with pytest.raises(ValueError, match="num_workers must be non-negative"):
        DataLoaderConfig(num_workers=-1)


def test_split_ratio_validation():
    """Test build_dataloaders validates split ratios."""
    torch = pytest.importorskip("torch")

    class DummyTokenizer:
        def batch_encode_plus(self, texts, **kwargs):
            return {"input_ids": torch.zeros((len(texts), 4), dtype=torch.long)}

    # Invalid ratio sum
    with pytest.raises(ValueError, match="split ratios must sum to 1.0"):
        datasets.build_dataloaders(
            "dummy.tsv",
            DummyTokenizer(),
            split_ratio=(0.7, 0.2),  # Sums to 0.9, not 1.0
        )

    # Negative ratio
    with pytest.raises(ValueError, match="split ratios must be positive"):
        datasets.build_dataloaders(
            "dummy.tsv",
            DummyTokenizer(),
            split_ratio=(-0.1, 1.1),
        )


def test_invalid_signature_handling(tmp_path):
    """Test dataset parsing handles invalid signatures gracefully."""
    data_file = tmp_path / "invalid.tsv"
    data_file.write_text("missing_tab_no_label\n")

    with pytest.raises(ValueError, match="Invalid TSV format"):
        datasets.parse_tsv_dataset(str(data_file))


def test_empty_dataset_parsing(tmp_path):
    """Test dataset parsing handles empty input."""
    data_file = tmp_path / "empty.tsv"
    data_file.write_text("")

    result = datasets.parse_tsv_dataset(str(data_file))
    assert len(result) == 0, "Result must not be empty"


def test_partial_dataset_parsing(tmp_path):
    """Test dataset parsing handles partial/malformed rows."""
    data_file = tmp_path / "partial.tsv"
    data_file.write_text("valid\t1\ninvalid_line\nvalid2\t0\n")

    result = datasets.parse_tsv_dataset(str(data_file))
    # Should skip malformed line
    assert len(result) == 2, "Result must not be empty"


def test_split_length_normalization():
    """Test split lengths normalize to dataset size."""
    torch = pytest.importorskip("torch")

    dataset = torch.utils.data.TensorDataset(torch.randn(100, 10), torch.randint(0, 2, (100,)))

    train_ds, val_ds = datasets.split_dataset(dataset, split_ratio=(0.8, 0.2))
    assert len(train_ds) + len(val_ds) == 100, "Train_ds must not be empty"


def test_split_error_conditions():
    """Test split_dataset handles error conditions."""
    torch = pytest.importorskip("torch")

    torch.utils.data.TensorDataset(torch.randn(10, 5), torch.randint(0, 2, (10,)))

    # Empty dataset
    with pytest.raises(ValueError, match="Cannot split empty dataset"):
        datasets.split_dataset(
            torch.utils.data.TensorDataset(torch.zeros(0, 5), torch.zeros(0, dtype=torch.long)),
            split_ratio=(0.8, 0.2),
        )

    # Single sample with validation
    with pytest.raises(ValueError, match="Insufficient samples for validation split"):
        datasets.split_dataset(
            torch.utils.data.TensorDataset(torch.randn(1, 5), torch.tensor([0])),
            split_ratio=(0.5, 0.5),
        )


def test_deterministic_split_reproducibility():
    """Test splits are reproducible with fixed seed."""
    torch = pytest.importorskip("torch")

    dataset = torch.utils.data.TensorDataset(torch.randn(100, 10), torch.randint(0, 2, (100,)))

    train1, val1 = datasets.split_dataset(dataset, split_ratio=(0.8, 0.2), seed=123)
    train2, val2 = datasets.split_dataset(dataset, split_ratio=(0.8, 0.2), seed=123)

    # Same indices
    assert len(train1) == len(train2), "Train1 must not be empty"
    assert len(val1) == len(val2), "Val1 must not be empty"


def test_tsv_dataset_text_extraction(tmp_path):
    """Test TSV parsing extracts text and labels correctly."""
    data_file = tmp_path / "data.tsv"
    data_file.write_text("hello world\t1\nfoo bar\t0\n")

    result = datasets.parse_tsv_dataset(str(data_file))
    assert len(result) == 2, "Result must not be empty"
    assert result[0][0] == "hello world", "Result must not be empty"
    assert result[0][1] == 1, "Result must not be empty"
    assert result[1][0] == "foo bar", "Result must not be empty"
    assert result[1][1] == 0, "Result must not be empty"


def test_collate_fn_missing_keys():
    """Test collate function handles missing required keys."""
    torch = pytest.importorskip("torch")

    batch = [
        {"attention_mask": torch.ones(4)},  # Missing input_ids
        {"attention_mask": torch.ones(4)},
    ]

    with pytest.raises(KeyError, match="input_ids"):
        datasets.default_collate(batch)


def test_dataloader_batch_size_override(tmp_path):
    """Test dataloader respects batch size configuration."""
    torch = pytest.importorskip("torch")

    data_file = tmp_path / "data.tsv"
    data_file.write_text("a\t1\nb\t0\nc\t1\nd\t0\n")

    class DummyTokenizer:
        def batch_encode_plus(self, texts, **kwargs):
            return {"input_ids": torch.zeros((len(texts), 4), dtype=torch.long)}

    loader, _ = datasets.build_dataloaders(
        str(data_file),
        DummyTokenizer(),
        batch_size=2,
    )

    assert loader.batch_size == 2, "batch_size is not valid"
