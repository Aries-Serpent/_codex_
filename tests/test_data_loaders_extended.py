import json
from pathlib import Path
import pytest

from codex_ml.data import loaders


def test_jsonl_empty_file(tmp_path):
    f = tmp_path / "empty.jsonl"
    f.write_text("", encoding="utf-8")
    records, meta = loaders.load_jsonl(f)
    assert records == []
    assert meta["num_records"] == 0
    assert meta["empty_file"] is True
    assert meta["skipped_malformed"] == 0


def test_jsonl_bom_and_malformed(tmp_path):
    f = tmp_path / "data.jsonl"
    # Include BOM + one good line + one malformed + one good
    content = "\ufeff" + json.dumps({"a": 1}) + "\n" + "{bad json}\n" + json.dumps({"b": 2}) + "\n"
    f.write_text(content, encoding="utf-8")
    records, meta = loaders.load_jsonl(f)
    assert len(records) == 2
    assert meta["skipped_malformed"] == 1
    assert meta["empty_file"] is False


def test_csv_quoted_fields(tmp_path):
    f = tmp_path / "quoted.csv"
    f.write_text('id,text,note\n1,"hello, world","a \\"quoted\\" note"\n2,plain,"multi,comma,entry"\n', encoding="utf-8")
    records, meta = loaders.load_csv(f)
    assert len(records) == 2
    assert records[0]["note"].startswith('a "quoted"')
    assert meta["empty_file"] is False


def test_csv_empty(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text("col1,col2\n", encoding="utf-8")
    records, meta = loaders.load_csv(f)
    assert len(records) == 0
    assert meta["empty_file"] is True