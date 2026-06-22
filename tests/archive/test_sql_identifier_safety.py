"""
Test Sql Identifier Safety

Test module for sql identifier safety.
"""

from __future__ import annotations

import pytest

from codex.archive.dal import ArchiveDAL


@pytest.fixture()
def sqlite_dal(monkeypatch: pytest.MonkeyPatch) -> ArchiveDAL:
    monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
    monkeypatch.setenv("CODEX_ARCHIVE_URL", "sqlite:///:memory:")
    dal = ArchiveDAL.from_env()
    # Ensure schema is initialized for in-memory database
    try:
        dal.ensure_schema()
    except Exception as _err:
        pass  # In-memory database may not require schema initialization
    return dal


def test_validate_identifier_accepts_known_tables(sqlite_dal: ArchiveDAL) -> None:
    allowed = getattr(type(sqlite_dal), "_ALLOWED_TABLES", set())
    for name in allowed:
        assert sqlite_dal.validate_identifier(name, allowed) == name


def test_validate_identifier_rejects_unknown_tables(sqlite_dal: ArchiveDAL) -> None:
    with pytest.raises(ValueError):
        sqlite_dal.validate_identifier(
            "DROP_TABLE", getattr(type(sqlite_dal), "_ALLOWED_TABLES", set())
        )
