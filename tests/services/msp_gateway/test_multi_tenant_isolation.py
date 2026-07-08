"""
Integration tests for multi-tenant isolation.

Verifies that data and resources from different tenants are properly isolated,
with no cross-tenant access or data leakage.
"""

from __future__ import annotations

import json

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("pydantic_settings")

from fastapi import FastAPI, Request
from fastapi.testclient import (
    TestClient,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)

# pragma: allowlist secret # pragma: allowlist secret
from services.msp_gateway.middleware import RateLimitMiddleware, TenantContextMiddleware
from services.msp_gateway.middleware import tenant_context as tc_module
from services.msp_gateway.middleware.tenant_context import TenantRegistry


def test_multi_tenant_isolation_data_separation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that each tenant has isolated data stores."""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TenantContextMiddleware)

    # Simulated per-tenant data store
    tenant_data = {}

    @app.post("/v1/store")
    async def store_data(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return {"error": "no tenant"}, 401

        body = await request.json()
        tenant_id = tenant["tenant_id"]

        # Isolate storage by tenant_id
        if tenant_id not in tenant_data:
            tenant_data[tenant_id] = []

        tenant_data[tenant_id].append(body.get("item"))
        return {"stored": True, "tenant_id": tenant_id}

    @app.get("/v1/items")
    async def get_items(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return {"error": "no tenant"}, 401

        tenant_id = tenant["tenant_id"]
        items = tenant_data.get(tenant_id, [])
        return {"tenant_id": tenant_id, "items": items, "count": len(items)}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("tenant-a", "A", "key-a")
    registry.create_tenant("tenant-b", "B", "key-b")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)
    monkeypatch.setattr(tc_module.settings, "rate_limit_enabled", False)

    with TestClient(app) as client:
        # Tenant A stores items
        client.post("/v1/store", json={"item": "a1"}, headers={"Authorization": "******"})
        client.post("/v1/store", json={"item": "a2"}, headers={"Authorization": "******"})

        # Tenant B stores items
        client.post("/v1/store", json={"item": "b1"}, headers={"Authorization": "******"})

        # Tenant A retrieves items
        resp_a = client.get("/v1/items", headers={"Authorization": "******"})

        # Tenant B retrieves items
        resp_b = client.get("/v1/items", headers={"Authorization": "******"})

    assert resp_a.json()["count"] == 2, "Tenant A must see only its items"
    assert "a1" in resp_a.json()["items"], "Tenant A item a1 must be present"
    assert "a2" in resp_a.json()["items"], "Tenant A item a2 must be present"
    assert "b1" not in resp_a.json()["items"], "Tenant A must not see Tenant B items"

    assert resp_b.json()["count"] == 1, "Tenant B must see only its items"
    assert "b1" in resp_b.json()["items"], "Tenant B item b1 must be present"
    assert "a1" not in resp_b.json()["items"], "Tenant B must not see Tenant A items"


def test_multi_tenant_isolation_cross_tenant_access_denied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenants cannot access other tenants' resources."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/resource/{resource_tenant_id}")
    async def get_resource(request: Request, resource_tenant_id: str):
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return {"error": "no tenant"}, 401

        # Enforce tenant isolation: only access own resources
        if tenant["tenant_id"] != resource_tenant_id:
            return {"error": "forbidden"}, 403

        return {
            "requester": tenant["tenant_id"],
            "resource": resource_tenant_id,
            "data": "sensitive",
        }

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("tenant-1", "1", "key-1")
    registry.create_tenant("tenant-2", "2", "key-2")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        # Tenant 1 accesses own resource
        own_resp = client.get(
            "/v1/resource/tenant-1",
            headers={"Authorization": "******"},
        )

        # Tenant 1 attempts to access Tenant 2 resource
        cross_resp = client.get(
            "/v1/resource/tenant-2",
            headers={"Authorization": "******"},
        )

    assert own_resp.status_code == 200, "Tenant must access own resource"
    assert cross_resp.status_code == 403, "Tenant must not access other tenant resource"


def test_multi_tenant_isolation_per_tenant_rate_limits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that rate limits are enforced independently per tenant."""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/limited")
    async def limited(request: Request):
        return {"status": "ok"}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant(
        "tenant-rate-a",
        "A",
        "key-rate-a",
        quota={"requests_per_minute": 2},
    )
    registry.create_tenant(
        "tenant-rate-b",
        "B",
        "key-rate-b",
        quota={"requests_per_minute": 3},
    )

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)
    monkeypatch.setattr(tc_module.settings, "rate_limit_enabled", True)
    monkeypatch.setattr(tc_module.settings, "rate_limit_requests_per_minute", 2)

    with TestClient(app) as client:
        # Tenant A makes requests up to its limit
        a1 = client.get("/v1/limited", headers={"Authorization": "******"})
        a2 = client.get("/v1/limited", headers={"Authorization": "******"})
        a3 = client.get("/v1/limited", headers={"Authorization": "******"})

        # Tenant B can still make requests (independent quota)
        b1 = client.get("/v1/limited", headers={"Authorization": "******"})
        b2 = client.get("/v1/limited", headers={"Authorization": "******"})

    assert a1.status_code == 200, "Tenant A first request succeeds"
    assert a2.status_code == 200, "Tenant A second request succeeds"
    assert a3.status_code == 429, "Tenant A third request hits rate limit"
    assert b1.status_code == 200, "Tenant B first request succeeds"
    assert b2.status_code == 200, "Tenant B second request succeeds"


def test_multi_tenant_isolation_tenant_metadata_isolation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant metadata is isolated and not accessible across tenants."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/tenant/info")
    async def tenant_info(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return {"error": "no tenant"}, 401

        return {
            "tenant_id": tenant["tenant_id"],
            "name": tenant.get("name"),
            "metadata": tenant.get("metadata", {}),
            "quota": tenant.get("quota", {}),
        }

    registry = TenantRegistry(backend="memory")
    registry.create_tenant(
        "secure-tenant",
        "Secure",
        "key-secure",
        metadata={"api_key": "secret-123", "internal_id": "xyz"},
        quota={"requests_per_minute": 100},
    )
    registry.create_tenant(
        "other-tenant",
        "Other",
        "key-other",
        metadata={"api_key": "secret-456"},
        quota={"requests_per_minute": 50},
    )

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        # Each tenant retrieves its own info
        secure_resp = client.get(
            "/v1/tenant/info",
            headers={"Authorization": "******"},
        )
        other_resp = client.get(
            "/v1/tenant/info",
            headers={"Authorization": "******"},
        )

    secure_data = secure_resp.json()
    other_data = other_resp.json()

    assert secure_data["tenant_id"] == "secure-tenant", "Condition must be true"
    assert secure_data["quota"]["requests_per_minute"] == 100, "Condition must be true"
    assert secure_data["metadata"]["api_key"] == "secret-123", "Condition must be true"

    assert other_data["tenant_id"] == "other-tenant", "Condition must be true"
    assert other_data["quota"]["requests_per_minute"] == 50, "Condition must be true"
    assert other_data["metadata"]["api_key"] == "secret-456", "Condition must be true"

    # Metadata must not leak
    assert "secret-123" not in json.dumps(other_data), "Secure metadata must not leak"
    assert "secret-456" not in json.dumps(secure_data), "Other metadata must not leak"


def test_multi_tenant_isolation_concurrent_requests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that concurrent requests from different tenants maintain isolation."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    request_log = []

    @app.post("/v1/process")
    async def process(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return {"error": "no tenant"}, 401

        body = await request.json()
        tenant_id = tenant["tenant_id"]

        # Log the request
        request_log.append({
            "tenant_id": tenant_id,
            "item": body.get("item"),
        })

        return {"processed": True, "tenant_id": tenant_id, "item": body.get("item")}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("tenant-x", "X", "key-x")
    registry.create_tenant("tenant-y", "Y", "key-y")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        # Simulate interleaved requests from different tenants
        client.post("/v1/process", json={"item": "x1"}, headers={"Authorization": "******"})
        client.post("/v1/process", json={"item": "y1"}, headers={"Authorization": "******"})
        client.post("/v1/process", json={"item": "x2"}, headers={"Authorization": "******"})
        client.post("/v1/process", json={"item": "y2"}, headers={"Authorization": "******"})

    # Verify each request was processed with correct tenant context
    assert len(request_log) == 4, "All requests must be processed"
    assert request_log[0]["tenant_id"] == "tenant-x", "Condition must be true"
    assert request_log[1]["tenant_id"] == "tenant-y", "Condition must be true"
    assert request_log[2]["tenant_id"] == "tenant-x", "Condition must be true"
    assert request_log[3]["tenant_id"] == "tenant-y", "Condition must be true"


def test_multi_tenant_isolation_tenant_activation_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that inactive tenants are completely blocked from access."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/service")
    async def service(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return {"error": "no tenant"}, 401
        return {"status": "service active", "tenant_id": tenant["tenant_id"]}

    registry = TenantRegistry(backend="memory")
    active = registry.create_tenant("tenant-active", "Active", "key-active")
    inactive = registry.create_tenant("tenant-inactive", "Inactive", "key-inactive")

    # Deactivate one tenant
    registry.update_tenant("tenant-inactive", active=False)

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        # Active tenant can access
        active_resp = client.get(
            "/v1/service",
            headers={"Authorization": "******"},
        )

        # Inactive tenant is blocked
        inactive_resp = client.get(
            "/v1/service",
            headers={"Authorization": "******"},
        )

    assert active_resp.status_code == 200, "Active tenant must access service"
    assert inactive_resp.status_code == 403, "Inactive tenant must be blocked"


def test_multi_tenant_isolation_policies_per_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant policies are isolated and not shared."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/policies")
    async def get_policies(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return {"error": "no tenant"}, 401

        return {
            "tenant_id": tenant["tenant_id"],
            "policies": tenant.get("policies", []),
        }

    registry = TenantRegistry(backend="memory")
    registry.create_tenant(
        "tenant-restricted",
        "Restricted",
        "key-restricted",
        policies=[
            "policy-no-export",
            "policy-no-redaction",
        ],
    )
    registry.create_tenant(
        "tenant-open",
        "Open",
        "key-open",
        policies=[],
    )

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        restricted_resp = client.get(
            "/v1/policies",
            headers={"Authorization": "******"},
        )
        open_resp = client.get(
            "/v1/policies",
            headers={"Authorization": "******"},
        )

    restricted_policies = restricted_resp.json()["policies"]
    open_policies = open_resp.json()["policies"]

    assert len(restricted_policies) == 2, "Restricted tenant must have policies"
    assert "policy-no-export" in restricted_policies, "Condition must be true"
    assert len(open_policies) == 0, "Open tenant must have no policies"
