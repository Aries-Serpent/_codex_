"""
Test Data Loaders Extended

Test module for data loaders extended.
"""

import json

from codex_ml.data import loaders


def test_jsonl_empty_file(tmp_path):
    f = tmp_path / "empty.jsonl"
    f.write_text("", encoding="utf-8")
    records, meta = loaders.load_jsonl(f)
    assert records == [], "records is not valid"
    assert meta["num_records"] == 0, "Condition must be true"
    assert meta["empty_file"] is True, "Condition must be true"
    assert meta["skipped_malformed"] == 0, "Condition must be true"


def test_jsonl_bom_and_malformed(tmp_path):
    f = tmp_path / "data.jsonl"
    # Include BOM + one good line + one malformed + one good
    content = "\ufeff" + json.dumps({"a": 1}) + "\n" + "{bad json}\n" + json.dumps({"b": 2}) + "\n"
    f.write_text(content, encoding="utf-8")
    records, meta = loaders.load_jsonl(f)
    assert len(records) == 2, "Records must not be empty"
    assert meta["skipped_malformed"] == 1, "Condition must be true"
    assert meta["empty_file"] is False, "Condition must be true"


def test_csv_quoted_fields(tmp_path):
    f = tmp_path / "quoted.csv"
    f.write_text(
        'id,text,note\n1,"hello, world","a \\"quoted\\" note"\n2,plain,"multi,comma,entry"\n',
        encoding="utf-8",
    )
    records, meta = loaders.load_csv(f)
    assert len(records) == 2, "Records must not be empty"
    assert records[0]["note"].startswith('a "quoted"'), "rec is not valid"
    assert meta["empty_file"] is False, "Condition must be true"


def test_csv_empty(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text("col1,col2\n", encoding="utf-8")
    records, meta = loaders.load_csv(f)
    assert len(records) == 0, "Records must not be empty"
    assert meta["empty_file"] is True, "Condition must be true"
