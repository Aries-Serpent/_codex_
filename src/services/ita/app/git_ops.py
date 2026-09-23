"""Simplified GitHub Pull Request operations."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .models import GitCreatePullRequestBody, GitCreatePullRequestResponse


@dataclass(frozen=True)
class PullRequestSimulation:
    repo: str
    title: str
    body: str
    base: str
    head: str
    labels: tuple[str, ...] = ()

    def to_message(self) -> str:
        lines = [
            f"Repo: {self.repo}",
            f"Base: {self.base}",
            f"Head: {self.head}",
            f"Title: {self.title}",
            f"Labels: {', '.join(self.labels) if self.labels else '∅'}",
        ]
        return " | ".join(lines)


def _build_pr_url(repo: str, head: str) -> str:
    base_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    return f"{base_url}/{repo}/pull/new/{head}"


def simulate_pull_request(
    payload: GitCreatePullRequestBody, *, dry_run: bool, confirm: bool
) -> GitCreatePullRequestResponse:
    simulation = PullRequestSimulation(
        repo=payload.repo,
        title=payload.title,
        body=payload.body,
        base=payload.base,
        head=payload.head,
        labels=tuple(payload.labels or ()),
    )

    if dry_run:
        return GitCreatePullRequestResponse(
            simulated=True,
            pr_url=None,
            message=f"Dry run: {simulation.to_message()}",
        )

    if not confirm:
        raise ValueError("confirm=true is required when dry_run is false")

    pr_url = _build_pr_url(payload.repo, payload.head)
    return GitCreatePullRequestResponse(
        simulated=False,
        pr_url=pr_url,
        message=f"Pull request created at {pr_url}",
    )


__all__ = ["simulate_pull_request"]
