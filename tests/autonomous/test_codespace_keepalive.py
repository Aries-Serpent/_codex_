"""Focused tests for the repository-owned Codespace keepalive daemon."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from scripts.autonomous import codespace_keepalive


def set_mark_time(path: Path, timestamp: datetime) -> None:
    epoch = timestamp.timestamp()
    os.utime(path, (epoch, epoch))


def test_active_marker_expires(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    marker = tmp_path / "agent-session.active"
    marker.write_text("active\n", encoding="utf-8")
    now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(codespace_keepalive, "utc_now", lambda: now)

    set_mark_time(marker, now - timedelta(seconds=901))

    assert codespace_keepalive.active_marker_fresh(marker, 900) is False


def test_heartbeat_advances_only_for_active_session(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runtime_dir = tmp_path / "runtime"
    marker = runtime_dir / "agent-session.active"
    runtime_dir.mkdir()
    marker.write_text("active\n", encoding="utf-8")
    now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(codespace_keepalive, "utc_now", lambda: now)
    set_mark_time(marker, now)

    heartbeat = codespace_keepalive.write_heartbeat(
        runtime_dir=runtime_dir,
        marker=marker,
        pid=os.getpid(),
        started_at=now - timedelta(minutes=5),
        max_duration_seconds=8 * 60 * 60,
        marker_ttl_seconds=900,
        service_probe=lambda: {"reachable": True, "http_status": 200},
        now=now,
    )

    assert heartbeat["active"] is True
    assert heartbeat["remaining_seconds"] == 28_500
    payload = json.loads((runtime_dir / "codespace_keepalive.json").read_text(encoding="utf-8"))
    assert payload["pid"] == os.getpid()
    assert payload["service"] == {"reachable": True, "http_status": 200}


def test_stale_pid_is_not_treated_as_owned(tmp_path: Path) -> None:
    pid_file = tmp_path / "keepalive.pid"
    pid_file.write_text("999999999\n", encoding="utf-8")

    assert codespace_keepalive.pid_is_owned(pid_file, tmp_path / "repo") is False


def test_connection_uses_forced_tty_terminal_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, Any] = {}

    class FakeProcess:
        pid = 4321

    def fake_popen(command: list[str], **kwargs: Any) -> FakeProcess:
        captured["command"] = command
        captured["kwargs"] = kwargs
        return FakeProcess()

    monkeypatch.setenv("CODESPACE_NAME", "future-codespace")
    monkeypatch.setenv("CODEX_BACKUP_KEY", "test-token")
    monkeypatch.setattr(codespace_keepalive, "github_cli_path", lambda: Path("/usr/bin/gh"))
    monkeypatch.setattr(codespace_keepalive.subprocess, "Popen", fake_popen)

    process = codespace_keepalive.connection_process(
        runtime_dir=tmp_path,
        max_duration_seconds=28_800,
    )

    assert process is not None
    command = captured["command"]
    assert "-tt" in command
    assert any("codex-codespace-keepalive" in item for item in command)
    assert command[-1].startswith("sh -c '")
    assert command[-1].endswith("'")
    assert "sleep 30" in command[-1]
    assert captured["kwargs"]["env"]["GH_TOKEN"] == "test-token"


def test_start_is_idempotent_when_owned_process_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runtime_dir = tmp_path / "runtime"
    repo_root = tmp_path / "repo"
    runtime_dir.mkdir()
    repo_root.mkdir()
    pid_file = runtime_dir / "codespace_keepalive.pid"
    pid_file.write_text("12345\n", encoding="utf-8")
    monkeypatch.setattr(codespace_keepalive, "pid_is_owned", lambda *_args, **_kwargs: True)

    result = codespace_keepalive.start_daemon(runtime_dir=runtime_dir, repo_root=repo_root)

    assert result == {"started": False, "already_running": True, "pid": 12345}


def test_periodic_checkpoint_command_passes_custom_runtime_dir(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "custom-runtime"
    repo_root = tmp_path / "repo"
    started_at = datetime(2026, 11, 25, 21, 0, tzinfo=timezone.utc)

    command = codespace_keepalive.periodic_checkpoint_command(
        runtime_dir=runtime_dir,
        repo_root=repo_root,
        started_at=started_at,
    )

    assert "--runtime-dir" in command
    assert str(runtime_dir) in command
    assert "--runtime-only" in command


def test_periodic_continuity_checkpoint_interval_parser() -> None:
    args = codespace_keepalive.build_parser().parse_args(
        ["run", "--continuity-checkpoint-interval-seconds", "900"]
    )

    assert args.continuity_checkpoint_interval_seconds == 900


def test_status_reports_platform_policy_boundary(tmp_path: Path) -> None:
    status_path = tmp_path / "runtime" / "codespace_keepalive.json"
    status_path.parent.mkdir()
    payload: dict[str, Any] = {
        "pid": os.getpid(),
        "active": True,
        "platform_idle_timeout_minutes": 30,
    }
    status_path.write_text(json.dumps(payload), encoding="utf-8")

    status = codespace_keepalive.read_status(status_path.parent)

    assert status["platform_idle_timeout_minutes"] == 30
    assert status["active"] is False
    assert status["running"] is False
    assert status["overrides_platform_idle_policy"] is False
