"""Pydantic models for the Cognitive Brain Skills Registry.

Defines the canonical data contracts for skill manifests, execution results,
telemetry events, AAIS scores, and routing decisions.
"""

from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Sub-models used inside SkillManifest
# ---------------------------------------------------------------------------


class BudgetConfig(BaseModel):
    """Resource budget limits for a skill invocation."""

    model_config = ConfigDict(extra="ignore")

    calls: int = Field(default=1000, ge=1, description="Max invocations per policy window")
    tokens: int = Field(default=200_000, ge=1, description="Max LLM tokens per policy window")
    wallclock_ms: int = Field(
        default=600_000, ge=1, description="Max wall-clock time per call in ms"
    )


class PolicyConfig(BaseModel):
    """Policy controls: allowlist, risk tier, and budgets."""

    model_config = ConfigDict(extra="ignore")

    allowlist: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Caller IDs allowed to invoke this skill; '*' means any caller",
    )
    risk_tier: Literal["low", "medium", "high"] = Field(
        default="low",
        description="Risk classification of the skill",
    )
    budgets: BudgetConfig = Field(default_factory=BudgetConfig)


class TelemetryConfig(BaseModel):
    """Telemetry emission flags."""

    model_config = ConfigDict(extra="ignore")

    emit_jsonl: bool = Field(default=True, description="Write JSONL record per invocation")
    emit_otel: bool = Field(default=False, description="Emit OpenTelemetry span per invocation")


class CompressionMeta(BaseModel):
    """Compression metadata for a skill archive."""

    model_config = ConfigDict(extra="ignore")

    method: str = Field(default="7z", description="Compression algorithm")
    level: str = Field(default="max", description="Compression level")
    size_before: int | None = Field(
        default=None, description="Archive size before compression (bytes)"
    )
    size_after: int | None = Field(
        default=None, description="Archive size after compression (bytes)"
    )

    @property
    def compression_ratio(self) -> float | None:
        """Return size_after/size_before if both are set, else None."""
        if self.size_before and self.size_after and self.size_before > 0:
            return self.size_after / self.size_before
        return None


class DocMeta(BaseModel):
    """Documentation provenance metadata embedded in a skill manifest."""

    model_config = ConfigDict(extra="ignore")

    doc_id: str = Field(..., description="Stable document identifier")
    hash: str = Field(default="", description="SHA-256 of the source document")
    aais_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="AAIS quality score (0–1)",
    )
    token_count: int = Field(default=0, ge=0, description="Approximate token count of the doc")
    embed_index_ref: str = Field(default="", description="Path or name of the embedding index")


class PDALoopConfig(BaseModel):
    """PDA Loop (Plan-Do-Assess) integration metadata for a skill.

    When present, the skill participates in the AfterMath feedback loop:
    each invocation appends a structured entry to the PDA iterations log,
    allowing the cognitive brain to track fix success rates over time.
    """

    model_config = ConfigDict(extra="ignore")

    enabled: bool = Field(default=True, description="Whether PDA loop recording is active")
    plan: str = Field(default="", description="What the skill plans to do (P phase)")
    do: str = Field(default="", description="What the skill executes (D phase)")
    assess: str = Field(default="", description="How the skill verifies the outcome (A phase)")
    aftermath_store: str = Field(
        default=".codex/aftermath/pda_iterations.jsonl",
        description="Path to the JSONL store for AfterMath entries",
    )


class IORef(BaseModel):
    """References to JSON Schema files for input/output validation."""

    model_config = ConfigDict(extra="ignore")

    input_schema: str = Field(default="schema/input.json")
    output_schema: str = Field(default="schema/output.json")


# ---------------------------------------------------------------------------
# Top-level Skill Manifest
# ---------------------------------------------------------------------------


class SkillManifest(BaseModel):
    """Complete manifest describing a packaged skill."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="Stable dotted skill identifier, e.g. 'doc.retriever.core'")
    version: str = Field(default="1.0.0", description="Semantic version string")
    name: str = Field(..., description="Human-readable skill name")
    description: str = Field(default="", description="Purpose and behaviour summary")
    capability_tags: list[str] = Field(
        default_factory=list,
        description="Searchable capability labels (e.g. ['docs', 'retrieval'])",
    )
    entrypoint: str = Field(
        ...,
        description="Python import path in 'module:function' format",
    )
    io: IORef = Field(default_factory=IORef)
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)
    compression: CompressionMeta = Field(default_factory=CompressionMeta)
    doc: DocMeta | None = Field(default=None)
    pda_loop: PDALoopConfig | None = Field(
        default=None,
        description="PDA Loop + AfterMath integration config (optional)",
    )


# ---------------------------------------------------------------------------
# Registered Skill (manifest + resolved metadata)
# ---------------------------------------------------------------------------


class RegisteredSkill(BaseModel):
    """A skill that has been loaded and registered in the SkillRegistry."""

    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)

    manifest: SkillManifest
    source_path: str = Field(default="", description="Filesystem path of manifest.yaml")
    # budget_used tracks cumulative usage against limits; reset per policy window
    budget_used: dict[str, int] = Field(
        default_factory=lambda: {"calls": 0, "tokens": 0, "wallclock_ms": 0}
    )

    @property
    def skill_id(self) -> str:
        return self.manifest.id

    @property
    def version(self) -> str:
        return self.manifest.version

    def has_budget_headroom(
        self, *, calls: int = 1, tokens: int = 0, wallclock_ms: int = 0
    ) -> bool:
        """Return True if the requested additional usage fits within budget limits."""
        m = self.manifest.policy.budgets
        return (
            self.budget_used["calls"] + calls <= m.calls
            and self.budget_used["tokens"] + tokens <= m.tokens
            and self.budget_used["wallclock_ms"] + wallclock_ms <= m.wallclock_ms
        )

    def caller_allowed(self, caller_id: str) -> bool:
        """Return True if caller_id is on the allowlist or the allowlist is ['*']."""
        allow = self.manifest.policy.allowlist
        return "*" in allow or caller_id in allow


# ---------------------------------------------------------------------------
# Execution Result types
# ---------------------------------------------------------------------------


class BudgetUsed(BaseModel):
    """Actual resource usage for one skill invocation."""

    model_config = ConfigDict(extra="ignore")

    calls: int = Field(default=1)
    tokens: int = Field(default=0)
    wallclock_ms: int = Field(default=0)


class ExecutionMetrics(BaseModel):
    """Metrics captured during a skill execution."""

    model_config = ConfigDict(extra="ignore")

    latency_ms: int = Field(default=0)
    budget_used: BudgetUsed = Field(default_factory=BudgetUsed)
    aais_score: float | None = Field(default=None)
    compression_ratio: float | None = Field(default=None)


class ExecutionError(BaseModel):
    """Structured error payload returned when execution fails."""

    model_config = ConfigDict(extra="ignore")

    type: str = Field(default="ExecutionError")
    message: str = Field(default="")
    retryable: bool = Field(default=False)


class ExecutionResult(BaseModel):
    """Canonical result returned by the ExecutionEnvelope."""

    model_config = ConfigDict(extra="ignore")

    status: Literal["ok", "error"] = Field(default="ok")
    data: dict[str, Any] = Field(default_factory=dict)
    error: ExecutionError | None = Field(default=None)
    metrics: ExecutionMetrics = Field(default_factory=ExecutionMetrics)
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# Routing types
# ---------------------------------------------------------------------------


class RoutingScore(BaseModel):
    """Per-skill scoring breakdown produced by the stratified router."""

    model_config = ConfigDict(extra="ignore")

    skill_id: str
    version: str
    total_score: float = Field(ge=0.0, le=1.0)
    match_score: float = Field(ge=0.0, le=1.0)
    freshness_score: float = Field(ge=0.0, le=1.0)
    aais_score: float = Field(ge=0.0, le=1.0)
    cost_penalty: float = Field(ge=0.0, le=1.0)
    risk_penalty: float = Field(ge=0.0, le=1.0)


class RoutingDecision(BaseModel):
    """The routing decision returned by StratifiedRouter.route()."""

    model_config = ConfigDict(extra="ignore")

    selected_skill_id: str | None = Field(default=None)
    selected_version: str | None = Field(default=None)
    scores: list[RoutingScore] = Field(default_factory=list)
    fallback_used: bool = Field(default=False)
    reason: str = Field(default="")


# ---------------------------------------------------------------------------
# Telemetry event
# ---------------------------------------------------------------------------


class TelemetryEvent(BaseModel):
    """One structured telemetry record emitted after each skill execution."""

    model_config = ConfigDict(extra="ignore")

    ts: str = Field(..., description="ISO-8601 timestamp")
    skill_id: str
    version: str
    status: Literal["ok", "error"]
    latency_ms: int = Field(default=0)
    budget_used: BudgetUsed = Field(default_factory=BudgetUsed)
    aais_score: float | None = Field(default=None)
    compression_ratio: float | None = Field(default=None)
    trace_id: str = Field(default="")


# ---------------------------------------------------------------------------
# AAIS score
# ---------------------------------------------------------------------------


class AAISScore(BaseModel):
    """Breakdown of an AAIS (Agent-Aligned Information Score) evaluation."""

    model_config = ConfigDict(extra="ignore")

    concision: float = Field(ge=0.0, le=1.0, description="Token/idea density")
    acronym_discipline: float = Field(ge=0.0, le=1.0, description="Defined-once usage")
    structure: float = Field(ge=0.0, le=1.0, description="Headings, bullets, schemas")
    clarity: float = Field(ge=0.0, le=1.0, description="Active/imperative voice")
    citation_lineage: float = Field(ge=0.0, le=1.0, description="Doc ID / hash / ref present")

    @property
    def total(self) -> float:
        """Weighted total: 0.25*C + 0.20*A + 0.20*S + 0.20*Cl + 0.15*L."""
        return round(
            0.25 * self.concision
            + 0.20 * self.acronym_discipline
            + 0.20 * self.structure
            + 0.20 * self.clarity
            + 0.15 * self.citation_lineage,
            4,
        )


__all__ = [
    "AAISScore",
    "BudgetConfig",
    "BudgetUsed",
    "CompressionMeta",
    "DocMeta",
    "ExecutionError",
    "ExecutionMetrics",
    "ExecutionResult",
    "IORef",
    "PDALoopConfig",
    "PolicyConfig",
    "RegisteredSkill",
    "RoutingDecision",
    "RoutingScore",
    "SkillManifest",
    "TelemetryConfig",
    "TelemetryEvent",
]
