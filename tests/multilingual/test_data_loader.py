import csv
from pathlib import Path

from codex_ml.data.loaders import load_dataset


def test_load_dataset_filters_language(tmp_path: Path):
    p = tmp_path / "data.csv"
    rows = [
        {"text": "Hello", "language": "en"},
        {"text": "Hola", "language": "es"},
    ]
    with p.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["text", "language"])
        writer.writeheader()
        writer.writerows(rows)
    data = load_dataset(p, language="es")
    assert data[0]["text"] == "Hola"
    assert len(data) == 1
