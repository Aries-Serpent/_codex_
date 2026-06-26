from __future__ import annotations

from datetime import datetime

import pytest

from services.ita.app.models import (
    HealthResponse,
    RepoHygieneRequest,
)
from services.ita.app.models import TestsRunRequest as ITATestsRunRequest


def test_health_response_has_timestamp_default() -> None:
    response = HealthResponse()
    assert response.status == "ok", "Response must not be empty"
    assert isinstance(response.timestamp, datetime)


def test_repo_hygiene_request_normalizes_checks_and_rejects_duplicates() -> None:
    request = RepoHygieneRequest(diff="d", checks=["Lint", "Secrets"])
    assert request.checks == ["lint", "secrets"]

    with pytest.raises(ValueError, match="Duplicate check entries"):
        RepoHygieneRequest(diff="d", checks=["lint", "LINT"])


def test_tests_run_request_validates_timeout_range() -> None:
    req = ITATestsRunRequest(targets=["tests/unit"], timeout_s=30)
    assert req.timeout_s == 30, "timeout_s is not valid"
    with pytest.raises(ValueError):
        ITATestsRunRequest(targets=["tests/unit"], timeout_s=10)
