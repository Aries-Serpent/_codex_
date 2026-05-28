from __future__ import annotations

import pytest

from services.ita.app.hygiene import run_hygiene_checks
from services.ita.app.models import RepoHygieneRequest


def test_run_hygiene_checks_detects_multiple_issue_types() -> None:
    diff = "\n".join(
        [
            "diff --git a/new.py b/new.py", # pragma: allowlist secret # pragma: allowlist secret
            "+++ b/new.py",
            "+print('TODO debug') ",
            "+API_KEY='AWS_SECRET_KEY=ABCDEFGHJKLMNOPQRST'",
        ]
    )
    request = RepoHygieneRequest(diff=diff, checks=["format", "lint", "secrets", "license"])
    issues = run_hygiene_checks(request)
    issue_types = {issue.type for issue in issues}
    assert {"format", "lint", "secrets", "license"}.issubset(issue_types)


def test_run_hygiene_checks_rejects_unknown_checks() -> None:
    request = RepoHygieneRequest(diff="", checks=["format"])
    request.checks = ["format", "bogus"]
    with pytest.raises(ValueError, match="Unsupported hygiene checks requested"):
        run_hygiene_checks(request)
