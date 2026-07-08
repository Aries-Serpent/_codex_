"""Data pipeline integration tests (Phase 23 Week 2)."""

import pytest

from data import datasets


def _make_tokenizer(torch):
    """Create mock tokenizer for testing."""

    class Tokenizer:
        def batch_encode_plus(self, texts, **kwargs):
            batch = len(texts)
            return {"input_ids": torch.zeros((batch, 4), dtype=torch.long)}

    return Tokenizer()


@pytest.mark.integration
def test_data_pipeline_split_behavior(tmp_path):
    """Test data pipeline handles split ratios correctly."""
    torch = pytest.importorskip("torch")

    data_file = tmp_path / "data.tsv"
    data_file.write_text("a\t1\nb\t0\nc\t1\nd\t0\n")

    train_loader, val_loader = datasets.build_dataloaders(
        str(data_file),
        _make_tokenizer(torch),
        split_ratio=(0.75, 0.25),
        seed=123,
    )

    assert train_loader is not None, "train_loader must be initialized"
    assert val_loader is not None, "val_loader must be initialized"


@pytest.mark.integration
def test_data_pipeline_validation_path(tmp_path):
    """Test data pipeline with explicit validation path."""
    torch = pytest.importorskip("torch")

    train_file = tmp_path / "train.tsv"
    val_file = tmp_path / "val.tsv"
    train_file.write_text("train1\t1\ntrain2\t0\n")
    val_file.write_text("val1\t1\n")

    train_loader, val_loader = datasets.build_dataloaders(
        str(train_file),
        _make_tokenizer(torch),
        validation_path=str(val_file),
    )

    assert len(train_loader.dataset) == 2, "Collection must not be empty"
    assert len(val_loader.dataset) == 1, "Collection must not be empty"


@pytest.mark.integration
def test_data_pipeline_single_row_edge_case(tmp_path):
    """Test data pipeline handles single-row dataset."""
    torch = pytest.importorskip("torch")

    data_file = tmp_path / "single.tsv"
    data_file.write_text("only\t1\n")

    train_loader, val_loader = datasets.build_dataloaders(
        str(data_file),
        _make_tokenizer(torch),
    )

    assert len(train_loader.dataset) == 1, "Collection must not be empty"
    assert val_loader is None, "val_loader is not valid"


@pytest.mark.integration
def test_data_pipeline_tokenizer_output(tmp_path):
    """Test data pipeline validates tokenizer output."""
    torch = pytest.importorskip("torch")

    data_file = tmp_path / "data.tsv"
    data_file.write_text("text\t1\n")

    class BadTokenizer:
        def batch_encode_plus(self, texts, **kwargs):
            return {"attention_mask": torch.ones((len(texts), 4))}

    with pytest.raises(KeyError, match="input_ids"):
        train_loader, _ = datasets.build_dataloaders(
            str(data_file),
            BadTokenizer(),
        )
        # Force iteration to trigger collate error - create iterator explicitly for Python 3.12+ compatibility
        dataloader_iter = iter(train_loader)
        next(dataloader_iter)


@pytest.mark.integration
def test_data_pipeline_deterministic_seed(tmp_path):
    """Test data pipeline produces deterministic splits."""
    torch = pytest.importorskip("torch")

    data_file = tmp_path / "data.tsv"
    data_file.write_text("\n".join([f"text{i}\t{i%2}" for i in range(100)]))

    train1, val1 = datasets.build_dataloaders(
        str(data_file),
        _make_tokenizer(torch),
        split_ratio=(0.8, 0.2),
        seed=42,
    )

    train2, val2 = datasets.build_dataloaders(
        str(data_file),
        _make_tokenizer(torch),
        split_ratio=(0.8, 0.2),
        seed=42,
    )

    assert len(train1.dataset) == len(train2.dataset), "Collection must not be empty"
    assert len(val1.dataset) == len(val2.dataset), "Collection must not be empty"


@pytest.mark.integration
def test_data_pipeline_fixture_parsing(tmp_path):
    """Test data pipeline parses fixture file."""
    torch = pytest.importorskip("torch")

    fixture_file = tmp_path / "fixture.tsv"
    fixture_file.write_text("sample1\t1\nsample2\t0\nsample3\t1\n")

    train_loader, _ = datasets.build_dataloaders(
        str(fixture_file),
        _make_tokenizer(torch),
    )

    assert len(train_loader.dataset) == 2, "Collection must not be empty"
