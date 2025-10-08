from __future__ import annotations

import json
import os

import pytest

typer = pytest.importorskip("typer", reason="typer not installed")
from typer.testing import CliRunner  # type: ignore  # noqa: E402

from codex_ml.cli import tracking_decide  # noqa: E402


@pytest.fixture(autouse=True)
def restore_env(monkeypatch: pytest.MonkeyPatch) -> None:
    original = dict(os.environ)

    def restore() -> None:
        for key in list(os.environ):
            if key not in original:
                os.environ.pop(key)
        for key, value in original.items():
            os.environ[key] = value

    monkeypatch.addfinalizer(restore)


def test_tracking_decide_rewrites_remote_when_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.setenv("MLFLOW_OFFLINE", "1")
    result = runner.invoke(
        tracking_decide.app,
        ["decide", "--uri", "http://example:5000", "--pretty", "--no-pretty"],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["effective_uri"].startswith("file:"), payload
    assert payload["fallback_reason"] is not None
    assert payload["allow_remote"] is False


def test_tracking_decide_honours_allow_remote(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.delenv("MLFLOW_OFFLINE", raising=False)
    result = runner.invoke(
        tracking_decide.app,
        [
            "decide",
            "--uri",
            "http://remote-host:5000",
            "--env",
            "MLFLOW_ALLOW_REMOTE=1",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["effective_uri"] == "http://remote-host:5000"
    assert payload["allow_remote"] is True
    assert payload["fallback_reason"] is None
