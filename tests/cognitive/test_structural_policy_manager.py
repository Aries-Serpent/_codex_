"""Tests for StructuralPolicyManager — RBAC engine (S108, Phase 5 planset).

Covers all permission tiers, evaluate_permission paths, TTL cache,
grant/revoke operations, audit log, and edge cases.

Run: pytest tests/cognitive/test_structural_policy_manager.py -v
"""

from __future__ import annotations

import json
import time

import pytest

from codex.cognitive.structural_policy_manager import (
    ACTION_TIER_MAP,
    PermissionTier,
    StructuralPolicyManager,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def spm(tmp_path):
    """Fresh StructuralPolicyManager with audit log in tmp_path."""
    return StructuralPolicyManager(
        cache_ttl_seconds=300,
        audit_log=tmp_path / "rbac_audit.jsonl",
    )


@pytest.fixture()
def spm_with_extras(tmp_path):
    return StructuralPolicyManager(
        cache_ttl_seconds=300,
        audit_log=tmp_path / "rbac_audit.jsonl",
        extra_actors={
            "org-member-1": PermissionTier.ORG_OWNER,
            "delegate-bot": PermissionTier.DELEGATE_ADMIN,
            "ci-reader": PermissionTier.READ_ONLY_AGENT,
        },
    )


# ---------------------------------------------------------------------------
# PermissionTier ordering
# ---------------------------------------------------------------------------


def test_permission_tier_ordering():
    """SYSTEM_OWNER < ORG_OWNER < DELEGATE_ADMIN < READ_ONLY_AGENT < DENIED."""
    assert PermissionTier.SYSTEM_OWNER < PermissionTier.ORG_OWNER, "SYSTEM_OWNER is not valid"
    assert PermissionTier.ORG_OWNER < PermissionTier.DELEGATE_ADMIN, "ORG_OWNER is not valid"
    assert PermissionTier.DELEGATE_ADMIN < PermissionTier.READ_ONLY_AGENT, "DELEGATE_ADMIN is not valid"
    assert PermissionTier.READ_ONLY_AGENT < PermissionTier.DENIED, "READ_ONLY_AGENT is not valid"


# ---------------------------------------------------------------------------
# Role resolution
# ---------------------------------------------------------------------------


def test_system_owner_resolved(spm):
    assert spm.get_tier("mbaetiong") == PermissionTier.SYSTEM_OWNER, "Condition must be true"


def test_github_actions_bot_resolved(spm):
    assert spm.get_tier("github-actions[bot]") == PermissionTier.READ_ONLY_AGENT, "Condition must be true"


def test_unknown_actor_is_denied(spm):
    assert spm.get_tier("random-stranger") == PermissionTier.DENIED, "Condition must be true"


def test_extra_actors_org_owner(spm_with_extras):
    assert spm_with_extras.get_tier("org-member-1") == PermissionTier.ORG_OWNER, "Condition must be true"


def test_extra_actors_delegate(spm_with_extras):
    assert spm_with_extras.get_tier("delegate-bot") == PermissionTier.DELEGATE_ADMIN, "Condition must be true"


def test_extra_actors_read_only(spm_with_extras):
    assert spm_with_extras.get_tier("ci-reader") == PermissionTier.READ_ONLY_AGENT, "Condition must be true"


# ---------------------------------------------------------------------------
# evaluate_permission — SYSTEM_OWNER (all allowed)
# ---------------------------------------------------------------------------


def test_system_owner_can_promote_pattern(spm):
    assert spm.evaluate_permission("mbaetiong", "promote_pattern") is True


def test_system_owner_can_modify_policy(spm):
    assert spm.evaluate_permission("mbaetiong", "modify_policy") is True


def test_system_owner_can_get_session_context(spm):
    assert spm.evaluate_permission("mbaetiong", "get_session_context") is True


def test_system_owner_can_inject_session_context(spm):
    assert spm.evaluate_permission("mbaetiong", "inject_session_context") is True


def test_system_owner_can_store_memory(spm):
    assert spm.evaluate_permission("mbaetiong", "store_memory") is True


# ---------------------------------------------------------------------------
# evaluate_permission — READ_ONLY_AGENT (limited)
# ---------------------------------------------------------------------------


def test_read_only_agent_can_read_context(spm):
    assert spm.evaluate_permission("github-actions[bot]", "get_session_context") is True


def test_read_only_agent_cannot_store_memory(spm):
    assert spm.evaluate_permission("github-actions[bot]", "store_memory") is False


def test_read_only_agent_cannot_promote_pattern(spm):
    assert spm.evaluate_permission("github-actions[bot]", "promote_pattern") is False


def test_read_only_agent_cannot_inject_context(spm):
    assert spm.evaluate_permission("github-actions[bot]", "inject_session_context") is False


# ---------------------------------------------------------------------------
# evaluate_permission — DENIED actor
# ---------------------------------------------------------------------------


def test_denied_actor_cannot_read(spm):
    assert spm.evaluate_permission("unknown-bot", "get_session_context") is False


def test_denied_actor_cannot_write(spm):
    assert spm.evaluate_permission("unknown-bot", "store_memory") is False


def test_empty_actor_is_denied(spm):
    assert spm.evaluate_permission("", "get_session_context") is False


def test_empty_action_is_denied(spm):
    assert spm.evaluate_permission("mbaetiong", "") is False


def test_unknown_action_is_denied(spm):
    """Unknown actions must deny by default (fail-deny)."""
    assert spm.evaluate_permission("mbaetiong", "nonexistent_action") is False


# ---------------------------------------------------------------------------
# Grant / Revoke operations
# ---------------------------------------------------------------------------


def test_grant_org_owner(spm):
    spm.grant_org_owner("new-member")
    assert spm.get_tier("new-member") == PermissionTier.ORG_OWNER, "Condition must be true"


def test_grant_delegate_admin(spm):
    spm.grant_delegate_admin("new-delegate")
    assert spm.get_tier("new-delegate") == PermissionTier.DELEGATE_ADMIN, "Condition must be true"


def test_revoke_downgrades_to_read_only(spm):
    spm.grant_org_owner("promoted-user")
    spm.revoke("promoted-user")
    assert spm.get_tier("promoted-user") == PermissionTier.READ_ONLY_AGENT, "Condition must be true"


def test_grant_evicts_cache(spm):
    # First resolution populates cache
    _ = spm.get_tier("cache-test-user")
    # Grant should evict cache
    spm.grant_org_owner("cache-test-user")
    # New resolution must return updated tier
    assert spm.get_tier("cache-test-user") == PermissionTier.ORG_OWNER, "Condition must be true"


# ---------------------------------------------------------------------------
# TTL cache
# ---------------------------------------------------------------------------


def test_ttl_cache_serves_cached_value(spm):
    """Second call for same actor returns cached result."""
    tier1 = spm.get_tier("mbaetiong")
    tier2 = spm.get_tier("mbaetiong")
    assert tier1 == tier2 == PermissionTier.SYSTEM_OWNER, "tier1 is not valid"


def test_ttl_cache_expires(tmp_path):
    """Expired cache entries are re-resolved from actor map."""
    spm = StructuralPolicyManager(cache_ttl_seconds=0, audit_log=tmp_path / "a.jsonl")
    tier1 = spm.get_tier("mbaetiong")
    time.sleep(0.01)  # TTL=0 expires immediately
    tier2 = spm.get_tier("mbaetiong")
    assert tier1 == tier2, "tier1 is not valid"


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------


def test_audit_log_written_on_allow(spm):
    spm.evaluate_permission("mbaetiong", "get_session_context")
    entries = spm.read_audit_log()
    assert len(entries) >= 1, "Entries must not be empty"
    last = entries[-1]
    assert last["actor"] == "mbaetiong", "Condition must be true"
    assert last["action"] == "get_session_context", "Condition must be true"
    assert last["allowed"] is True, "Condition must be true"


def test_audit_log_written_on_deny(spm):
    spm.evaluate_permission("unknown", "store_memory")
    entries = spm.read_audit_log()
    assert any(e["actor"] == "unknown" and e["allowed"] is False for e in entries), "Condition must be true"


def test_audit_log_is_valid_jsonl(spm, tmp_path):
    spm.evaluate_permission("mbaetiong", "promote_pattern")
    spm.evaluate_permission("unknown", "modify_policy")
    log_path = tmp_path / "rbac_audit.jsonl"
    lines = log_path.read_text().splitlines()
    for line in lines:
        parsed = json.loads(line)
        assert "actor" in parsed, "Condition must be true"
        assert "action" in parsed, "Condition must be true"
        assert "allowed" in parsed, "Condition must be true"


def test_read_audit_log_empty_when_no_file(tmp_path):
    spm = StructuralPolicyManager(audit_log=tmp_path / "nonexistent.jsonl")
    assert spm.read_audit_log() == [], "Condition must be true"


# ---------------------------------------------------------------------------
# Action tier map completeness
# ---------------------------------------------------------------------------


def test_all_actions_in_map_are_valid_tiers():
    for action, tier in ACTION_TIER_MAP.items():
        assert isinstance(tier, PermissionTier), f"{action} has invalid tier {tier!r}"


def test_promote_pattern_requires_system_owner():
    assert ACTION_TIER_MAP["promote_pattern"] == PermissionTier.SYSTEM_OWNER, "Condition must be true"


def test_get_session_context_allows_read_only():
    assert ACTION_TIER_MAP["get_session_context"] == PermissionTier.READ_ONLY_AGENT, "Condition must be true"
