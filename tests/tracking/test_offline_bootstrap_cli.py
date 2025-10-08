from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _run(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    base_env = os.environ.copy()
    if env:
        base_env.update(env)
    base_env.setdefault("PYTHONPATH", str(Path(__file__).resolve().parents[2] / "src"))
    cmd = [sys.executable, "-S", "-m", "codex_ml.cli.offline_bootstrap"] + args
    return subprocess.run(cmd, capture_output=True, text=True, env=base_env)


@pytest.fixture()
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    env = os.environ.copy()
    for key in ["MLFLOW_TRACKING_URI", "WANDB_MODE", "WANDB_DISABLED"]:
        env.pop(key, None)
        monkeypatch.delenv(key, raising=False)
    return env


def test_env_exports_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _clean_env: dict[str, str]
) -> None:
    monkeypatch.chdir(tmp_path)
    result = _run(
        [
            "env",
            "--no-print",
            "--write",
            "exports.sh",
            "--json-out",
            "decision.json",
        ],
        env=_clean_env,
    )
    assert result.returncode == 0, result.stderr

    exports = (tmp_path / "exports.sh").read_text(encoding="utf-8")
    assert 'MLFLOW_TRACKING_URI="file://' in exports

    decision = json.loads((tmp_path / "decision.json").read_text(encoding="utf-8"))
    assert decision["offline"] is True
    assert decision["mlflow_tracking_uri"].startswith("file://")


def test_respects_existing_file_uri(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _clean_env: dict[str, str]
) -> None:
    monkeypatch.chdir(tmp_path)
    env = _clean_env.copy()
    env["MLFLOW_TRACKING_URI"] = f"file://{(tmp_path / 'mlruns').as_posix()}"
    result = _run(["env", "--no-print", "--json-out", "decision.json"], env=env)
    assert result.returncode == 0, result.stderr

    decision = json.loads((tmp_path / "decision.json").read_text(encoding="utf-8"))
    assert decision["mlflow_tracking_uri"].startswith("file://")


def test_remote_uri_blocked_without_flag(tmp_path: Path, _clean_env: dict[str, str]) -> None:
    env = _clean_env.copy()
    env["MLFLOW_TRACKING_URI"] = "http://mlflow.example"
    result = _run(["env", "--no-print", "--json-out", str(tmp_path / "decision.json")], env=env)
    assert result.returncode == 0, result.stderr

    decision = json.loads((tmp_path / "decision.json").read_text(encoding="utf-8"))
    assert decision["offline"] is True
    assert decision["mlflow_tracking_uri"].startswith("file://")


def test_remote_uri_allowed_with_flag(tmp_path: Path, _clean_env: dict[str, str]) -> None:
    env = _clean_env.copy()
    env["MLFLOW_TRACKING_URI"] = "http://mlflow.example"
    env["MLFLOW_TRACKING_URI_REQUESTED"] = "http://mlflow.example"
    env["MLFLOW_ALLOW_REMOTE"] = "1"
    result = _run(
        ["env", "--allow-remote", "--no-print", "--json-out", str(tmp_path / "decision.json")],
        env=env,
    )
    assert result.returncode == 0, result.stderr

    decision = json.loads((tmp_path / "decision.json").read_text(encoding="utf-8"))
    assert decision["mlflow_tracking_uri"].startswith("http://")


def test_sets_wandb_mode_when_missing(tmp_path: Path, _clean_env: dict[str, str]) -> None:
    result = _run(
        ["env", "--no-print", "--json-out", str(tmp_path / "decision.json")], env=_clean_env
    )
    assert result.returncode == 0, result.stderr
    decision = json.loads((tmp_path / "decision.json").read_text(encoding="utf-8"))
    assert decision["wandb_env"].get("WANDB_MODE") == "offline"
