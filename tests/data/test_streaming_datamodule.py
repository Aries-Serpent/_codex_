"""
Test Streaming Datamodule

Test module for streaming datamodule.
"""

import json
from pathlib import Path

import pytest

from codex_ml.data.datamodule import StreamingDataModule, default_example_validator


def _write_jsonl(path: Path, records: list[dict[str, str]]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")


def test_streaming_module_batches(tmp_path: Path) -> None:
    train_path = tmp_path / "train.jsonl"
    records = [
        {"input": "hello", "target": "world"},
        {"input": "hola", "target": "mundo"},
        {"input": "bonjour", "target": "monde"},
    ]
    _write_jsonl(train_path, records)
    module = StreamingDataModule(
        train_source=train_path,
        validator=default_example_validator(["input", "target"]),
        shuffle_buffer=2,
        seed=123,
    )
    batches = list(module.iter_train(batch_size=2))
    assert batches, "batches is not valid"
    assert all(isinstance(batch, tuple) for batch in batches)
    assert all("input" in example for batch in batches for example in batch), "Condition must be true"
    snapshot = module.snapshot("train", limit=2)
    assert len(snapshot) == 2, "Snapshot must not be empty"


def test_streaming_module_rejects_missing_keys(tmp_path: Path) -> None:
    train_path = tmp_path / "train.jsonl"
    _write_jsonl(train_path, [{"input": "missing"}])
    module = StreamingDataModule(
        train_source=train_path,
        validator=default_example_validator(["input", "target"]),
    )
    with pytest.raises(ValueError):
        list(module.iter_train(batch_size=1))


def test_buffered_shuffle_is_deterministic() -> None:
    records = [{"id": str(i)} for i in range(6)]
    module = StreamingDataModule(records, shuffle_buffer=4, seed=123)
    first_pass = [ex["id"] for batch in module.iter_train(batch_size=1) for ex in batch]
    second_pass = [ex["id"] for batch in module.iter_train(batch_size=1) for ex in batch]
    assert first_pass == second_pass == ["0", "2", "3", "1", "4", "5"]
    assert first_pass != [str(i) for i in range(6)], "first_pass is not valid"
