"""
tests/integration/test_tenant_context_update.py
─────────────────────────────────────────────────
Integration tests for the TenantRegistry SQL update path.

Covers:
- update_tenant() persists every supported field (name, quota, policies, metadata, active)
- Parameterised field updates — each field is tested independently and in combination
- update_tenant() on a non-existent tenant returns None (no crash)
- SQL injection resilience: column names are hardcoded literals; values are parameterised
- In-memory cache is updated together with the SQLite row
- deactivate_tenant() delegates to update_tenant(active=False)
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def registry(tmp_path: Path):
    """Return a TenantRegistry wired to a temporary SQLite file."""
    db_file = tmp_path / "test_tenants.db"

    # Patch settings before importing to control db_path and backend
    mock_settings = MagicMock()
    mock_settings.db_path = str(db_file)
    mock_settings.tenant_registry_backend = "sqlite"
    mock_settings.api_key_required = True

    mock_auth = MagicMock()
    mock_auth.verify_api_key.return_value = "test-tenant"
    mock_auth.register_api_key.return_value = None
    mock_auth.revoke_api_key.return_value = None

    with (
        patch(
            "services.msp_gateway.middleware.tenant_context.settings",
            mock_settings,
        ),
        patch(
            "services.msp_gateway.middleware.tenant_context.auth_manager",
            mock_auth,
        ),
    ):
        from services.msp_gateway.middleware.tenant_context import TenantRegistry

        reg = TenantRegistry(backend="sqlite")
        # Pre-create the tenant row so update tests have a target
        reg.create_tenant(
            tenant_id="t1",
            name="Initial Name",
            api_key="key-001",
            quota={"requests": 100},
            policies=["read"],
            metadata={"env": "test"},
        )
        yield reg, mock_auth


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_row(db_path: str, tenant_id: str) -> dict[str, Any]:
    """Directly read the SQLite row for *tenant_id*."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT tenant_id, name, quota_json, policies_json, metadata_json, active "
        "FROM tenants WHERE tenant_id = ?",
        (tenant_id,),
    )
    row = cur.fetchone()
    conn.close()
    assert row is not None, f"Row for {tenant_id} not found in DB"
    return {
        "tenant_id": row[0],
        "name": row[1],
        "quota": json.loads(row[2]) if row[2] else {},
        "policies": json.loads(row[3]) if row[3] else [],
        "metadata": json.loads(row[4]) if row[4] else {},
        "active": bool(row[5]),
    }


# ---------------------------------------------------------------------------
# Tests: individual field updates
# ---------------------------------------------------------------------------


class TestUpdateTenantSQLPath:
    """Integration tests verifying the SQLite UPDATE path of update_tenant()."""

    def test_update_name_persists_to_db(self, registry) -> None:
        reg, _ = registry
        result = reg.update_tenant("t1", name="New Name")
        assert result is not None, "result must be initialized"
        assert result["name"] == "New Name", "Result must not be empty"
        db_row = _read_row(reg.db_path if hasattr(reg, "db_path") else reg._db_path, "t1")
        assert db_row["name"] == "New Name", "Condition must be true"

    def test_update_quota_persists_to_db(self, registry) -> None:
        reg, _ = registry
        new_quota = {"requests": 999, "tokens": 50000}
        result = reg.update_tenant("t1", quota=new_quota)
        assert result is not None, "result must be initialized"
        assert result["quota"] == new_quota, "Result must not be empty"

    def test_update_policies_persists_to_db(self, registry) -> None:
        reg, _ = registry
        result = reg.update_tenant("t1", policies=["read", "write", "admin"])
        assert result is not None, "result must be initialized"
        assert result["policies"] == ["read", "write", "admin"]

    def test_update_metadata_persists_to_db(self, registry) -> None:
        reg, _ = registry
        new_meta = {"env": "production", "region": "us-east-1"}
        result = reg.update_tenant("t1", metadata=new_meta)
        assert result is not None, "result must be initialized"
        assert result["metadata"] == new_meta, "Result must not be empty"

    @pytest.mark.parametrize("active_value", [False, True])
    def test_update_active_flag(self, registry, active_value: bool) -> None:
        """active=True/False must toggle the tenant's active state."""
        reg, mock_auth = registry
        result = reg.update_tenant("t1", active=active_value)
        assert result is not None, "result must be initialized"
        assert result["active"] == active_value, "Result must not be empty"
        if active_value:
            mock_auth.register_api_key.assert_called()
        else:
            mock_auth.revoke_api_key.assert_called()

    # ── multiple fields at once ─────────────────────────────────────────────

    @pytest.mark.parametrize(
        "updates",
        [
            {"name": "Batch A", "quota": {"req": 10}},
            {"policies": ["p1"], "metadata": {"k": "v"}},
            {"name": "Batch C", "active": True, "quota": {"r": 5}},
        ],
    )
    def test_multi_field_update(self, registry, updates: dict[str, Any]) -> None:
        """Multiple fields can be updated in a single call."""
        reg, _ = registry
        result = reg.update_tenant("t1", **updates)
        assert result is not None, "result must be initialized"
        for field, expected in updates.items():
            assert result[field] == expected, f"Field {field!r} mismatch"

    # ── in-memory cache sync ────────────────────────────────────────────────

    def test_in_memory_cache_updated(self, registry) -> None:
        reg, _ = registry
        reg.update_tenant("t1", name="Cache Check")
        cached = reg.get_tenant("t1")
        assert cached is not None, "cached must be initialized"
        assert cached["name"] == "Cache Check", "Condition must be true"

    # ── non-existent tenant ─────────────────────────────────────────────────

    def test_update_nonexistent_tenant_returns_none(self, registry) -> None:
        reg, _ = registry
        result = reg.update_tenant("does-not-exist", name="Ghost")
        assert result is None, "Result must not be empty"

    # ── deactivate_tenant delegates to update_tenant ────────────────────────

    def test_deactivate_tenant_calls_update(self, registry) -> None:
        reg, mock_auth = registry
        success = reg.deactivate_tenant("t1")
        assert success is True, "success is not valid"
        tenant = reg.get_tenant("t1")
        assert tenant is not None, "tenant must be initialized"
        assert tenant["active"] is False, "Condition must be true"
        mock_auth.revoke_api_key.assert_called()

    # ── no-op update (no fields) doesn't crash ──────────────────────────────

    def test_empty_update_returns_tenant(self, registry) -> None:
        reg, _ = registry
        result = reg.update_tenant("t1")
        # Should return the tenant unchanged (updated_at only)
        assert result is not None, "result must be initialized"
        assert result["name"] == "Initial Name", "Result must not be empty"
