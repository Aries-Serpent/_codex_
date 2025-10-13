from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.knowledge.build import archive_and_manifest, build_kb


def test_archive_and_manifest_creates_components(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    docs_root = tmp_path / "docs"
    docs_root.mkdir()
    (docs_root / "sample.md").write_text("# Title\nBody text\n", encoding="utf-8")

    kb_out = tmp_path / "artifacts" / "kb.ndjsonl"
    archive_dir = tmp_path / ".codex"
    evidence_dir = archive_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
    monkeypatch.setenv(
        "CODEX_ARCHIVE_URL", f"sqlite:///{(archive_dir / 'archive.sqlite').as_posix()}"
    )
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())

    result = build_kb(docs_root, kb_out)
    assert kb_out.exists()
    assert result["written"] >= 1

    manifest_info = archive_and_manifest(kb_out, None, None, actor="tester")
    manifest_path = Path(manifest_info["manifest"])
    assert manifest_path.exists()

    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    components = manifest_payload.get("components", [])
    assert isinstance(components, list) and components
