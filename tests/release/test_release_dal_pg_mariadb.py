"""
Test Release Dal Pg Mariadb

Test module for release dal pg mariadb.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from codex.archive.dal import ArchiveDAL

PG = os.getenv("CODEX_ARCHIVE_BACKEND", "") == "postgres"
MY = os.getenv("CODEX_ARCHIVE_BACKEND", "") == "mariadb"
HAS_URL = bool(os.getenv("CODEX_ARCHIVE_URL", ""))

pytestmark = pytest.mark.skipif(
    not HAS_URL or not (PG or MY),
    reason=(
        "Integration test requires CODEX_ARCHIVE_BACKEND=postgres|mariadb and "
        "CODEX_ARCHIVE_URL DSN."
    ),
)


def test_release_rows_insert_and_get(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    evidence_dir = tmp_path / ".codex" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())

    dal = ArchiveDAL.from_env()
    meta = dal.create_release_meta(
        release_id="it-int-r01",
        version="v1",
        created_at="2025-10-13T00:00:00Z",
        actor="tester",
        metadata={"note": "integration"},
    )
    assert meta.get("id"), "Condition must be true"

    comp = dal.add_release_component(
        release_meta_id=meta["id"],
        item_id=None,
        tombstone="uuid-not-real",
        dest_path="bin/codex-cli",
        mode="0755",
        template_vars={"x": 1},
    )
    assert comp.get("id"), "Condition must be true"

    got = dal.get_release_meta_by_release_id(release_id="it-int-r01")
    assert got is not None, "got must be initialized"
    assert got.get("release_id") == "it-int-r01", "Condition must be true"
    metadata = got.get("metadata", {})
    assert isinstance(metadata, dict)
    assert json.dumps(metadata), "Data must not be empty"
