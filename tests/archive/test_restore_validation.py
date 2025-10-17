"""Regression coverage for archive restore validation and diagnostics."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from codex.archive.backend import ArchiveConfig
from codex.archive.cli import cli
from codex.archive.service import ArchiveService


class TestRestoreValidation:
    """Exercise restore flows across failure and success modes."""

    def test_restore_missing_database(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Restore should fail gracefully when the archive backend is absent."""

        evidence_dir = tmp_path / ".codex" / "evidence"
        db_path = tmp_path / ".codex" / "archive.sqlite"

        monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path.as_posix()}")
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        output_file = tmp_path / "restored.txt"

        result = runner.invoke(
            cli,
            [
                "restore",
                "8e3531b9-c839-4a07-9dec-507c36136eb1",
                output_file.as_posix(),
                "--by",
                "test-user",
            ],
        )

        assert result.exit_code != 0
        assert not output_file.exists()
        assert "error" in result.output.lower()

    def test_restore_missing_tombstone_logs_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A missing tombstone should surface an error and evidence entry."""

        evidence_dir = tmp_path / ".codex" / "evidence"
        db_path = tmp_path / ".codex" / "archive.sqlite"

        monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path.as_posix()}")
        monkeypatch.chdir(tmp_path)

        config = ArchiveConfig(url=f"sqlite:///{db_path.as_posix()}", backend="sqlite")
        ArchiveService(config, apply_schema=True)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "restore",
                "nonexistent-tombstone-uuid",
                (tmp_path / "restored.txt").as_posix(),
                "--by",
                "test-user",
            ],
        )

        assert result.exit_code != 0
        assert "not found" in result.output.lower()

        evidence_file = evidence_dir / "archive_ops.jsonl"
        assert evidence_file.exists()
        events = [
            json.loads(line)
            for line in evidence_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert any(event.get("action") == "RESTORE_FAIL" for event in events)

    def test_restore_failure_records_evidence(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Failures should emit RESTORE_FAIL events for auditing."""

        evidence_dir = tmp_path / ".codex" / "evidence"
        db_path = tmp_path / ".codex" / "archive.sqlite"

        monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path.as_posix()}")
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "restore",
                "test-tombstone-uuid",
                (tmp_path / "restored.txt").as_posix(),
                "--by",
                "test-actor",
            ],
        )

        assert result.exit_code != 0
        evidence_file = evidence_dir / "archive_ops.jsonl"
        assert evidence_file.exists()
        events = [
            json.loads(line)
            for line in evidence_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert any(event.get("action") == "RESTORE_FAIL" for event in events)

    def test_restore_backend_validation_outputs_diagnostics(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Backend validation should surface diagnostic output."""

        evidence_dir = tmp_path / ".codex" / "evidence"
        db_path = tmp_path / ".codex" / "archive.sqlite"

        monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path.as_posix()}")
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "restore",
                "test-tombstone",
                (tmp_path / "restored.txt").as_posix(),
                "--by",
                "test-user",
            ],
        )

        assert "[DEBUG]" in result.output or "backend" in result.output.lower()

    def test_restore_success_logs_evidence(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Successful restores should produce RESTORE evidence entries."""

        evidence_dir = tmp_path / ".codex" / "evidence"
        db_path = tmp_path / ".codex" / "archive.sqlite"

        monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path.as_posix()}")
        monkeypatch.chdir(tmp_path)

        config = ArchiveConfig(url=f"sqlite:///{db_path.as_posix()}", backend="sqlite")
        service = ArchiveService(config, apply_schema=True)

        source = tmp_path / "test.txt"
        source.write_text("test content", encoding="utf-8")
        result = service.archive_path(
            repo="test-repo",
            path=source,
            reason="dead",
            archived_by="test-user",
            commit_sha="deadbeef",
        )

        runner = CliRunner()
        output_file = tmp_path / "restored.txt"
        restore_result = runner.invoke(
            cli,
            [
                "restore",
                result.tombstone_id,
                output_file.as_posix(),
                "--by",
                "restore-user",
            ],
        )

        assert restore_result.exit_code == 0, restore_result.output
        assert output_file.read_text(encoding="utf-8") == "test content"

        evidence_file = evidence_dir / "archive_ops.jsonl"
        events = [
            json.loads(line)
            for line in evidence_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        restore_events = [event for event in events if event.get("action") == "RESTORE"]
        assert restore_events
        assert restore_events[0]["tombstone"] == result.tombstone_id
        assert restore_events[0]["actor"] == "restore-user"


class TestHealthCheck:
    """Validate the archive backend health-check command."""

    def test_health_check_reports_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing backend should return a failure exit code."""

        db_path = tmp_path / ".codex" / "archive.sqlite"
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path.as_posix()}")
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["health-check"])

        assert result.exit_code != 0 or "FAILED" in result.output

    def test_health_check_reports_success(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Operational backend should pass the health check."""

        db_path = tmp_path / ".codex" / "archive.sqlite"
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path.as_posix()}")
        monkeypatch.chdir(tmp_path)

        config = ArchiveConfig(url=f"sqlite:///{db_path.as_posix()}", backend="sqlite")
        ArchiveService(config, apply_schema=True)

        runner = CliRunner()
        result = runner.invoke(cli, ["health-check"])

        assert result.exit_code == 0
        assert "OK" in result.output
