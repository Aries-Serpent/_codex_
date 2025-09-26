import json
from pathlib import Path
import pytest

from codex_ml.data import loaders


def test_load_jsonl(tmp_path):
    file = tmp_path / "data.jsonl"
    lines = [
        {"id": 1, "text": "hello"},
        {"id": 2, "text": "world"},
    ]
    with file.open("w", encoding="utf-8") as f:
        for obj in lines:
            f.write(json.dumps(obj) + "\n")

    records, meta = loaders.load_jsonl(file)
    assert len(records) == 2
    assert meta["num_records"] == 2
    assert meta["format"] == "jsonl"
    assert "checksum" in meta and len(meta["checksum"]) == 64
    # Deterministic checksum: recompute
    checksum2 = loaders.compute_file_checksum(file)
    assert checksum2 == meta["checksum"]


def test_load_csv(tmp_path):
    file = tmp_path / "data.csv"
    content = "id,text\n1,foo\n2,bar\n"
    file.write_text(content, encoding="utf-8")
    records, meta = loaders.load_csv(file)
    assert len(records) == 2
    assert records[0]["id"] == "1"
    assert meta["format"] == "csv"
    assert meta["num_records"] == 2
    assert "checksum" in meta and len(meta["checksum"]) == 64


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        loaders.load_jsonl("missing.jsonl")