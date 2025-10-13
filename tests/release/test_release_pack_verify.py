from __future__ import annotations

import json

from codex.archive.api import store
from codex.release.api import pack_release, verify_bundle


def test_pack_and_verify(tmp_path, monkeypatch):
    root = tmp_path
    (root / "dist").mkdir()
    (root / "work" / "release_staging").mkdir(parents=True, exist_ok=True)
    # Configure archive (SQLite)
    monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
    monkeypatch.setenv(
        "CODEX_ARCHIVE_URL",
        f"sqlite:///{(root / '.codex' / 'archive.sqlite').as_posix()}",
    )
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", (root / ".codex" / "evidence").as_posix())
    (root / ".codex" / "evidence").mkdir(parents=True, exist_ok=True)
    # Store an artifact → tombstone
    src_bytes = b'{"hello":"world"}\n'
    out = store(
        repo="_codex_",
        path="configs/sample.json",
        by="tester",
        reason="release_component",
        commit_sha="HEAD",
        bytes_in=src_bytes,
        mime="application/json",
        lang="json",
    )
    # Manifest
    manifest = {
        "release_id": "codex-test-r01",
        "version": "v0",
        "created_at": "2025-10-13T00:00:00Z",
        "actor": "tester",
        "target": {"platforms": ["linux/amd64"], "apps": []},
        "components": [
            {
                "tombstone": out["tombstone"],
                "dest_path": "configs/sample.json",
                "mode": "0644",
                "type": "file",
            }
        ],
        "symlinks": [],
        "post_unpack_commands": [],
        "checks": {"sha256_manifest": "<filled at pack time>"},
    }
    (root / "release.manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # Pack
    bundle, locked = pack_release(
        root / "release.manifest.json",
        root / "work" / "release_staging",
        root / "dist" / "codex-release.tar.gz",
    )
    assert bundle.exists()
    assert "sha256_manifest" in locked["checks"]
    # Verify
    verification = verify_bundle(bundle)
    assert verification["ok"] is True
    assert verification["sha256_manifest"] == locked["checks"]["sha256_manifest"]
