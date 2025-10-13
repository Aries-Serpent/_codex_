from __future__ import annotations

import json

from codex.archive.api import store
from codex.release.api import pack_release, unpack_bundle


def test_unpack(tmp_path, monkeypatch):
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
    # Store artifacts
    tombstone_bin = store(
        repo="_codex_",
        path="bin/codex-cli",
        by="tester",
        reason="release_component",
        commit_sha="HEAD",
        bytes_in=b"#!/bin/sh\necho codex\n",
        mime="text/x-shellscript",
        lang="shell",
    )
    tombstone_cfg = store(
        repo="_codex_",
        path="configs/app.json",
        by="tester",
        reason="release_component",
        commit_sha="HEAD",
        bytes_in=b'{"name":"{{app}}"}\n',
        mime="application/json",
        lang="json",
    )
    manifest = {
        "release_id": "codex-test-r02",
        "version": "v0",
        "created_at": "2025-10-13T00:00:00Z",
        "actor": "tester",
        "target": {},
        "components": [
            {
                "tombstone": tombstone_bin["tombstone"],
                "dest_path": "bin/codex-cli",
                "mode": "0755",
                "type": "file",
            },
            {
                "tombstone": tombstone_cfg["tombstone"],
                "dest_path": "configs/app.json",
                "mode": "0644",
                "type": "file",
                "template_vars": {"app": "codex"},
            },
        ],
        "symlinks": [{"link_path": "bin/codex", "target": "bin/codex-cli"}],
        "post_unpack_commands": [],
        "checks": {"sha256_manifest": "<filled at pack time>"},
    }
    (root / "release.manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    bundle, _ = pack_release(
        root / "release.manifest.json",
        root / "work" / "release_staging",
        root / "dist" / "codex-release.tar.gz",
    )
    dest = root / "unpacked"
    unpack_bundle(bundle, dest, allow_scripts=False)
    assert (dest / "bin" / "codex-cli").exists()
    assert (dest / "bin" / "codex").is_symlink()
    assert (dest / "configs" / "app.json").read_text(encoding="utf-8").strip() == '{"name":"codex"}'
