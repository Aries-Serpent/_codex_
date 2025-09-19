"""Models used by the Codex bridge client."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class _StrictModel(BaseModel):
    model_config = {
        "extra": "forbid",
    }


class KnowledgeSearchResult(_StrictModel):
    snippet: str
    source: str
    score: float


class KnowledgeSearchResponse(_StrictModel):
    results: List[KnowledgeSearchResult]


class RepoHygieneIssue(_StrictModel):
    type: str
    path: str
    message: str
    severity: str


class RepoHygieneResponse(_StrictModel):
    issues: List[RepoHygieneIssue]


class TestsRunSummary(_StrictModel):
    total: int
    passed: int
    failed: int
    duration_s: float


class TestFailure(_StrictModel):
    name: str
    message: str


class TestsRunResponse(_StrictModel):
    summary: TestsRunSummary
    failures: List[TestFailure]


class GitCreatePullRequestResponse(_StrictModel):
    simulated: bool
    pr_url: Optional[HttpUrl] = None
    message: str


__all__ = [
    "KnowledgeSearchResponse",
    "RepoHygieneResponse",
    "TestsRunResponse",
    "GitCreatePullRequestResponse",
]
