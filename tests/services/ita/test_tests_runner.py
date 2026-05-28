from __future__ import annotations

from services.ita.app.models import TestsRunRequest as ITATestsRunRequest
from services.ita.app.tests_runner import _determine_failure_message, simulate_test_execution


def test_determine_failure_message_uses_keyword_specific_hints() -> None:
    assert "Lint failures" in _determine_failure_message("lint target")
    assert "Type errors" in _determine_failure_message("mypy target")
    assert "unspecified error" in _determine_failure_message("unit")


def test_simulate_test_execution_reports_summary_and_failures(monkeypatch) -> None:
    monkeypatch.setattr("services.ita.app.tests_runner.random.Random.random", lambda self: 0.0)
    response = simulate_test_execution(
        ITATestsRunRequest(targets=["tests/unit", "integration-suite", "fail-case"], timeout_s=120)
    )
    assert response.summary.total == 3
    assert response.summary.failed >= 1
    assert any("fail-case" in item.name for item in response.failures)
