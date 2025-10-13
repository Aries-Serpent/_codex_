from __future__ import annotations

import json
import zipfile
from pathlib import Path

from codex_crm import cli


def _create_pa_zip(tmp_path: Path) -> Path:
    archive_path = tmp_path / "legacy_pa.zip"
    manifest = {"name": "Sample", "version": "1.0"}
    flow = {"if": {"status": "open"}, "then": ["notify"]}
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr("flows/sample.json", json.dumps(flow))
    return archive_path


def test_cli_import_pa_zip(tmp_path: Path) -> None:
    archive_path = _create_pa_zip(tmp_path)
    output_dir = tmp_path / "out"
    exit_code = cli.main(["import-pa-zip", "--in", str(archive_path), "--out", str(output_dir)])
    assert exit_code == 0

    generated = output_dir / "legacy_pa.template.json"
    data = json.loads(generated.read_text(encoding="utf-8"))
    assert "flows" in data
    assert "sample" in data["flows"]


def test_cli_gen_diagram(tmp_path: Path) -> None:
    output_file = tmp_path / "diagram.mmd"
    exit_code = cli.main(
        [
            "gen-diagram",
            "--flow",
            "Intake",
            "--steps",
            "Create;Triage;Close",
            "--out",
            str(output_file),
        ]
    )
    assert exit_code == 0
    contents = output_file.read_text(encoding="utf-8")
    assert "Create" in contents


def test_cli_evidence_pack(tmp_path: Path) -> None:
    output_dir = tmp_path / "evidence"
    exit_code = cli.main(["evidence-pack", "--out", str(output_dir)])
    assert exit_code == 0
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["message"] == "Evidence pack placeholder"


def test_cli_apply_placeholders() -> None:
    exit_code = cli.main(["apply-zd"])
    assert exit_code == 0
    exit_code = cli.main(["apply-d365"])
    assert exit_code == 0
