"""
Integration tests for MSP Gateway tenant routing.

Verifies that tenant context is correctly resolved from API keys and routed
through the request lifecycle, ensuring proper tenant isolation in endpoints.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("pydantic_settings")

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from services.msp_gateway.middleware import TenantContextMiddleware
from services.msp_gateway.middleware import tenant_context as tc_module
from services.msp_gateway.middleware.tenant_context import TenantRegistry


def test_tenant_routing_single_endpoint_different_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that different API keys route to different tenants on same endpoint."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/resource")
    async def get_resource(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if tenant:
            return {"tenant_id": tenant["tenant_id"], "endpoint": "get_resource"}
        return {"error": "no tenant"}

    # Create registry with two tenants
    registry = TenantRegistry(backend="memory")
    tenant_a = registry.create_tenant("tenant-a", "Tenant A", "key-a")
    tenant_b = registry.create_tenant("tenant-b", "Tenant B", "key-b")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        # Request with tenant-a key
        response_a = client.get(
            "/v1/resource",
            headers={"Authorization": "******"},
        )
        # Request with tenant-b key
        response_b = client.get(
            "/v1/resource",
            headers={"Authorization": "******"},
        )

    assert response_a.status_code == 200, "Tenant A request must succeed"
    assert response_b.status_code == 200, "Tenant B request must succeed"
    assert response_a.json()["tenant_id"] == "tenant-a", "Tenant A must be routed correctly"
    assert response_b.json()["tenant_id"] == "tenant-b", "Tenant B must be routed correctly"


def test_tenant_routing_multiple_endpoints_same_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that same tenant accesses multiple endpoints with one key."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/resource")
    async def get_resource(request: Request):
        tenant = getattr(request.state, "tenant", None)
        return {"tenant_id": tenant["tenant_id"] if tenant else None, "endpoint": "resource"}

    @app.post("/v1/query")
    async def post_query(request: Request):
        tenant = getattr(request.state, "tenant", None)
        return {"tenant_id": tenant["tenant_id"] if tenant else None, "endpoint": "query"}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("tenant-shared", "Shared Tenant", "key-shared")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        resource_resp = client.get(
            "/v1/resource",
            headers={"Authorization": "******"},
        )
        query_resp = client.post(
            "/v1/query",
            headers={"Authorization": "******"},
        )

    assert resource_resp.status_code == 200, "Resource endpoint must be accessible"
    assert query_resp.status_code == 200, "Query endpoint must be accessible"
    assert resource_resp.json()["tenant_id"] == "tenant-shared", "Condition must be true"
    assert query_resp.json()["tenant_id"] == "tenant-shared", "Condition must be true"


def test_tenant_routing_invalid_key_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that invalid API keys are rejected and don't access endpoints."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/protected")
    async def protected(request: Request):
        tenant = getattr(request.state, "tenant", None)
        return {"tenant_id": tenant["tenant_id"] if tenant else None}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("tenant-valid", "Valid Tenant", "key-valid")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        # Valid key
        valid_resp = client.get(
            "/v1/protected",
            headers={"Authorization": "******"},
        )
        # Invalid key
        invalid_resp = client.get(
            "/v1/protected",
            headers={"Authorization": "******"},
        )
        # Missing key
        missing_resp = client.get("/v1/protected")

    assert valid_resp.status_code == 200, "Valid key must be accepted"
    assert invalid_resp.status_code == 401, "Invalid key must be rejected"
    assert missing_resp.status_code == 401, "Missing key must be rejected"


def test_tenant_routing_inactive_tenant_forbidden(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that inactive tenants cannot access endpoints."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/resource")
    async def resource(request: Request):
        tenant = getattr(request.state, "tenant", None)
        return {"tenant_id": tenant["tenant_id"] if tenant else None}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("tenant-active", "Active", "key-active")
    registry.create_tenant("tenant-inactive", "Inactive", "key-inactive")
    registry.deactivate_tenant("tenant-inactive")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        # Active tenant request
        active_resp = client.get(
            "/v1/resource",
            headers={"Authorization": "******"},
        )
        # Inactive tenant request
        inactive_resp = client.get(
            "/v1/resource",
            headers={"Authorization": "******"},
        )

    assert active_resp.status_code == 200, "Active tenant must be allowed"
    assert inactive_resp.status_code == 403, "Inactive tenant must be forbidden"


def test_tenant_routing_context_isolation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant context in request.state is properly isolated per request."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    captured_tenants = []

    @app.get("/v1/capture")
    async def capture(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if tenant:
            captured_tenants.append(tenant["tenant_id"])
        return {"captured": len(captured_tenants)}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("tenant-x", "X", "key-x")
    registry.create_tenant("tenant-y", "Y", "key-y")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        # Multiple requests from different tenants
        client.get("/v1/capture", headers={"Authorization": "******"})
        client.get("/v1/capture", headers={"Authorization": "******"})
        client.get("/v1/capture", headers={"Authorization": "******"})

    # Verify each request captured its own tenant ID
    assert len(captured_tenants) == 3, "All requests must be processed"
    assert captured_tenants == ["tenant-x", "tenant-y", "tenant-x"], "Condition must be true"


def test_tenant_routing_public_endpoints_no_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that public endpoints don't require tenant context."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/health")
    async def health(request: Request):
        tenant = getattr(request.state, "tenant", None)
        return {"status": "ok", "has_tenant": tenant is not None}

    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        # Access public endpoint without key
        response = client.get("/health")

    assert response.status_code == 200, "Health endpoint must be public"
    assert response.json()["has_tenant"] is False, "Public endpoint should have no tenant"


def test_tenant_routing_per_tenant_quotas(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant routing includes per-tenant quota information."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/quota")
    async def get_quota(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if tenant:
            return {
                "tenant_id": tenant["tenant_id"],
                "quota": tenant.get("quota", {}),
            }
        return {"error": "no tenant"}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant(
        "tenant-limited",
        "Limited",
        "key-limited",
        quota={"requests_per_minute": 10, "tokens_per_minute": 100},
    )
    registry.create_tenant(
        "tenant-unlimited",
        "Unlimited",
        "key-unlimited",
        quota={"requests_per_minute": 1000, "tokens_per_minute": 100000},
    )

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        limited_resp = client.get(
            "/v1/quota",
            headers={"Authorization": "******"},
        )
        unlimited_resp = client.get(
            "/v1/quota",
            headers={"Authorization": "******"},
        )

    assert limited_resp.json()["quota"]["requests_per_minute"] == 10, "Condition must be true"
    assert unlimited_resp.json()["quota"]["requests_per_minute"] == 1000, "Condition must be true"
