"""Shared fixtures for Cognitive App Phase 2 test suite."""

from __future__ import annotations

import asyncio
import json
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ──────────────────────────────────────────────────────────────────────────────
# Database Fixtures  # pragma: allowlist secret  # pragma: allowlist secret
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def in_memory_db() -> Generator[sqlite3.Connection, None, None]:
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create decision table
    cursor.execute(
        """
        CREATE TABLE decisions (
            decision_id TEXT PRIMARY KEY,
            lane TEXT NOT NULL,
            candidate TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            k1_factor REAL NOT NULL,
            coherence_metric REAL NOT NULL,
            superposition_state TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT DEFAULT 'submitted',
            feedback TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    # Create memory patterns table
    cursor.execute(
        """
        CREATE TABLE patterns (
            pattern_id TEXT PRIMARY KEY,
            pattern_name TEXT NOT NULL,
            lane TEXT NOT NULL,
            description TEXT NOT NULL,
            confidence REAL NOT NULL,
            usage_count INTEGER NOT NULL,
            tags TEXT,
            compressed_size_bytes INTEGER,
            compression_ratio REAL,
            stored_timestamp TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # Create STM table
    cursor.execute(
        """
        CREATE TABLE stm (
            stm_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            context TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # Create workflow table
    cursor.execute(
        """
        CREATE TABLE workflows (
            workflow_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            last_run TEXT,
            run_count_7d INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            created_at TEXT NOT NULL
        )
        """
    )

    # Create rate limit table
    cursor.execute(
        """
        CREATE TABLE rate_limits (
            id INTEGER PRIMARY KEY,
            limit_value INTEGER NOT NULL,
            remaining INTEGER NOT NULL,
            used INTEGER NOT NULL,
            reset_time TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
    yield conn
    conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# Request/Response Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def valid_decision_payload() -> dict[str, Any]:
    """Valid decision submission payload."""
    return {
        "lane": "security",
        "candidate": "Fix CVE-2026-XXXXX in src/auth/token_handler.py",
        "confidence_score": 0.92,
        "k1_factor": 0.28,
        "coherence_metric": 0.87,
        "superposition_state": ["APPROVED", "NEEDS_REVIEW"],
    }


@pytest.fixture
def valid_pattern_payload() -> dict[str, Any]:
    """Valid memory pattern storage payload."""
    return {
        "pattern_name": "security-patterns-v1",
        "lane": "security",
        "description": "Successfully fixed CVE-2026-XXXXX using token rotation mechanism",
        "confidence": 0.88,
        "usage_count": 1,
        "tags": ["security", "token-rotation", "cve-fix"],
    }


@pytest.fixture
def valid_stm_payload() -> dict[str, Any]:
    """Valid STM push payload."""
    return {
        "content": "Current campaign: Phase 15. Lane security objective: Fix 8+ vulns.",
        "context": "orchestrator",
        "lifetime_seconds": 3600,
    }


@pytest.fixture
def valid_gate_payload() -> dict[str, Any]:
    """Valid WEC gate check payload."""
    return {
        "pr_number": 1234,
        "required_checks": [
            "auto-approve-workflows",
            "agent-auth-delegation",
            "pre-release-validation",
        ],
        "action": "check",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Authentication & Authorization Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def valid_auth_header() -> dict[str, str]:
    """Valid authorization header."""
    return {"Authorization": "******"}


@pytest.fixture
def invalid_auth_header() -> dict[str, str]:
    """Invalid authorization header."""
    return {"Authorization": "******"}


@pytest.fixture
def hmac_secret() -> str:
    """HMAC secret for webhook verification."""
    return "test_webhook_secret_key_12345"


@pytest.fixture
def github_webhook_payload() -> str:
    """Sample GitHub webhook payload."""
    return json.dumps(
        {
            "action": "opened",
            "pull_request": {
                "number": 1234,
                "title": "Test PR",
                "body": "Test PR body",
                "head": {"sha": "abc123def456"},
            },
        }
    )


def _compute_hmac_signature(payload: str, secret: str) -> str:
    """Compute HMAC-SHA256 signature for webhook verification."""
    import hashlib
    import hmac

    return "sha256=" + hmac.new(
        secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()


@pytest.fixture
def valid_webhook_signature(github_webhook_payload: str, hmac_secret: str) -> str:
    """Valid HMAC signature for webhook."""
    return _compute_hmac_signature(github_webhook_payload, hmac_secret)


@pytest.fixture
def invalid_webhook_signature() -> str:
    """Invalid HMAC signature."""
    return "sha256=invalid_signature_1234567890abcdef"


# ──────────────────────────────────────────────────────────────────────────────
# Mock API Response Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_github_api():
    """Mock GitHub API responses."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total_count": 100,
            "workflows": [
                {
                    "id": 1,
                    "name": "pre-release-validation",
                    "conclusion": "success",
                    "status": "completed",
                }
            ],
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_otel_spans():
    """Mock OpenTelemetry spans."""
    with patch("opentelemetry.trace.get_tracer") as mock_tracer:
        mock_span = MagicMock()
        mock_tracer.return_value.start_as_current_span.return_value.__enter__ = (
            MagicMock(return_value=mock_span)
        )
        mock_tracer.return_value.start_as_current_span.return_value.__exit__ = (
            MagicMock(return_value=None)
        )
        yield mock_tracer


# ──────────────────────────────────────────────────────────────────────────────
# Time & Timestamp Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def now_iso() -> str:
    """Current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


@pytest.fixture
def one_hour_ago() -> str:
    """One hour ago in ISO format."""
    return (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()


@pytest.fixture
def one_day_ago() -> str:
    """One day ago in ISO format."""
    return (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()


# ──────────────────────────────────────────────────────────────────────────────
# Test Data Generators
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def generate_decision_ids():
    """Generate unique decision IDs."""
    counter = 0

    def _generate(lane: str = "security") -> str:
        nonlocal counter
        counter += 1
        return f"dec_{lane}_{counter:08d}_{int(time.time())}"

    return _generate


@pytest.fixture
def generate_pattern_ids():
    """Generate unique pattern IDs."""
    counter = 0

    def _generate(lane: str = "security") -> str:
        nonlocal counter
        counter += 1
        return f"pat_{lane}_{counter:08d}_{int(time.time())}"

    return _generate


@pytest.fixture
def generate_stm_ids():
    """Generate unique STM IDs."""
    counter = 0

    def _generate() -> str:
        nonlocal counter
        counter += 1
        return f"stm_{counter:08d}_{int(time.time())}"

    return _generate


# ──────────────────────────────────────────────────────────────────────────────
# Performance Testing Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def timer():
    """Simple timer for performance measurements."""
    class Timer:
        def __init__(self):
            self.start_time = 0
            self.elapsed_ms = 0

        def __enter__(self):
            self.start_time = time.perf_counter()
            return self

        def __exit__(self, *args):
            self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        @property
        def ms(self) -> float:
            return self.elapsed_ms

    return Timer()


# ──────────────────────────────────────────────────────────────────────────────
# Async Test Helpers
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    """Create an async test client (placeholder)."""
    yield AsyncMock()


# ──────────────────────────────────────────────────────────────────────────────
# Markers & Parametrization Helpers
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def all_lanes() -> list[str]:
    """All valid lane names."""
    return ["security", "coverage", "stability", "complexity", "docs"]


@pytest.fixture
def all_statuses() -> list[str]:
    """All valid decision statuses."""
    return ["submitted", "approved", "rejected", "in_progress", "completed"]


@pytest.fixture
def all_decision_endpoints() -> list[str]:
    """All decision endpoints for parametrization."""
    return [
        "/api/decisions/submit",
        "/api/decisions/{decision_id}",
        "/api/decisions/recent",
        "/api/decisions/history",
    ]


@pytest.fixture
def all_memory_endpoints() -> list[str]:
    """All memory endpoints for parametrization."""
    return [
        "/api/memory/store",
        "/api/memory/retrieve/{pattern_name}",
        "/api/memory/stm/push",
        "/api/memory/stats",
    ]


@pytest.fixture
def all_workflow_endpoints() -> list[str]:
    """All workflow endpoints for parametrization."""
    return [
        "/api/workflows/status",
        "/api/workflows/gate",
        "/api/workflows/rate-limit",
    ]
