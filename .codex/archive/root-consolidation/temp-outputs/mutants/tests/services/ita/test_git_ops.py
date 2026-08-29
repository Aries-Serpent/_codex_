from __future__ import annotations

import pytest

from services.ita.app.git_ops import PullRequestSimulation, _build_pr_url, simulate_pull_request
from services.ita.app.models import GitCreatePullRequestBody


def _payload() -> GitCreatePullRequestBody:
    return GitCreatePullRequestBody(
        repo="octo/repo",
        title="Improve tests",
        body="Adds focused test coverage",
        base="main",
        head="feature/tests",
        labels=["qa", "coverage"],
    )


def test_pull_request_simulation_to_message_handles_labels() -> None:
    msg = PullRequestSimulation(
        repo="octo/repo",
        title="t",
        body="b",
        base="main",
        head="feature",
        labels=("qa",),
    ).to_message()
    assert "Repo: octo/repo" in msg, "Condition must be true"
    assert "Labels: qa" in msg, "Condition must be true"


def test_build_pr_url_uses_default_github_domain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_SERVER_URL", raising=False)
    assert (_build_pr_url("octo/repo", "feature/tests")
        == "https://github.com/octo/repo/pull/new/feature/tests"
    )


def test_simulate_pull_request_dry_run() -> None:
    response = simulate_pull_request(_payload(
    ), dry_run=True, confirm=False)
    assert response.simulated is True, "Response must not be empty"
    assert response.pr_url is None, "Response must not be empty"


def test_simulate_pull_request_requires_confirm() -> None:
    with pytest.raises(ValueError, match="confirm=true"):
        simulate_pull_request(_payload(), dry_run=False, confirm=False)


def test_simulate_pull_request_creates_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.example")
    response = simulate_pull_request(_payload(), dry_run=False, confirm=True)
    assert response.simulated is False, "Response must not be empty"
    assert str(response.pr_url) == "https://github.example/octo/repo/pull/new/feature/tests"
