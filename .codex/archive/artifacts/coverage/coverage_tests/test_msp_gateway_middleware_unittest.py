from __future__ import annotations

import asyncio
import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from services.msp_gateway.middleware import tenant_context as tc_module
from services.msp_gateway.middleware.rate_limit import (
    RateLimitMiddleware,
    TokenBucket,
    rate_limiter,
)
from services.msp_gateway.middleware.tenant_context import (
    TenantContextMiddleware,
    TenantRegistry,
)


class MSPRateLimitCoverageTests(unittest.TestCase):
    def test_token_bucket_and_rate_limiter_core_paths(self) -> None:
        bucket = TokenBucket(capacity=10, tokens=0.0, last_refill=time.time(), refill_rate=1.0)
        self.assertFalse(bucket.consume(1))
        self.assertGreaterEqual(bucket.available_tokens(), 0.0)

        from services.msp_gateway.middleware import rate_limit as rl_module

        limiter = rl_module.RateLimiter()
        with patch.object(rl_module.settings, "rate_limit_enabled", False):
            self.assertTrue(limiter.check_request_limit("tenant-off"))
            self.assertTrue(limiter.check_token_limit("tenant-off", 500))

        with (
            patch.object(rl_module.settings, "rate_limit_enabled", True),
            patch.object(rl_module.settings, "rate_limit_requests_per_minute", 2),
            patch.object(rl_module.settings, "rate_limit_tokens_per_minute", 3),
        ):
            self.assertTrue(limiter.check_request_limit("tenant-on", {"requests_per_minute": 2}))
            self.assertFalse(limiter.check_token_limit("tenant-on", 4, {"tokens_per_minute": 3}))

    def test_extract_requested_tokens_variants(self) -> None:
        self.assertEqual(RateLimitMiddleware._extract_requested_tokens(b""), 512)
        self.assertEqual(RateLimitMiddleware._extract_requested_tokens(b"nope"), 512)
        self.assertEqual(
            RateLimitMiddleware._extract_requested_tokens(json.dumps({"max_tokens": -5}).encode()),
            1,
        )
        self.assertEqual(
            RateLimitMiddleware._extract_requested_tokens(json.dumps({"max_tokens": "x"}).encode()),
            512,
        )

    def test_dispatch_request_limit_exceeded(self) -> None:
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/v1/query")
        async def query() -> dict[str, bool]:
            return {"ok": True}

        async def fake_call_next(request: Request):
            return JSONResponse({"ok": True})

        async def run() -> int:
            scope = {"type": "http", "method": "GET", "path": "/v1/query", "headers": []}
            request = Request(scope)
            request.state.tenant = {"tenant_id": "tenant-a", "quota": {}}
            with patch.object(rate_limiter, "check_request_limit", return_value=False):
                middleware = RateLimitMiddleware(app)
                response = await middleware.dispatch(request, fake_call_next)
            return response.status_code

        self.assertEqual(asyncio.run(run()), 429)

    def test_dispatch_skips_public_and_missing_tenant(self) -> None:
        app = FastAPI()
        middleware = RateLimitMiddleware(app)

        async def fake_call_next(request: Request):
            return JSONResponse({"ok": True})

        async def run(path: str, with_tenant: bool) -> int:
            request = Request({"type": "http", "method": "GET", "path": path, "headers": []})
            if with_tenant:
                request.state.tenant = {"tenant_id": "tenant-a", "quota": {}}
            response = await middleware.dispatch(request, fake_call_next)
            return response.status_code

        self.assertEqual(asyncio.run(run("/health", False)), 200)
        self.assertEqual(asyncio.run(run("/v1/other", False)), 200)

    def test_dispatch_token_preflight_exceeded(self) -> None:
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        async def fake_call_next(request: Request):
            return JSONResponse({"ok": True})

        async def run() -> int:
            scope = {"type": "http", "method": "GET", "path": "/v1/query", "headers": []}
            request = Request(scope)
            request.state.tenant = {"tenant_id": "tenant-a", "quota": {"tokens_per_minute": 2}}

            bucket = TokenBucket(capacity=2, tokens=0.0, last_refill=0.0, refill_rate=0.0)
            with (
                patch.object(rate_limiter, "check_request_limit", return_value=True),
                patch.object(rate_limiter, "_get_or_create_bucket", return_value=bucket),
            ):
                middleware = RateLimitMiddleware(app)
                response = await middleware.dispatch(request, fake_call_next)
            return response.status_code

        self.assertEqual(asyncio.run(run()), 429)

    def test_dispatch_infer_rebuilds_response(self) -> None:
        app = FastAPI()

        class _InjectTenantMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                request.state.tenant = {"tenant_id": "tenant-z", "quota": {"tokens_per_minute": 1000}}
                return await call_next(request)

        @app.post("/v1/infer")
        async def infer(request: Request):
            payload = await request.json()
            return JSONResponse({"tokens_used": payload.get("max_tokens", 1)})

        app.add_middleware(RateLimitMiddleware)
        app.add_middleware(_InjectTenantMiddleware)

        token_bucket = TokenBucket(capacity=1000, tokens=1000.0, last_refill=0.0, refill_rate=0.0)
        with (
            patch.object(rate_limiter, "check_request_limit", return_value=True),
            patch.object(rate_limiter, "_get_or_create_bucket", return_value=token_bucket),
        ):
            with TestClient(app) as client:
                resp = client.post("/v1/infer", json={"max_tokens": 5})
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(token_bucket.tokens, 0.0)


class MSPTenantContextCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.data_dir = Path(self._tmpdir.name) / "runtime"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "tenant_registry.db"
        if self.db_path.exists():
            self.db_path.unlink()

    def test_tenant_registry_sqlite_and_memory_paths(self) -> None:
        with patch.object(tc_module.settings, "db_path", str(self.db_path)):
            registry = TenantRegistry(backend="sqlite")
            created = registry.create_tenant("tenant-1", "Tenant 1", "k1")
            self.assertEqual(created["tenant_id"], "tenant-1")
            self.assertIsNotNone(registry.get_tenant("tenant-1"))
            self.assertIsNotNone(registry.get_tenant_by_api_key("k1"))
            updated = registry.update_tenant("tenant-1", name="Tenant One", active=False)
            self.assertIsNotNone(updated)
            self.assertTrue(registry.deactivate_tenant("tenant-1"))
            registry.delete_tenant("tenant-1")
            self.assertFalse(registry.get_tenant("tenant-1")["active"])

        memory_registry = TenantRegistry(backend="memory")
        memory_registry.create_tenant("tenant-2", "Tenant 2", "k2")
        self.assertEqual(len(memory_registry.list_tenants()), 1)
        with self.assertRaises(ValueError):
            memory_registry.delete_tenant("missing")

    def test_middleware_auth_branches(self) -> None:
        async def fake_next(request):
            tenant = getattr(request.state, "tenant", None)
            return JSONResponse({"tenant_id": tenant["tenant_id"] if tenant else None})

        class _Headers:
            def __init__(self, authorization: str | None):
                self._authorization = authorization

            def get(self, key: str):
                if key == "Authorization":
                    return self._authorization
                return None

        async def run_with_auth(auth_header: str | None, tenant_value):
            request = SimpleNamespace(
                url=SimpleNamespace(path="/v1/resource"),
                headers=_Headers(auth_header),
                state=SimpleNamespace(),
            )
            middleware = TenantContextMiddleware(FastAPI())
            with (
                patch.object(tc_module.settings, "api_key_required", True),
                patch.object(tc_module.tenant_registry, "get_tenant_by_api_key", return_value=tenant_value),
            ):
                return await middleware.dispatch(request, fake_next)

        missing = asyncio.run(run_with_auth(None, None))
        self.assertEqual(missing.status_code, 401)

        invalid = asyncio.run(run_with_auth("not-bearer", None))
        self.assertEqual(invalid.status_code, 401)
        bearer_prefix = "Bearer"

        inactive = asyncio.run(
            run_with_auth(
                f"{bearer_prefix} inactive",
                {"tenant_id": "inactive", "active": False},
            )
        )
        self.assertEqual(inactive.status_code, 403)

        active = asyncio.run(
            run_with_auth(
                f"{bearer_prefix} active",
                {"tenant_id": "active", "active": True},
            )
        )
        self.assertEqual(active.status_code, 200)
