"""
Test Offline Decision

Test module for offline decision.
"""

from __future__ import annotations

from codex_ml.tracking.offline import decide_offline


def test_sqlite_uri_preserved_offline(monkeypatch, tmp_path):
    sqlite_uri = f"sqlite:///{(tmp_path / 'mlflow.db').as_posix()}"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", sqlite_uri)

    decision = decide_offline(
        prefer_offline=True,
        allow_remote=False,
        mlruns_dir=tmp_path / "mlruns",
    )

    assert decision.mlflow_tracking_uri == sqlite_uri, "mlflow_tracking_uri is not valid"
    assert decision.offline is True, "offline is not valid"
    assert decision.reason == "respecting existing MLFLOW_TRACKING_URI", "reason is not valid"
