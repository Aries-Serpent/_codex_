"""Smoke tests for :mod:`codex_ml.cli.env_check`."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def test_run_health_check(monkeypatch, tmp_path):
    from codex_ml.cli import env_check

    calls = []

    def fake_run(cmd, cwd):
        calls.append(cmd)
        return 0

    monkeypatch.setattr(env_check, "_run", fake_run)

    result = env_check.run_health_check(tmp_path)
    assert all(code == 0 for code in result.values()), "Result must not be empty"
    assert len(calls) == 3, "Calls must not be empty"


def test_main_aggregates_return_codes(monkeypatch, tmp_path):
    from codex_ml.cli import env_check

    monkeypatch.setattr(
        env_check,
        "run_health_check",
        lambda root: {"env_snapshot_rc": 0, "dependency_audit_rc": 1, "secret_scan_rc": 0},
    )
    rc = env_check.main(["--repo-root", str(tmp_path)])
    assert rc == 1, "rc is not valid"
