"""Cognitive Brain Skills — Public API.

from codex.logging.structured_logger import logger
This package provides:

- :class:`~codex.skills.models.SkillManifest` — manifest schema
- :class:`~codex.skills.registry.SkillRegistry` — discover / register / resolve
- :class:`~codex.skills.envelope.ExecutionEnvelope` — policy gate + execution
- :class:`~codex.skills.routing.StratifiedRouter` — stratified skill selection
- :func:`~codex.skills.aais.score_text` — AAIS quality scoring
- :mod:`~codex.skills.telemetry` — JSONL + OTel emission
- :mod:`~codex.skills.compression` — 7z/zip archive packaging
- :func:`~codex.skills.doc_loader.load_agent_docs_as_skills` — Markdown doc ingestion

Quick start::

    from codex.skills import get_registry, ExecutionEnvelope

    registry = get_registry()
    registry.discover()

    env = ExecutionEnvelope(registry)
    result = env.run("doc.retriever.core", {"query": "AAIS scoring"})
    logger.info(result.status, result.data)
"""

from __future__ import annotations

from .aais import AAISScorer, score_text
from .compression import CompressionResult, compress_skill, install_skill
from .doc_loader import load_agent_docs_as_skills
from .envelope import ExecutionEnvelope, PolicyViolation

# Research-branch integration: lightweight dataclass manifest + doc loader
from .loader import SkillDocLoader
from .manifest import SkillExecutionEnvelope
from .manifest import SkillManifest as SkillManifestDC
from .models import (
    AAISScore,
    BudgetConfig,
    BudgetUsed,
    CompressionMeta,
    DocMeta,
    ExecutionError,
    ExecutionMetrics,
    ExecutionResult,
    IORef,
    PolicyConfig,
    RegisteredSkill,
    RoutingDecision,
    RoutingScore,
    SkillManifest,
    TelemetryConfig,
    TelemetryEvent,
)
from .registry import SkillRegistry, get_registry, reset_registry
from .routing import StratifiedRouter
from .telemetry import emit_event, read_events, skill_invocation_span, summarise_events

__all__ = [
    # Models
    "AAISScore",
    "BudgetConfig",
    "BudgetUsed",
    "CompressionMeta",
    "CompressionResult",
    "DocMeta",
    "ExecutionError",
    "ExecutionMetrics",
    "ExecutionResult",
    "IORef",
    "PolicyConfig",
    "RegisteredSkill",
    "RoutingDecision",
    "RoutingScore",
    "SkillManifest",
    "TelemetryConfig",
    "TelemetryEvent",
    # Registry
    "SkillRegistry",
    "get_registry",
    "reset_registry",
    # Envelope
    "ExecutionEnvelope",
    "PolicyViolation",
    # Routing
    "StratifiedRouter",
    # AAIS
    "AAISScorer",
    "score_text",
    # Telemetry
    "emit_event",
    "read_events",
    "summarise_events",
    # Compression
    "compress_skill",
    "install_skill",
    # Doc loader
    "load_agent_docs_as_skills",
    # Research-branch: lightweight dataclass-based skill primitives
    "SkillDocLoader",
    "SkillExecutionEnvelope",
    "SkillManifestDC",
    "skill_invocation_span",
]
