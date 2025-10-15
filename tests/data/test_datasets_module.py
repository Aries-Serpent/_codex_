import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest  # noqa: E402

import data.datasets as datasets  # noqa: E402

torch = pytest.importorskip("torch")
TORCH_STUB = getattr(torch, "__version__", "").endswith("stub")
pytestmark = pytest.mark.skipif(TORCH_STUB, reason="datasets tests require real torch")


def _write_dataset(tmp_path: Path, name: str, rows: list[tuple[str, int]]) -> Path:
    file_path = tmp_path / name
    with file_path.open("w", encoding="utf-8") as handle:
        for text, label in rows:
            handle.write(f"{text}\t{label}\n")
    return file_path


def test_text_classification_dataset_parses_rows(tmp_path: Path) -> None:
    path = _write_dataset(tmp_path, "train.tsv", [("hello", 0), ("world", 1)])
    dataset = datasets.TextClassificationDataset(str(path))
    assert len(dataset) == 2
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
    assert train_examples + val_examples == 4
    batch_inputs, batch_labels = next(iter(train_loader))
    assert batch_inputs.shape[0] == 2
    assert batch_labels.dtype == torch.long
