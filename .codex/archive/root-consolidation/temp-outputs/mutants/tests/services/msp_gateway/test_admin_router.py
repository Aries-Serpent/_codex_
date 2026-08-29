from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

pytest.importorskip("pydantic_settings")

from services.msp_gateway.routers import admin
from services.msp_gateway.schemas.requests import TenantUpdateRequest


def _tenant_payload() -> dict[str, object]:
    return {
        "tenant_id": "tenant-1",
        "name": "Tenant One",
        "quota": {"requests_per_minute": 10, "tokens_per_minute": 100},
        "policies": [],
        "active": True,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "metadata": {},
    }


def test_update_tenant_calls_registry_once(monkeypatch) -> None:
    registry = MagicMock()
    registry.update_tenant.return_value = _tenant_payload()
    monkeypatch.setattr(admin.settings, "admin_api_enabled", True)
    monkeypatch.setattr(admin, "tenant_registry", registry)

    response = asyncio.run(admin.update_tenant("tenant-1", TenantUpdateRequest(name="Updated")))

    registry.update_tenant.assert_called_once_with(
        tenant_id="tenant-1",
        name="Updated",
        quota=None,
        policies=None,
        metadata=None,
        active=None,
    )
    assert response.tenant_id == "tenant-1", "Response must not be empty"


def test_delete_tenant_skips_preemptive_deactivate(monkeypatch) -> None:
    registry = MagicMock()
    monkeypatch.setattr(admin.settings, "admin_api_enabled", True)
    monkeypatch.setattr(admin, "tenant_registry", registry)

    response = asyncio.run(admin.delete_tenant("tenant-1"))

    registry.deactivate_tenant.assert_not_called()
    registry.delete_tenant.assert_called_once_with("tenant-1")
    assert response.status_code == 204, "Response must not be empty"
