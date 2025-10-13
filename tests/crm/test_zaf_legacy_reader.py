from __future__ import annotations

import json
import zipfile
from pathlib import Path

from codex_crm.zaf_legacy import read_zaf, scaffold_template


def _create_zaf_zip(tmp_path: Path) -> Path:
    manifest = {"name": "Legacy App", "version": "0.1"}
    archive_path = tmp_path / "zaf.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr("src/app.js", "console.log('hello');")
        archive.writestr("assets/logo.png", b"binarydata")
    return archive_path


def test_read_and_scaffold_zaf(tmp_path: Path) -> None:
    archive_path = _create_zaf_zip(tmp_path)
    bundle = read_zaf(archive_path)

    assert bundle["manifest"]["name"] == "Legacy App"
    assert "src/app.js" in bundle["files"]

    output_dir = tmp_path / "scaffold"
    created_files = scaffold_template(bundle, output_dir)

    expected_manifest = output_dir / "manifest.json"
    assert expected_manifest.exists()
    assert any(path.name == "app.js" for path in created_files)
    assert (output_dir / "README.md").exists()
