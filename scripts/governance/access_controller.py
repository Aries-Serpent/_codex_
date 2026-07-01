#!/usr/bin/env python3
"""
Principal-Action-Resource (PAR) + Attribute-Based Access Control (ABAC)
Access Control Layer for Codex Governance.

This module implements a sophisticated access control system that combines:

1. PAR (Principal-Action-Resource) model for role-based decisions
2. ABAC (Attribute-Based Access Control) for fine-grained edge cases
3. Graceful degradation (4 levels) for system failures
4. <10ms decision latency (p99)
5. Concurrent request handling (100+)
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Callable

logger = logging.getLogger(__name__)


# ============================================================================
# ABAC Enumerations
# ============================================================================


class DegradationLevel(int, Enum):
    """Graceful degradation levels."""

    L1_FULL = 1  # PAR + ABAC + Audit logging
    L2_PAR_ONLY = 2  # PAR only (ABAC service down)
    L3_NO_AUDIT = 3  # PAR + ABAC, audit logging silent fails
    L4_RELOAD = 4  # Reload cache from source


# ============================================================================
# ABAC Data Structures
# ============================================================================


@dataclass
class PrincipalAttributes:
    """Attributes of a principal (user/agent)."""

    principal_id: str
    department: str = ""
    clearance_level: str = ""  # "low", "medium", "high", "critical"
    is_active: bool = True
    is_mfa_enabled: bool = False
    location: str = "unknown"
    custom_attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAttributes:
    """Attributes of a resource."""

    resource_id: str
    classification: str = "public"  # "public", "internal", "confidential", "secret"
    owner_id: str = ""
    sensitive: bool = False
    requires_approval: bool = False
    custom_attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentAttributes:
    """Environmental attributes for decision making."""

    timestamp: float = field(default_factory=time.time)
    time_of_day_hour: int = 0  # 0-23
    is_business_hours: bool = True
    is_maintenance_window: bool = False
    network_location: str = "office"  # "office", "vpn", "public", "unknown"
    threat_level: str = "normal"  # "normal", "elevated", "critical"


@dataclass
class ABACRule:
    """An ABAC rule for access control."""

    name: str
    description: str
    condition: Callable[[PrincipalAttributes, ResourceAttributes, EnvironmentAttributes], bool]
    effect: str  # "allow" or "deny"
    priority: int = 100  # Higher priority evaluated first


# ============================================================================
# Access Controller
# ============================================================================


class AccessController:
    """
    Principal-Action-Resource (PAR) + Attribute-Based Access Control (ABAC)
    access controller with graceful degradation.
    """

    def __init__(
        self,
        rbac_engine: Any,  # RBACEngine instance
        degradation_level: DegradationLevel = DegradationLevel.L1_FULL,
    ):
        """
        Initialize the access controller.

        Args:
            rbac_engine: The underlying RBAC engine
            degradation_level: Current degradation level
        """
        self.rbac_engine = rbac_engine
        self.degradation_level = degradation_level

        self._abac_rules: list[ABACRule] = []
        self._rules_lock = threading.RLock()

        self._principal_attrs: dict[str, PrincipalAttributes] = {}
        self._resource_attrs: dict[str, ResourceAttributes] = {}
        self._attrs_lock = threading.RLock()

        self._env_attrs = EnvironmentAttributes()
        self._env_lock = threading.RLock()

        self._decision_log: list[dict[str, Any]] = []
        self._decision_log_lock = threading.RLock()

        self._stats = {
            "par_checks": 0,
            "abac_checks": 0,
            "degradation_events": 0,
            "avg_latency_ms": 0.0,
        }
        self._stats_lock = threading.RLock()

        # Bootstrap default ABAC rules
        self._bootstrap_default_rules()

    # ========================================================================
    # ABAC Rule Management
    # ========================================================================

    def add_abac_rule(self, rule: ABACRule) -> None:
        """Add an ABAC rule."""
        with self._rules_lock:
            self._abac_rules.append(rule)
            # Sort by priority (higher first)
            self._abac_rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Added ABAC rule: {rule.name}")

    def remove_abac_rule(self, rule_name: str) -> None:
        """Remove an ABAC rule by name."""
        with self._rules_lock:
            self._abac_rules = [r for r in self._abac_rules if r.name != rule_name]
        logger.info(f"Removed ABAC rule: {rule_name}")

    def _bootstrap_default_rules(self) -> None:
        """Bootstrap default ABAC rules."""
        # Rule 1: Require MFA for sensitive resources
        def mfa_rule(principal: PrincipalAttributes, resource: ResourceAttributes, env: EnvironmentAttributes) -> bool:
            if resource.classification in ["confidential", "secret"]:
                return principal.is_mfa_enabled
            return True

        self.add_abac_rule(
            ABACRule(
                name="require_mfa_for_sensitive",
                description="Require MFA for confidential/secret resources",
                condition=mfa_rule,
                effect="deny",
                priority=200,
            )
        )

        # Rule 2: Restrict access outside business hours for critical ops
        def business_hours_rule(principal: PrincipalAttributes, resource: ResourceAttributes, env: EnvironmentAttributes) -> bool:
            if resource.requires_approval and not env.is_business_hours:
                return principal.clearance_level in ["high", "critical"]
            return True

        self.add_abac_rule(
            ABACRule(
                name="business_hours_restriction",
                description="Restrict critical ops outside business hours",
                condition=business_hours_rule,
                effect="deny",
                priority=180,
            )
        )

        # Rule 3: Prevent access during maintenance windows
        def maintenance_rule(principal: PrincipalAttributes, resource: ResourceAttributes, env: EnvironmentAttributes) -> bool:
            if env.is_maintenance_window:
                return principal.department in ["devops", "platform"]
            return True

        self.add_abac_rule(
            ABACRule(
                name="maintenance_window_restriction",
                description="Only DevOps can access during maintenance",
                condition=maintenance_rule,
                effect="deny",
                priority=190,
            )
        )

        # Rule 4: Threat escalation - require higher clearance
        def threat_rule(principal: PrincipalAttributes, resource: ResourceAttributes, env: EnvironmentAttributes) -> bool:
            if env.threat_level == "critical":
                return principal.clearance_level in ["high", "critical"]
            return True

        self.add_abac_rule(
            ABACRule(
                name="threat_escalation",
                description="Require high clearance during critical threats",
                condition=threat_rule,
                effect="deny",
                priority=210,
            )
        )

    # ========================================================================
    # Principal Attributes
    # ========================================================================

    def set_principal_attrs(self, attrs: PrincipalAttributes) -> None:
        """Set attributes for a principal."""
        with self._attrs_lock:
            self._principal_attrs[attrs.principal_id] = attrs

    def get_principal_attrs(self, principal_id: str) -> PrincipalAttributes:
        """Get attributes for a principal."""
        with self._attrs_lock:
            if principal_id in self._principal_attrs:
                return self._principal_attrs[principal_id]
        return PrincipalAttributes(principal_id=principal_id)

    # ========================================================================
    # Resource Attributes
    # ========================================================================

    def set_resource_attrs(self, attrs: ResourceAttributes) -> None:
        """Set attributes for a resource."""
        with self._attrs_lock:
            self._resource_attrs[attrs.resource_id] = attrs

    def get_resource_attrs(self, resource_id: str) -> ResourceAttributes:
        """Get attributes for a resource."""
        with self._attrs_lock:
            if resource_id in self._resource_attrs:
                return self._resource_attrs[resource_id]
        return ResourceAttributes(resource_id=resource_id)

    # ========================================================================
    # Environment Attributes
    # ========================================================================

    def update_environment(self, attrs: EnvironmentAttributes) -> None:
        """Update environmental attributes."""
        with self._env_lock:
            self._env_attrs = attrs

    def get_environment(self) -> EnvironmentAttributes:
        """Get current environmental attributes."""
        with self._env_lock:
            return self._env_attrs

    # ========================================================================
    # Access Control Decision
    # ========================================================================

    def decide(
        self,
        principal_id: str,
        action: str,
        resource_id: str,
        raise_on_deny: bool = True,
    ) -> bool:
        """
        Make an access control decision using PAR + ABAC.

        Args:
            principal_id: Principal identifier
            action: Action string
            resource_id: Resource identifier
            raise_on_deny: Raise exception on denial

        Returns:
            True if allowed, False otherwise
        """
        start_time = time.time()

        # L1: Full evaluation
        if self.degradation_level == DegradationLevel.L1_FULL:
            allowed = self._evaluate_par(principal_id, action, resource_id)
            if allowed:
                allowed = self._evaluate_abac(principal_id, resource_id)

        # L2: PAR only
        elif self.degradation_level == DegradationLevel.L2_PAR_ONLY:
            allowed = self._evaluate_par(principal_id, action, resource_id)
            with self._stats_lock:
                self._stats["degradation_events"] += 1

        # L3: PAR + ABAC, silent audit failure
        elif self.degradation_level == DegradationLevel.L3_NO_AUDIT:
            allowed = self._evaluate_par(principal_id, action, resource_id)
            if allowed:
                try:
                    allowed = self._evaluate_abac(principal_id, resource_id)
                except Exception as e:
                    logger.error(f"ABAC evaluation failed (silent): {e}")
                    # Continue with PAR result
            with self._stats_lock:
                self._stats["degradation_events"] += 1

        # L4: Reload cache
        elif self.degradation_level == DegradationLevel.L4_RELOAD:
            self.rbac_engine._permission_cache.clear()
            allowed = self._evaluate_par(principal_id, action, resource_id)
            if allowed:
                allowed = self._evaluate_abac(principal_id, resource_id)
            with self._stats_lock:
                self._stats["degradation_events"] += 1

        else:
            allowed = False

        # Log decision
        latency_ms = (time.time() - start_time) * 1000
        self._log_decision(principal_id, action, resource_id, allowed, latency_ms)

        if not allowed and raise_on_deny:
            from scripts.governance.rbac_engine import PermissionDeniedError

            raise PermissionDeniedError(principal_id, action, "resource", resource_id)

        return allowed

    def _evaluate_par(self, principal_id: str, action: str, resource_id: str) -> bool:
        """Evaluate PAR (Principal-Action-Resource) model using RBAC engine."""
        try:
            from scripts.governance.rbac_engine import Action, ResourceType

            # Map string action to enum
            action_enum = Action[action.upper()] if hasattr(Action, action.upper()) else Action.READ

            # Use RBAC engine for PAR evaluation
            result = self.rbac_engine.check_permission(
                principal_id, action_enum, ResourceType.CODE, resource_id, raise_on_deny=False
            )

            with self._stats_lock:
                self._stats["par_checks"] += 1

            return result
        except Exception as e:
            logger.error(f"PAR evaluation error: {e}")
            return False

    def _evaluate_abac(self, principal_id: str, resource_id: str) -> bool:
        """Evaluate ABAC (Attribute-Based Access Control) rules."""
        principal = self.get_principal_attrs(principal_id)
        resource = self.get_resource_attrs(resource_id)
        env = self.get_environment()

        with self._stats_lock:
            self._stats["abac_checks"] += 1

        # Check all rules
        with self._rules_lock:
            for rule in self._abac_rules:
                try:
                    result = rule.condition(principal, resource, env)
                    if rule.effect == "deny" and not result:
                        logger.info(f"ABAC rule denied: {rule.name}")
                        return False
                    elif rule.effect == "allow" and result:
                        logger.info(f"ABAC rule allowed: {rule.name}")
                        return True
                except Exception as e:
                    logger.error(f"ABAC rule error ({rule.name}): {e}")
                    continue

        return True  # Default allow if no denying rules matched

    def _log_decision(
        self, principal_id: str, action: str, resource_id: str, allowed: bool, latency_ms: float
    ) -> None:
        """Log access control decision."""
        decision = {
            "timestamp": time.time(),
            "principal_id": principal_id,
            "action": action,
            "resource_id": resource_id,
            "allowed": allowed,
            "latency_ms": latency_ms,
            "degradation_level": self.degradation_level.value,
        }

        with self._decision_log_lock:
            self._decision_log.append(decision)

        # Update latency stats
        with self._stats_lock:
            if self._stats["avg_latency_ms"] == 0:
                self._stats["avg_latency_ms"] = latency_ms
            else:
                self._stats["avg_latency_ms"] = (self._stats["avg_latency_ms"] + latency_ms) / 2

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_stats(self) -> dict[str, Any]:
        """Get access controller statistics."""
        with self._stats_lock:
            return dict(self._stats)

    def get_decision_log(self, principal_id: Optional[str] = None) -> list[dict[str, Any]]:
        """Get access control decision log."""
        with self._decision_log_lock:
            if principal_id:
                return [d for d in self._decision_log if d["principal_id"] == principal_id]
            return list(self._decision_log)

    # ========================================================================
    # Metrics
    # ========================================================================

    def get_p99_latency(self) -> float:
        """Get p99 latency across all decisions."""
        with self._decision_log_lock:
            if not self._decision_log:
                return 0.0
            latencies = sorted([d["latency_ms"] for d in self._decision_log])
            p99_index = int(len(latencies) * 0.99)
            return latencies[p99_index] if p99_index < len(latencies) else 0.0

    def get_throughput(self) -> float:
        """Get decisions per second (last 60s window)."""
        current_time = time.time()
        window_start = current_time - 60.0

        with self._decision_log_lock:
            recent = [d for d in self._decision_log if d["timestamp"] > window_start]
            return len(recent) / 60.0 if recent else 0.0
