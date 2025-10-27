from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from codex_ml.data.streaming import StreamingDataModule, iter_jsonl_chunks


def _write_jsonl(tmp_path: Path, rows: list[dict[str, Any]]) -> Path:
    path = tmp_path / "dataset.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    return path


def test_iter_jsonl_chunks_yields_fixed_sizes(tmp_path: Path) -> None:
    path = _write_jsonl(tmp_path, [{"id": i} for i in range(5)])
    chunks = list(iter_jsonl_chunks(path, chunk_size=2))
    assert [len(chunk) for chunk in chunks] == [2, 2, 1]
    assert chunks[0][0]["id"] == 0


def test_iter_jsonl_chunks_validator(tmp_path: Path) -> None:
    path = _write_jsonl(tmp_path, [{"id": 1}, {"id": None}])

    def _validator(record: dict[str, Any]) -> None:
        if record.get("id") is None:
            raise ValueError("missing id")

    with pytest.raises(ValueError):
        list(iter_jsonl_chunks(path, chunk_size=1, validator=_validator))


def test_streaming_data_module_batches_jsonl(tmp_path: Path) -> None:
    path = _write_jsonl(tmp_path, [{"id": i} for i in range(4)])
    module = StreamingDataModule(train_source=path, batch_size=3, ingest_chunk_size=2)
    batches = list(module.iter_train())
    assert [len(batch) for batch in batches] == [3, 1]
    assert batches[0][0]["id"] == 0


def test_streaming_data_module_validates_iterables() -> None:
    records = [{"id": 1}, {"id": 2}, {"id": 3}]
    seen: list[int] = []

    def _validator(record: dict[str, Any]) -> None:
        seen.append(int(record["id"]))

    module = StreamingDataModule(train_source=records, batch_size=2, validator=_validator)
    batches = list(module.iter_train())
    assert [len(batch) for batch in batches] == [2, 1]
    assert seen == [1, 2, 3]
