"""Cognitive Brain Module — Multi-layer Reasoning Architecture + Runtime Kernel."""

from src.codex.cognitive_brain.calibration import ConfidenceCalibrator
from src.codex.cognitive_brain.capability_registry import (
    CAPABILITY_SCHEMA_VERSION,
    CapabilityRegistry,
    ModelCapabilityProfile,
    ToolSurfaceCategory,
    ToolSurfaceProfile,
    check_capability_schema_version,
    get_default_registry,
    get_tool_surface_registry,
)
from src.codex.cognitive_brain.fallbacks import (
    FallbackChain,
    FallbackResult,
    import_optional,
    rate_limited_call,
    safe_default_config,
    with_fallback,
)
from src.codex.cognitive_brain.kernel import (
    CognitiveBrainKernel,
    KernelConfig,
    assert_loaded,
    auto_load,
    boot,
    get_kernel,
    reset_kernel,
)
from src.codex.cognitive_brain.knowledge_base import KnowledgeBase, QueryInterface
from src.codex.cognitive_brain.model_negotiator import ModelNegotiator, NegotiationResult
from src.codex.cognitive_brain.orchestrator import (
    MCPOrchestrator,
    ToolchainPlan,
    ToolchainStep,
)
from src.codex.cognitive_brain.policy import (
    CandidatePlan,
    DeterministicPolicy,
    PolicyContext,
    ScoredPlan,
)
from src.codex.cognitive_brain.reasoning_engine import (
    ActionLayer,
    FeedbackLayer,
    ImprovementLayer,
    PerceptionLayer,
    ReasoningEngine,
    ReasoningLayer,
)
from src.codex.cognitive_brain.session_guard import (
    SessionCreateResult,
    SessionGuard,
    get_default_guard,
    reset_default_guard,
    safe_create_session,
)
from src.codex.cognitive_brain.shell_policy import (
    GateDecision,
    PolicyVerdict,
    ShellPolicy,
    get_default_policy,
    reset_default_policy,
)
from src.codex.cognitive_brain.telemetry import (
    CognitiveTelemetry,
    InMemoryTelemetryBackend,
    NDJSONTelemetryBackend,
    TelemetryEvent,
)

__all__ = [
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
]
