"""Cognitive Brain Module — Multi-layer Reasoning Architecture + Runtime Kernel."""

from src.codex.cognitive_brain.calibration import ConfidenceCalibrator
from src.codex.cognitive_brain.capability_registry import (
    CapabilityRegistry,
    ModelCapabilityProfile,
    get_default_registry,
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
    "boot",
    "get_kernel",
    "reset_kernel",
]
