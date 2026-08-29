from __future__ import annotations

from services.ita.app.models import TestsRunRequest as ITATestsRunRequest
from services.ita.app.tests_runner import _determine_failure_message, simulate_test_execution


def test_determine_failure_message_uses_keyword_specific_hints() -> None:
    assert "Lint failures" in _determine_failure_message("lint target"), "Condition must be true"
    assert "Type errors" in _determine_failure_message("mypy target"), "Error should be raised or set"
    assert "unspecified error" in _determine_failure_message("unit"), "Error should be raised or set"


def test_simulate_test_execution_reports_summary_and_failures(monkeypatch) -> None:
    monkeypatch.setattr("services.ita.app.tests_runner.random.Random.random", lambda self: 0.0)
    response = simulate_test_execution(
        ITATestsRunRequest(targets=["tests/unit", "integration-suite", "fail-case"], timeout_s=120)
    )
    assert response.summary.total == 3, "Response must not be empty"
    assert response.summary.failed >= 1, "failed must be greater than zero"
    assert any("fail-case" in item.name for item in response.failures), "Response must not be empty"
