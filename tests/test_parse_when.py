from datetime import timezone

from codex.logging.query_logs import parse_when


def test_parse_when_z():
    dt = parse_when("2025-08-19T12:34:56Z")
    assert dt.tzinfo is not None
    assert dt.utcoffset() == timezone.utc.utcoffset(dt)


def test_parse_when_offset():
    dt = parse_when("2025-08-19T07:34:56-05:00")
    assert dt.tzinfo is not None
    assert dt.utcoffset().total_seconds() == -5 * 3600


def test_parse_when_naive():
    dt = parse_when("2025-08-19T12:34:56")
    assert dt.tzinfo is None
