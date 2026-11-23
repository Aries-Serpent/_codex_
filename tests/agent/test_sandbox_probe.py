"""Tests for Copilot agent sandbox capability probing."""

from __future__ import annotations

import json

from scripts.agent.sandbox_probe import (
    build_probe,
    probe_unshare,
    read_workspace_sandbox_setting,
)


def test_read_workspace_sandbox_setting_accepts_valid_values(tmp_path) -> None:
    settings_dir = tmp_path / ".vscode"
    settings_dir.mkdir()
    (settings_dir / "settings.json").write_text(
        json.dumps({"github.copilot.chat.cli.sandbox.enabled": "allowNetwork"}),
        encoding="utf-8",
    )

    assert read_workspace_sandbox_setting(tmp_path) == "allowNetwork"


def test_read_workspace_sandbox_setting_rejects_unknown_value(tmp_path) -> None:
    settings_dir = tmp_path / ".vscode"
    settings_dir.mkdir()
    (settings_dir / "settings.json").write_text(
        json.dumps({"github.copilot.chat.cli.sandbox.enabled": "invalid"}),
        encoding="utf-8",
    )

    assert read_workspace_sandbox_setting(tmp_path) == "unknown"


def test_build_probe_recommends_off_when_namespace_is_denied(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.agent.sandbox_probe.probe_bwrap",
        lambda: {
            "available": True,
            "namespace_capable": False,
            "reason": "namespace-denied",
        },
    )
    monkeypatch.setattr(
        "scripts.agent.sandbox_probe.probe_unshare",
        lambda: {
            "available": True,
            "namespace_capable": False,
            "reason": "namespace-denied",
        },
    )

    probe = build_probe(tmp_path)

    assert probe["sandbox_capable"] is False
    assert probe["recommended_setting"] == "off"


def test_probe_unshare_reports_namespace_denial(monkeypatch) -> None:
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _name: "/usr/bin/unshare")

    class Result:
        returncode = 1

    monkeypatch.setattr(
        "scripts.agent.sandbox_probe.subprocess.run",
        lambda *_args, **_kwargs: Result(),
    )

    result = probe_unshare()

    assert result == {
        "available": True,
        "namespace_capable": False,
        "reason": "namespace-denied",
    }


def test_build_probe_recommends_allow_network_when_configured(tmp_path, monkeypatch) -> None:
    settings_dir = tmp_path / ".vscode"
    settings_dir.mkdir()
    (settings_dir / "settings.json").write_text(
        json.dumps({"github.copilot.chat.cli.sandbox.enabled": "allowNetwork"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "scripts.agent.sandbox_probe.probe_bwrap",
        lambda: {
            "available": True,
            "namespace_capable": True,
            "reason": "namespace-capable",
        },
    )
    monkeypatch.setattr(
        "scripts.agent.sandbox_probe.probe_unshare",
        lambda: {
            "available": True,
            "namespace_capable": False,
            "reason": "namespace-denied",
        },
    )

    probe = build_probe(tmp_path)

    assert probe["sandbox_capable"] is True
    assert probe["recommended_setting"] == "allowNetwork"
    assert "unshare" in probe
    assert "kernel_container" in probe
