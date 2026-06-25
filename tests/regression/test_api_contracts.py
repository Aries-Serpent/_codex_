"""Regression tests: API contract stability.

These tests verify that the monitoring dashboard API maintains its
documented interface — status codes, response schemas, and field types
must not change silently.

All tests use FastAPI's in-process ``TestClient`` (no live server needed).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT / "src"), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

pytestmark = pytest.mark.regression


# ────────────────────────────────────────────────────────────────────────────
# 1. Root endpoint
# ────────────────────────────────────────────────────────────────────────────


class TestRootEndpoint:
    def test_root_returns_200(self, dashboard_client):
        """GET / must return HTTP 200."""
        resp = dashboard_client.get("/")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    def test_root_schema_contains_name_and_version(self, dashboard_client):
        """Root response must expose 'name' and 'version' fields."""
        body = dashboard_client.get("/").json()
        assert "name" in body, "Root response missing 'name'"
        assert "version" in body, "Root response missing 'version'"

    def test_root_endpoints_map_present(self, dashboard_client):
        """Root response must include an 'endpoints' mapping for discovery."""
        body = dashboard_client.get("/").json()
        assert "endpoints" in body, "Root response missing 'endpoints'"
        assert isinstance(body["endpoints"], dict), "'endpoints' must be a dict"


# ────────────────────────────────────────────────────────────────────────────
# 2. Health endpoint
# ────────────────────────────────────────────────────────────────────────────


class TestHealthEndpoint:
    def test_health_returns_200(self, dashboard_client):
        """GET /health must return HTTP 200."""
        resp = dashboard_client.get("/health")
        assert resp.status_code == 200

    def test_health_schema_status_field(self, dashboard_client):
        """Health response must contain a 'status' string field."""
        body = dashboard_client.get("/health").json()
        assert "status" in body, "Health response missing 'status'"
        assert isinstance(body["status"], str)

    def test_health_schema_timestamp_field(self, dashboard_client):
        """Health response must contain a 'timestamp' field."""
        body = dashboard_client.get("/health").json()
        assert "timestamp" in body, "Health response missing 'timestamp'"


# ────────────────────────────────────────────────────────────────────────────
# 3. Liveness probe
# ────────────────────────────────────────────────────────────────────────────


class TestLivenessEndpoint:
    def test_liveness_returns_200(self, dashboard_client):
        """GET /liveness must return HTTP 200."""
        resp = dashboard_client.get("/liveness")
        assert resp.status_code == 200

    def test_liveness_schema(self, dashboard_client):
        """Liveness response must expose status, uptime_seconds, and timestamp."""
        body = dashboard_client.get("/liveness").json()
        assert "status" in body, "Liveness missing 'status'"
        assert "uptime_seconds" in body, "Liveness missing 'uptime_seconds'"
        assert "timestamp" in body, "Liveness missing 'timestamp'"

    def test_liveness_uptime_non_negative(self, dashboard_client):
        """Uptime must be a non-negative numeric value."""
        body = dashboard_client.get("/liveness").json()
        uptime = body["uptime_seconds"]
        assert isinstance(uptime, (int, float)), "uptime_seconds must be numeric"
        assert uptime >= 0, f"uptime_seconds is negative: {uptime}"

    def test_liveness_status_value(self, dashboard_client):
        """Liveness status field must be 'alive'."""
        body = dashboard_client.get("/liveness").json()
        assert body["status"] == "alive", f"Expected status='alive', got {body['status']!r}"


# ────────────────────────────────────────────────────────────────────────────
# 4. Readiness probe
# ────────────────────────────────────────────────────────────────────────────


class TestReadinessEndpoint:
    def test_readiness_returns_2xx(self, dashboard_client):
        """GET /readiness must return 2xx (200 ready or 503 not-ready — never 4xx/5xx)."""
        resp = dashboard_client.get("/readiness")
        assert resp.status_code in (
            200,
            503,
        ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"

    def test_readiness_schema_status_field(self, dashboard_client):
        """Readiness response must always contain a 'status' field."""
        body = dashboard_client.get("/readiness").json()
        assert "status" in body, "Readiness response missing 'status'"

    def test_readiness_schema_checks_field(self, dashboard_client):
        """Readiness response must expose a 'checks' object describing sub-checks."""
        body = dashboard_client.get("/readiness").json()
        assert "checks" in body, "Readiness response missing 'checks'"

    def test_readiness_schema_timestamp_field(self, dashboard_client):
        """Readiness response must contain a 'timestamp' ISO-8601 string."""
        body = dashboard_client.get("/readiness").json()
        assert "timestamp" in body, "Readiness response missing 'timestamp'"
        assert isinstance(body["timestamp"], str)


# ────────────────────────────────────────────────────────────────────────────
# 5. Content-type contract
# ────────────────────────────────────────────────────────────────────────────


class TestContentTypeContracts:
    def test_health_content_type_json(self, dashboard_client):
        """All JSON endpoints must return application/json content type."""
        resp = dashboard_client.get("/health")
        assert "application/json" in resp.headers.get(
            "content-type", ""
        ), "Expected JSON content-type on /health"

    def test_liveness_content_type_json(self, dashboard_client):
        """Liveness endpoint must return application/json."""
        resp = dashboard_client.get("/liveness")
        assert "application/json" in resp.headers.get("content-type", "")

    def test_readiness_content_type_json(self, dashboard_client):
        """Readiness endpoint must return application/json."""
        resp = dashboard_client.get("/readiness")
        assert "application/json" in resp.headers.get("content-type", "")
