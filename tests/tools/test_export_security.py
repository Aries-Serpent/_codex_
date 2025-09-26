import pathlib

import pytest

from tools.codex_sqlite_align import _validate_identifier
from tools.export_to_parquet import _ensure_within_base


@pytest.mark.parametrize(
    "identifier",
    ["table", "schema.table", "schema_name.table_2024"],
)
def test_validate_identifier_accepts_valid(identifier):
    assert _validate_identifier(identifier) == identifier


@pytest.mark.parametrize(
    "identifier",
    [
        "",  # empty
        "schema..table",  # empty segment
        "bad-name",  # hyphen
        "table; DROP TABLE users;--",  # injection attempt
    ],
)
def test_validate_identifier_rejects_invalid(identifier):
    with pytest.raises(ValueError):
        _validate_identifier(identifier)


def test_ensure_within_base_accepts_child(tmp_path):
    base = tmp_path
    child = base / "sub" / "dir"
    resolved = _ensure_within_base(child, base)
    assert resolved == child.resolve()


def test_ensure_within_base_blocks_escape(tmp_path):
    base = tmp_path
    outside = pathlib.Path(tmp_path).resolve().parent
    with pytest.raises(ValueError):
        _ensure_within_base(outside, base)
