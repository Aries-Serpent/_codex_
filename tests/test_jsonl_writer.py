from __future__ import annotations

import json

from codex_ml.utils.jsonl import append_jsonl


def test_append_jsonl_appends_records(tmp_path) -> None:
    target = tmp_path / "metrics" / "events.jsonl"

    append_jsonl(target, {"step": 1, "loss": 0.5})
    append_jsonl(target, {"step": 2, "loss": 0.25})

    data = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line]
    assert data == [
        {"step": 1, "loss": 0.5},
        {"step": 2, "loss": 0.25},
    ]
