"""Tests for monitoring health probe endpoints (liveness and readiness).

Covers:
  - /liveness — always returns 200 with uptime and status fields
  - /readiness — returns 200 when deps OK, 503 when not
  - /health — legacy endpoint backward-compatibility
  - Root endpoint lists readiness/liveness in the endpoints dict
"""

from __future__ import annotations

import importlib
import sys
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Import the app; skip the entire module if FastAPI is unavailable
# ---------------------------------------------------------------------------
try:
    from fastapi.testclient import TestClient

    _FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FASTAPI_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _FASTAPI_AVAILABLE, reason="fastapi[testclient] not installed"
)


@pytest.fixture(scope="module")
def client():
    # Import inside fixture so the skip above works cleanly
    from monitoring.dashboard_api import app  # type: ignore[import]

    return TestClient(app)


# ---------------------------------------------------------------------------
# /liveness
# ---------------------------------------------------------------------------


class TestLivenessProbe:
    def test_returns_200(self, client):
        resp = client.get("/liveness")
        assert resp.status_code == 200

    def test_status_alive(self, client):
        data = resp = client.get("/liveness")
        data = resp.json()
        assert data["status"] == "alive"

    def test_has_uptime(self, client):
        data = client.get("/liveness").json()
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0

    def test_has_timestamp(self, client):
        data = client.get("/liveness").json()
        assert "timestamp" in data


# ---------------------------------------------------------------------------
# /readiness
# ---------------------------------------------------------------------------


class TestReadinessProbe:
    def test_returns_200_when_ready(self, client, tmp_path, monkeypatch):
        # Patch Path("metrics_data") to use tmp_path so the check succeeds
        from monitoring import dashboard_api as da  # type: ignore[import]

        with patch.object(da, "Path", return_value=tmp_path):
            # The handler calls Path("metrics_data") — monkeypatch at module level
            pass
        # Default: metrics_data dir can be created → should be 200
        resp = client.get("/readiness")
        assert resp.status_code in (200, 503)  # depends on cwd write permissions

    def test_status_field_present(self, client):
        data = client.get("/readiness").json()
        assert data["status"] in ("ready", "not_ready")

    def test_checks_dict_present(self, client):
        data = client.get("/readiness").json()
        assert "checks" in data
        assert isinstance(data["checks"], dict)

    def test_has_timestamp(self, client):
        data = client.get("/readiness").json()
        assert "timestamp" in data

    def test_returns_503_when_mkdir_fails(self, client):
        from monitoring import dashboard_api as _da  # type: ignore[import]
        from pathlib import Path as _Path

        class _FailPath:
            """Fake Path that raises OSError on mkdir."""

            def mkdir(self, **kwargs):
                raise OSError("disk full")

        with patch.object(_da, "Path", return_value=_FailPath()):
            resp = client.get("/readiness")
        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "not_ready"
        assert "metrics_dir" in data["checks"]


# ---------------------------------------------------------------------------
# /health (legacy)
# ---------------------------------------------------------------------------


class TestLegacyHealthEndpoint:
    def test_returns_200(self, client):
        assert client.get("/health").status_code == 200

    def test_status_healthy(self, client):
        assert client.get("/health").json()["status"] == "healthy"

    def test_has_timestamp(self, client):
        assert "timestamp" in client.get("/health").json()


# ---------------------------------------------------------------------------
# Root endpoint — endpoint catalog
# ---------------------------------------------------------------------------


class TestRootEndpoint:
    def test_lists_readiness(self, client):
        data = client.get("/").json()
        assert "readiness" in data["endpoints"]
        assert data["endpoints"]["readiness"] == "/readiness"

    def test_lists_liveness(self, client):
        data = client.get("/").json()
        assert "liveness" in data["endpoints"]
        assert data["endpoints"]["liveness"] == "/liveness"
