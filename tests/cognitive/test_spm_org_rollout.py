"""S109 org rollout tests for StructuralPolicyManager.

Tests that COGNITIVE_BRAIN_ALLOWED_ACTORS env var correctly elevates actors
to ORG_OWNER tier without code changes (GitHub repo variable pattern).
"""

from __future__ import annotations

from codex.cognitive.structural_policy_manager import PermissionTier, StructuralPolicyManager

# ---------------------------------------------------------------------------
# Env var org rollout
# ---------------------------------------------------------------------------


def test_env_actors_elevated_to_org_owner(monkeypatch):
    """Actors in COGNITIVE_BRAIN_ALLOWED_ACTORS get ORG_OWNER tier."""
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", "alice,bob")
    spm = StructuralPolicyManager()
    assert spm.get_tier("alice") == PermissionTier.ORG_OWNER, "Condition must be true"
    assert spm.get_tier("bob") == PermissionTier.ORG_OWNER, "Condition must be true"


def test_env_actors_with_whitespace(monkeypatch):
    """Whitespace around actor names is stripped."""
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", " alice , bob , carol ")
    spm = StructuralPolicyManager()
    assert spm.get_tier("alice") == PermissionTier.ORG_OWNER, "Condition must be true"
    assert spm.get_tier("bob") == PermissionTier.ORG_OWNER, "Condition must be true"
    assert spm.get_tier("carol") == PermissionTier.ORG_OWNER, "Condition must be true"


def test_env_actors_system_owner_not_downgraded(monkeypatch):
    """SYSTEM_OWNER (mbaetiong) cannot be downgraded via env var."""
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", "mbaetiong")
    spm = StructuralPolicyManager()
    assert spm.get_tier("mbaetiong") == PermissionTier.SYSTEM_OWNER, "Condition must be true"


def test_env_actors_empty_string(monkeypatch):
    """Empty COGNITIVE_BRAIN_ALLOWED_ACTORS is a no-op."""
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", "")
    spm = StructuralPolicyManager()
    assert spm.get_tier("unknown") == PermissionTier.DENIED, "Condition must be true"


def test_env_actors_not_set(monkeypatch):
    """Unset COGNITIVE_BRAIN_ALLOWED_ACTORS leaves defaults intact."""
    monkeypatch.delenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", raising=False)
    spm = StructuralPolicyManager()
    assert spm.get_tier("mbaetiong") == PermissionTier.SYSTEM_OWNER, "Condition must be true"
    assert spm.get_tier("random_user") == PermissionTier.DENIED, "Condition must be true"


def test_env_actor_can_store_memory(monkeypatch, tmp_path):
    """ORG_OWNER-tier actor from env var can store_memory."""
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", "alice")
    spm = StructuralPolicyManager(audit_log=tmp_path / "audit.jsonl")
    assert spm.evaluate_permission("alice", "store_memory") is True


def test_env_actor_cannot_promote_pattern(monkeypatch, tmp_path):
    """ORG_OWNER-tier actor from env var cannot promote_pattern (SO only)."""
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", "alice")
    spm = StructuralPolicyManager(audit_log=tmp_path / "audit.jsonl")
    assert spm.evaluate_permission("alice", "promote_pattern") is False


def test_env_actor_can_report_completion(monkeypatch, tmp_path):
    """ORG_OWNER-tier actor can report_completion."""
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", "alice")
    spm = StructuralPolicyManager(audit_log=tmp_path / "audit.jsonl")
    assert spm.evaluate_permission("alice", "report_completion") is True


def test_env_actor_github_actions_cannot_inject_session_context(monkeypatch, tmp_path):
    """github-actions[bot] is restricted from inject_session_context."""
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", "github-actions[bot]")
    spm = StructuralPolicyManager(audit_log=tmp_path / "audit.jsonl")
    assert spm.evaluate_permission("github-actions[bot]", "inject_session_context") is False


def test_env_actor_github_actions_stays_read_only(monkeypatch):
    """github-actions[bot] remains READ_ONLY_AGENT even when listed in env."""
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", "github-actions[bot]")
    spm = StructuralPolicyManager()
    assert spm.get_tier("github-actions[bot]") == PermissionTier.READ_ONLY_AGENT, "Condition must be true"


def test_env_actor_can_inject_session_context(monkeypatch, tmp_path):
    """ORG_OWNER-tier actor can inject_session_context."""
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", "copilot-swe-agent[bot]")
    spm = StructuralPolicyManager(audit_log=tmp_path / "audit.jsonl")
    assert spm.evaluate_permission("copilot-swe-agent[bot]", "inject_session_context") is True


def test_parse_allowed_actors_single():
    """Single actor parsed correctly."""
    result = StructuralPolicyManager._parse_allowed_actors("mbaetiong")
    assert result == ["mbaetiong"], "Result must not be empty"


def test_parse_allowed_actors_multiple():
    """Multiple actors parsed correctly."""
    result = StructuralPolicyManager._parse_allowed_actors("alice,bob,carol")
    assert result == ["alice", "bob", "carol"]


def test_parse_allowed_actors_empty():
    """Empty string returns empty list."""
    assert StructuralPolicyManager._parse_allowed_actors("") == [], "Condition must be true"


def test_parse_allowed_actors_trailing_comma():
    """Trailing comma is ignored."""
    result = StructuralPolicyManager._parse_allowed_actors("alice,bob,")
    assert result == ["alice", "bob"]


# ---------------------------------------------------------------------------
# COGNITIVE_BRAIN_INJECTION_ENABLED feature flag
# ---------------------------------------------------------------------------


def test_injection_enabled_flag_true(monkeypatch):
    """COGNITIVE_BRAIN_INJECTION_ENABLED=true allows injection."""
    from unittest.mock import MagicMock, patch

    monkeypatch.setenv("COGNITIVE_BRAIN_INJECTION_ENABLED", "true")
    monkeypatch.setenv("COGNITIVE_BRAIN_ALLOWED_ACTORS", "mbaetiong")

    from codex.cognitive.mcp_session_bridge import register_mcp_session_hook

    with (
        patch("codex.cognitive.mcp_session_bridge.AgentBrainAPI"),
        patch("codex.cognitive.mcp_session_bridge.SessionContextInjector") as MockInj,
    ):
        mock_payload = MagicMock()
        mock_payload.to_prompt_block.return_value = "## Brain Block"
        mock_payload.session_id = "s109"
        mock_payload.injected_patterns = ["P-043"]
        MockInj.return_value.inject.return_value = mock_payload

        ctx = {"actor": "mbaetiong", "system_prompt": "Base prompt"}
        result = register_mcp_session_hook(ctx)
        assert result.get("cognitive_brain_injected") is True, "Result must not be empty"


def test_injection_disabled_flag_false(monkeypatch):
    """COGNITIVE_BRAIN_INJECTION_ENABLED=false skips injection entirely."""
    monkeypatch.setenv("COGNITIVE_BRAIN_INJECTION_ENABLED", "false")

    from codex.cognitive.mcp_session_bridge import register_mcp_session_hook

    ctx = {"actor": "mbaetiong", "system_prompt": "Base prompt"}
    result = register_mcp_session_hook(ctx)
    # Should be returned unmodified
    assert "cognitive_brain_injected" not in result, "Result must not be empty"
    assert result["system_prompt"] == "Base prompt", "Result must not be empty"


def test_injection_disabled_flag_zero(monkeypatch):
    """COGNITIVE_BRAIN_INJECTION_ENABLED=0 skips injection."""
    monkeypatch.setenv("COGNITIVE_BRAIN_INJECTION_ENABLED", "0")

    from codex.cognitive.mcp_session_bridge import register_mcp_session_hook

    ctx = {"actor": "mbaetiong"}
    result = register_mcp_session_hook(ctx)
    assert "cognitive_brain_injected" not in result, "Result must not be empty"
