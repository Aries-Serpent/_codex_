"""Focused tests for MCP adapter loading and health routes."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mcp.server import adapter_loader, routes_health


def test_load_adapter_uses_explicit_class(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeAdapter:
        pass

    monkeypatch.setattr(
        adapter_loader,
        "_import_class",
        lambda path: FakeAdapter if path == "pkg.valid.FakeAdapter" else None,
    )

    adapter, cls_path = adapter_loader.load_adapter("pkg.valid.FakeAdapter")

    assert isinstance(adapter, FakeAdapter)
    assert cls_path == "pkg.valid.FakeAdapter", "cls_path is not valid"


def test_import_class_loads_real_symbol() -> None:
    cls = adapter_loader._import_class("mcp.server.adapter_loader.MockAdapter")

    assert cls is adapter_loader.MockAdapter, "cls is not valid"


def test_import_class_returns_none_for_missing_module() -> None:
    cls = adapter_loader._import_class("mcp.server.does_not_exist.Missing")

    assert cls is None, "cls is not valid"


def test_load_adapter_falls_back_to_mock_adapter_when_all_imports_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(adapter_loader, "_import_class", lambda path: None)

    adapter, cls_path = adapter_loader.load_adapter("pkg.missing.Adapter")

    assert isinstance(adapter, adapter_loader.MockAdapter)
    assert cls_path == adapter_loader.DEFAULT_ADAPTER, "cls_path is not valid"


def test_load_adapter_uses_fallback_when_primary_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FallbackAdapter:
        pass

    def _fake_import(path: str) -> type | None:
        if path == "pkg.missing.Adapter":
            return None
        if path == adapter_loader.DEFAULT_ADAPTER:
            return FallbackAdapter
        return None

    monkeypatch.setattr(adapter_loader, "_import_class", _fake_import)

    adapter, cls_path = adapter_loader.load_adapter("pkg.missing.Adapter")

    assert isinstance(adapter, FallbackAdapter)
    assert cls_path == adapter_loader.DEFAULT_ADAPTER, "cls_path is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_lazy_connect_all_succeeds_when_adapter_lacks_connect_method(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    class PassiveAdapter:
        pass

    def _load_adapter() -> tuple[PassiveAdapter, str]:
        nonlocal called
        called = True
        return PassiveAdapter(), "passive"

    monkeypatch.setattr(adapter_loader, "load_adapter", _load_adapter)

    assert await adapter_loader.lazy_connect_all() is True, "Condition must be true"
    assert called is True, "called is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_lazy_connect_all_returns_true_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class HealthyAdapter:
        def __init__(self) -> None:
            self.connected = False

        def connect(self) -> None:
            self.connected = True

    adapter = HealthyAdapter()
    monkeypatch.setattr(adapter_loader, "load_adapter", lambda: (adapter, "healthy"))

    assert await adapter_loader.lazy_connect_all(timeout=0.01) is True, "Condition must be true"
    assert adapter.connected is True, "connected is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_lazy_connect_all_returns_false_on_connect_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingAdapter:
        def connect(self) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(adapter_loader, "load_adapter", lambda: (FailingAdapter(), "failing"))

    assert await adapter_loader.lazy_connect_all(timeout=0.01) is False, "Condition must be true"


def test_health_route_reports_adapter_status() -> None:
    class HealthyAdapter:
        def health_check(self) -> dict[str, str]:
            return {"status": "ok", "backend": "fake"}

    app = FastAPI()
    routes_health.register_health_routes(
        app, adapter_loader_fn=lambda: (HealthyAdapter(), "fake.adapter")
    )
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200, "Response must not be empty"
    class BrokenAdapter:
        def health_check(self) -> dict[str, str]:
            raise RuntimeError("unhealthy")

    app = FastAPI()
    routes_health.register_health_routes(
        app, adapter_loader_fn=lambda: (BrokenAdapter(), "broken.adapter")
    )
    client = TestClient(app)

    root_response = client.get("/health")
    mcp_response = client.get("/mcp/v1/health")

    assert root_response.status_code == 200, "Response must not be empty"
    assert root_response.json()["adapter_status"] == {"status": "degraded"}, "Response must not be empty"
    assert mcp_response.status_code == 200, "Response must not be empty"
