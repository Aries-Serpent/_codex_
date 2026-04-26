"""Focused tests for MCP adapter loading and health routes."""

from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mcp.server import adapter_loader, routes_health


def test_load_adapter_uses_explicit_class(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeAdapter:
        pass

    monkeypatch.setattr(adapter_loader, "_import_class", lambda path: FakeAdapter if "valid" in path else None)

    adapter, cls_path = adapter_loader.load_adapter("pkg.valid.FakeAdapter")

    assert isinstance(adapter, FakeAdapter)
    assert cls_path == "pkg.valid.FakeAdapter"


def test_import_class_loads_real_symbol() -> None:
    cls = adapter_loader._import_class("mcp.server.adapter_loader.MockAdapter")

    assert cls is adapter_loader.MockAdapter


def test_load_adapter_falls_back_to_mock_adapter_when_all_imports_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(adapter_loader, "_import_class", lambda path: None)

    adapter, cls_path = adapter_loader.load_adapter("pkg.missing.Adapter")

    assert isinstance(adapter, adapter_loader.MockAdapter)
    assert cls_path == adapter_loader.DEFAULT_ADAPTER


def test_load_adapter_uses_fallback_when_primary_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    class FallbackAdapter:
        pass

    def _fake_import(path: str):
        if path == "pkg.missing.Adapter":
            return None
        if path == adapter_loader.DEFAULT_ADAPTER:
            return FallbackAdapter
        return None

    monkeypatch.setattr(adapter_loader, "_import_class", _fake_import)

    adapter, cls_path = adapter_loader.load_adapter("pkg.missing.Adapter")

    assert isinstance(adapter, FallbackAdapter)
    assert cls_path == adapter_loader.DEFAULT_ADAPTER


@pytest.mark.asyncio
async def test_lazy_connect_all_returns_true_without_connect(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    class PassiveAdapter:
        pass

    def _load_adapter() -> tuple[PassiveAdapter, str]:
        nonlocal called
        called = True
        return PassiveAdapter(), "passive"

    monkeypatch.setattr(adapter_loader, "load_adapter", _load_adapter)

    assert await adapter_loader.lazy_connect_all() is True
    assert called is True


@pytest.mark.asyncio
async def test_lazy_connect_all_returns_true_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class HealthyAdapter:
        def __init__(self) -> None:
            self.connected = False

        def connect(self) -> None:
            self.connected = True

    adapter = HealthyAdapter()
    monkeypatch.setattr(adapter_loader, "load_adapter", lambda: (adapter, "healthy"))

    assert await adapter_loader.lazy_connect_all(timeout=0.01) is True
    assert adapter.connected is True


@pytest.mark.asyncio
async def test_lazy_connect_all_returns_false_on_connect_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingAdapter:
        def connect(self) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(adapter_loader, "load_adapter", lambda: (FailingAdapter(), "failing"))

    assert await adapter_loader.lazy_connect_all(timeout=0.01) is False


def test_health_route_reports_adapter_status() -> None:
    class HealthyAdapter:
        def health_check(self) -> dict[str, str]:
            return {"status": "ok", "backend": "fake"}

    app = FastAPI()
    routes_health.register_health_routes(app, adapter_loader_fn=lambda: (HealthyAdapter(), "fake.adapter"))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "mcp-facade",
        "status": "ok",
        "adapter": "fake.adapter",
        "adapter_status": {"status": "ok", "backend": "fake"},
    }


def test_health_endpoints_degrade_when_health_check_raises() -> None:
    class BrokenAdapter:
        def health_check(self) -> dict[str, str]:
            raise RuntimeError("unhealthy")

    app = FastAPI()
    routes_health.register_health_routes(app, adapter_loader_fn=lambda: (BrokenAdapter(), "broken.adapter"))
    client = TestClient(app)

    root_response = client.get("/health")
    mcp_response = client.get("/mcp/v1/health")

    assert root_response.status_code == 200
    assert root_response.json()["adapter_status"] == {"status": "degraded"}
    assert mcp_response.status_code == 200
    assert mcp_response.json() == {
        "status": "ok",
        "adapter": "broken.adapter",
        "adapter_status": {"status": "degraded"},
    }
