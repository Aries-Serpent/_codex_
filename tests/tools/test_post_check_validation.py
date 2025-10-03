from __future__ import annotations

from tools import post_check_validation


def test_post_check_validation_passes(monkeypatch) -> None:
    # Ensure environment keys that affect MLflow guards do not leak between tests.
    for key in ("MLFLOW_TRACKING_URI", "CODEX_MLFLOW_URI", "MLFLOW_ALLOW_REMOTE"):
        monkeypatch.delenv(key, raising=False)

    report = post_check_validation.run_post_check_validation()
    assert report.passed, report.to_dict()
    for check in report.checks:
        assert check.passed, f"{check.name} failed: {check.details}"
