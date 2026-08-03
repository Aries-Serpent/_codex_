"""Cognitive Brain Kernel — central orchestration entry point.

The kernel wires together all Cognitive Brain sub-systems:

    CapabilityRegistry  → capability profiles with TTL cache
    ModelNegotiator     → gates unsupported session parameters
    DeterministicPolicy → physics-inspired plan scoring
    MCPOrchestrator     → MCP toolchain planner
    FallbackChain       → auto-recovery strategies
    CognitiveTelemetry  → structured event logging

It provides:
- A single ``boot()`` / ``get_kernel()`` API for environment auto-load.
- Task-level convenience methods (``negotiate_model``, ``plan_tools``).
- Explicit startup log + telemetry confirming the brain is loaded.
- CCA stability guards (deduplication, turn isolation).

Usage::

    from src.codex.cognitive_brain.kernel import get_kernel

    kernel = get_kernel()
    safe_cfg = kernel.negotiate_model("claude-haiku-4.5", raw_cfg)
    toolchain = kernel.plan_tools("repo_introspection")
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from src.codex.cognitive_brain.capability_registry import (
    CapabilityRegistry,
)
from src.codex.cognitive_brain.model_negotiator import ModelNegotiator, NegotiationResult
from src.codex.cognitive_brain.orchestrator import MCPOrchestrator, ToolchainPlan
from src.codex.cognitive_brain.policy import (
    DeterministicPolicy,
    PolicyContext,
)
from src.codex.cognitive_brain.telemetry import CognitiveTelemetry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Kernel version
# ---------------------------------------------------------------------------

__kernel_version__ = "1.0.0"

# ---------------------------------------------------------------------------
# CCA stability flags (mandatory per AGENTS.md)
# Read at call-time (inside _assert_cca_stability) so tests can monkeypatch.
# ---------------------------------------------------------------------------


def _read_cca_flags() -> tuple[str, bool, bool]:
    """Return (version_lock, dedup_enabled, turn_isolation) from env at call time."""
    lock = os.getenv("COPILOT_AGENT_CCA_VERSION_LOCK", "stable")
    dedup = os.getenv("COPILOT_AGENT_DEDUPLICATION_ENABLED", "true").lower() == "true"
    turn = os.getenv("COPILOT_AGENT_TURN_ISOLATION_ENABLED", "true").lower() == "true"
    return lock, dedup, turn


# ---------------------------------------------------------------------------
# Kernel configuration
# ---------------------------------------------------------------------------


@dataclass
class KernelConfig:
    """Runtime configuration for the :class:`CognitiveBrainKernel`."""

    policy_seed: int = 42
    policy_weights: Dict[str, float] = field(default_factory=dict)
    registry_ttl_seconds: float = 3600.0
    fallback_model_chain: List[str] = field(default_factory=list)
    allow_shell: bool = False
    available_mcp_tools: Optional[List[str]] = None
    telemetry_ndjson_path: Optional[str] = None
    session_id: Optional[str] = None

    @classmethod
    def from_env(cls) -> "KernelConfig":
        """Build a :class:`KernelConfig` from environment variables."""
        return cls(
            policy_seed=int(os.getenv("COGNITIVE_BRAIN_POLICY_SEED", "42")),
            registry_ttl_seconds=float(os.getenv("COGNITIVE_BRAIN_REGISTRY_TTL", "3600")),
            allow_shell=os.getenv("COGNITIVE_BRAIN_ALLOW_SHELL", "false").lower() == "true",
            telemetry_ndjson_path=os.getenv("COGNITIVE_BRAIN_TELEMETRY_PATH"),
            session_id=os.getenv("CODEX_SESSION_ID"),
        )


# ---------------------------------------------------------------------------
# Kernel
# ---------------------------------------------------------------------------


class CognitiveBrainKernel:
    """Central runtime kernel for the Cognitive Brain subsystem.

    Parameters
    ----------
    config:
        Kernel configuration.  Defaults to :meth:`KernelConfig.from_env`.
    """

    def __init__(self, config: Optional[KernelConfig] = None) -> None:
        self._config = config or KernelConfig.from_env()
        self._boot_time: Optional[float] = None

        # Assemble sub-systems.
        self._registry = CapabilityRegistry(ttl_seconds=self._config.registry_ttl_seconds)
        self._negotiator = ModelNegotiator(
            registry=self._registry,
            fallback_chain=self._config.fallback_model_chain or None,
        )
        self._policy = DeterministicPolicy(
            seed=self._config.policy_seed,
            weights=self._config.policy_weights or None,
        )
        self._orchestrator = MCPOrchestrator(
            policy=self._policy,
            allow_shell=self._config.allow_shell,
            available_tools=self._config.available_mcp_tools,
        )

        # Telemetry backends.
        from src.codex.cognitive_brain.telemetry import (
            InMemoryTelemetryBackend,
            NDJSONTelemetryBackend,
        )

        backends = [InMemoryTelemetryBackend()]
        if self._config.telemetry_ndjson_path:
            backends.append(NDJSONTelemetryBackend(self._config.telemetry_ndjson_path))
        self._telemetry = CognitiveTelemetry(
            backends=backends,
            session_id=self._config.session_id,
        )

        self._loaded = False

    # ------------------------------------------------------------------
    # Boot
    # ------------------------------------------------------------------

    def boot(self) -> None:
        """Initialise all sub-systems and emit the startup telemetry event.

        Idempotent — safe to call multiple times; only the first call
        has effect.
        """
        if self._loaded:
            return
        self._boot_time = time.monotonic()
        self._assert_cca_stability()
        cca_lock, dedup, turn_iso = _read_cca_flags()
        config_summary = {
            "version": __kernel_version__,
            "policy_seed": self._config.policy_seed,
            "allow_shell": self._config.allow_shell,
            "cca_version_lock": cca_lock,
            "deduplication": dedup,
            "turn_isolation": turn_iso,
        }
        self._telemetry.startup(__kernel_version__, config_summary)
        self._loaded = True
        logger.info(
            "🧠 Cognitive Brain Kernel v%s loaded "
            "(policy_seed=%d cca_lock=%s dedup=%s turn_isolation=%s)",
            __kernel_version__,
            self._config.policy_seed,
            cca_lock,
            dedup,
            turn_iso,
        )

    @property
    def is_loaded(self) -> bool:
        """True if :meth:`boot` has been called successfully."""
        return self._loaded

    # ------------------------------------------------------------------
    # Model negotiation
    # ------------------------------------------------------------------

    def negotiate_model(
        self,
        model_id: str,
        session_config: Dict[str, Any],
        required_capabilities: Optional[Sequence[str]] = None,
    ) -> NegotiationResult:
        """Gate and rewrite *session_config* for *model_id*.

        Strips parameters unsupported by the model (e.g. ``reasoning_effort``
        on ``claude-haiku-4.5``), selects a fallback if required capabilities
        are unavailable, and emits a telemetry event.
        """
        t0 = time.monotonic()
        result = self._negotiator.negotiate(model_id, session_config, required_capabilities)
        duration_ms = (time.monotonic() - t0) * 1000
        self._telemetry.negotiation(
            model_id=model_id,
            stripped=result.stripped_params,
            fallback_used=result.fallback_used,
            resolved_model=result.resolved_model_id,
            duration_ms=duration_ms,
        )
        return result

    def safe_session_config(
        self,
        model_id: str,
        session_config: Dict[str, Any],
        required_capabilities: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """Convenience wrapper — returns the cleaned config dict with ``model`` key."""
        return self._negotiator.safe_session_config(model_id, session_config, required_capabilities)

    # ------------------------------------------------------------------
    # Tool orchestration
    # ------------------------------------------------------------------

    def plan_tools(
        self,
        task_intent: str,
        context: Optional[PolicyContext] = None,
        *,
        decision_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> ToolchainPlan:
        """Select an ordered MCP toolchain for *task_intent*.

        Emits both an orchestration telemetry event and a forensics event
        with ``decision_id``, ``turn_id``, and ``task_id`` for traceability.
        """
        import uuid as _uuid

        t0 = time.monotonic()
        plan = self._orchestrator.plan(task_intent, context)
        duration_ms = (time.monotonic() - t0) * 1000
        self._telemetry.orchestration(
            task_intent=task_intent,
            primary_tool=plan.primary_tool,
            plan_notes=plan.notes,
            duration_ms=duration_ms,
        )
        # Forensics event with rejected alternatives.
        _decision_id = decision_id or str(_uuid.uuid4())
        rejected = [
            step.tool
            for step in (plan.fallback_plan.steps if plan.fallback_plan else [])
            if plan.primary_tool and step.tool != plan.primary_tool
        ]
        self._telemetry.forensics(
            decision_id=_decision_id,
            turn_id=turn_id,
            task_id=task_id,
            selected_toolchain=plan.primary_tool,
            rejected_alternatives=rejected,
            negotiation_outcome=None,
            task_intent=task_intent,
            duration_ms=duration_ms,
        )
        return plan

    # ------------------------------------------------------------------
    # Entrypoint guard
    # ------------------------------------------------------------------

    def assert_loaded(self) -> None:
        """Assert that the kernel has been booted; emit a diagnostic if not.

        Call this at reasoning-critical entrypoints to guarantee the
        cognitive brain is initialised before any reasoning occurs.

        Raises
        ------
        RuntimeError
            If the kernel has not been booted and
            ``COGNITIVE_BRAIN_FAILSAFE_OFF=true`` is set (fail-fast mode).
        """
        if self._loaded:
            return
        failsafe_off = os.getenv("COGNITIVE_BRAIN_FAILSAFE_OFF", "false").lower() == "true"
        msg = (
            "CognitiveBrainKernel.assert_loaded(): kernel not yet booted. "
            "Call boot() or get_kernel() before entering reasoning-critical code."
        )
        if failsafe_off:
            logger.error(msg)
            raise RuntimeError(msg)
        logger.warning("%s  Auto-booting now.", msg)
        self.boot()

    # ------------------------------------------------------------------
    # Telemetry access
    # ------------------------------------------------------------------

    @property
    def telemetry(self) -> CognitiveTelemetry:
        """Return the telemetry facade for querying recorded events."""
        return self._telemetry

    # ------------------------------------------------------------------
    # CCA stability
    # ------------------------------------------------------------------

    @staticmethod
    def _assert_cca_stability() -> None:
        """Log warnings if CCA stability env vars are misconfigured.

        Reads env vars at call time so that monkeypatching in tests works.
        """
        cca_lock, dedup, turn_iso = _read_cca_flags()
        if cca_lock != "stable":
            logger.warning(
                "COPILOT_AGENT_CCA_VERSION_LOCK is '%s'; expected 'stable'. "
                "Risk of CCA version upgrade causing duplicate function-call errors.",
                cca_lock,
            )
        if not dedup:
            logger.warning(
                "COPILOT_AGENT_DEDUPLICATION_ENABLED is not 'true'. "
                "Payload deduplication disabled — risk of duplicate fc_call IDs."
            )
        if not turn_iso:
            logger.warning(
                "COPILOT_AGENT_TURN_ISOLATION_ENABLED is not 'true'. "
                "Turn-state isolation disabled — risk of state leakage across turns."
            )

    # ------------------------------------------------------------------
    # Accessors for sub-systems
    # ------------------------------------------------------------------

    @property
    def registry(self) -> CapabilityRegistry:
        return self._registry

    @property
    def negotiator(self) -> ModelNegotiator:
        return self._negotiator

    @property
    def policy(self) -> DeterministicPolicy:
        return self._policy

    @property
    def orchestrator(self) -> MCPOrchestrator:
        return self._orchestrator


# ---------------------------------------------------------------------------
# Module-level singleton (auto-load)
# ---------------------------------------------------------------------------

_kernel_instance: Optional[CognitiveBrainKernel] = None
_kernel_lock = threading.Lock()


def boot(config: Optional[KernelConfig] = None) -> CognitiveBrainKernel:
    """Boot and return the process-level :class:`CognitiveBrainKernel`.

    Thread-safe.  Multiple calls return the same instance without re-booting.
    Pass a new *config* only on the first call (subsequent configs are ignored).
    """
    global _kernel_instance
    with _kernel_lock:
        if _kernel_instance is None:
            _kernel_instance = CognitiveBrainKernel(config)
            _kernel_instance.boot()
    return _kernel_instance


def get_kernel() -> CognitiveBrainKernel:
    """Return the booted kernel, auto-booting with default config if needed."""
    return boot()


def reset_kernel() -> None:
    """Reset the singleton (for testing only)."""
    global _kernel_instance
    with _kernel_lock:
        _kernel_instance = None


# ---------------------------------------------------------------------------
# Environment auto-load
# ---------------------------------------------------------------------------
# FR-5 (Environment Auto-Load): call `get_kernel()` (or `boot()`) from
# application entry points and agent boot hooks.  The helper below is
# provided for scripts that want conditional auto-boot without importing
# all kernel internals.
#
# To trigger auto-boot from a script or entry point:
#
#   from src.codex.cognitive_brain.kernel import auto_load
#   auto_load()
#
# Set COGNITIVE_BRAIN_FAILSAFE_OFF=true to disable all auto-boot calls.


def auto_load() -> Optional[CognitiveBrainKernel]:
    """Boot the kernel if COGNITIVE_BRAIN_AUTO_LOAD=true (default) and
    COGNITIVE_BRAIN_FAILSAFE_OFF is not set.

    Safe to call multiple times; returns None when auto-load is disabled.
    Does not raise — failures are logged as warnings.
    """
    failsafe_off = os.getenv("COGNITIVE_BRAIN_FAILSAFE_OFF", "false").lower() == "true"
    if failsafe_off:
        return None
    auto = os.getenv("COGNITIVE_BRAIN_AUTO_LOAD", "true").lower()
    if auto != "true":
        return None
    try:
        return get_kernel()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Cognitive Brain auto-load failed (non-fatal): %s", exc)
        return None
