from __future__ import annotations

import os
from pathlib import Path

import pytest

from codex.archive.api import refer_dup_to_canonical, store
from codex.archive.dal import ArchiveDAL

BACKEND = os.getenv("CODEX_ARCHIVE_BACKEND", "")
DSN = os.getenv("CODEX_ARCHIVE_URL", "")

pytestmark = pytest.mark.skipif(
    not DSN or BACKEND not in ("postgres", "mariadb"),
    reason="requires CODEX_ARCHIVE_BACKEND=postgres|mariadb and CODEX_ARCHIVE_URL",
)


def test_referent_insert_and_lookup(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", (tmp_path / ".codex" / "evidence").as_posix())
    (tmp_path / ".codex" / "evidence").mkdir(parents=True, exist_ok=True)
    dal = ArchiveDAL.from_env()
    a = store(
        repo="_codex_",
        path="src/foo.py",
        by="it",
        reason="test",
        commit_sha="HEAD",
        bytes_in=b"print(1)\n",
        mime="text/x-python",
        lang="python",
    )
    b = store(
        repo="_codex_",
        path="src/foo_old.py",
        by="it",
        reason="test",
        commit_sha="HEAD",
        bytes_in=b"print(1)\n",
        mime="text/x-python",
        lang="python",
    )
    refer_dup_to_canonical(duplicate_tombstone=b["tombstone"], canonical_tombstone=a["tombstone"])
    assert dal is not None
