# BEGIN: CODEX_DATA_TESTS
from pathlib import Path

import pytest

from codex_ml.data.loaders import collect_stats, iter_jsonl, iter_txt, stream_paths


def _write(tmp: Path, name: str, lines):
    p = tmp / name
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def test_jsonl_stream_basic(tmp_path: Path):
    data = [
        '{"prompt":"p1","completion":"c1"}',
        '{"prompt":"p2","completion":"c2"}',
    ]
    f = _write(tmp_path, "a.jsonl", data)
    rows = list(iter_jsonl(f))
    assert len(rows) == 2
    assert rows[0].prompt == "p1" and rows[0].completion == "c1"


def test_txt_stream_basic(tmp_path: Path):
    f = _write(tmp_path, "a.txt", ["p1\tc1", "p2\tc2"])
    rows = list(iter_txt(f))
    assert rows[1].prompt == "p2"


def test_stream_paths_with_limits(tmp_path: Path):
    f1 = _write(tmp_path, "a.jsonl", ['{"prompt":"x","completion":"y"}'] * 5)
    out = list(stream_paths([f1], fmt="jsonl", max_samples=3))
    assert len(out) == 3


def test_collect_stats(tmp_path: Path):
    f1 = _write(tmp_path, "a.txt", ["hello\tworld", "foo\tbar baz"])
    stats = collect_stats(iter_txt(f1))
    assert stats["samples"] == 2
    assert stats["avg_prompt_len"] > 0
    assert stats["avg_completion_tokens"] > 0


def test_validation_errors(tmp_path: Path):
    bad = _write(tmp_path, "bad.jsonl", ['{"prompt": 123, "completion": "ok"}'])
    it = iter_jsonl(bad)
    with pytest.raises(Exception):
        next(it)


# END: CODEX_DATA_TESTS
