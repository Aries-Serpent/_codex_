"""
Test Env Check Cli

Test module for env check cli.
"""

from pathlib import Path

from codex_ml.cli import env_check


def test_env_check_invokes_subtools(monkeypatch, tmp_path: Path):
    called = []

    def fake_run(cmd, cwd):  # type: ignore[override]
        called.append((cmd, cwd))

        class R:
            returncode = 0

        return R().returncode

    monkeypatch.setattr(env_check, "_run", fake_run)

    result = env_check.run_health_check(tmp_path)
    assert result["env_snapshot_rc"] == 0, "Result must not be empty"
    assert result["dependency_audit_rc"] == 0, "Result must not be empty"
    assert result["secret_scan_rc"] == 0, "Result must not be empty"

    cmds = [c[0] for c in called]
    assert "codex_env_snapshot.py" in cmds[0], "Condition must be true"
    assert any("codex_dependency_audit.py" in c for c in cmds), "Condition must be true"
    assert any("codex_secret_scan_stub.py" in c for c in cmds), "Condition must be true"
