from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from services.msp_gateway.middleware import tenant_context as tc_module
from services.msp_gateway.middleware.tenant_context import TenantContextMiddleware, TenantRegistry


def test_tenant_registry_sqlite_crud(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "tenants.db"
    monkeypatch.setattr(tc_module.settings, "db_path", str(db_path))
    monkeypatch.setattr(tc_module.settings, "rate_limit_requests_per_minute", 7)
    monkeypatch.setattr(tc_module.settings, "rate_limit_tokens_per_minute", 70)

    registry = TenantRegistry(backend="sqlite")
    created = registry.create_tenant("tenant-a", "Tenant A", "key-a")
    assert created["quota"]["requests_per_minute"] == 7, "Condition must be true"

    fetched = registry.get_tenant("tenant-a")
    assert fetched is not None and fetched["name"] == "Tenant A", "fetched must be initialized"
    assert registry.get_tenant_by_api_key("key-a")["tenant_id"] == "tenant-a", "Condition must be true"

    updated = registry.update_tenant("tenant-a", name="Tenant Updated", active=False)
    assert updated is not None and updated["active"] is False, "updated must be initialized"
    assert registry.deactivate_tenant("tenant-a") is True, "Condition must be true"

    registry.delete_tenant("tenant-a")
    deleted = registry.get_tenant("tenant-a")
    assert deleted is not None, "deleted must be initialized"
    assert deleted.get("active", False) is False

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT name FROM tenants WHERE tenant_id = ?", ("tenant-a",)).fetchone()
    conn.close()
    assert row is not None, "row must be initialized"


def test_tenant_registry_memory_listing() -> None:
    registry = TenantRegistry(backend="memory")
    registry.create_tenant(
        "t1", "T1", "k1", quota={"requests_per_minute": 1, "tokens_per_minute": 2}
    )
    registry.create_tenant(
        "t2", "T2", "k2", quota={"requests_per_minute": 3, "tokens_per_minute": 4}
    )
    tenant_ids = {item["tenant_id"] for item in registry.list_tenants()}
    assert tenant_ids == {"t1", "t2"}


def test_tenant_middleware_auth_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/v1/resource")
    async def resource(request: Request):
        tenant = getattr(request.state, "tenant", None)
        return {"tenant_id": tenant["tenant_id"] if tenant else None}

    monkeypatch.setattr(tc_module.settings, "api_key_required", True)

    # Missing auth header
    with TestClient(app) as client:
        missing = client.get("/v1/resource")
    assert missing.status_code == 401, "status_code is not valid"

    # Invalid key
    monkeypatch.setattr(tc_module.tenant_registry, "get_tenant_by_api_key", lambda _: None)
    with TestClient(app) as client:
        invalid = client.get("/v1/resource", headers={"Authorization": "Bearer bad"})
    assert invalid.status_code == 401, "status_code is not valid"

    # Inactive tenant
    monkeypatch.setattr(
        tc_module.tenant_registry,
        "get_tenant_by_api_key",
        lambda _: {"tenant_id": "t-inactive", "active": False},
    )
    with TestClient(app) as client:
        inactive = client.get("/v1/resource", headers={"Authorization": "Bearer bad"})
    assert inactive.status_code == 403, "status_code is not valid"

    # Active tenant
    monkeypatch.setattr(
        tc_module.tenant_registry,
        "get_tenant_by_api_key",
        lambda _: {"tenant_id": "t-active", "active": True},
    )
    with TestClient(app) as client:
        ok = client.get("/v1/resource", headers={"Authorization": "Bearer ok"})
    assert ok.status_code == 200, "status_code is not valid"
    assert ok.json()["tenant_id"] == "t-active", "Condition must be true"


def test_tenant_middleware_public_and_auth_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware)

    @app.get("/admin/tenants")
    async def admin():
        return {"ok": True}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    monkeypatch.setattr(tc_module.settings, "api_key_required", False)
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200, "status_code is not valid"
        assert client.get("/admin/tenants").status_code == 200, "status_code is not valid"
