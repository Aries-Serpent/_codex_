from __future__ import annotations

import json
from pathlib import Path

from codex_ml.data.datamodule import StreamingDataModule


def test_streaming_datamodule_batches(tmp_path: Path) -> None:
    train = tmp_path / "train.jsonl"
    train.write_text("\n".join(json.dumps({"i": i}) for i in range(5)), encoding="utf-8")
    module = StreamingDataModule(train_path=train, batch_size=2)
    batches = list(module.iter_train())
    assert len(batches) == 3
    assert batches[0][0]["i"] == 0


def test_streaming_validator_called(tmp_path: Path) -> None:
    train = tmp_path / "train.jsonl"
    train.write_text(json.dumps({"i": 1}), encoding="utf-8")
    seen: list[int] = []

    def validate(record: dict[str, int]) -> None:
        seen.append(record["i"])

    module = StreamingDataModule(train_path=train, validator=validate)
    list(module.iter_train())
    assert seen == [1]
