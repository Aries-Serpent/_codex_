"""
Phase 1 — Autonomy State Registry

Single authoritative source of truth for autonomy mode, kill-switch,
dry-run flag, runtime budgets, and allowed surfaces.

Every actuation surface MUST query this registry before taking action.

Usage::

    from codex.autonomy.registry import AutonomyRegistry

    reg = AutonomyRegistry.load()          # reads .codex/autonomy_registry.yaml
    reg.assert_permitted("AUT-007", "REPO_STATE_WRITE")  # raises if denied

Blueprint: .codex/docs/AUTONOMY_BLUEPRINT.md — Phase 1
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Default registry path (can be overridden by env var for testing)
_DEFAULT_REGISTRY_PATH = Path(".codex/autonomy_registry.yaml")
_REGISTRY_PATH_ENV = "CODEX_AUTONOMY_REGISTRY"


class AutonomyMode(str, Enum):
    """Operating modes ordered from most-restrictive to most-permissive."""

    OFF = "OFF"
    OBSERVE = "OBSERVE"
    DRY_RUN = "DRY_RUN"
    ASSISTED = "ASSISTED"
    SAFE_AUTO = "SAFE_AUTO"
    ELEVATED_AUTO = "ELEVATED_AUTO"

    @property
    def level(self) -> int:
        """Numeric level; higher = more permissive."""
        return list(AutonomyMode).index(self)

    def allows_at_least(self, minimum: "AutonomyMode") -> bool:
        """Return True if this mode is at least as permissive as *minimum*."""
        return self.level >= minimum.level


class ControlClass(str, Enum):
    """Normalised control classes from the blueprint."""

    READ_ONLY = "READ_ONLY"
    PROMPT_ONLY = "PROMPT_ONLY"
    ADVISORY_WRITE = "ADVISORY_WRITE"
    REPO_STATE_WRITE = "REPO_STATE_WRITE"
    INFRA_WRITE = "INFRA_WRITE"
    REMOTE_EXEC = "REMOTE_EXEC"
    EXTERNAL_BRIDGE = "EXTERNAL_BRIDGE"


# Alias kept for backward compatibility with blueprint terminology
MutationClass = ControlClass

# Minimum mode required for each control class
_MINIMUM_MODE: dict[ControlClass, AutonomyMode] = {
    ControlClass.READ_ONLY: AutonomyMode.OBSERVE,
    ControlClass.PROMPT_ONLY: AutonomyMode.DRY_RUN,
    ControlClass.ADVISORY_WRITE: AutonomyMode.ASSISTED,
    ControlClass.REPO_STATE_WRITE: AutonomyMode.ASSISTED,
    ControlClass.INFRA_WRITE: AutonomyMode.ELEVATED_AUTO,
    ControlClass.REMOTE_EXEC: AutonomyMode.SAFE_AUTO,
    ControlClass.EXTERNAL_BRIDGE: AutonomyMode.ELEVATED_AUTO,
}


class AutonomyPolicyError(RuntimeError):
    """Raised when an actuation surface is denied by policy."""


@dataclass
class AutonomyRegistry:
    """
    In-memory representation of the autonomy state registry.

    Load from YAML with :meth:`load`; the raw dict is parsed into typed fields
    so that all access is validated at read time.
    """

    schema_version: str = "1.0.0"
    policy_version: str = "blueprint-v1"

    autonomy_mode: AutonomyMode = AutonomyMode.SAFE_AUTO
    kill_switch: bool = False
    dry_run: bool = False

    max_iterations: int = 50
    budget_seconds: int = 3600

    allowed_surfaces: list[str] = field(default_factory=list)
    allowed_runners: list[str] = field(default_factory=list)
    approval_required_classes: list[str] = field(default_factory=list)

    expires_at: Optional[str] = None

    token_resolution_order: list[str] = field(
        default_factory=lambda: ["github_app", "oidc", "scoped_pat", "codex_master"]
    )

    audit_log_path: str = ".codex/autonomy_audit.ndjson"
    metrics_log_path: str = ".codex/autonomy_metrics.ndjson"
    audit_coverage_target: float = 0.95

    # ── Class-level cache ─────────────────────────────────────────────────────

    _instance: "Optional[AutonomyRegistry]" = field(default=None, init=False, repr=False)

    # ── Construction ──────────────────────────────────────────────────────────

    @classmethod
    def load(
        cls,
        path: Optional[Path] = None,
        *,
        reload: bool = False,
    ) -> "AutonomyRegistry":
        """
        Load the registry from YAML.

        Parameters
        ----------
        path:
            Override the default registry file path.  If *None*, falls back to
            the ``CODEX_AUTONOMY_REGISTRY`` env-var, then the repo default.
        reload:
            Force re-read even if a cached instance exists.
        """
        if path is None:
            env_path = os.environ.get(_REGISTRY_PATH_ENV)
            path = Path(env_path) if env_path else _DEFAULT_REGISTRY_PATH

        try:
            import yaml  # noqa: PLC0415 — optional at module level
        except ImportError:  # pragma: no cover
            logger.warning("PyYAML not available; returning default registry")
            return cls()

        if not path.exists():
            logger.warning("Registry file not found at %s; using defaults", path)
            return cls()

        try:
            raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (IOError, OSError) as exc:  # noqa: BLE001
            logger.error("Failed to parse registry %s: %s", path, exc)
            return cls()

        return cls._from_dict(raw)

    @classmethod
    def _from_dict(cls, raw: dict[str, Any]) -> "AutonomyRegistry":
        mode_str = raw.get("autonomy_mode", "SAFE_AUTO")
        try:
            mode = AutonomyMode(mode_str)
        except ValueError:
            logger.warning("Unknown autonomy_mode '%s'; defaulting to SAFE_AUTO", mode_str)
            mode = AutonomyMode.SAFE_AUTO

        return cls(
            schema_version=raw.get("schema_version", "1.0.0"),
            policy_version=raw.get("policy_version", "blueprint-v1"),
            autonomy_mode=mode,
            kill_switch=bool(raw.get("kill_switch", False)),
            dry_run=bool(raw.get("dry_run", False)),
            max_iterations=int(raw.get("max_iterations", 50)),
            budget_seconds=int(raw.get("budget_seconds", 3600)),
            allowed_surfaces=list(raw.get("allowed_surfaces", [])),
            allowed_runners=list(raw.get("allowed_runners", [])),
            approval_required_classes=list(raw.get("approval_required_classes", [])),
            expires_at=raw.get("expires_at"),
            token_resolution_order=list(
                raw.get("token_resolution_order", ["github_app", "oidc", "scoped_pat"])
            ),
            audit_log_path=raw.get("audit_log_path", ".codex/autonomy_audit.ndjson"),
            metrics_log_path=raw.get("metrics_log_path", ".codex/autonomy_metrics.ndjson"),
            audit_coverage_target=float(raw.get("audit_coverage_target", 0.95)),
        )

    # ── Policy enforcement ────────────────────────────────────────────────────

    def is_permitted(
        self,
        surface_id: str,
        control_class: str | ControlClass,
        *,
        actor: str = "",
    ) -> tuple[bool, str]:
        """
        Evaluate whether *surface_id* may perform *control_class*.

        Returns
        -------
        (allowed, reason) :
            *allowed* is True when the action is permitted;
            *reason* explains the decision.
        """
        # 1. Kill-switch — overrides everything
        if self.kill_switch:
            return False, "kill_switch=true — all actuation denied"

        # 2. Surface allowlist
        if self.allowed_surfaces and surface_id not in self.allowed_surfaces:
            return False, f"surface '{surface_id}' not in allowed_surfaces"

        # 3. Normalise control class
        try:
            cc = ControlClass(control_class) if isinstance(control_class, str) else control_class
        except ValueError:
            return False, f"unknown control_class '{control_class}'"

        # 4. Mode floor
        min_mode = _MINIMUM_MODE.get(cc, AutonomyMode.ASSISTED)
        if not self.autonomy_mode.allows_at_least(min_mode):
            return (
                False,
                f"autonomy_mode={self.autonomy_mode.value} insufficient for "
                f"{cc.value} (requires {min_mode.value})",
            )

        # 5. Approval-required classes
        if cc.value in self.approval_required_classes:
            return False, f"{cc.value} requires explicit human approval"

        # 6. Dry-run: permit decisioning but flag as dry-run
        if self.dry_run and cc not in (ControlClass.READ_ONLY, ControlClass.PROMPT_ONLY):
            return True, "dry_run=true — decision allowed but mutation will be skipped"

        return True, "allowed"

    def assert_permitted(
        self,
        surface_id: str,
        control_class: str | ControlClass,
        *,
        actor: str = "",
    ) -> None:
        """
        Assert the action is permitted, raising :exc:`AutonomyPolicyError` if not.
        """
        allowed, reason = self.is_permitted(surface_id, control_class, actor=actor)
        if not allowed:
            raise AutonomyPolicyError(
                f"Policy denied: surface={surface_id} class={control_class} — {reason}"
            )
        logger.debug("Policy allowed: surface=%s class=%s — %s", surface_id, control_class, reason)

    # ── Convenience ───────────────────────────────────────────────────────────

    @property
    def is_off(self) -> bool:
        return self.kill_switch or self.autonomy_mode == AutonomyMode.OFF

    @property
    def effective_mode(self) -> AutonomyMode:
        """Returns OFF when kill_switch is set, otherwise autonomy_mode."""
        return AutonomyMode.OFF if self.kill_switch else self.autonomy_mode
