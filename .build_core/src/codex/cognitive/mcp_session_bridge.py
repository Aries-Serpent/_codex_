"""MCP Server session bridge for cognitive brain context injection.

Phase 1, Pre-commit 3 (S108): Pilot Deployment — Internal Airtight System.

Registers ``SessionContextInjector`` as a session lifecycle hook within the
GitHub Copilot MCP Server protocol.

Access control
--------------
* Actor must be in ``ALLOWED_ACTORS`` (``mbaetiong`` for the internal pilot).
* Fail-open: unauthorised actors receive an unmodified context — the session
  is never broken, it simply runs without cognitive brain enrichment.

PDA loop integration
--------------------
* PLAN: actor validated before any API call.
* DO: context payload assembled and injected into ``system_prompt``.
* ASSESS: injection success flagged on ``mcp_context``; audit can inspect
  ``cognitive_brain_injected``.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from codex.cognitive.agent_brain_api import AgentBrainAPI
from codex.cognitive.session_hook import SessionContextInjector
from codex.cognitive.structural_policy_manager import default_policy_manager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Access control — delegated to StructuralPolicyManager (Phase 5, S108)
# ---------------------------------------------------------------------------

#: Kept for backward-compat; policy decisions now go through
#: default_policy_manager.evaluate_permission().
ALLOWED_ORG: str = "Aries-Serpent"
ALLOWED_ACTORS: frozenset[str] = frozenset({"mbaetiong"})


def validate_actor(actor: str) -> bool:
    """Return True if *actor* is authorised to inject session context.

    Delegates to ``StructuralPolicyManager`` (Phase 5, S108).
    Falls back to ``ALLOWED_ACTORS`` allowlist if the policy manager is
    unavailable (belt-and-suspenders).
    """
    # Primary: StructuralPolicyManager RBAC check with audit log
    try:
        return default_policy_manager.evaluate_permission(actor, "inject_session_context")
    except Exception as e:  # codeql[py/catch-all-except]
        logger.warning(
            f"Policy manager unavailable for actor '{actor}', falling back to allowlist: {type(e).__name__}: {e}"  # noqa: E501
        )
        return actor in ALLOWED_ACTORS


# ---------------------------------------------------------------------------
# Main hook
# ---------------------------------------------------------------------------


def register_mcp_session_hook(mcp_context: dict[str, Any]) -> dict[str, Any]:
    """MCP Server lifecycle hook: called at session initialisation.

    Validates actor, assembles ``SessionContextPayload``, and returns an
    enriched *mcp_context* with the cognitive-brain block appended to the
    ``"system_prompt"`` key.

    Parameters
    ----------
    mcp_context:
        Incoming MCP session context dictionary.  Expected keys (optional):

        * ``"actor"`` — GitHub username of the session initiator.
        * ``"session_number"`` — ordinal session counter.
        * ``"pr_title"`` — PR title for keyword-based pattern matching.
        * ``"pr_body"`` — PR body for keyword-based pattern matching.
        * ``"system_prompt"`` — existing system prompt to append to.

    Returns
    -------
    dict
        The original ``mcp_context`` dictionary, possibly enriched with:

        * ``"system_prompt"`` — appended cognitive brain block (authorised).
        * ``"cognitive_brain_injected": True`` — injection success flag.
        * ``"cognitive_brain_session_id"`` — payload session ID.

    Notes
    -----
    Fail-open design: unauthorised actors receive the *unmodified* context.
    Any exception during injection is caught and logged; the original context
    is returned to avoid breaking the session.

    S109 org rollout: respects ``COGNITIVE_BRAIN_INJECTION_ENABLED`` env var
    (repo variable).  Defaults to ``true``; set to ``false`` to disable globally
    without a code change.

    AfterMath: records hook invocation for loop-continuity metrics.
    """
    # S109: check global injection feature flag
    injection_enabled = os.environ.get("COGNITIVE_BRAIN_INJECTION_ENABLED", "true").lower()
    if injection_enabled not in ("1", "true", "yes"):
        logger.debug(
            "Cognitive brain injection disabled via COGNITIVE_BRAIN_INJECTION_ENABLED=%s",
            injection_enabled,
        )
        return mcp_context

    actor = mcp_context.get("actor", "")
    if not validate_actor(actor):
        logger.debug("Cognitive brain injection skipped for actor: %s", actor)
        return mcp_context

    try:
        brain = AgentBrainAPI(agent_id="copilot-coding-agent")
        injector = SessionContextInjector(brain_api=brain)

        session_meta: dict[str, Any] = {
            "session_number": mcp_context.get("session_number", 0),
            "pr_title": mcp_context.get("pr_title", ""),
            "pr_body": mcp_context.get("pr_body", ""),
            "actor": actor,
        }

        # PDA: DO — inject context
        payload = injector.inject(session_meta)

        # Append cognitive brain block to system prompt
        existing_prompt: str = mcp_context.get("system_prompt", "")
        mcp_context["system_prompt"] = existing_prompt + "\n\n" + payload.to_prompt_block()
        mcp_context["cognitive_brain_injected"] = True
        mcp_context["cognitive_brain_session_id"] = payload.session_id

        logger.info(
            "Cognitive brain context injected for actor=%s session=%s patterns=%s",
            actor,
            payload.session_id,
            payload.injected_patterns,
        )

    except (ValueError, TypeError, RuntimeError) as exc:
        logger.error(
            "Cognitive brain injection failed for actor=%s: %s — returning original context.",
            actor,
            exc,
        )

    return mcp_context
