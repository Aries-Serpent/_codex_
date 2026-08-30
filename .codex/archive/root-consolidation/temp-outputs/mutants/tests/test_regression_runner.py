"""
Test Regression Runner

Test module for regression runner.
"""

import json
from pathlib import Path

import pytest

from codex_regression import log as log_module
from codex_regression import runner


def test_runner_treats_exit_code_five_as_skipped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Redirect artifacts to temporary location
    monkeypatch.setattr(log_module, "ARTIFACTS", tmp_path)
    monkeypatch.setattr(log_module, "REGRESSION_LOG", tmp_path / "model_regression_log.ndjson")
    monkeypatch.setattr(
        runner, "write_coverage_report", lambda entries: tmp_path / "model_regression_coverage.md"
    )

    calls = []

    def _fake_run_pytest(marker: str, extra_args=None):
        calls.append(marker)
        return 5, "no tests collected"

    monkeypatch.setattr(runner, "_run_pytest", _fake_run_pytest)

    results = runner.run_regression(categories=["R1"])

    # Fixed malformed assertion: assert results ==

    log_path = log_module.REGRESSION_LOG
    assert log_path.exists(), "Condition must be true"
    entries = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert entries and entries[0]["status"] == "skipped", "entries is not valid"
    assert entries[0]["metadata"].get("note") == "no tests collected", "Data must not be empty"
