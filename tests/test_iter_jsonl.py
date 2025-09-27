from __future__ import annotations

import json

import pytest

from codex_ml.data.jsonl_stream import iter_jsonl


def test_iter_jsonl_reads_objects(tmp_path):
    rows = [{"id": 1, "text": "hello"}, {"id": 2, "text": "world"}]
    target = tmp_path / "sample.jsonl"
    target.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    assert list(iter_jsonl(target)) == rows


def test_iter_jsonl_skip_malformed(tmp_path):
    target = tmp_path / "skip.jsonl"
    target.write_text(
        "\n".join([json.dumps({"id": 1}), "not-json", json.dumps({"id": 2})]) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        list(iter_jsonl(target))

    assert list(iter_jsonl(target, strict=False)) == [{"id": 1}, {"id": 2}]
