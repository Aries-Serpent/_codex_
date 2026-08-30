"""Fixtures and utilities for CODEX_MASTER_KEY testing.

This module provides:
- Token resolution and validation fixtures
- Mock GitHub API response builders
- Test data generators with timestamped test variables
- Rate limit and error simulation utilities
"""

from __future__ import annotations

import json
import os
import time
import unittest.mock as mock
from datetime import datetime, timezone
from io import BytesIO
from typing import (  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    Any,
    Optional,
)
from urllib.error import HTTPError

import pytest

from scripts.ci._token_resolver import get_token

# ─────────────────────────────────────────────────────────────────────────────
# Token Resolution & Configuration
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def github_token() -> str:
    """Return GitHub token from environment, prefer CODEX_MASTER_KEY."""
    token = (
        get_token(required_elevated=True)[0]
        or get_token(required_elevated=True)[0]
        or get_token(required_elevated=False)[0]
        or os.environ.get("GITHUB_TOKEN", "")
    )
    if not token:
        pytest.skip("No GitHub token available (CODEX_MASTER_KEY, CODEX_BACKUP_KEY, etc.)")
    return token


@pytest.fixture
def api_headers(github_token: str) -> dict[str, str]:
    """Return standard GitHub API headers with token."""
    return {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }


@pytest.fixture
def gh_api_base() -> str:
    """Return base GitHub API URL."""
    return "https://api.github.com"


@pytest.fixture
def repo_owner() -> str:
    """Return repository owner."""
    return "Aries-Serpent"


@pytest.fixture
def repo_name() -> str:
    """Return repository name."""
    return "_codex_"


@pytest.fixture
def org_name() -> str:
    """Return organization name."""
    return "Aries-Serpent"


# ─────────────────────────────────────────────────────────────────────────────
# Test Data Generators
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def test_var_name_base() -> str:
    """Return base name for test variables (timestamped to avoid conflicts)."""
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"CODEX_API_TEST_REPO_{ts}"


@pytest.fixture
def test_var_name_org(test_var_name_base: str) -> str:
    """Return org-scoped test variable name."""
    return test_var_name_base.replace("REPO", "ORG")


@pytest.fixture
def test_branch_name() -> str:
    """Return test branch name."""
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    import uuid
    short_uuid = str(uuid.uuid4())[:8]
    return f"test/api/branch-{short_uuid}"


@pytest.fixture
def test_webhook_url() -> str:
    """Return mock webhook URL."""
    return "https://example.com/webhook"


# ─────────────────────────────────────────────────────────────────────────────
# Mock GitHub API Response Builders
# ─────────────────────────────────────────────────────────────────────────────


def mock_response(
    payload: dict,
    status: int = 200,
    headers: Optional[dict[str, str]] = None,
) -> mock.MagicMock:
    """Return a mock urllib response with the given payload and status."""
    if headers is None:
        headers = {}

    # Default rate limit headers
    if "X-RateLimit-Limit" not in headers:
        headers["X-RateLimit-Limit"] = "60"
    if "X-RateLimit-Remaining" not in headers:
        headers["X-RateLimit-Remaining"] = "59"
    if "X-RateLimit-Reset" not in headers:
        headers["X-RateLimit-Reset"] = str(int(time.time()) + 3600)

    body = json.dumps(payload).encode()
    cm = mock.MagicMock()
    cm.__enter__ = mock.Mock(return_value=cm)
    cm.__exit__ = mock.Mock(return_value=False)
    cm.read = mock.Mock(return_value=body)
    cm.status = status
    cm.headers = headers
    cm.getheader = mock.Mock(side_effect=lambda k: headers.get(k))
    return cm


def mock_http_error(
    code: int,
    reason: str = "Error",
    body: str = "{}",
) -> HTTPError:
    """Return an HTTPError with the given status code and body."""
    headers = mock.MagicMock()
    headers.get = mock.Mock(return_value="")
    return HTTPError(
        url="https://api.github.com/test",
        code=code,
        msg=reason,
        hdrs=headers,
        fp=BytesIO(body.encode()),
    )


@pytest.fixture
def mock_variable_response():
    """Return callable that generates mock variable API responses."""

    def _make(name: str, value: str, scope: str = "repo") -> dict[str, Any]:
        return {
            "name": name,
            "value": value,
            "created_at": datetime.now(tz=timezone.utc).isoformat() + "Z",
            "updated_at": datetime.now(tz=timezone.utc).isoformat() + "Z",
        }

    return _make


@pytest.fixture
def mock_workflow_run_response():
    """Return callable that generates mock workflow run responses."""

    def _make(
        run_id: int = 12345,
        status: str = "in_progress",
        conclusion: Optional[str] = None,
    ) -> dict[str, Any]:
        return {
            "id": run_id,
            "name": "Test Workflow",
            "status": status,
            "conclusion": conclusion,
            "created_at": datetime.now(tz=timezone.utc).isoformat() + "Z",
            "updated_at": datetime.now(tz=timezone.utc).isoformat() + "Z",
            "event": "push",
            "head_branch": "main",
            "head_sha": "abc1234567890def",
        }

    return _make


# ─────────────────────────────────────────────────────────────────────────────
# Rate Limit Utilities
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_rate_limit_headers():
    """Return headers simulating rate limit state."""

    def _make(
        remaining: int = 59,
        limit: int = 60,
        reset_in_secs: int = 3600,
    ) -> dict[str, str]:
        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(time.time()) + reset_in_secs),
        }

    return _make


# ─────────────────────────────────────────────────────────────────────────────
# Error Simulation Utilities
# ─────────────────────────────────────────────────────────────────────────────


class APIErrorScenarios:
    """Predefined API error scenarios for testing."""

    @staticmethod
    def missing_token() -> HTTPError:
        """401 Unauthorized — missing token."""
        return mock_http_error(
            401,
            "Unauthorized",
            '{"message": "Bad credentials"}',
        )

    @staticmethod
    def insufficient_scope() -> HTTPError:
        """403 Forbidden — insufficient scope."""
        return mock_http_error(
            403,
            "Forbidden",
            '{"message": "Resource not accessible by integration"}',
        )

    @staticmethod
    def resource_not_found() -> HTTPError:
        """404 Not Found."""
        return mock_http_error(
            404,
            "Not Found",
            '{"message": "Not Found"}',
        )

    @staticmethod
    def conflict() -> HTTPError:
        """409 Conflict — concurrent modification."""
        return mock_http_error(
            409,
            "Conflict",
            '{"message": "Resource conflict"}',
        )

    @staticmethod
    def unprocessable_entity() -> HTTPError:
        """422 Unprocessable Entity."""
        return mock_http_error(
            422,
            "Unprocessable Entity",
            '{"message": "Validation Failed"}',
        )

    @staticmethod
    def rate_limited() -> HTTPError:
        """429 Too Many Requests."""
        return mock_http_error(
            429,
            "Too Many Requests",
            '{"message": "API rate limit exceeded"}',
        )


@pytest.fixture
def api_errors():
    """Return API error scenario builder."""
    return APIErrorScenarios


# ─────────────────────────────────────────────────────────────────────────────
# Audit Trail Utilities
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def audit_log_path() -> str:
    """Return path to audit log for this test session."""
    return ".codex/test_audit_trail.jsonl"


def log_api_call(
    path: str,
    method: str,
    status: int,
    scope: str,
    timestamp: Optional[str] = None,
) -> dict[str, Any]:
    """Generate an API call audit entry."""
    if timestamp is None:
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "timestamp": timestamp,
        "method": method,
        "endpoint": path,
        "status": status,
        "scope": scope,
    }


@pytest.fixture
def audit_logger(audit_log_path: str):
    """Return function to log API calls to audit trail."""

    def _log(entry: dict[str, Any]):
        import pathlib
        pathlib.Path(audit_log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(audit_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    return _log
