"""
Test Tenant Isolation

Test module for tenant isolation.
"""

# Tenant isolation tests for adapters (mock-based)
from mcp.backends.mock_backend import InMemoryMockBackend


def test_tenant_isolation():
    adapter = InMemoryMockBackend()
    adapter.connect()
    a_ns = "tenant-A"
    b_ns = "tenant-B"
    item_a = {"id": "id-a", "embedding": [1.0, 0.0], "content": "alpha", "metadata": {}}
    item_b = {"id": "id-b", "embedding": [0.0, 1.0], "content": "beta", "metadata": {}}
    adapter.upsert_batch(a_ns, [item_a])
    adapter.upsert_batch(b_ns, [item_b])
    res_a = adapter.query_top_k(a_ns, [1.0, 0.0], top_k=10)
    res_b = adapter.query_top_k(b_ns, [0.0, 1.0], top_k=10)
    ids_a = {r["id"] for r in res_a}
    ids_b = {r["id"] for r in res_b}
    assert "id-a" in ids_a, "Condition must be true"
    assert "id-b" in ids_b, "Condition must be true"
    assert "id-b" not in ids_a, "Condition must be true"
    assert "id-a" not in ids_b, "Condition must be true"
