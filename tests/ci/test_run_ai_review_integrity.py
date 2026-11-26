"""Exact-SHA AI review regressions for the PR approval driver."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import pytest

AGENTS_ROOT = Path(__file__).resolve().parents[2] / ".github" / "agents"
if str(AGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENTS_ROOT))

from codex_reviewer.github_client import GitHubAPIClient
from codex_reviewer.main import CodexQuantumReviewer, ReviewContext, ReviewResult
from codex_reviewer.secret_patterns import SecretPatterns
from codex_reviewer.security import SecurityValidator

from scripts.ci import run_ai_review

SHA = "a" * 40
OTHER_SHA = "b" * 40


def pull_request(changed_files: int = 1) -> dict[str, Any]:
    return {
        "state": "open",
        "number": 5766,
        "changed_files": changed_files,
        "head": {"sha": SHA, "ref": "0D_base_"},
        "base": {"ref": "main"},
        "user": {"login": "author"},
        "body": "review me",
        "labels": [],
        "requested_reviewers": [],
    }


def context() -> ReviewContext:
    return ReviewContext(
        pr_number=5766,
        repo="Aries-Serpent/_codex_",
        files_changed=["src/example.py"],
        diff="+example",
        base_branch="main",
        head_branch="0D_base_",
        author="author",
        description="review me",
        head_sha=SHA,
    )


def clean_result() -> ReviewResult:
    return ReviewResult(
        status="approved",
        confidence=0.99,
        suggestions=[],
        orchestration_plan={},
        next_steps=[],
        knowledge_gaps=[],
    )


def test_load_review_context_paginates_all_changed_files(monkeypatch: Any) -> None:
    def request(_method: str, path: str, _token: str, **_kwargs: Any) -> tuple[int, Any]:
        if path == "/repos/o/r/pulls/1":
            return 200, pull_request(changed_files=101)
        if path.endswith("page=1"):
            return 200, [
                {"filename": f"file-{index}.py", "patch": f"+file-{index}"} for index in range(100)
            ]
        if path.endswith("page=2"):
            return 200, [{"filename": "file-100.py", "patch": "+file-100"}]
        raise AssertionError(f"unexpected path: {path}")

    monkeypatch.setattr(run_ai_review, "github_request", request)

    _pr, names, _diff = run_ai_review.load_review_context("o/r", 1, "read-token")

    assert len(names) == 101
    assert names[-1] == "file-100.py"


@pytest.mark.asyncio
async def test_xss_scan_requires_identifier_boundary() -> None:
    validator = SecurityValidator()
    review_context = context()
    review_context.diff = "diff --git a/src/connection.py b/src/connection.py\n--- a/src/connection.py\n+++ b/src/connection.py\n+RequestsConnectionError = ConnectionError"
    review_context.files_changed = ["src/connection.py"]

    vulnerabilities = await validator._check_xss(review_context.files_changed, review_context.diff)

    assert vulnerabilities == []


def test_secrets_baseline_is_not_high_risk_source() -> None:
    assert not SecretPatterns.is_high_risk_file(".secrets.baseline")
    assert SecretPatterns.should_exclude_file(".secrets.baseline")


def test_security_source_files_are_not_high_risk_artifacts() -> None:
    for filename in (
        ".github/agents/codex_reviewer/secret_patterns.py",
        "scripts/ci/secrets_findings_formatter.py",
        "scripts/github_secrets_sync.py",
    ):
        assert not SecretPatterns.is_high_risk_file(filename)


def test_load_review_context_rejects_incomplete_file_listing(monkeypatch: Any) -> None:
    def request(_method: str, path: str, _token: str, **_kwargs: Any) -> tuple[int, Any]:
        if path == "/repos/o/r/pulls/1":
            return 200, pull_request(changed_files=2)
        if path.endswith("page=1"):
            return 200, [{"filename": "only-one.py"}]
        raise AssertionError(path)

    monkeypatch.setattr(run_ai_review, "github_request", request)

    with pytest.raises(RuntimeError, match="incomplete"):
        run_ai_review.load_review_context("o/r", 1, "read-token")


def test_load_review_context_uses_file_patches_without_diff_media(monkeypatch: Any) -> None:
    def request(_method: str, path: str, _token: str, **kwargs: Any) -> tuple[int, Any]:
        if path == "/repos/o/r/pulls/1":
            return 200, pull_request(changed_files=1)
        if path.endswith("page=1"):
            return 200, [
                {
                    "filename": "src/example.py",
                    "patch": "@@ -1 +1 @@\n-old\n+new",
                }
            ]
        raise AssertionError(f"unexpected path: {path}; {kwargs}")

    monkeypatch.setattr(run_ai_review, "github_request", request)

    _pr, names, diff = run_ai_review.load_review_context("o/r", 1, "read-token")

    assert names == ["src/example.py"]
    assert "diff --git a/src/example.py b/src/example.py" in diff
    assert "--- a/src/example.py" in diff
    assert "+++ b/src/example.py" in diff
    assert "-old" in diff
    assert "+new" in diff


def test_load_review_context_falls_back_to_full_diff_for_patchless_file(
    monkeypatch: Any,
) -> None:
    full_diff = "diff --git a/assets/model.bin b/assets/model.bin\nBinary files differ\n"

    def request(_method: str, path: str, _token: str, **kwargs: Any) -> tuple[int, Any]:
        if path == "/repos/o/r/pulls/1" and "diff" not in kwargs.get("accept", ""):
            return 200, pull_request(changed_files=1)
        if path.endswith("page=1"):
            return 200, [{"filename": "assets/model.bin", "patch": None}]
        if path == "/repos/o/r/pulls/1" and "diff" in kwargs.get("accept", ""):
            return 200, full_diff
        raise AssertionError(f"unexpected path: {path}; {kwargs}")

    monkeypatch.setattr(run_ai_review, "github_request", request)

    _pr, names, diff = run_ai_review.load_review_context("o/r", 1, "read-token")

    assert names == ["assets/model.bin"]
    assert diff == full_diff


def test_load_review_context_rejects_incomplete_full_diff(monkeypatch: Any) -> None:
    def request(_method: str, path: str, _token: str, **kwargs: Any) -> tuple[int, Any]:
        if path == "/repos/o/r/pulls/1" and "diff" not in kwargs.get("accept", ""):
            return 200, pull_request(changed_files=1)
        if path.endswith("page=1"):
            return 200, [{"filename": "assets/model.bin", "patch": None}]
        if path == "/repos/o/r/pulls/1" and "diff" in kwargs.get("accept", ""):
            return 200, "diff --git a/other.txt b/other.txt\n"
        raise AssertionError(f"unexpected path: {path}; {kwargs}")

    monkeypatch.setattr(run_ai_review, "github_request", request)

    with pytest.raises(RuntimeError, match="full diff is incomplete"):
        run_ai_review.load_review_context("o/r", 1, "read-token")


def test_python_quality_analysis_is_substantive() -> None:
    reviewer = CodexQuantumReviewer()
    diff = """diff --git a/example.py b/example.py
--- a/example.py
+++ b/example.py
+try:
+    work()
+except:
+    pass
"""

    result = asyncio.run(reviewer._analyze_python_quality("example.py", diff))

    assert any(issue["type"] == "bare_except" for issue in result)


def test_clean_complete_review_can_approve() -> None:
    reviewer = CodexQuantumReviewer()
    summary = {
        category: {"category": category, "gaps": []}
        for category in ("code_quality", "security", "performance", "documentation")
    }

    confidence = reviewer._calculate_confidence([], summary)
    result = reviewer._aggregate_results(list(summary.values()))

    assert confidence > 0.95
    assert result.status == "approved"


def test_low_severity_opportunity_does_not_block_approval() -> None:
    reviewer = CodexQuantumReviewer()
    analyses = [
        {"category": category, "gaps": []}
        for category in ("code_quality", "security", "performance", "documentation")
    ]
    analyses.append(
        {
            "category": "quantum_patterns",
            "patterns": [
                {
                    "type": "superposition_opportunity",
                    "description": "advisory parallelism opportunity",
                }
            ],
        }
    )

    result = reviewer._aggregate_results(analyses)

    assert result.status == "approved"
    assert len(result.suggestions) == 1
    assert result.suggestions[0]["severity"] == "low"


def test_security_scan_ignores_nonexecutable_fixture_patterns(monkeypatch: Any) -> None:
    diff = """diff --git a/scripts/example.py b/scripts/example.py
--- /dev/null
+++ b/scripts/example.py
+token = app.get_installation_token(installation_id=1)
+set_owner_protected_secret = True
+command = ["git", "config"]  # never shell=True
+lock_handle = Path("runtime").open("a+", encoding="utf-8")
+f"sys.path.insert(0, {value!r}); "
+patterns = [r"os.system\\s*\\(", r"shell=True", r"eval\\s*\\(", r"<script"]
 diff --git a/tests/example.py b/tests/example.py
--- /dev/null
+++ b/tests/example.py
+github_token = "ghp_1234567890abcdefghij123456789012"
+private_key = "-----BEGIN " + "PRIVATE KEY-----\\ncanary\\n-----END PRIVATE KEY-----"
+output = "../reports/example.txt"
"""
    validator = SecurityValidator()
    review_context = context()
    review_context.diff = diff
    review_context.files_changed = ["scripts/example.py", "tests/example.py", "package.json"]

    findings = asyncio.run(validator.scan(review_context))

    assert findings == []


def test_github_client_posts_commit_id(monkeypatch: Any) -> None:
    client = GitHubAPIClient(token="token")
    captured: dict[str, Any] = {}

    async def make_request(_url: str, payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return {"id": 1}

    monkeypatch.setattr(client, "_make_request", make_request)

    asyncio.run(client.post_review("o/r", 1, "body", "APPROVE", commit_id=SHA))

    assert captured["commit_id"] == SHA
    assert captured["event"] == "APPROVE"


def test_head_drift_is_rejected_before_publication(monkeypatch: Any) -> None:
    reviewer = CodexQuantumReviewer(head_verifier=lambda _context: False)

    async def unexpected(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("drifted review must not be published")

    monkeypatch.setattr(reviewer, "_github_api_post_review", unexpected)

    with pytest.raises(RuntimeError, match="head changed"):
        asyncio.run(reviewer._post_review(context(), clean_result()))


def test_publication_failure_reaches_driver(monkeypatch: Any) -> None:
    reviewer = CodexQuantumReviewer()

    class FailingClient:
        async def post_review(self, **_kwargs: Any) -> dict[str, Any]:
            raise RuntimeError("denied")

    reviewer.github_client = FailingClient()

    with pytest.raises(RuntimeError, match="denied"):
        asyncio.run(
            reviewer._github_api_post_review(
                "o/r",
                1,
                "body",
                "APPROVE",
                [],
                SHA,
            )
        )


def test_mint_review_token_revokes_after_repository_validation_error(
    monkeypatch: Any,
) -> None:
    revoked: list[str] = []

    class App:
        def __init__(self, _config: Any) -> None:
            pass

        def get_installation_token(self, **_kwargs: Any) -> Any:
            return type(
                "Token",
                (),
                {"token": "review-token", "permissions": {"pull_requests": "write"}},
            )()

    monkeypatch.setattr(run_ai_review, "resolve_app_id", lambda: ("1", "test"))
    monkeypatch.setattr(run_ai_review, "resolve_app_installation_id", lambda: ("2", "test"))
    monkeypatch.setattr(
        run_ai_review,
        "resolve_app_private_key",
        lambda: (
            "-----BEGIN " + "PRIVATE KEY-----\nfixture-canary\n-----END PRIVATE KEY-----",
            "test",
        ),
    )
    monkeypatch.setattr(run_ai_review, "GitHubApp", App)
    monkeypatch.setattr(
        run_ai_review,
        "github_request",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("lookup failed")),
    )
    monkeypatch.setattr(run_ai_review, "revoke_token", lambda token: revoked.append(token) or True)

    with pytest.raises(RuntimeError, match="lookup failed"):
        run_ai_review.mint_review_token("o/r")

    assert revoked == ["review-token"]


def test_driver_returns_nonzero_for_failed_review_and_revokes(
    monkeypatch: Any, capsys: Any
) -> None:
    revoked: list[str] = []
    monkeypatch.setattr(run_ai_review, "get_token", lambda **_kwargs: ("read-token", "test"))
    monkeypatch.setattr(
        run_ai_review,
        "load_review_context",
        lambda *_args, **_kwargs: (pull_request(), ["src/example.py"], "+example"),
    )
    monkeypatch.setattr(run_ai_review, "mint_review_token", lambda _repo: ("review-token", 1))

    async def execute(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return {"status": "review_failed", "error": "publication denied"}

    monkeypatch.setattr(run_ai_review, "execute_review", execute)
    monkeypatch.setattr(run_ai_review, "revoke_token", lambda token: revoked.append(token) or True)
    monkeypatch.setattr("sys.argv", ["run_ai_review.py", "--pr", "5766", "--sha", SHA])

    assert run_ai_review.main() == 1
    assert revoked == ["review-token"]
    assert json.loads(capsys.readouterr().out)["review_result"]["status"] == "review_failed"
