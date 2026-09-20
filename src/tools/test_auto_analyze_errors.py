import hashlib
import json
from pathlib import Path

from tools.auto_analyze_errors import group_errors, load_entries, parse_ts


def write_ndjson(path: Path, entries) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")


def test_grouping(tmp_path):
    data = [
        {"ts": "2025-01-01T00:00:00Z", "error": "Error A", "step": "1"},
        {"ts": "2025-01-01T13:00:00Z", "error": "Error A", "step": "2"},
        {"ts": "2025-01-02T00:00:00Z", "error": "Error B", "step": "3"},
    ]
    p = tmp_path / "errors.ndjson"
    write_ndjson(p, data)
    entries = load_entries(p)
    result = group_errors(entries)
    expected = [
        {
            "id": hashlib.sha256("Error A".encode("utf-8")).hexdigest()[:8],
            "message": "Error A",
            "count": 2,
        },
        {
            "id": hashlib.sha256("Error B".encode("utf-8")).hexdigest()[:8],
            "message": "Error B",
            "count": 1,
        },
    ]
    assert result == expected


def test_since_and_unanswered(tmp_path):
    data = [
        {"ts": "2025-01-01T00:00:00Z", "error": "Error A"},
        {"ts": "2025-01-02T00:00:00Z", "error": "Error B", "answer_id": "foo"},
        {"ts": "2025-01-03T00:00:00Z", "error": "Error C"},
    ]
    p = tmp_path / "errors.ndjson"
    write_ndjson(p, data)
    entries = load_entries(p)
    since = parse_ts("2025-01-02T00:00:00Z")
    result_all = group_errors(entries, since=since)
    expected_all = [
        {
            "id": hashlib.sha256("Error B".encode("utf-8")).hexdigest()[:8],
            "message": "Error B",
            "count": 1,
        },
        {
            "id": hashlib.sha256("Error C".encode("utf-8")).hexdigest()[:8],
            "message": "Error C",
            "count": 1,
        },
    ]
    assert result_all == expected_all

    result_unanswered = group_errors(entries, since=since, unanswered_only=True)
    expected_unanswered = [
        {
            "id": hashlib.sha256("Error C".encode("utf-8")).hexdigest()[:8],
            "message": "Error C",
            "count": 1,
        }
    ]
    assert result_unanswered == expected_unanswered
