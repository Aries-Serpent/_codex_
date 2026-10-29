"""Regression coverage for gateway API-key migration and sanitized logging."""

import logging
import re
import sqlite3
from unittest.mock import Mock

import pytest

from services.msp_gateway import security
from services.msp_gateway.middleware import tenant_context
from services.msp_gateway.providers.retrieval_adapter import RetrievalAdapter

_HOSTILE = "tenant\r\nFORGED\x00\x1b[31m\x85"
_CONTROLS = re.compile(r"[\x00-\x1f\x7f-\x9f]")


@pytest.mark.parametrize(
    ("backend", "cached_hash"),
    [
        ("sqlite", None),
        ("sqlite", "legacy"),
        ("sqlite", "current"),
        ("memory", "legacy"),
        ("memory", "current"),
    ],
)
def test_legacy_api_key_migrates_on_every_lookup_path(tmp_path, monkeypatch, backend, cached_hash):
    db_path = tmp_path / "tenants.db"
    monkeypatch.setattr(tenant_context.settings, "db_path", str(db_path))
    auth = security.AuthManager()
    monkeypatch.setattr(tenant_context, "auth_manager", auth)
    registry = tenant_context.TenantRegistry(backend=backend)
    registry.create_tenant("legacy-tenant", "Legacy", "legacy-key")
    current_hash = security.hash_api_key("legacy-key")
    legacy_hash = security.legacy_hash_api_key("legacy-key")
    registry.tenants["legacy-tenant"]["api_key_hash"] = legacy_hash
    if backend == "sqlite":
        with sqlite3.connect(db_path) as conn:
            conn.execute("UPDATE tenants SET api_key = ?", (legacy_hash,))
    auth.api_keys.clear()
    if cached_hash:
        auth.register_api_key_hash(
            legacy_hash if cached_hash == "legacy" else current_hash, "legacy-tenant"
        )

    assert registry.get_tenant_by_api_key("wrong-key") is None
    assert registry.tenants["legacy-tenant"]["api_key_hash"] == legacy_hash
    tenant = registry.get_tenant_by_api_key("legacy-key")
    assert tenant["api_key_hash"] == current_hash
    assert auth.api_keys == {current_hash: "legacy-tenant"}
    if backend == "sqlite":
        with sqlite3.connect(db_path) as conn:
            assert conn.execute("SELECT api_key FROM tenants").fetchone() == (current_hash,)
    auth.revoke_api_key("legacy-key")
    assert not auth.api_keys


@pytest.mark.parametrize("operation", ["blocked", "redacted", "tenant", "retrieval"])
def test_alerted_log_sinks_strip_controls(monkeypatch, caplog, operation):
    caplog.set_level(logging.DEBUG)
    if operation == "blocked":
        monkeypatch.setattr(security.policy_enforcer, "check_blocked_patterns", lambda _: _HOSTILE)
        assert security.validate_prompt("prompt", _HOSTILE) == (False, _HOSTILE)
    elif operation == "redacted":
        monkeypatch.setattr(
            security.policy_enforcer,
            "redact_sensitive_content",
            lambda _: ("redacted", [_HOSTILE]),
        )
        assert security.redact_content("prompt", _HOSTILE) == ("redacted", [_HOSTILE])
    elif operation == "tenant":
        monkeypatch.setattr(tenant_context, "auth_manager", security.AuthManager())
        registry = tenant_context.TenantRegistry(backend="memory")
        registry.create_tenant(_HOSTILE, "Tenant", "test-key")
        caplog.clear()
        assert registry.update_tenant(_HOSTILE, name="Updated") is not None
    else:
        adapter = RetrievalAdapter.__new__(RetrievalAdapter)
        adapter.engine = Mock()
        adapter.engine.search.side_effect = ValueError(_HOSTILE)
        assert adapter.query(_HOSTILE, "query") == []

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name.startswith("services.msp_gateway")
    ]
    assert messages
    assert all(_CONTROLS.search(message) is None for message in messages)
    if operation == "retrieval":
        assert len(messages) == 2
