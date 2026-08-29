"""Phase 24 E2E workflow tests."""

import pytest

from data import datasets


def _make_tokenizer(torch):
    class Tokenizer:
        def batch_encode_plus(self, texts, **kwargs):
            batch = len(texts)
            return {"input_ids": torch.zeros((batch, 4), dtype=torch.long)}

    return Tokenizer()


@pytest.mark.e2e
def test_end_to_end_dataloaders_split(tmp_path):
    """Test end-to-end dataloader split workflow."""
    torch = pytest.importorskip("torch")
    data_file = tmp_path / "data.tsv"
    data_file.write_text("hello\t1\nworld\t0\n", encoding="utf-8")

    train_loader, val_loader = datasets.build_dataloaders(
        str(data_file),
        _make_tokenizer(torch),
        split_ratio=(0.5, 0.5),
        seed=123,
    )

    assert train_loader is not None, "train_loader must be initialized"
    assert val_loader is not None, "val_loader must be initialized"


@pytest.mark.e2e
def test_end_to_end_validation_path(tmp_path):
    """Test end-to-end validation path workflow."""
    torch = pytest.importorskip("torch")
    train_path = tmp_path / "train.tsv"
    val_path = tmp_path / "val.tsv"
    train_path.write_text("hello\t1\nworld\t0\n", encoding="utf-8")
    val_path.write_text("holdout\t1\n", encoding="utf-8")

    train_loader, val_loader = datasets.build_dataloaders(
        str(train_path),
        _make_tokenizer(torch),
        validation_path=str(val_path),
    )

    assert len(train_loader.dataset) == 2, "Collection must not be empty"
    assert len(val_loader.dataset) == 1, "Collection must not be empty"


@pytest.mark.e2e
def test_end_to_end_single_row_no_val(tmp_path):
    """Test end-to-end single-row workflow."""
    torch = pytest.importorskip("torch")
    data_file = tmp_path / "single.tsv"
    data_file.write_text("only\t1\n", encoding="utf-8")

    train_loader, val_loader = datasets.build_dataloaders(
        str(data_file),
        _make_tokenizer(torch),
    )

    assert len(train_loader.dataset) == 1, "Collection must not be empty"
    assert val_loader is None, "val_loader is not valid"


@pytest.mark.e2e
def test_end_to_end_missing_input_ids(tmp_path):
    """Test end-to-end missing input_ids error handling."""
    torch = pytest.importorskip("torch")
    data_file = tmp_path / "data.tsv"
    data_file.write_text("hello\t1\nworld\t0\n", encoding="utf-8")

    class BadTokenizer:
        def batch_encode_plus(self, texts, **kwargs):
            return {"attention_mask": torch.ones((len(texts), 4), dtype=torch.long)}

    with pytest.raises(KeyError):
        train_loader, _ = datasets.build_dataloaders(
            str(data_file),
            BadTokenizer(),
        )
        # Force iteration to trigger error
        next(iter(train_loader))
