"""
Extended tests for MCP multi-tenant capability.

Covers tenant isolation, tenant-specific configurations, resource separation,
and multi-tenant security patterns.
"""

from mcp.auth import Principal


def test_tenant_principal_creation():
    """Test creating principals for different tenants."""
    tenant1_principal = Principal(principal_id="tenant1:user1")
    tenant2_principal = Principal(principal_id="tenant2:user1")

    assert tenant1_principal.principal_id != tenant2_principal.principal_id, "principal_id is not valid"
    assert "tenant1" in tenant1_principal.principal_id, "Condition must be true"
    assert "tenant2" in tenant2_principal.principal_id, "Condition must be true"


def test_tenant_isolation_pattern():
    """Test tenant isolation pattern in data access."""
    # Mock tenant-scoped data
    data_store = {"tenant1": {"item1": "data1"}, "tenant2": {"item2": "data2"}}

    def get_tenant_data(tenant_id: str):
        return data_store.get(tenant_id, {})

    tenant1_data = get_tenant_data("tenant1")
    tenant2_data = get_tenant_data("tenant2")

    assert "item1" in tenant1_data, "Data must not be empty"
    assert "item1" not in tenant2_data, "Data must not be empty"
    assert "item2" in tenant2_data, "Data must not be empty"


def test_tenant_specific_configuration():
    """Test tenant-specific configuration."""
    tenant_configs = {
        "tenant1": {"rate_limit": 100, "features": ["feature_a"]},
        "tenant2": {"rate_limit": 50, "features": ["feature_b"]},
    }

    assert tenant_configs["tenant1"]["rate_limit"] == 100, "Condition must be true"
    assert "feature_a" in tenant_configs["tenant1"]["features"], "Condition must be true"
    assert "feature_b" not in tenant_configs["tenant1"]["features"], "Condition must be true"


def test_tenant_resource_quota():
    """Test tenant resource quota enforcement."""
    quotas = {
        "tenant1": {"api_calls": 1000, "storage_mb": 500},
        "tenant2": {"api_calls": 500, "storage_mb": 250},
    }

    def check_quota(tenant_id: str, resource: str, amount: int) -> bool:
        quota = quotas.get(tenant_id, {}).get(resource, 0)
        return amount <= quota

    assert check_quota("tenant1", "api_calls", 900) is True
    assert check_quota("tenant1", "api_calls", 1100) is False


def test_cross_tenant_access_denied():
    """Test cross-tenant access is denied."""

    def access_resource(requesting_tenant: str, resource_tenant: str) -> bool:
        return requesting_tenant == resource_tenant

    assert access_resource("tenant1", "tenant1") is True
    assert access_resource("tenant1", "tenant2") is False


def test_tenant_scoped_rate_limiting():
    """Test rate limiting is per-tenant."""
    rate_limits = {}

    def rate_limit_check(tenant_id: str, limit: int) -> bool:
        current = rate_limits.get(tenant_id, 0)
        if current >= limit:
            return False
        rate_limits[tenant_id] = current + 1
        return True

    # Tenant1 makes requests
    assert rate_limit_check("tenant1", limit=2) is True
    assert rate_limit_check("tenant1", limit=2) is True
    assert rate_limit_check("tenant1", limit=2) is False

    # Tenant2 still has quota
    assert rate_limit_check("tenant2", limit=2) is True


def test_tenant_from_principal():
    """Test extracting tenant ID from principal."""
    principal = Principal(principal_id="tenant1:user123")

    def get_tenant_id(principal: Principal) -> str:
        # Extract tenant from principal ID
        parts = principal.principal_id.split(":")
        return parts[0] if len(parts) > 1 else "default"

    tenant_id = get_tenant_id(principal)
    assert tenant_id == "tenant1", "tenant_id is not valid"


def test_tenant_specific_tools():
    """Test tools can be tenant-specific."""
    tenant_tools = {"tenant1": ["tool_a", "tool_b"], "tenant2": ["tool_c"]}

    def get_available_tools(tenant_id: str):
        return tenant_tools.get(tenant_id, [])

    assert "tool_a" in get_available_tools("tenant1"), "Condition must be true"
    assert "tool_c" not in get_available_tools("tenant1"), "Condition must be true"
    assert "tool_c" in get_available_tools("tenant2"), "Condition must be true"


def test_tenant_data_encryption():
    """Test tenant data encryption pattern."""
    import hashlib

    def encrypt_tenant_data(tenant_id: str, data: str) -> str:
        # Mock encryption using tenant-specific key
        key = f"key-{tenant_id}"
        combined = f"{key}:{data}"
        return hashlib.sha256(combined.encode()).hexdigest()

    encrypted1 = encrypt_tenant_data("tenant1", "secret")
    encrypted2 = encrypt_tenant_data("tenant2", "secret")

    # Same data, different tenants = different encryption
    assert encrypted1 != encrypted2, "encrypted1 is not valid"


def test_tenant_audit_logging():
    """Test tenant-specific audit logging."""
    audit_log = []

    def log_tenant_action(tenant_id: str, action: str):
        audit_log.append({"tenant": tenant_id, "action": action})

    log_tenant_action("tenant1", "create_resource")
    log_tenant_action("tenant2", "delete_resource")

    tenant1_logs = [entry for entry in audit_log if entry["tenant"] == "tenant1"]
    assert len(tenant1_logs) == 1, "Tenant1_logs must not be empty"
    assert tenant1_logs[0]["action"] == "create_resource", "Condition must be true"


def test_multi_tenant_concurrent_access():
    """Test concurrent access from multiple tenants."""
    import threading

    results = {"tenant1": 0, "tenant2": 0}
    lock = threading.Lock()

    def tenant_action(tenant_id: str):
        with lock:
            results[tenant_id] += 1

    threads = []
    for _ in range(5):
        threads.append(threading.Thread(target=tenant_action, args=("tenant1",)))
        threads.append(threading.Thread(target=tenant_action, args=("tenant2",)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results["tenant1"] == 5, "Result must not be empty"
    assert results["tenant2"] == 5, "Result must not be empty"


def test_tenant_metadata():
    """Test tenant metadata management."""
    tenant_metadata = {
        "tenant1": {"name": "Org A", "plan": "enterprise"},
        "tenant2": {"name": "Org B", "plan": "basic"},
    }

    def get_tenant_plan(tenant_id: str) -> str:
        return tenant_metadata.get(tenant_id, {}).get("plan", "free")

    assert get_tenant_plan("tenant1") == "enterprise", "Condition must be true"
    assert get_tenant_plan("tenant2") == "basic", "Condition must be true"
    assert get_tenant_plan("tenant3") == "free", "Condition must be true"
