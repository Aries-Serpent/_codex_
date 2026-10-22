"""Cognitive Brain Module — Multi-layer Reasoning Architecture + Runtime Kernel.

Heavyweight submodules are imported lazily so that stdlib-only contract,
policy, and pipeline modules (``authority``, ``improvement_pipeline``,
``isolated_execution``, ``outcome_tracking``) remain importable in
environments where optional dependencies such as numpy are absent.
"""

from importlib import import_module
from typing import TYPE_CHECKING

from .authority import AuthorityDecision, AuthorityEnvelope, AuthorityLimits
from .fallbacks import (
    FallbackChain,
    FallbackResult,
    import_optional,
    rate_limited_call,
    safe_default_config,
    with_fallback,
)

if TYPE_CHECKING:
    from .calibration import ConfidenceCalibrator
    from .capability_registry import (
        CAPABILITY_SCHEMA_VERSION,
        CapabilityRegistry,
        ModelCapabilityProfile,
        ToolSurfaceCategory,
        ToolSurfaceProfile,
        check_capability_schema_version,
        get_default_registry,
        get_tool_surface_registry,
    )
    from .kernel import (
        CognitiveBrainKernel,
        KernelConfig,
        assert_loaded,
        auto_load,
        boot,
        get_kernel,
        reset_kernel,
    )
    from .knowledge_base import KnowledgeBase, QueryInterface
    from .model_negotiator import ModelNegotiator, NegotiationResult
    from .orchestrator import MCPOrchestrator, ToolchainPlan, ToolchainStep
    from .policy import CandidatePlan, DeterministicPolicy, PolicyContext, ScoredPlan
    from .reasoning_engine import (
        ActionLayer,
        FeedbackLayer,
        ImprovementLayer,
        PerceptionLayer,
        ReasoningEngine,
        ReasoningLayer,
    )
    from .session_guard import (
        SessionCreateResult,
        SessionGuard,
        get_default_guard,
        reset_default_guard,
        safe_create_session,
    )
    from .shell_executor import ShellExecutionDenied, execute_command
    from .shell_policy import (
        GateDecision,
        PolicyVerdict,
        ShellPolicy,
        get_default_policy,
        reset_default_policy,
    )
    from .telemetry import (
        CognitiveTelemetry,
        InMemoryTelemetryBackend,
        NDJSONTelemetryBackend,
        TelemetryEvent,
    )

_LAZY_EXPORTS = {
    "ConfidenceCalibrator": ".calibration",
    "CAPABILITY_SCHEMA_VERSION": ".capability_registry",
    "CapabilityRegistry": ".capability_registry",
    "ModelCapabilityProfile": ".capability_registry",
    "ToolSurfaceCategory": ".capability_registry",
    "ToolSurfaceProfile": ".capability_registry",
    "check_capability_schema_version": ".capability_registry",
    "get_default_registry": ".capability_registry",
    "get_tool_surface_registry": ".capability_registry",
    "CognitiveBrainKernel": ".kernel",
    "KernelConfig": ".kernel",
    "assert_loaded": ".kernel",
    "auto_load": ".kernel",
    "boot": ".kernel",
    "get_kernel": ".kernel",
    "reset_kernel": ".kernel",
    "KnowledgeBase": ".knowledge_base",
    "QueryInterface": ".knowledge_base",
    "ModelNegotiator": ".model_negotiator",
    "NegotiationResult": ".model_negotiator",
    "MCPOrchestrator": ".orchestrator",
    "ToolchainPlan": ".orchestrator",
    "ToolchainStep": ".orchestrator",
    "CandidatePlan": ".policy",
    "DeterministicPolicy": ".policy",
    "PolicyContext": ".policy",
    "ScoredPlan": ".policy",
    "ActionLayer": ".reasoning_engine",
    "FeedbackLayer": ".reasoning_engine",
    "ImprovementLayer": ".reasoning_engine",
    "PerceptionLayer": ".reasoning_engine",
    "ReasoningEngine": ".reasoning_engine",
    "ReasoningLayer": ".reasoning_engine",
    "SessionCreateResult": ".session_guard",
    "SessionGuard": ".session_guard",
    "get_default_guard": ".session_guard",
    "reset_default_guard": ".session_guard",
    "safe_create_session": ".session_guard",
    "ShellExecutionDenied": ".shell_executor",
    "execute_command": ".shell_executor",
    "GateDecision": ".shell_policy",
    "PolicyVerdict": ".shell_policy",
    "ShellPolicy": ".shell_policy",
    "get_default_policy": ".shell_policy",
    "reset_default_policy": ".shell_policy",
    "CognitiveTelemetry": ".telemetry",
    "InMemoryTelemetryBackend": ".telemetry",
    "NDJSONTelemetryBackend": ".telemetry",
    "TelemetryEvent": ".telemetry",
}


def __getattr__(name: str):
    """Resolve heavyweight submodules on first access."""

    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name, __name__), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))

__all__ = [
    # Authority envelope (Stage 1)
    "AuthorityDecision",
    "AuthorityEnvelope",
    "AuthorityLimits",
    # Reasoning engine (existing)
    "ReasoningEngine",
    "PerceptionLayer",
    "ReasoningLayer",
    "ActionLayer",
    "FeedbackLayer",
    "ImprovementLayer",
    "KnowledgeBase",
    "QueryInterface",
    "ConfidenceCalibrator",
    # Capability registry
    "CapabilityRegistry",
    "ModelCapabilityProfile",
    "get_default_registry",
    # Capability schema (Phase 2C)
    "CAPABILITY_SCHEMA_VERSION",
    "ToolSurfaceCategory",
    "ToolSurfaceProfile",
    "get_tool_surface_registry",
    "check_capability_schema_version",
    # Model negotiator
    "ModelNegotiator",
    "NegotiationResult",
    # Deterministic policy
    "DeterministicPolicy",
    "PolicyContext",
    "CandidatePlan",
    "ScoredPlan",
    # MCP orchestrator
    "MCPOrchestrator",
    "ToolchainPlan",
    "ToolchainStep",
    # Fallbacks
    "FallbackChain",
    "FallbackResult",
    "with_fallback",
    "rate_limited_call",
    "import_optional",
    "safe_default_config",
    # Telemetry
    "CognitiveTelemetry",
    "TelemetryEvent",
    "InMemoryTelemetryBackend",
    "NDJSONTelemetryBackend",
    # Kernel
    "CognitiveBrainKernel",
    "KernelConfig",
    "assert_loaded",
    "auto_load",
    "boot",
    "get_kernel",
    "reset_kernel",
    # Session guard (Phase 2B)
    "SessionGuard",
    "SessionCreateResult",
    "get_default_guard",
    "reset_default_guard",
    "safe_create_session",
    # Shell policy (Phase 2A)
    "ShellPolicy",
    "GateDecision",
    "PolicyVerdict",
    "get_default_policy",
    "reset_default_policy",
    "ShellExecutionDenied",
    "execute_command",
]
