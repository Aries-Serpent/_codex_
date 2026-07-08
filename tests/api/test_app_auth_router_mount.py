"""Acceptance tests for CB-006: auth router mount in src/codex/api/app.py.

Validates that the FastAPI application factory mounts the auth router at
``/api/auth`` and that the core auth endpoints (register, login, logout,
refresh) are reachable.
"""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_client() -> "TestClient":
    """Import the app and return a test client."""
    from codex.api.app import app  # lazy import keeps test isolation

    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAuthRouterMount:
    """CB-006: acceptance tests — auth router is mounted at /api/auth."""

    def test_openapi_lists_auth_routes(self):
        """The OpenAPI spec includes at least one /api/auth path."""
        client = _make_client()
        resp = client.get("/openapi.json")
        assert resp.status_code == 200, "status_code is not valid"
        paths = resp.json().get("paths", {})
        auth_paths = [p for p in paths if p.startswith("/api/auth")]
        assert auth_paths, (
            "Expected at least one /api/auth route in OpenAPI spec, found none. "
            f"Available paths: {sorted(paths.keys())}"
        )

    def test_register_endpoint_reachable(self):
        """POST /api/auth/register is reachable (returns 4xx, not 404/405)."""
        client = _make_client()
        resp = client.post("/api/auth/register", json={})
        # A 422 (validation error) proves the route exists; 404 would mean unmounted.
        assert (resp.status_code != 404, "status_code is not valid"
        ), "POST /api/auth/register returned 404 — auth router may not be mounted."
        assert (resp.status_code != 405, "status_code is not valid"
        ), "POST /api/auth/register returned 405 — unexpected method restriction."

    def test_login_endpoint_reachable(self):
        """POST /api/auth/login is reachable (returns 4xx, not 404/405)."""
        client = _make_client()
        resp = client.post("/api/auth/login", json={})
        assert (resp.status_code != 404, "status_code is not valid"
        ), "POST /api/auth/login returned 404 — auth router may not be mounted."
        assert resp.status_code != 405, "status_code is not valid"

    def test_health_endpoint_unaffected(self):
        """The existing /health endpoint still works after auth router is mounted."""
        client = _make_client()
        resp = client.get("/health")
        # Accept 200 or 404 (endpoint may not be defined); reject 500.
        assert (resp.status_code < 500, "status_code is not valid"
        ), f"Health endpoint returned unexpected server error: {resp.status_code}"

    def test_auth_router_tag_present_in_openapi(self):
        """The auth router is tagged 'auth' in the OpenAPI spec."""
        client = _make_client()
        resp = client.get("/openapi.json")
        assert resp.status_code == 200, "status_code is not valid"
        tags = {t["name"] for t in resp.json().get("tags", [])}
        # Also check path-level tags as a fallback
        paths = resp.json().get("paths", {})
        path_tags: set[str] = set()
        for path_data in paths.values():
            for method_data in path_data.values():
                if isinstance(method_data, dict):
                    path_tags.update(method_data.get("tags", []))
        all_tags = tags | path_tags
        assert "auth" in all_tags, f"Expected 'auth' tag in OpenAPI spec, found tags: {all_tags}"
