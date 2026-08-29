"""Integration tests for MCP session bridge (Pre-commit 4, S108).

Source: comment-3977050660 Phase 2 Pre-commit 4.

Validates that:
- Authorised actor (mbaetiong) gets cognitive brain block injected.
- Unauthorised actor passes through unmodified.
- HF PR surfaces P-043 in injected patterns.
- API failure triggers graceful handling (no session crash).
"""

from __future__ import annotations

import pytest

from codex.cognitive.mcp_session_bridge import register_mcp_session_hook, validate_actor

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def authorized_context():
    return {
        "actor": "mbaetiong",
        "session_number": 108,
        "pr_title": "HuggingFace training pipeline fix",
        "pr_body": "Fixes shard crash in distributed training",
        "system_prompt": "You are a helpful coding assistant.",
    }


@pytest.fixture()
def unauthorized_context():
    return {
        "actor": "external-contributor",
        "session_number": 1,
        "pr_title": "Minor docs fix",
        "system_prompt": "You are a helpful coding assistant.",
    }


# ---------------------------------------------------------------------------
# validate_actor
# ---------------------------------------------------------------------------


def test_validate_actor_system_owner():
    assert validate_actor("mbaetiong") is True, "validate_act is not valid"


def test_validate_actor_unknown():
    assert validate_actor("external-contributor") is False, "validate_act is not valid"


def test_validate_actor_empty():
    assert validate_actor("") is False, "validate_act is not valid"


# ---------------------------------------------------------------------------
# register_mcp_session_hook — authorised
# ---------------------------------------------------------------------------


def test_authorized_actor_receives_injection(authorized_context, mocker):
    """Authorised actor gets cognitive brain block appended to system prompt."""
    mock_api_cls = mocker.patch(
        "codex.cognitive.mcp_session_bridge.AgentBrainAPI",
        autospec=True,
    )
    mock_api = mock_api_cls.return_value
    mock_api.get_session_context.return_value = mocker.MagicMock(
        session_id="s108",
        active_patterns=[{"id": "P-043", "introduced_session": 107}],
        continuation_from="",
    )

    result = register_mcp_session_hook(authorized_context)

    assert result["cognitive_brain_injected"] is True, "Result must not be empty"
    assert "🧠 Cognitive Brain Context" in result["system_prompt"], "Result must not be empty"
    assert "You are a helpful coding assistant." in result["system_prompt"], "Result must not be empty"


def test_authorized_actor_session_id_recorded(authorized_context, mocker):
    mock_api_cls = mocker.patch(
        "codex.cognitive.mcp_session_bridge.AgentBrainAPI",
        autospec=True,
    )
    mock_api_cls.return_value.get_session_context.return_value = mocker.MagicMock(
        session_id="s108",
        active_patterns=[],
        continuation_from="",
    )
    result = register_mcp_session_hook(authorized_context)
    assert "cognitive_brain_session_id" in result, "Result must not be empty"
    assert result["cognitive_brain_session_id"] == "s108", "Result must not be empty"


def test_hf_pr_surfaces_pattern_p043(authorized_context, mocker):
    """PR mentioning HuggingFace must surface P-043 in the injected block."""
    mock_api_cls = mocker.patch(
        "codex.cognitive.mcp_session_bridge.AgentBrainAPI",
        autospec=True,
    )
    mock_api = mock_api_cls.return_value
    mock_api.get_session_context.return_value = mocker.MagicMock(
        session_id="s108",
        active_patterns=[
            {"id": "P-043", "introduced_session": 107},
            {"id": "P-038", "introduced_session": 105},
        ],
        continuation_from="",
    )

    result = register_mcp_session_hook(authorized_context)
    assert "P-043" in result["system_prompt"], "Result must not be empty"


# ---------------------------------------------------------------------------
# register_mcp_session_hook — unauthorised
# ---------------------------------------------------------------------------


def test_unauthorized_actor_passes_through_unmodified(unauthorized_context):
    """Unauthorised actor: context returned without modification (fail-open)."""
    original_prompt = unauthorized_context["system_prompt"]
    result = register_mcp_session_hook(unauthorized_context)

    assert "cognitive_brain_injected" not in result, "Result must not be empty"
    assert result["system_prompt"] == original_prompt, "Result must not be empty"


def test_unauthorized_actor_no_session_id(unauthorized_context):
    result = register_mcp_session_hook(unauthorized_context)
    assert "cognitive_brain_session_id" not in result, "Result must not be empty"


# ---------------------------------------------------------------------------
# register_mcp_session_hook — failure handling
# ---------------------------------------------------------------------------


def test_api_failure_does_not_crash_session(authorized_context, mocker):
    """API failure must not raise; session continues with original context."""
    # Use non-autospec mock so store_memory is freely callable during reconstruction
    mock_api = mocker.MagicMock()
    mock_api.get_session_context.side_effect = RuntimeError("Simulated failure")
    mock_api.store_memory.return_value = None
    mocker.patch(
        "codex.cognitive.mcp_session_bridge.AgentBrainAPI",
        return_value=mock_api,
    )

    # Must not raise
    result = register_mcp_session_hook(authorized_context)

    # Session prompt must still be present
    assert "system_prompt" in result, "Result must not be empty"


def test_missing_system_prompt_key_handled(mocker):
    """Context without 'system_prompt' key must not crash."""
    ctx = {"actor": "mbaetiong", "session_number": 108}
    mocker.patch(
        "codex.cognitive.mcp_session_bridge.AgentBrainAPI",
        autospec=True,
    ).return_value.get_session_context.return_value = mocker.MagicMock(
        session_id="s108",
        active_patterns=[],
        continuation_from="",
    )
    result = register_mcp_session_hook(ctx)
    assert "system_prompt" in result, "Result must not be empty"
