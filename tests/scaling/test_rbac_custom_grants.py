"""Regression coverage for scoped, expiring custom permission evaluation."""

from unittest.mock import patch

import pytest

from codex.scaling.infrastructure.rbac_engine import (
    AccessLevel,
    Permission,
    RBACEngine,
    ResourceType,
    RoleType,
)


@pytest.fixture
def rbac():
    """Give both users read-only roles in both tenants."""
    engine = RBACEngine()
    for user in ("user1", "user2"):
        for tenant in ("tenant1", "tenant2"):
            engine.grant_role(user, tenant, RoleType.VIEWER)
    return engine


def test_custom_grant_expires_at_boundary(rbac):
    permission = Permission(ResourceType.POD, "write", AccessLevel.WRITE)
    rbac.add_custom_permission_grant("user1", "tenant1", permission, expires_at=100.0)
    with patch("codex.scaling.infrastructure.rbac_engine.time.time", return_value=99.0):
        assert rbac.check_permission("user1", "tenant1", ResourceType.POD, "write")[0]
    with patch("codex.scaling.infrastructure.rbac_engine.time.time", return_value=100.0):
        assert not rbac.check_permission("user1", "tenant1", ResourceType.POD, "write")[0]


@pytest.mark.parametrize(
    "user,tenant,resource,action",
    [
        ("user2", "tenant1", ResourceType.POD, "write"),
        ("user1", "tenant2", ResourceType.POD, "write"),
        ("user1", "tenant1", ResourceType.SERVICE, "write"),
        ("user1", "tenant1", ResourceType.POD, "delete"),
    ],
)
def test_custom_grant_does_not_escape_scope(rbac, user, tenant, resource, action):
    rbac.add_custom_permission_grant(
        "user1", "tenant1", Permission(ResourceType.POD, "write", AccessLevel.WRITE)
    )
    assert not rbac.check_permission(user, tenant, resource, action)[0]


@pytest.mark.parametrize("deny_source", ["role", "custom"])
def test_explicit_denial_takes_precedence(rbac, deny_source):
    denied = Permission(ResourceType.POD, "write", AccessLevel.DENY)
    if deny_source == "role":
        rbac.roles[RoleType.VIEWER].permissions.add(denied)
    else:
        rbac.add_custom_permission_grant("user1", "tenant1", denied)
    rbac.add_custom_permission_grant(
        "user1", "tenant1", Permission(ResourceType.POD, "write", AccessLevel.ADMIN)
    )
    allowed, reason = rbac.check_permission("user1", "tenant1", ResourceType.POD, "write")
    assert not allowed
    assert "explicitly denied" in reason


def test_highest_matching_grant_is_used(rbac):
    for level in (AccessLevel.READ, AccessLevel.WRITE):
        rbac.add_custom_permission_grant(
            "user1", "tenant1", Permission(ResourceType.POD, "write", level)
        )
    assert rbac.check_permission("user1", "tenant1", ResourceType.POD, "write")[0]


def test_custom_grant_requires_assigned_role(rbac):
    rbac.add_custom_permission_grant(
        "user1", "tenant1", Permission(ResourceType.POD, "write", AccessLevel.WRITE)
    )
    rbac.revoke_role("user1", "tenant1")
    assert not rbac.check_permission("user1", "tenant1", ResourceType.POD, "write")[0]
