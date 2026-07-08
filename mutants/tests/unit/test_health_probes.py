"""Tests for monitoring health probe endpoints (liveness and readiness).

Covers:
  - /liveness — always returns 200 with uptime and status fields
  - /readiness — returns 200 when deps OK, 503 when not
  - /health — legacy endpoint backward-compatibility
  - Root endpoint lists readiness/liveness in the endpoints dict
"""

from __future__ import annotations

from pathlib import Path
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

pytestmark = pytest.mark.skipif(not _FASTAPI_AVAILABLE, reason="fastapi[testclient] not installed")


@pytest.fixture(scope="module")
def client():
    import tempfile

    import monitoring.dashboard_api as _da  # type: ignore[import]

    # Import inside fixture so the skip above works cleanly

    # Patch Path so /readiness never touches the repo working directory
    with tempfile.TemporaryDirectory() as _tmp:
        _tmpdir = Path(_tmp)
        patcher = patch.object(_da, "Path", return_value=_tmpdir)
        patcher.start()
        try:
            yield TestClient(_da.app)
        finally:
            patcher.stop()


# ---------------------------------------------------------------------------
# /liveness
# ---------------------------------------------------------------------------


class TestLivenessProbe:
    def test_returns_200(self, client):
        resp = client.get("/liveness")
        assert resp.status_code == 200, "status_code is not valid"

    def test_status_alive(self, client):
        data = client.get("/liveness").json()
        assert data["status"] == "alive", "Data must not be empty"

    def test_has_uptime(self, client):
        data = client.get("/liveness").json()
        assert "uptime_seconds" in data, "Data must not be empty"
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0, "Value must be greater than zero"

    def test_has_timestamp(self, client):
        data = client.get("/liveness").json()
        assert "timestamp" in data, "Data must not be empty"


# ---------------------------------------------------------------------------
# /readiness
# ---------------------------------------------------------------------------


class TestReadinessProbe:
    def test_returns_200_when_ready(self, client, tmp_path):
        from monitoring import dashboard_api as da  # type: ignore[import]

        with patch.object(da, "Path", return_value=tmp_path):
            resp = client.get("/readiness")
        assert resp.status_code == 200, "status_code is not valid"

    def test_status_field_present(self, client):
        data = client.get("/readiness").json()
        assert data["status"] in ("ready", "not_ready")

    def test_checks_dict_present(self, client):
        data = client.get("/readiness").json()
        assert "checks" in data, "Data must not be empty"
        assert isinstance(data["checks"], dict)

    def test_has_timestamp(self, client):
        data = client.get("/readiness").json()
        assert "timestamp" in data, "Data must not be empty"

    def test_returns_503_when_mkdir_fails(self, client):
        from monitoring import dashboard_api as _da  # type: ignore[import]

        class _FailPath:
            """Fake Path that raises OSError on mkdir."""

            def mkdir(self, **kwargs):
                raise OSError("disk full")

        with patch.object(_da, "Path", return_value=_FailPath()):
            resp = client.get("/readiness")
        assert resp.status_code == 503, "status_code is not valid"
        data = resp.json()
        assert data["status"] == "not_ready", "Data must not be empty"
        assert "metrics_dir" in data["checks"], "Data must not be empty"


# ---------------------------------------------------------------------------
# /health (legacy)
# ---------------------------------------------------------------------------


class TestLegacyHealthEndpoint:
    def test_returns_200(self, client):
        assert client.get("/health").status_code == 200, "status_code is not valid"

    def test_status_healthy(self, client):
        assert client.get("/health").json()["status"] == "healthy", "Condition must be true"

    def test_has_timestamp(self, client):
        assert "timestamp" in client.get("/health").json(), "Condition must be true"


# ---------------------------------------------------------------------------
# Root endpoint — endpoint catalog
# ---------------------------------------------------------------------------


class TestRootEndpoint:
    def test_lists_readiness(self, client):
        data = client.get("/").json()
        assert "readiness" in data["endpoints"], "Data must not be empty"
        assert data["endpoints"]["readiness"] == "/readiness", "Data must not be empty"

    def test_lists_liveness(self, client):
        data = client.get("/").json()
        assert "liveness" in data["endpoints"], "Data must not be empty"
        assert data["endpoints"]["liveness"] == "/liveness", "Data must not be empty"
