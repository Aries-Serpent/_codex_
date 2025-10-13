from __future__ import annotations

import json
import sqlite3

from codex.archive.api import store
from codex.archive.dal import ArchiveDAL
from codex.release.api import pack_release


def test_release_persist_rows(tmp_path, monkeypatch):
    root = tmp_path
    (root / "dist").mkdir(parents=True, exist_ok=True)
    (root / "work" / "release_staging").mkdir(parents=True, exist_ok=True)
    (root / ".codex" / "evidence").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
    monkeypatch.setenv(
        "CODEX_ARCHIVE_URL",
        f"sqlite:///{(root / '.codex' / 'archive.sqlite').as_posix()}",
    )
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", (root / ".codex" / "evidence").as_posix())
    out = store(
        repo="_codex_",
        path="bin/codex-cli",
        by="tester",
        reason="release_component",
        commit_sha="HEAD",
        bytes_in=b"#!/bin/sh\necho codex\n",
        mime="text/x-shellscript",
        lang="shell",
    )
    manifest = {
        "release_id": "codex-it-r01",
        "version": "v1",
        "created_at": "2025-10-13T00:00:00Z",
        "actor": "tester",
        "target": {"platforms": ["linux/amd64"]},
        "components": [
            {
                "tombstone": out["tombstone"],
                "dest_path": "bin/codex-cli",
                "mode": "0755",
                "type": "file",
            }
        ],
        "symlinks": [],
        "post_unpack_commands": [],
        "checks": {"sha256_manifest": "<filled at pack time>"},
    }
    manifest_path = root / "release.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    bundle, _ = pack_release(
        manifest_path,
        root / "work" / "release_staging",
        root / "dist" / "codex-release.tar.gz",
    )
    assert bundle.exists()

    dal = ArchiveDAL.from_env()
    meta = dal.get_release_meta_by_release_id(release_id="codex-it-r01")
    assert meta is not None
    conn = sqlite3.connect((root / ".codex" / "archive.sqlite").as_posix())
    conn.row_factory = sqlite3.Row
    rows = list(
        conn.execute(
            "SELECT * FROM release_component WHERE release_id = ?",
            (meta["id"],),
        )
    )
    assert len(rows) == 1
    assert rows[0]["tombstone"] == out["tombstone"]
    conn.close()
