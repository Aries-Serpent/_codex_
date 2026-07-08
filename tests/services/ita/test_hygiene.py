from __future__ import annotations

import pytest

from services.ita.app.hygiene import run_hygiene_checks
from services.ita.app.models import RepoHygieneRequest


def test_run_hygiene_checks_detects_multiple_issue_types() -> None:
    diff = "\n".join(
        [
            "diff --git a/new.py b/new.py",  # pragma: allowlist secret
            "+++ b/new.py",
            "+logger.info('TODO debug') ",
            "+API_KEY='AWS_SECRET_KEY=ABCDEFGHJKLMNOPQRST'",  # pragma: allowlist secret
        ]
    )
    request = RepoHygieneRequest(diff=diff, checks=["format", "lint", "secrets", "license"])
    issues = run_hygiene_checks(request)
    issue_types = {issue.type for issue in issues}
    assert {"format", "lint", "secrets", "license"}.issubset(issue_types)


def test_run_hygiene_checks_rejects_unknown_checks() -> None:
    request = RepoHygieneRequest(diff="", checks=["format", "bogus"])
    with pytest.raises(ValueError, match="Unsupported hygiene checks requested"):
        run_hygiene_checks(request)


def test_run_hygiene_checks_only_returns_requested_issue_types() -> None:
    diff = "\n".join(
        [
            "diff --git a/new.py b/new.py",  # pragma: allowlist secret
            "+++ b/new.py",
            "+logger.info('TODO debug') ",
            "+API_KEY='AWS_SECRET_KEY=ABCDEFGHJKLMNOPQRST'",  # pragma: allowlist secret
        ]
    )
    request = RepoHygieneRequest(diff=diff, checks=["secrets"])
    issues = run_hygiene_checks(request)

    assert issues, "issues is not valid"
    assert {issue.type for issue in issues} == {"secrets"}, "for is not valid"


def test_run_hygiene_checks_clean_diff_returns_no_issues() -> None:
    diff = "\n".join(
        [
            "diff --git a/new.py b/new.py",
            "+++ b/new.py",
            "+logger.info('hello world')",
        ]
    )
    request = RepoHygieneRequest(diff=diff, checks=["format", "lint", "secrets", "license"])
    issues = run_hygiene_checks(request)

    assert issues == [], "issues is not valid"
