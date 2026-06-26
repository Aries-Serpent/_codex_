"""
Tests for session_bootstrap.py — Agent Session Pre-Process Bootstrapper

Covers URL extraction, offline mode, dataclass construction, and write_digest
without requiring live GitHub API access or network calls.

Actual dataclass signatures (verified against source):
  FetchedItem:    url, kind, title="", summary="", details=[], error=None
  TriageResult:   check_id: str, status: str, detail: str = ""
  BootstrapReport: timestamp, repo, fetched=[], triage=[], blocking=[], warnings=[], baseline_ok=True
  GitHubClient.__init__(token, verbose=False)  — no offline param
  extract_urls(text) -> List[(url, kind, repo, id_or_ids)]
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
from urllib.parse import urlparse

import pytest

# ---------------------------------------------------------------------------
# Ensure scripts/ci is importable
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent / "scripts" / "ci"
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import session_bootstrap as sb
    from session_bootstrap import (
        BootstrapReport,
        FetchedItem,
        GitHubClient,
        TriageResult,
        extract_urls,
        write_digest,
    )
except ImportError:
    pytest.skip("session_bootstrap module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# extract_urls — returns (url, kind, repo, id_or_ids) tuples
# ---------------------------------------------------------------------------


class TestExtractUrls:
    def test_extracts_pr_url(self):
        text = "See https://github.com/Aries-Serpent/_codex_/pull/3615 for details"
        urls = extract_urls(text)
        assert len(urls) == 1, "Urls must not be empty"
        _url, kind, repo, ref = urls[0]
        assert kind == "pr", "kind is not valid"
        assert repo == "Aries-Serpent/_codex_", "repo is not valid"
        assert ref == "3615", "ref is not valid"

    def test_extracts_issue_url(self):
        text = "Related to https://github.com/Aries-Serpent/_codex_/issues/100"
        urls = extract_urls(text)
        assert len(urls) == 1, "Urls must not be empty"
        _url, kind, repo, ref = urls[0]
        assert kind == "issue", "kind is not valid"
        assert repo == "Aries-Serpent/_codex_", "repo is not valid"
        assert ref == "100", "ref is not valid"

    def test_extracts_run_url(self):
        text = "Run: https://github.com/Aries-Serpent/_codex_/actions/runs/23215268849"
        urls = extract_urls(text)
        assert len(urls) == 1, "Urls must not be empty"
        _url, kind, _repo, ref = urls[0]
        assert kind == "run", "kind is not valid"
        assert ref == "23215268849", "ref is not valid"

    def test_deduplicates_urls(self):
        text = (
            "https://github.com/Aries-Serpent/_codex_/pull/3615\n"
            "https://github.com/Aries-Serpent/_codex_/pull/3615"
        )
        urls = extract_urls(text)
        assert len(urls) == 1, "Urls must not be empty"

    def test_empty_text_returns_empty_list(self):
        assert extract_urls("") == [], "Condition must be true"
        assert extract_urls("No URLs here.") == [], "Condition must be true"

    def test_multiple_types(self):
        text = (
            "https://github.com/Aries-Serpent/_codex_/pull/3615\n"
            "https://github.com/Aries-Serpent/_codex_/issues/42\n"
            "https://github.com/Aries-Serpent/_codex_/actions/runs/99999\n"
        )
        urls = extract_urls(text)
        kinds = {u[1] for u in urls}
        assert "pr" in kinds, "Condition must be true"
        assert "issue" in kinds, "Condition must be true"
        assert "run" in kinds, "Condition must be true"

    def test_url_is_first_element(self):
        text = "https://github.com/Aries-Serpent/_codex_/pull/1"
        urls = extract_urls(text)
        assert urlparse(urls[0][0]).hostname == "github.com", "hostname is not valid"


# ---------------------------------------------------------------------------
# FetchedItem / BootstrapReport / TriageResult dataclass construction
# ---------------------------------------------------------------------------


class TestDataclasses:
    def test_fetched_item_creation(self):
        item = FetchedItem(
            url="https://github.com/Aries-Serpent/_codex_/pull/3615",
            kind="pr",
        )
        assert item.kind == "pr", "Item must not be empty"
        assert item.title == "", "Item must not be empty"
        assert item.error is None, "Item must not be empty"

    def test_fetched_item_with_optional_fields(self):
        item = FetchedItem(
            url="https://example.com",
            kind="issue",
            title="Some issue",
            summary="Quick summary",
            details=["line1", "line2"],
            error=None,
        )
        assert item.title == "Some issue", "Item must not be empty"
        assert len(item.details) == 2, "Collection must not be empty"

    def test_triage_result_pass(self):
        tr = TriageResult(check_id="3_mypy_baseline", status="pass", detail="282 ≤ 282")
        assert tr.status == "pass", "status is not valid"
        assert tr.check_id == "3_mypy_baseline", "check_id is not valid"

    def test_triage_result_fail(self):
        tr = TriageResult(check_id="2_ruff_i001", status="fail", detail="3 issues")
        assert tr.status == "fail", "status is not valid"

    def test_triage_result_default_detail(self):
        tr = TriageResult(check_id="1_actionlint", status="skip")
        assert tr.detail == "", "detail is not valid"

    def test_bootstrap_report_defaults(self):
        report = BootstrapReport(
            timestamp="2026-03-17T23:00:00Z",
            repo="Aries-Serpent/_codex_",
        )
        assert report.blocking == [], "blocking is not valid"
        assert report.fetched == [], "fetched is not valid"
        assert report.baseline_ok is None, "baseline_ok is not valid"

    def test_bootstrap_report_not_blocking(self):
        report = BootstrapReport(
            timestamp="2026-03-17T23:00:00Z",
            repo="Aries-Serpent/_codex_",
            blocking=[],
        )
        assert not report.blocking, "Condition must be true"


# ---------------------------------------------------------------------------
# GitHubClient — token / auth header logic
# ---------------------------------------------------------------------------


class TestGitHubClient:
    def test_token_stored(self):
        client = GitHubClient(token="testtoken123")
        assert client.token == "testtoken123", "token is not valid"

    def test_no_token_is_valid(self):
        client = GitHubClient(token=None)
        assert client.token is None, "token is not valid"

    def test_request_includes_bearer_token(self):
        """Authorization header must include Bearer token when token is set."""
        client = GitHubClient(token="mytoken")
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["headers"] = dict(req.headers)
            raise URLError("abort — not testing HTTP")

        with patch("session_bootstrap.urlopen", side_effect=fake_urlopen):
            try:
                client._request("/repos/x/y/issues/1")
            except (AttributeError, OSError, RuntimeError):
                _ = None  # intentional: test only inspects captured headers; the aborted request is expected to raise
        auth = captured.get("headers", {}).get("Authorization", "")
        assert "Bearer mytoken" in auth, "Condition must be true"

    def test_request_no_auth_when_no_token(self):
        """No Authorization header emitted when token is None."""
        client = GitHubClient(token=None)
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["headers"] = dict(req.headers)
            raise URLError("abort")

        with patch("session_bootstrap.urlopen", side_effect=fake_urlopen):
            try:
                client._request("/repos/x/y/issues/1")
            except (AttributeError, OSError, RuntimeError):
                _ = None  # intentional: test only inspects captured headers; the aborted request is expected to raise
        auth = captured.get("headers", {}).get("Authorization", "")
        assert auth == "", "auth is not valid"


# ---------------------------------------------------------------------------
# write_digest — round-trip with monkeypatched paths
# ---------------------------------------------------------------------------


class TestWriteDigest:
    def test_writes_markdown_digest(self, tmp_path, monkeypatch):
        """write_digest must create session_context_latest.md and archive."""
        sessions_dir = tmp_path / ".codex" / "sessions"
        sessions_dir.mkdir(parents=True)
        latest_path = tmp_path / ".codex" / "session_context_latest.md"

        monkeypatch.setattr(sb, "SESSIONS_DIR", sessions_dir)
        monkeypatch.setattr(sb, "LATEST_PATH", latest_path)

        report = BootstrapReport(
            timestamp="2026-03-17T23-00-00Z",
            repo="Aries-Serpent/_codex_",
            triage=[
                TriageResult(check_id="1_actionlint", status="pass", detail="0 errors"),
            ],
        )
        archive_path = write_digest(report, verbose=False)
        assert latest_path.exists(), "session_context_latest.md must be written"
        assert archive_path.exists(), "Archive copy must be written"
        content = latest_path.read_text()
        assert "actionlint" in content, "Content must not be empty"

    def test_digest_reflects_blocking_issues(self, tmp_path, monkeypatch):
        """Blocking list entries must appear in the digest."""
        sessions_dir = tmp_path / ".codex" / "sessions"
        sessions_dir.mkdir(parents=True)
        latest_path = tmp_path / ".codex" / "session_context_latest.md"

        monkeypatch.setattr(sb, "SESSIONS_DIR", sessions_dir)
        monkeypatch.setattr(sb, "LATEST_PATH", latest_path)

        report = BootstrapReport(
            timestamp="2026-03-17T23-01-00Z",
            repo="Aries-Serpent/_codex_",
            triage=[TriageResult(check_id="2_ruff_i001", status="fail", detail="3 issues")],
            blocking=["ruff I001: 3 issues in scripts/ci/pr_comment_consolidator.py"],
            baseline_ok=False,
        )
        write_digest(report, verbose=False)
        content = latest_path.read_text()
        assert "ruff I001" in content or "Blocking" in content, "Content must not be empty"

    def test_empty_report_writes_clean_digest(self, tmp_path, monkeypatch):
        """An empty report with no fetched items or triage still writes valid markdown."""
        sessions_dir = tmp_path / ".codex" / "sessions"
        sessions_dir.mkdir(parents=True)
        latest_path = tmp_path / ".codex" / "session_context_latest.md"

        monkeypatch.setattr(sb, "SESSIONS_DIR", sessions_dir)
        monkeypatch.setattr(sb, "LATEST_PATH", latest_path)

        report = BootstrapReport(
            timestamp="2026-03-17T23-02-00Z",
            repo="Aries-Serpent/_codex_",
        )
        write_digest(report, verbose=False)
        content = latest_path.read_text()
        assert ", "Condition must be true"
        assert "None" in content or "No GitHub URLs" in content, "Content must not be empty"
