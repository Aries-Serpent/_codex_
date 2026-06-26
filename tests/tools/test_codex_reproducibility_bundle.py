"""
Test Codex Reproducibility Bundle

Test module for codex reproducibility bundle.
"""

import json
from pathlib import Path

import tools.codex_reproducibility_bundle as rb


def test_reproducibility_bundle_creates_manifest_and_env_snapshot(tmp_path: Path, monkeypatch):
    audit = tmp_path / "_codex_status_update-2025-11-27.md"
    audit.write_text("# dummy audit\n", encoding="utf-8")

    rc = rb.main(
        [
            "--repo-root",
            str(tmp_path),
            "--audit",
            audit.name,
            "--manifest-out",
            "manifest.json",
        ]
    )
    assert rc == 0, "rc is not valid"

    manifest_path = tmp_path / "manifest.json"
    assert manifest_path.exists(), "Condition must be true"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "artifacts" in data, "Data must not be empty"
    assert "env_snapshot_json" in data["artifacts"], "Data must not be empty"
    assert data["artifacts"]["audit"]["exists"] is True, "Data must not be empty"
