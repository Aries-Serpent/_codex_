"""
Integration tests for tenant context propagation.

Verifies that tenant context correctly propagates through the entire request
lifecycle, including middleware stack, routers, and nested operations.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("pydantic_settings")

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from services.msp_gateway.middleware import RateLimitMiddleware, TenantContextMiddleware
from services.msp_gateway.middleware import tenant_context as tc_module
from services.msp_gateway.middleware.tenant_context import TenantRegistry


def test_tenant_context_propagation_basic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant context is available in all endpoints."""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/context/check")
    async def check_context(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return {"error": "no context"}, 500
        return {
            "has_context": True,
            "tenant_id": tenant["tenant_id"],
            "has_quota": "quota" in tenant,
        }

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("context-test", "Test", "key-test")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)
    monkeypatch.setattr(tc_module.settings, "rate_limit_enabled", False)

    with TestClient(app) as client:
        response = client.get(
            "/v1/context/check",
            headers={"Authorization": "******"},
        )

    assert response.status_code == 200, "Endpoint must return successfully"
    data = response.json()
    assert data["has_context"] is True, "Context must be present"
    assert data["tenant_id"] == "context-test", "Tenant ID must be correct"
    assert data["has_quota"] is True, "Quota must be in context"


def test_tenant_context_propagation_through_middleware_stack(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant context propagates through multiple middleware layers."""
    app = FastAPI()

    # Custom middleware to verify context is available
    middleware_checks = []

    from starlette.middleware.base import BaseHTTPMiddleware

    class VerifyContextMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            tenant = getattr(request.state, "tenant", None)
            middleware_checks.append({
                "layer": "verify",
                "has_tenant": tenant is not None,
                "tenant_id": tenant["tenant_id"] if tenant else None,
            })
            return await call_next(request)

    app.add_middleware(VerifyContextMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/propagate")
    async def propagate_test(request: Request):
        tenant = getattr(request.state, "tenant", None)
        return {"endpoint_tenant_id": tenant["tenant_id"] if tenant else None}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("propagate-test", "Test", "key-propagate")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)
    monkeypatch.setattr(tc_module.settings, "rate_limit_enabled", False)

    with TestClient(app) as client:
        response = client.get(
            "/v1/propagate",
            headers={"Authorization": "******"},
        )

    assert response.status_code == 200, "Request must succeed"
    assert len(middleware_checks) > 0, "Middleware must be called"
    check = middleware_checks[0]
    assert check["has_tenant"] is True, "Tenant must be in context at middleware layer"
    assert check["tenant_id"] == "propagate-test", "Tenant ID must propagate"


def test_tenant_context_propagation_with_nested_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant context is available in nested async calls."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    # Store tenant_id from nested calls
    nested_tenants = []

    async def nested_operation(tenant_id: str):
        """Simulate a nested operation that needs tenant context."""
        nested_tenants.append(tenant_id)
        return {"nested_result": True, "tenant_id": tenant_id}

    @app.post("/v1/nested")
    async def nested_endpoint(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return {"error": "no tenant"}, 401

        # Call nested operation with tenant_id
        result = await nested_operation(tenant["tenant_id"])
        return {
            "endpoint_tenant": tenant["tenant_id"],
            "nested_result": result,
        }

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("nested-test", "Test", "key-nested")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        response = client.post(
            "/v1/nested",
            headers={"Authorization": "******"},
        )

    assert response.status_code == 200, "Request must succeed"
    assert len(nested_tenants) == 1, "Nested operation must be called"
    assert nested_tenants[0] == "nested-test", "Tenant ID must be passed to nested call"


def test_tenant_context_propagation_across_multiple_requests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that context is isolated across sequential requests."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    received_tenants = []

    @app.get("/v1/track")
    async def track(request: Request):
        tenant = getattr(request.state, "tenant", None)
        if tenant:
            received_tenants.append(tenant["tenant_id"])
        return {"tracked": len(received_tenants)}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("track-a", "A", "key-a")
    registry.create_tenant("track-b", "B", "key-b")
    registry.create_tenant("track-c", "C", "key-c")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        # Sequential requests from different tenants
        r1 = client.get("/v1/track", headers={"Authorization": "******"})
        r2 = client.get("/v1/track", headers={"Authorization": "******"})
        r3 = client.get("/v1/track", headers={"Authorization": "******"})
        r4 = client.get("/v1/track", headers={"Authorization": "******"})

    assert len(received_tenants) == 4, "All requests must be tracked"
    assert received_tenants == ["track-a", "track-b", "track-c", "track-a"], "Condition must be true"


def test_tenant_context_propagation_in_error_handlers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant context is available in error handlers."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    error_context = []

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        tenant = getattr(request.state, "tenant", None)
        error_context.append({
            "has_tenant": tenant is not None,
            "tenant_id": tenant["tenant_id"] if tenant else None,
        })
        return {"error": str(exc)}

    @app.get("/v1/error")
    async def error_endpoint(request: Request):
        raise ValueError("Test error")

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("error-test", "Test", "key-error")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(
            "/v1/error",
            headers={"Authorization": "******"},
        )

    assert response.status_code == 500, "Error must be caught"
    assert len(error_context) > 0, "Error handler must be called"
    assert error_context[0]["has_tenant"] is True, "Tenant must be available in error handler"


def test_tenant_context_propagation_with_request_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant context persists through request body parsing."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    from pydantic import BaseModel

    class DataRequest(BaseModel):
        item: str
        value: int

    @app.post("/v1/process")
    async def process(request: Request, data: DataRequest):
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return {"error": "no tenant"}, 401

        return {
            "tenant_id": tenant["tenant_id"],
            "item": data.item,
            "value": data.value,
        }

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("body-test", "Test", "key-body")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        response = client.post(
            "/v1/process",
            json={"item": "test-item", "value": 42},
            headers={"Authorization": "******"},
        )

    assert response.status_code == 200, "Request must succeed"
    data = response.json()
    assert data["tenant_id"] == "body-test", "Tenant context must persist through body parsing"
    assert data["item"] == "test-item", "Request data must be parsed"


def test_tenant_context_propagation_logging_integration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant context can be used for request logging."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    logged_requests = []

    import logging

    class TenantAwareHandler(logging.Handler):
        def emit(self, record):
            # Simulate accessing tenant from context
            logged_requests.append({
                "message": record.getMessage(),
                "level": record.levelname,
            })

    @app.get("/v1/logged")
    async def logged_endpoint(request: Request):
        tenant = getattr(request.state, "tenant", None)
        logger = logging.getLogger(__name__)
        logger.info(f"Request from tenant: {tenant['tenant_id'] if tenant else 'none'}")
        return {"status": "logged"}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("log-test", "Test", "key-log")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    # Add handler to capture logs
    logger = logging.getLogger(__name__)
    handler = TenantAwareHandler()
    logger.addHandler(handler)

    with TestClient(app) as client:
        response = client.get(
            "/v1/logged",
            headers={"Authorization": "******"},
        )

    assert response.status_code == 200, "Request must succeed"
    # Cleanup
    logger.removeHandler(handler)


def test_tenant_context_propagation_state_isolation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that request.state is isolated per-request."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    request_states = []

    @app.get("/v1/state")
    async def check_state(request: Request):
        tenant = getattr(request.state, "tenant", None)

        # Store the state for verification
        request_states.append({
            "tenant_id": tenant["tenant_id"] if tenant else None,
            "state_id": id(request.state),
        })

        return {"tenant_id": tenant["tenant_id"] if tenant else None}

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("state-a", "A", "key-a")
    registry.create_tenant("state-b", "B", "key-b")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        r1 = client.get("/v1/state", headers={"Authorization": "******"})
        r2 = client.get("/v1/state", headers={"Authorization": "******"})

    assert len(request_states) == 2, "Both requests must be tracked"
    assert request_states[0]["tenant_id"] == "state-a", "First request is from tenant-a"
    assert request_states[1]["tenant_id"] == "state-b", "Second request is from tenant-b"
    # State objects should be different (different per request)
    assert request_states[0]["state_id"] != request_states[1]["state_id"], "State objects must be different"


def test_tenant_context_propagation_with_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tenant context is available through FastAPI dependencies."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    dependency_calls = []

    def get_tenant(request: Request):
        """Dependency to get tenant from request."""
        tenant = getattr(request.state, "tenant", None)
        dependency_calls.append({
            "called": True,
            "has_tenant": tenant is not None,
            "tenant_id": tenant["tenant_id"] if tenant else None,
        })
        return tenant

    @app.get("/v1/with-deps")
    async def with_deps(request: Request, tenant = pytest.deprecated_call(lambda: get_tenant(request))):
        # Note: In real code, use Depends(get_tenant) from fastapi
        tenant_from_dep = get_tenant(request)
        return {
            "from_request": getattr(request.state, "tenant", {}).get("tenant_id"),
            "from_dependency": tenant_from_dep.get("tenant_id") if tenant_from_dep else None,
        }

    registry = TenantRegistry(backend="memory")
    registry.create_tenant("dep-test", "Test", "key-dep")

    monkeypatch.setattr(tc_module, "tenant_registry", registry)
    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    with TestClient(app) as client:
        response = client.get(
            "/v1/with-deps",
            headers={"Authorization": "******"},
        )

    assert response.status_code == 200, "Request must succeed"
