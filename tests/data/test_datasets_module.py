"""
Test Datasets Module

Test module for datasets module.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

import data.datasets as datasets

torch = pytest.importorskip("torch")
TORCH_STUB = getattr(torch, "__version__", "").endswith("stub")
pytestmark = pytest.mark.skipif(TORCH_STUB, reason="datasets tests require real torch")


@pytest.fixture(autouse=True)
def disable_torch_profiler(monkeypatch):
    """Disable PyTorch profiler to avoid Protocol isinstance issues."""
    try:
        import torch.profiler as profiler_module

        # Disable profiler record function to prevent Protocol isinstance errors
        if hasattr(profiler_module, "_record_function_enter"):
            monkeypatch.setattr(
                profiler_module, "_record_function_enter", lambda *args, **kwargs: None
            )
        if hasattr(profiler_module, "_record_function_exit"):
            monkeypatch.setattr(
                profiler_module, "_record_function_exit", lambda *args, **kwargs: None
            )
    except (ImportError, AttributeError):
        _ = None  # PyTorch profiler not available or already disabled


def _write_dataset(tmp_path: Path, name: str, rows: list[tuple[str, int]]) -> Path:
    file_path = tmp_path / name
    with file_path.open("w", encoding="utf-8") as handle:
        for text, label in rows:
            handle.write(f"{text}\t{label}\n")
    return file_path


def test_text_classification_dataset_parses_rows(tmp_path: Path) -> None:
    path = _write_dataset(tmp_path, "train.tsv", [("hello", 0), ("world", 1)])
    dataset = datasets.TextClassificationDataset(str(path))
    assert len(dataset) == 2, "Dataset must not be empty"
    assert dataset[0] == ("hello", 0)
    assert dataset[1] == ("world", 1)


def test_build_dataloaders_with_split(tmp_path: Path) -> None:
    path = _write_dataset(
        tmp_path,
        "train.tsv",
        [("alpha", 0), ("beta", 1), ("gamma", 0), ("delta", 1)],
    )

    class DummyTokenizer:
        def __call__(self, texts, **kwargs):
            batch_size = len(texts)
            return {"input_ids": torch.arange(batch_size, dtype=torch.long).unsqueeze(1)}

        batch_encode_plus = __call__

    config = datasets.DataConfig(dataset_path=str(path), batch_size=2, split_ratio=(0.5, 0.5))
    train_loader, val_loader = datasets.build_dataloaders(DummyTokenizer(), config)

    train_examples = sum(len(batch[0]) for batch in train_loader)
    val_examples = sum(len(batch[0]) for batch in val_loader) if val_loader else 0
    assert train_examples + val_examples == 4, "val_examples is not valid"
    # Create iterator explicitly for Python 3.12+ compatibility
    train_iter = iter(train_loader)
    batch_inputs, batch_labels = next(train_iter)
    assert batch_inputs.shape[0] == 2, "Condition must be true"
    assert batch_labels.dtype == torch.long, "dtype is not valid"
