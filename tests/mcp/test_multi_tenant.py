import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from mcp.auth import MCPAuthenticator, MCPAuthorizer, Principal
from mcp.rate_limit import MCPRateLimiter
from mcp.registry import MCPToolRegistry


def _principal(tenant: str) -> Principal:
    auth = MCPAuthenticator()
    return Principal.from_credential(f"{tenant}:secret", tenant=tenant)


def test_multi_tenant_principal_contains_tenant():
    principal = _principal("tenant-a")
    assert principal.tenant == "tenant-a"


def test_multi_tenant_permission_hash_differs_by_tenant():
    authorizer = MCPAuthorizer()
    p1 = _principal("tenant-a")
    p2 = _principal("tenant-b")
    assert authorizer.compute_permission_hash(p1.principal_id, "tool") != \
        authorizer.compute_permission_hash(p2.principal_id, "tool")


def test_multi_tenant_rate_limiter_isolated():
    limiter = MCPRateLimiter(rate=10, capacity=2)
    assert limiter.allow("tenant-a", "tool")
    assert limiter.allow("tenant-b", "tool")


def test_multi_tenant_rate_limiter_blocks_per_tenant():
    limiter = MCPRateLimiter(rate=0, capacity=1)
    assert limiter.allow("tenant-a", "tool")
    assert not limiter.allow("tenant-a", "tool")


def test_multi_tenant_registry_stores_tenant_metadata():
    registry = MCPToolRegistry()
    registry.register_tool("tenant-tool", lambda **_: None, metadata={"tenant": "tenant-a"})
    assert registry.get_metadata("tenant-tool")["tenant"] == "tenant-a"


def test_multi_tenant_authenticator_generates_stable_tokens():
    auth = MCPAuthenticator()
    p = _principal("tenant-a")
    token1 = auth.generate_session_token(p)
    token2 = auth.generate_session_token(p)
    assert token1 == token2


def test_multi_tenant_authorizer_allows_valid_principal():
    authorizer = MCPAuthorizer()
    assert authorizer.authorize(_principal("tenant-a"), "tool")


def test_multi_tenant_authorizer_rejects_empty_tool():
    authorizer = MCPAuthorizer()
    assert not authorizer.authorize(_principal("tenant-a"), "")


def test_multi_tenant_registry_requires_confirmation_per_tenant():
    registry = MCPToolRegistry()
    registry.register_tool("danger", lambda **_: None, metadata={"confirm": True, "tenant": "a"})
    with pytest.raises(Exception):
        registry.enforce_safeguards("danger", {"tenant": "b"})


def test_multi_tenant_rate_limiter_snapshot_contains_offline_flag():
    limiter = MCPRateLimiter(rate=1, capacity=1)
    snapshot = limiter.snapshot_state()
    assert "offline" in snapshot


def test_multi_tenant_rate_limiter_restore_round_trip():
    limiter = MCPRateLimiter(rate=1, capacity=2)
    limiter.allow("tenant", "tool")
    snap = limiter.snapshot_state()
    other = MCPRateLimiter(rate=1, capacity=2)
    other.restore_state(snap["payload"], snap["checksum"])
    assert other.snapshot_state()["checksum"] == snap["checksum"]


def test_multi_tenant_authenticator_extract_headers_from_mapping():
    auth = MCPAuthenticator()
    principal = auth.authenticate({"X-API-Key": "secret"})
    assert principal.principal_id


def test_multi_tenant_authenticator_requires_api_key():
    auth = MCPAuthenticator()
    with pytest.raises(Exception):
        auth.authenticate({})


def test_multi_tenant_registry_offline_mode_toggle():
    registry = MCPToolRegistry(offline=False)
    assert registry.offline_mode() is False


def test_multi_tenant_registry_listing_contains_metadata():
    registry = MCPToolRegistry()
    registry.register_tool("tenant-x", lambda **_: None, metadata={"tenant": "x"})
    listed = registry.list_tools()[0]
    assert listed["metadata"]["tenant"] == "x"

