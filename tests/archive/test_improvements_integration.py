from __future__ import annotations

import json
import logging
from pathlib import Path

from click.testing import CliRunner

from codex.archive import batch
from codex.archive.cli import cli


class StubService:
    def __init__(self, base: Path) -> None:
        self.base = base

    def restore_to_path(self, tombstone: str, *, output_path: Path, actor: str) -> Path:
        output_path.write_text(f"{actor}:{tombstone}")
        return output_path


def _parse_json_from_output(text: str) -> dict:
    json_start = text.find("{")
    assert json_start != -1
    return json.loads(text[json_start:])


def test_cli_config_show_outputs_json(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [backend]
        backend = "sqlite"
        url = "sqlite:///./test.sqlite"

        [logging]
        level = "warning"
        format = "text"
        """
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["config-show", "--config-file", str(config_path)])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["backend"]["backend"] == "sqlite"
    assert payload["logging"]["level"] == "warning"


def test_batch_restore_dry_run(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([{"tombstone": "a", "output": "a.bin"}]))
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "batch-restore",
            str(manifest),
            "--actor",
            "tester",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    payload = _parse_json_from_output(result.output)
    assert payload["total"] == 1


def test_batch_restore_executes_with_stub_service(tmp_path: Path, monkeypatch) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([{"tombstone": "a", "output": "out.bin"}]))
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [batch]
        results_path = "results.json"
        progress_interval = 1
        """
    )

    service = StubService(tmp_path)

    monkeypatch.setattr("codex.archive.cli._service", lambda **kwargs: service)
    monkeypatch.setattr(
        "codex.archive.cli._setup_logger",
        lambda app_config: logging.getLogger("codex.archive.test"),
    )
    monkeypatch.setattr(
        "codex.archive.batch.BatchRestore.save_results",
        batch.BatchRestore.save_results,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "batch-restore",
            str(manifest),
            "--actor",
            "tester",
            "--config-file",
            str(config_path),
        ],
    )

    assert result.exit_code == 0
    payload = _parse_json_from_output(result.output)
    assert payload["succeeded"] == 1
    results_file = tmp_path / "results.json"
    assert results_file.exists()
