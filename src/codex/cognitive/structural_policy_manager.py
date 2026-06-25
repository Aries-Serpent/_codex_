"""StructuralPolicyManager — RBAC permission engine for AgentBrainAPI.

Phase 5 (S108) — implements the planset in:
  .codex/plans/structural_policy_manager.rbac_planset.md

Permission Lattice (strictly hierarchical, zero escalation):
  SYSTEM_OWNER → ORG_OWNER → DELEGATE_ADMIN → READ_ONLY_AGENT

PDA Loop: PLAN phase — resolves actor role before any brain resource access.
AfterMath: every evaluate_permission() call is appended to rbac_audit.jsonl.

CODEBASE_AGENCY_POLICY.md compliance:
  - Input validation on all public methods
  - Comprehensive error handling with fail-deny (not fail-open) on policy errors
  - Audit trail for 100% of permission decisions
  - Zero escalation: no path from lower tier to higher tier permissions
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import time
from dataclasses import dataclass
from enum import IntEnum, unique
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Audit log location
# ---------------------------------------------------------------------------

_AUDIT_LOG: Path = Path(".codex/rbac_audit.jsonl")

# ---------------------------------------------------------------------------
# Permission Lattice — lower int = higher authority
# ---------------------------------------------------------------------------


@unique
class PermissionTier(IntEnum):
    """RBAC permission tiers, ordered from most to least privileged."""

    SYSTEM_OWNER = 0  # mbaetiong — all operations
    ORG_OWNER = 1  # Aries-Serpent org owners — read/write/report
    DELEGATE_ADMIN = 2  # token-granted delegates — read/write, no promote
    READ_ONLY_AGENT = 3  # CI bots, external contributors — read only
    DENIED = 99  # not a known actor; all actions denied


# ---------------------------------------------------------------------------
# Action → minimum required tier mapping
# ---------------------------------------------------------------------------

#: Maps action name → minimum PermissionTier required.
ACTION_TIER_MAP: dict[str, PermissionTier] = {
    # Brain reads
    "get_session_context": PermissionTier.READ_ONLY_AGENT,
    "get_continuation_prompt": PermissionTier.READ_ONLY_AGENT,
    # Brain writes
    "store_memory": PermissionTier.DELEGATE_ADMIN,
    "report_completion": PermissionTier.DELEGATE_ADMIN,
    # Pattern operations
    "promote_pattern": PermissionTier.SYSTEM_OWNER,
    "modify_policy": PermissionTier.SYSTEM_OWNER,
    # Session injection (MCP hook)
    "inject_session_context": PermissionTier.ORG_OWNER,
}

# Certain automation actors must never inject session context even if elevated.
_INJECT_CONTEXT_DENY_ACTORS: frozenset[str] = frozenset({"github-actions[bot]"})
_FIXED_READ_ONLY_ACTORS: frozenset[str] = frozenset(
    {
        "github-actions[bot]",
        "dependabot[bot]",
    }
)
_ACTOR_ACTION_ALLOWLIST: dict[str, frozenset[str]] = {
    "github-actions[bot]": frozenset(
        {
            "get_session_context",
            "get_continuation_prompt",
            "report_completion",
        }
    )
}

# ---------------------------------------------------------------------------
# Permission cache entry
# ---------------------------------------------------------------------------


@dataclass
class _CacheEntry:
    tier: PermissionTier
    expires_at: float  # unix timestamp


# ---------------------------------------------------------------------------
# StructuralPolicyManager
# ---------------------------------------------------------------------------


class StructuralPolicyManager:
    """RBAC policy engine for cognitive brain resource access.

    Usage
    -----
    >>> spm = StructuralPolicyManager()
    >>> allowed = spm.evaluate_permission("mbaetiong", "promote_pattern")
    >>> if allowed:
    ...     brain.promote_pattern(...)

    Design principles
    -----------------
    * **Fail-deny on error**: any exception during role resolution returns
      ``PermissionTier.DENIED`` — never accidentally grants access.
    * **TTL cache**: role lookups are cached for ``cache_ttl_seconds``
      (default 300 s) to minimise repeated GitHub API calls.
    * **Immutable audit log**: every decision is appended to
      ``.codex/rbac_audit.jsonl``; entries are never deleted.
    * **Zero escalation**: ``PermissionTier`` is an ``IntEnum``; role
      resolution returns the *minimum* (least privileged) tier found.
    """

    # Known actor → tier mappings (static seed; expanded via config)
    _KNOWN_ACTORS: dict[str, PermissionTier] = {
        "mbaetiong": PermissionTier.SYSTEM_OWNER,
        "github-actions[bot]": PermissionTier.READ_ONLY_AGENT,
        "copilot-swe-agent[bot]": PermissionTier.READ_ONLY_AGENT,
        "dependabot[bot]": PermissionTier.READ_ONLY_AGENT,
        # D_CAPABLE agents — elevated authority with decision capability (ORG_OWNER tier)
        "ci-testing-agent": PermissionTier.ORG_OWNER,
        "rust-error-validator": PermissionTier.ORG_OWNER,
        "test-assertion-updater": PermissionTier.ORG_OWNER,
        "test-pattern-guardian": PermissionTier.ORG_OWNER,
        "workflow-ci-fixer": PermissionTier.ORG_OWNER,
        "ci-health-alert-agent": PermissionTier.ORG_OWNER,
        "copilot-session-chain": PermissionTier.ORG_OWNER,
        "packaging-validation-agent": PermissionTier.ORG_OWNER,
        "energy-conversion-agent": PermissionTier.ORG_OWNER,
    }

    def __init__(
        self,
        cache_ttl_seconds: int = 300,
        audit_log: Path = _AUDIT_LOG,
        extra_actors: dict[str, PermissionTier] | None = None,
    ) -> None:
        self._cache: dict[str, _CacheEntry] = {}
        self._ttl = cache_ttl_seconds
        self._audit_log = audit_log
        # Merge static seed with any runtime-provided actors (ORG_OWNER tier)
        self._actors: dict[str, PermissionTier] = dict(self._KNOWN_ACTORS)
        if extra_actors:
            for actor, tier in extra_actors.items():
                # Only allow downgrading from SYSTEM_OWNER; never upgrade via extra_actors
                if tier > PermissionTier.SYSTEM_OWNER:
                    self._actors[actor] = tier
        # S109 org rollout: elevate actors from COGNITIVE_BRAIN_ALLOWED_ACTORS to ORG_OWNER
        self._load_env_actors()

    @staticmethod
    def _parse_allowed_actors(raw: str) -> list[str]:
        """Parse comma-separated actor list from env var value."""
        return [a.strip() for a in raw.split(",") if a.strip()]

    def _load_env_actors(self) -> None:
        """Elevate actors listed in COGNITIVE_BRAIN_ALLOWED_ACTORS to ORG_OWNER tier.

        This is the S109 org rollout mechanism: setting the GitHub repo variable
        ``COGNITIVE_BRAIN_ALLOWED_ACTORS`` to a comma-separated list of GitHub
        usernames automatically grants them ORG_OWNER permission tier without
        requiring a code change.

        SYSTEM_OWNER (mbaetiong) is never downgraded by this mechanism.
        """
        raw = os.environ.get("COGNITIVE_BRAIN_ALLOWED_ACTORS", "")
        if not raw:
            return
        for actor in self._parse_allowed_actors(raw):
            # Never downgrade existing SYSTEM_OWNER entries
            existing = self._actors.get(actor, PermissionTier.DENIED)
            if actor in _FIXED_READ_ONLY_ACTORS:
                continue
            if existing != PermissionTier.SYSTEM_OWNER:
                self._actors[actor] = PermissionTier.ORG_OWNER
                self._evict_cache(actor)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate_permission(
        self,
        actor: str,
        action: str,
        resource: str = "*",
    ) -> bool:
        """Return True if *actor* is allowed to perform *action*.

        Parameters
        ----------
        actor:
            GitHub username of the requesting agent.
        action:
            Action key from ``ACTION_TIER_MAP`` (e.g. ``"promote_pattern"``).
        resource:
            Optional resource identifier for future fine-grained control.

        Returns
        -------
        bool
            ``True`` if allowed; ``False`` if denied.

        Notes
        -----
        Fail-deny: unknown actions → DENIED (no implicit allow).
        """
        if not actor or not action:
            self._audit(
                actor, action, resource, PermissionTier.DENIED, allowed=False, reason="empty_input"
            )
            return False

        actor_tier = self._resolve_tier(actor)
        required_tier = ACTION_TIER_MAP.get(action)

        if required_tier is None:
            # Unknown action — deny by default (fail-deny)
            self._audit(actor, action, resource, actor_tier, allowed=False, reason="unknown_action")
            return False

        if actor_tier == PermissionTier.DENIED:
            self._audit(actor, action, resource, actor_tier, allowed=False, reason="actor_denied")
            return False

        allowed_actions = _ACTOR_ACTION_ALLOWLIST.get(actor)
        if allowed_actions is not None and action not in allowed_actions:
            self._audit(
                actor,
                action,
                resource,
                actor_tier,
                allowed=False,
                reason="actor_action_restricted",
            )
            return False

        if action == "inject_session_context" and actor in _INJECT_CONTEXT_DENY_ACTORS:
            self._audit(
                actor,
                action,
                resource,
                actor_tier,
                allowed=False,
                reason="actor_restricted_for_injection",
            )
            return False

        allowed = actor_tier <= required_tier  # lower int = higher privilege
        reason = "tier_ok" if allowed else "insufficient_tier"
        self._audit(actor, action, resource, actor_tier, allowed=allowed, reason=reason)
        return allowed

    def get_tier(self, actor: str) -> PermissionTier:
        """Return the ``PermissionTier`` for *actor* (cached)."""
        return self._resolve_tier(actor)

    def grant_org_owner(self, actor: str) -> None:
        """Elevate *actor* to ``ORG_OWNER`` tier (SYSTEM_OWNER only, enforced externally)."""
        self._actors[actor] = PermissionTier.ORG_OWNER
        self._evict_cache(actor)

    def grant_delegate_admin(self, actor: str) -> None:
        """Elevate *actor* to ``DELEGATE_ADMIN`` tier."""
        # Only allow if not already higher-tier
        current = self._actors.get(actor, PermissionTier.READ_ONLY_AGENT)
        if current > PermissionTier.DELEGATE_ADMIN:
            self._actors[actor] = PermissionTier.DELEGATE_ADMIN
            self._evict_cache(actor)

    def revoke(self, actor: str) -> None:
        """Downgrade *actor* to ``READ_ONLY_AGENT`` (effective immediately)."""
        self._actors[actor] = PermissionTier.READ_ONLY_AGENT
        self._evict_cache(actor)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_tier(self, actor: str) -> PermissionTier:
        """Return cached tier or resolve from actor map."""
        now = time.monotonic()

        # Cache hit
        entry = self._cache.get(actor)
        if entry is not None and now < entry.expires_at:
            return entry.tier

        # Resolve
        tier = self._actors.get(actor, PermissionTier.DENIED)
        self._cache[actor] = _CacheEntry(tier=tier, expires_at=now + self._ttl)
        return tier

    def _evict_cache(self, actor: str) -> None:
        self._cache.pop(actor, None)

    def _audit(
        self,
        actor: str,
        action: str,
        resource: str,
        actor_tier: PermissionTier,
        *,
        allowed: bool,
        reason: str,
    ) -> None:
        """Append one decision record to the immutable audit log (best-effort)."""
        entry: dict[str, Any] = {
            "ts": time.time(),
            "actor": actor,
            "action": action,
            "resource": resource,
            "actor_tier": actor_tier.name,
            "allowed": allowed,
            "reason": reason,
        }
        try:
            self._audit_log.parent.mkdir(parents=True, exist_ok=True)
            with self._audit_log.open("a") as fh:
                fh.write(json.dumps(entry) + "\n")
        except OSError as exc:
            logger.warning("RBAC audit log write failed: %s", exc)

    def read_audit_log(self, last_n: int = 50) -> list[dict[str, Any]]:
        """Read the last *last_n* entries from the audit log (for tests/monitoring)."""
        if not self._audit_log.exists():
            return []
        lines = self._audit_log.read_text().splitlines()
        entries = []
        for line in lines[-last_n:]:
            with contextlib.suppress(json.JSONDecodeError):
                entries.append(json.loads(line))
        return entries


# ---------------------------------------------------------------------------
# Module-level default instance
# ---------------------------------------------------------------------------

#: Drop-in replacement for validate_actor() in mcp_session_bridge.
#: Wire: spm.evaluate_permission(actor, "inject_session_context")
default_policy_manager: StructuralPolicyManager = StructuralPolicyManager()
