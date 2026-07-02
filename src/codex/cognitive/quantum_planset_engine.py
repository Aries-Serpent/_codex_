"""
from codex.logging.structured_logger import logger
Quantum-Inspired Planset Engine for Codebase Improvement.

This module provides ``QuantumPlansetEngine``: a physics-inspired planner that
custom agents use to generate, score, and execute improvement strategies for the
``_codex_`` codebase.

Quantum analogies applied
--------------------------
* **Superposition** — Multiple improvement strategies co-exist simultaneously,
  each weighted by a probability amplitude derived from the physics score.
* **Collapse / Measurement** — Calling :meth:`QuantumPlansetEngine.collapse`
  "observes" the planset and returns the single highest-scoring concrete
  execution path.  Repeated collapses may choose different paths when
  stochastic sampling is enabled.
* **Entanglement** — Steps that must execute together share a coupling bond.
  Selecting an entangled step automatically promotes its partner.
* **Decoherence** — Improvement opportunities decay over time.  A step that
  has been deferred many sessions loses amplitude and eventually drops below
  the execution threshold.

Physics scoring equation (from ``guru_adapter.py``)
----------------------------------------------------
::

    Score = (Impact × Confidence × Momentum) / (Energy × (1 + Risk) × (1 + Friction))

    Amplitude = sqrt(Score)          ← quantum probability amplitude
    P(select)  = Amplitude² / ΣAmplitude²   ← Born rule normalisation

Built-in planset templates
--------------------------
Five templates cover the most common codebase improvement areas:

* ``COVERAGE_IMPROVEMENT``     — raise test coverage toward 100 %
* ``SECURITY_REMEDIATION``     — resolve CodeQL alerts by priority
* ``CI_SELF_HEALING``          — detect + auto-fix failing CI checks
* ``DEPENDENCY_MODERNISATION`` — update deps with vulnerability scan
* ``DOCUMENTATION_HYGIENE``    — fix broken links, stale docs, missing frontmatter

Agent integration
-----------------
::

    from codex.cognitive import QuantumPlansetEngine

    engine = QuantumPlansetEngine()
    planset = engine.generate("SECURITY_REMEDIATION", context={"open_alerts": 42})
    path    = engine.collapse(planset)           # highest-scoring concrete steps
    for step in path:
        logger.info(step.agent, "→", step.action)

    # Serialise for storage / cross-agent handoff
    engine.save(planset, Path(".codex/plans/active_planset.json"))
    restored = engine.load(Path(".codex/plans/active_planset.json"))
"""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DECOHERENCE_HALF_LIFE_SESSIONS: float = 5.0  # amplitude halves every 5 sessions
_EXECUTION_THRESHOLD: float = 0.05  # steps below this amplitude are pruned
_MAX_PLAN_STEPS: int = 20  # safety cap on collapsed path length


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ImprovementArea(str, Enum):
    """Predefined codebase improvement areas with built-in templates."""

    COVERAGE_IMPROVEMENT = "COVERAGE_IMPROVEMENT"
    SECURITY_REMEDIATION = "SECURITY_REMEDIATION"
    CI_SELF_HEALING = "CI_SELF_HEALING"
    DEPENDENCY_MODERNISATION = "DEPENDENCY_MODERNISATION"
    DOCUMENTATION_HYGIENE = "DOCUMENTATION_HYGIENE"
    QI_TESTING = "QI_TESTING"
    CACHE_VALIDATION = "CACHE_VALIDATION"
    TEST_ASSERTION_UPDATE = "TEST_ASSERTION_UPDATE"
    RAG_PIPELINE = "RAG_PIPELINE"
    ML_PATTERN_FEEDING = "ML_PATTERN_FEEDING"
    WORKFLOW_HEALTH = "WORKFLOW_HEALTH"
    AGENT_CHAINING = "AGENT_CHAINING"


class StepStatus(str, Enum):
    """Lifecycle state of an individual plan step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    SKIPPED = "skipped"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class PhysicsParams:
    """
    Parameters for the physics scoring equation.

    All values should be positive.  Typical ranges:
    * ``impact``, ``confidence``, ``momentum`` → 0.0 – 1.0
    * ``energy`` → 1 – 50 (computational / human-effort cost)
    * ``risk``, ``friction`` → 0.0 – 1.0
    """

    impact: float = 0.5
    confidence: float = 0.5
    momentum: float = 5.0
    energy: float = 10.0
    risk: float = 0.2
    friction: float = 0.2

    def score(self) -> float:
        """
        Compute physics score.

        Returns 0.0 when the denominator is non-positive to avoid division
        by zero.
        """
        denominator = self.energy * (1.0 + self.risk) * (1.0 + self.friction)
        if denominator <= 0.0:
            return 0.0
        return (self.impact * self.confidence * self.momentum) / denominator

    def amplitude(self) -> float:
        """Quantum probability amplitude = sqrt(score)."""
        return math.sqrt(max(self.score(), 0.0))


@dataclass
class EntanglementBond:
    """Declares that two steps must execute together."""

    step_a: str
    step_b: str
    coupling_strength: float = 1.0  # 0.0 – 1.0; 1.0 = inseparable


@dataclass
class PlanStep:
    """
    A single executable step within a planset.

    Attributes
    ----------
    step_id:
        Unique identifier (e.g. ``"COVERAGE-01"``).
    agent:
        Custom agent responsible for execution
        (e.g. ``"coverage-gapfill-agent"``).
    action:
        Short imperative description of the action.
    description:
        Longer human-readable explanation.
    physics:
        Scoring parameters.  Used to rank steps and compute amplitude.
    decoherence_sessions:
        Number of sessions this step has been deferred.
        Amplitude is multiplied by ``0.5 ** (sessions / half_life)``.
    entangled_with:
        IDs of steps this step is entangled with.
    status:
        Current lifecycle state.
    created_at:
        ISO-8601 timestamp.
    """

    step_id: str
    agent: str
    action: str
    description: str
    physics: PhysicsParams = field(default_factory=PhysicsParams)
    decoherence_sessions: int = 0
    entangled_with: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # ------------------------------------------------------------------
    # Amplitude with decoherence applied
    # ------------------------------------------------------------------

    def effective_amplitude(self) -> float:
        """
        Return amplitude after applying decoherence decay.

        Decoherence factor = 0.5 ** (sessions_deferred / half_life)
        """
        decay = 0.5 ** (self.decoherence_sessions / _DECOHERENCE_HALF_LIFE_SESSIONS)
        return self.physics.amplitude() * decay

    def is_viable(self) -> bool:
        """Return True when effective amplitude exceeds the execution threshold."""
        return self.effective_amplitude() >= _EXECUTION_THRESHOLD

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["effective_amplitude"] = self.effective_amplitude()
        d["physics_score"] = self.physics.score()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlanStep:
        data = dict(data)
        data.pop("effective_amplitude", None)
        data.pop("physics_score", None)
        data["physics"] = PhysicsParams(**data.get("physics", {}))
        data["status"] = StepStatus(data.get("status", StepStatus.PENDING.value))
        return cls(**data)


@dataclass
class QuantumPlanset:
    """
    A quantum-superposed collection of improvement steps.

    Before :meth:`QuantumPlansetEngine.collapse` is called the planset exists
    in superposition: all viable steps are present simultaneously.  After
    collapse the engine returns a concrete ordered execution path.

    Attributes
    ----------
    planset_id:
        Unique identifier (e.g. ``"SECURITY_REMEDIATION-20260226"``).
    area:
        Improvement area this planset targets.
    steps:
        All steps in superposition.
    entanglement_bonds:
        Coupling constraints between steps.
    context:
        Free-form key/value data supplied by the calling agent
        (e.g. ``{"open_alerts": 42}``).
    created_at:
        ISO-8601 creation timestamp.
    collapsed_at:
        ISO-8601 timestamp of last collapse, or None.
    """

    planset_id: str
    area: str
    steps: list[PlanStep] = field(default_factory=list)
    entanglement_bonds: list[EntanglementBond] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    collapsed_at: Optional[str] = None

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    def viable_steps(self) -> list[PlanStep]:
        """Return steps that are above the decoherence threshold."""
        return [s for s in self.steps if s.is_viable()]

    def total_amplitude(self) -> float:
        """Sum of effective amplitudes across all viable steps."""
        return sum(s.effective_amplitude() for s in self.viable_steps())

    def probability(self, step: PlanStep) -> float:
        """Born-rule probability: amplitude² / Σamplitude²."""
        total_sq = sum(s.effective_amplitude() ** 2 for s in self.viable_steps())
        if total_sq == 0.0:
            return 0.0
        return (step.effective_amplitude() ** 2) / total_sq

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "planset_id": self.planset_id,
            "area": self.area,
            "steps": [s.to_dict() for s in self.steps],
            "entanglement_bonds": [asdict(b) for b in self.entanglement_bonds],
            "context": self.context,
            "created_at": self.created_at,
            "collapsed_at": self.collapsed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuantumPlanset:
        data = dict(data)
        data["steps"] = [PlanStep.from_dict(s) for s in data.get("steps", [])]
        data["entanglement_bonds"] = [
            EntanglementBond(**b) for b in data.get("entanglement_bonds", [])
        ]
        return cls(**data)


# ---------------------------------------------------------------------------
# Built-in planset templates
# ---------------------------------------------------------------------------


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    ImprovementArea.COVERAGE_IMPROVEMENT: [
        {
            "step_id": "COV-01",
            "agent": "coverage-gapfill-agent",
            "action": "identify low-coverage modules",
            "description": "Run pytest-cov and list modules below threshold.",
            "physics": {
                "impact": 0.9,
                "confidence": 0.95,
                "momentum": 8.0,
                "energy": 5.0,
                "risk": 0.05,
                "friction": 0.1,
            },
        },
        {
            "step_id": "COV-02",
            "agent": "coverage-gapfill-agent",
            "action": "generate targeted unit tests",
            "description": "Write tests for uncovered branches; target ≥90%.",
            "physics": {
                "impact": 0.85,
                "confidence": 0.8,
                "momentum": 7.0,
                "energy": 15.0,
                "risk": 0.1,
                "friction": 0.2,
            },
            "entangled_with": ["COV-01"],
        },
        {
            "step_id": "COV-03",
            "agent": "coverage-maintenance-agent",
            "action": "raise coverage threshold in pyproject.toml",
            "description": "Increment `[tool.coverage.report].fail_under` by 5 %.",
            "physics": {
                "impact": 0.7,
                "confidence": 0.9,
                "momentum": 5.0,
                "energy": 3.0,
                "risk": 0.15,
                "friction": 0.1,
            },
            "entangled_with": ["COV-02"],
        },
        {
            "step_id": "COV-04",
            "agent": "mutation-testing-agent",
            "action": "run mutation score on new tests",
            "description": "Ensure mutation score ≥60 % for added test files.",
            "physics": {
                "impact": 0.6,
                "confidence": 0.7,
                "momentum": 4.0,
                "energy": 25.0,
                "risk": 0.2,
                "friction": 0.3,
            },
            "entangled_with": ["COV-02"],
        },
    ],
    ImprovementArea.SECURITY_REMEDIATION: [
        {
            "step_id": "SEC-01",
            "agent": "codeql-alert-resolution-agent",
            "action": "collect open CodeQL alerts via resolution pipeline",
            "description": "Run resolution_pipeline.py stages=collect,analyse.",
            "physics": {
                "impact": 0.95,
                "confidence": 0.99,
                "momentum": 9.0,
                "energy": 5.0,
                "risk": 0.05,
                "friction": 0.05,
            },
        },
        {
            "step_id": "SEC-02",
            "agent": "codeql-alert-resolution-agent",
            "action": "auto-remediate P0/P1 alerts",
            "description": "Apply codemods for sql_injection, subprocess, hardcoded patterns.",
            "physics": {
                "impact": 0.9,
                "confidence": 0.8,
                "momentum": 9.0,
                "energy": 10.0,
                "risk": 0.2,
                "friction": 0.1,
            },
            "entangled_with": ["SEC-01"],
        },
        {
            "step_id": "SEC-03",
            "agent": "dependency-vulnerability-scanner",
            "action": "scan requirements for known CVEs",
            "description": "Run pip-audit; document CVEs without fixes in lock.txt.",
            "physics": {
                "impact": 0.85,
                "confidence": 0.95,
                "momentum": 7.0,
                "energy": 8.0,
                "risk": 0.1,
                "friction": 0.1,
            },
        },
        {
            "step_id": "SEC-04",
            "agent": "secret-detection-agent",
            "action": "scan for accidentally committed secrets",
            "description": "Run detect-secrets baseline; update .secrets.baseline.",
            "physics": {
                "impact": 0.8,
                "confidence": 0.9,
                "momentum": 6.0,
                "energy": 5.0,
                "risk": 0.05,
                "friction": 0.05,
            },
        },
        {
            "step_id": "SEC-05",
            "agent": "codeql-alert-resolution-agent",
            "action": "validate and close resolved alerts",
            "description": "Run stages=validate,close for confirmed fixes.",
            "physics": {
                "impact": 0.7,
                "confidence": 0.85,
                "momentum": 6.0,
                "energy": 5.0,
                "risk": 0.1,
                "friction": 0.1,
            },
            "entangled_with": ["SEC-02"],
        },
    ],
    ImprovementArea.CI_SELF_HEALING: [
        {
            "step_id": "CI-01",
            "agent": "ci-failure-resolution-agent",
            "action": "retrieve and categorise recent CI failures",
            "description": "Use get_job_logs(failed_only=True) for last 25 h.",
            "physics": {
                "impact": 0.9,
                "confidence": 0.95,
                "momentum": 9.0,
                "energy": 5.0,
                "risk": 0.05,
                "friction": 0.05,
            },
        },
        {
            "step_id": "CI-02",
            "agent": "ci-auto-healer-agent",
            "action": "apply embedded fix patterns",
            "description": "Match failures to fix library; apply patches; push.",
            "physics": {
                "impact": 0.85,
                "confidence": 0.75,
                "momentum": 8.0,
                "energy": 12.0,
                "risk": 0.2,
                "friction": 0.15,
            },
            "entangled_with": ["CI-01"],
        },
        {
            "step_id": "CI-03",
            "agent": "autonomous-test-healer-agent",
            "action": "stabilise flaky tests",
            "description": "Detect and apply @pytest.mark.retry or deterministic mocks.",
            "physics": {
                "impact": 0.75,
                "confidence": 0.7,
                "momentum": 6.0,
                "energy": 15.0,
                "risk": 0.25,
                "friction": 0.2,
            },
        },
        {
            "step_id": "CI-04",
            "agent": "workflow-optimization-agent",
            "action": "optimise workflow job parallelism and caching",
            "description": "Identify sequential jobs that can run in parallel; add cache keys.",
            "physics": {
                "impact": 0.65,
                "confidence": 0.8,
                "momentum": 5.0,
                "energy": 10.0,
                "risk": 0.1,
                "friction": 0.2,
            },
        },
    ],
    ImprovementArea.DEPENDENCY_MODERNISATION: [
        {
            "step_id": "DEP-01",
            "agent": "dependency-conflict-agent",
            "action": "audit requirements for conflicts",
            "description": "Run pip-check; detect version incompatibilities.",
            "physics": {
                "impact": 0.8,
                "confidence": 0.95,
                "momentum": 7.0,
                "energy": 5.0,
                "risk": 0.1,
                "friction": 0.1,
            },
        },
        {
            "step_id": "DEP-02",
            "agent": "dependency-vulnerability-scanner",
            "action": "upgrade packages with known CVEs",
            "description": "Apply pip-audit --fix; document unfixable CVEs in lock.txt.",
            "physics": {
                "impact": 0.9,
                "confidence": 0.85,
                "momentum": 8.0,
                "energy": 10.0,
                "risk": 0.2,
                "friction": 0.15,
            },
            "entangled_with": ["DEP-01"],
        },
        {
            "step_id": "DEP-03",
            "agent": "dependency-conflict-agent",
            "action": "pin compatible version ranges",
            "description": "Update pyproject.toml/requirements with compatible bounds.",
            "physics": {
                "impact": 0.7,
                "confidence": 0.8,
                "momentum": 6.0,
                "energy": 8.0,
                "risk": 0.15,
                "friction": 0.1,
            },
            "entangled_with": ["DEP-02"],
        },
    ],
    ImprovementArea.DOCUMENTATION_HYGIENE: [
        {
            "step_id": "DOC-01",
            "agent": "link-validator-agent",
            "action": "scan docs for broken internal/external links",
            "description": "Run validate-links.py; generate broken-link report.",
            "physics": {
                "impact": 0.7,
                "confidence": 0.98,
                "momentum": 6.0,
                "energy": 5.0,
                "risk": 0.02,
                "friction": 0.05,
            },
        },
        {
            "step_id": "DOC-02",
            "agent": "doc-freshness-checker",
            "action": "identify stale documentation",
            "description": "Flag docs with timestamps > 90 days and no recent changes.",
            "physics": {
                "impact": 0.65,
                "confidence": 0.9,
                "momentum": 5.0,
                "energy": 5.0,
                "risk": 0.05,
                "friction": 0.1,
            },
        },
        {
            "step_id": "DOC-03",
            "agent": "unified-doc-agent",
            "action": "add YAML frontmatter to agent files missing name/description",
            "description": "Patch .github/agents/*.md without frontmatter; validates via Copilot UI.",  # noqa: E501
            "physics": {
                "impact": 0.75,
                "confidence": 0.95,
                "momentum": 6.0,
                "energy": 5.0,
                "risk": 0.05,
                "friction": 0.05,
            },
        },
        {
            "step_id": "DOC-04",
            "agent": "documentation-consolidator",
            "action": "consolidate duplicate doc files",
            "description": "Identify files with >70 % similarity; merge and update cross-refs.",
            "physics": {
                "impact": 0.6,
                "confidence": 0.75,
                "momentum": 4.0,
                "energy": 15.0,
                "risk": 0.2,
                "friction": 0.3,
            },
        },
    ],
    ImprovementArea.QI_TESTING: [
        {
            "step_id": "QI-01",
            "agent": "quantum-compliance-tuning-agent",
            "action": "run raw scalability experiment and save baseline JSON",
            "description": (
                "Execute exp1b_revalidation.py --multi-seed --scenarios 200 "
                "--use-verified-labels; persist results to "
                "audit_artifacts/results/phase4_scalability_raw.json. "
                "Establishes per-seed accuracy baseline for patterns H/F/E/C."
            ),
            "physics": {
                "impact": 0.95,
                "confidence": 0.99,
                "momentum": 9.0,
                "energy": 8.0,
                "risk": 0.05,
                "friction": 0.05,
            },
        },
        {
            "step_id": "QI-02",
            "agent": "quantum-compliance-tuning-agent",
            "action": "generate per-pattern accuracy report",
            "description": (
                "Run per_pattern_report.py against baseline JSON; identify "
                "patterns below 95 % accuracy threshold (H, F, E, C). "
                "Output: audit_artifacts/poctune/iteration_N_per_pattern.json."
            ),
            "physics": {
                "impact": 0.9,
                "confidence": 0.98,
                "momentum": 8.0,
                "energy": 5.0,
                "risk": 0.05,
                "friction": 0.05,
            },
            "entangled_with": ["QI-01"],
        },
        {
            "step_id": "QI-03",
            "agent": "quantum-compliance-tuning-agent",
            "action": "update target_patterns.json tuning rules",
            "description": (
                "Increase effect_factor for failing patterns in "
                "audit_artifacts/poctune/target_patterns.json. "
                "BayesianAssessor.apply_tuning_rules() and "
                "FuzzyEngine.apply_membership_tuning() pick these up at runtime."
            ),
            "physics": {
                "impact": 0.85,
                "confidence": 0.85,
                "momentum": 7.0,
                "energy": 5.0,
                "risk": 0.15,
                "friction": 0.1,
            },
            "entangled_with": ["QI-02"],
        },
        {
            "step_id": "QI-04",
            "agent": "quantum-compliance-tuning-agent",
            "action": "run tuned experiment with CODEX_BAYESIAN_MODE + CODEX_FUZZY_MODE",
            "description": (
                "Re-run exp1b_revalidation.py with CODEX_BAYESIAN_MODE=true "
                "CODEX_FUZZY_MODE=true; save to "
                "audit_artifacts/poctune/iteration_N_results.json. "
                "Applies Bayesian posterior boosting and Fuzzy boundary shifts."
            ),
            "physics": {
                "impact": 0.88,
                "confidence": 0.82,
                "momentum": 7.5,
                "energy": 10.0,
                "risk": 0.2,
                "friction": 0.15,
            },
            "entangled_with": ["QI-03"],
        },
        {
            "step_id": "QI-05",
            "agent": "quantum-compliance-tuning-agent",
            "action": "compare per-pattern accuracy before vs after tuning",
            "description": (
                "Diff iteration_N_per_pattern.json against baseline; confirm "
                "improvement ≥5 pp on failing patterns. "
                "k₁ must remain ≤0.35; coherence must remain ≥0.650."
            ),
            "physics": {
                "impact": 0.8,
                "confidence": 0.9,
                "momentum": 7.0,
                "energy": 5.0,
                "risk": 0.1,
                "friction": 0.1,
            },
            "entangled_with": ["QI-04"],
        },
        {
            "step_id": "QI-06",
            "agent": "quantum-compliance-tuning-agent",
            "action": "regression guard — verify seed=42 accuracy=100% and k1≤0.35",
            "description": (
                "Run single-seed benchmark (seed=42, 110 scenarios). "
                "Assert accuracy==100 %, k₁≤0.35. "
                "Fail-fast: revert target_patterns.json if guard fails."
            ),
            "physics": {
                "impact": 0.92,
                "confidence": 0.97,
                "momentum": 9.0,
                "energy": 6.0,
                "risk": 0.05,
                "friction": 0.05,
            },
            "entangled_with": ["QI-05"],
        },
        {
            "step_id": "QI-07",
            "agent": "quantum-compliance-tuning-agent",
            "action": "accept or revert tuning iteration",
            "description": (
                "If improvement ≥5 pp AND no regression on A/B/D/G patterns "
                "AND regression guard passed → commit target_patterns.json. "
                "Otherwise revert file and schedule next iteration (max 5 total)."
            ),
            "physics": {
                "impact": 0.75,
                "confidence": 0.88,
                "momentum": 6.0,
                "energy": 5.0,
                "risk": 0.1,
                "friction": 0.1,
            },
            "entangled_with": ["QI-06"],
        },
    ],
    ImprovementArea.CACHE_VALIDATION: [
        {
            "step_id": "CACHE-01",
            "agent": "cache-management-agent",
            "action": "analyse cache implementation for correctness gaps",
            "description": (
                "Inspect cache classes for missing eviction, TTL, and consistency "
                "guarantees. Source: CUSTOM_AGENT_PLANSET_CACHE_LOGIC_VALIDATOR.md Phase 1."
            ),
            "physics": {
                "impact": 0.85,
                "confidence": 0.92,
                "momentum": 7.0,
                "energy": 6.0,
                "risk": 0.1,
                "friction": 0.1,
            },
        },
        {
            "step_id": "CACHE-02",
            "agent": "cache-management-agent",
            "action": "generate property-based tests for cache invariants",
            "description": (
                "Write hypothesis/property tests for cache correctness, consistency, "
                "and performance. Source: Phase 2 of cache validator planset."
            ),
            "physics": {
                "impact": 0.8,
                "confidence": 0.85,
                "momentum": 6.5,
                "energy": 10.0,
                "risk": 0.15,
                "friction": 0.15,
            },
            "entangled_with": ["CACHE-01"],
        },
        {
            "step_id": "CACHE-03",
            "agent": "cache-manager-integration",
            "action": "run cache validation suite and collect failure report",
            "description": "Execute property tests; export pass/fail report per cache class.",
            "physics": {
                "impact": 0.75,
                "confidence": 0.88,
                "momentum": 6.0,
                "energy": 8.0,
                "risk": 0.1,
                "friction": 0.1,
            },
            "entangled_with": ["CACHE-02"],
        },
        {
            "step_id": "CACHE-04",
            "agent": "cache-management-agent",
            "action": "fix identified cache defects and re-validate",
            "description": "Apply patches for failing invariants; re-run suite to confirm green.",
            "physics": {
                "impact": 0.7,
                "confidence": 0.8,
                "momentum": 5.5,
                "energy": 12.0,
                "risk": 0.2,
                "friction": 0.2,
            },
            "entangled_with": ["CACHE-03"],
        },
    ],
    ImprovementArea.TEST_ASSERTION_UPDATE: [
        {
            "step_id": "ASSERT-01",
            "agent": "test-alignment-fixer-enhanced",
            "action": "scan codebase for stale test assertions after API changes",
            "description": (
                "Detect mismatches between test assertions and current implementation. "
                "Source: CUSTOM_AGENT_PLANSET_TEST_ASSERTION_UPDATER.md."
            ),
            "physics": {
                "impact": 0.88,
                "confidence": 0.95,
                "momentum": 8.0,
                "energy": 6.0,
                "risk": 0.08,
                "friction": 0.08,
            },
        },
        {
            "step_id": "ASSERT-02",
            "agent": "test-alignment-fixer-enhanced",
            "action": "analyse implementation to derive correct expected values",
            "description": "Run implementation analyser to extract correct return types/values.",
            "physics": {
                "impact": 0.82,
                "confidence": 0.88,
                "momentum": 7.0,
                "energy": 8.0,
                "risk": 0.12,
                "friction": 0.1,
            },
            "entangled_with": ["ASSERT-01"],
        },
        {
            "step_id": "ASSERT-03",
            "agent": "test-alignment-fixer-enhanced",
            "action": "auto-update stale assertions preserving test intent",
            "description": "Apply minimal diffs to fix assertions; preserve coverage and intent.",
            "physics": {
                "impact": 0.85,
                "confidence": 0.82,
                "momentum": 7.5,
                "energy": 10.0,
                "risk": 0.18,
                "friction": 0.12,
            },
            "entangled_with": ["ASSERT-02"],
        },
        {
            "step_id": "ASSERT-04",
            "agent": "autonomous-test-healer-agent",
            "action": "validate updated assertions pass CI and mutation score ≥60%",
            "description": "Run pytest + mutmut on changed files; fail if score drops.",
            "physics": {
                "impact": 0.75,
                "confidence": 0.90,
                "momentum": 6.0,
                "energy": 15.0,
                "risk": 0.1,
                "friction": 0.1,
            },
            "entangled_with": ["ASSERT-03"],
        },
    ],
    ImprovementArea.RAG_PIPELINE: [
        {
            "step_id": "RAG-01",
            "agent": "rag-module-management-agent",
            "action": "implement Phase 3 production features (streaming, auth, rate-limit)",
            "description": (
                "Phase 1+2 complete. Implement Phase 3: streaming responses, "
                "API auth middleware, per-user rate limiting. "
                "Source: PRODUCTION_RAG_PIPELINE_PLANSET.md Phase 3."
            ),
            "physics": {
                "impact": 0.92,
                "confidence": 0.88,
                "momentum": 9.0,
                "energy": 12.0,
                "risk": 0.15,
                "friction": 0.1,
            },
        },
        {
            "step_id": "RAG-02",
            "agent": "rag-freshness-loop-agent",
            "action": "add incremental index refresh and stale-entry eviction",
            "description": "Wire freshness-loop to embedding pipeline; schedule nightly refresh.",
            "physics": {
                "impact": 0.85,
                "confidence": 0.85,
                "momentum": 8.0,
                "energy": 10.0,
                "risk": 0.12,
                "friction": 0.1,
            },
            "entangled_with": ["RAG-01"],
        },
        {
            "step_id": "RAG-03",
            "agent": "integration-test-runner",
            "action": "run end-to-end RAG pipeline integration tests",
            "description": "Validate query→retrieval→rerank→response pipeline under load.",
            "physics": {
                "impact": 0.8,
                "confidence": 0.9,
                "momentum": 7.0,
                "energy": 8.0,
                "risk": 0.1,
                "friction": 0.1,
            },
            "entangled_with": ["RAG-02"],
        },
        {
            "step_id": "RAG-04",
            "agent": "performance-monitor-agent",
            "action": "benchmark retrieval latency P95 ≤ 200ms",
            "description": "Run latency benchmarks; tune HNSW/IVF params if P95 > 200ms.",
            "physics": {
                "impact": 0.75,
                "confidence": 0.82,
                "momentum": 6.0,
                "energy": 10.0,
                "risk": 0.15,
                "friction": 0.15,
            },
            "entangled_with": ["RAG-03"],
        },
    ],
    ImprovementArea.ML_PATTERN_FEEDING: [
        {
            "step_id": "ML-01",
            "agent": "ml-validation-suite-agent",
            "action": "extract patterns from existing ML run history",
            "description": (
                "Parse audit_artifacts/results/ for recurring decision patterns. "
                "Source: ML_PATTERN_FEEDING_PLANSET.md Phase 1."
            ),
            "physics": {
                "impact": 0.88,
                "confidence": 0.92,
                "momentum": 8.0,
                "energy": 7.0,
                "risk": 0.08,
                "friction": 0.08,
            },
        },
        {
            "step_id": "ML-02",
            "agent": "cognitive-brain-manager",
            "action": "apply quantum interference to merge pattern libraries",
            "description": (
                "Feed extracted patterns through QuantumPlansetEngine.interference(); "
                "boost overlapping patterns constructively. Phase 2."
            ),
            "physics": {
                "impact": 0.85,
                "confidence": 0.85,
                "momentum": 8.0,
                "energy": 8.0,
                "risk": 0.1,
                "friction": 0.1,
            },
            "entangled_with": ["ML-01"],
        },
        {
            "step_id": "ML-03",
            "agent": "cognitive-brain-manager",
            "action": "feed merged patterns into cognitive brain pattern store",
            "description": "Call AgentBrainInterface.submit_learning() for each merged pattern.",
            "physics": {
                "impact": 0.9,
                "confidence": 0.88,
                "momentum": 8.5,
                "energy": 6.0,
                "risk": 0.08,
                "friction": 0.06,
            },
            "entangled_with": ["ML-02"],
        },
        {
            "step_id": "ML-04",
            "agent": "rag-freshness-loop-agent",
            "action": "automate nightly pattern extraction and brain update",
            "description": "Wire ML-01→ML-03 pipeline into nightly GitHub Actions schedule.",
            "physics": {
                "impact": 0.75,
                "confidence": 0.82,
                "momentum": 6.0,
                "energy": 8.0,
                "risk": 0.12,
                "friction": 0.1,
            },
            "entangled_with": ["ML-03"],
        },
    ],
    ImprovementArea.WORKFLOW_HEALTH: [
        {
            "step_id": "WF-01",
            "agent": "workflow-health-monitor",
            "action": "measure all workflow state amplitudes (quantum collapse of states)",
            "description": (
                "Fetch all workflow runs from last 72h; compute health amplitude "
                "per workflow. Source: WORKFLOW_HEALTH_AUTOMATION_PLANSET.md Phase 1."
            ),
            "physics": {
                "impact": 0.88,
                "confidence": 0.95,
                "momentum": 8.5,
                "energy": 5.0,
                "risk": 0.05,
                "friction": 0.05,
            },
        },
        {
            "step_id": "WF-02",
            "agent": "workflow-analytics-agent",
            "action": "apply entanglement effects — correlate dependent workflow failures",
            "description": "Identify workflows whose failures co-occur; flag coupled failure chains.",  # noqa: E501
            "physics": {
                "impact": 0.82,
                "confidence": 0.88,
                "momentum": 7.5,
                "energy": 6.0,
                "risk": 0.1,
                "friction": 0.08,
            },
            "entangled_with": ["WF-01"],
        },
        {
            "step_id": "WF-03",
            "agent": "workflow-health-monitor",
            "action": "calculate aggregate health metrics dashboard",
            "description": "Produce Markdown health table: success rate, P95 duration, flake rate.",
            "physics": {
                "impact": 0.78,
                "confidence": 0.92,
                "momentum": 7.0,
                "energy": 5.0,
                "risk": 0.05,
                "friction": 0.05,
            },
            "entangled_with": ["WF-02"],
        },
        {
            "step_id": "WF-04",
            "agent": "workflow-optimization-agent",
            "action": "quantum tunnelling detection — find workflows stuck in failure loops",
            "description": "Identify workflows failing >3 consecutive runs; auto-disable + alert.",
            "physics": {
                "impact": 0.85,
                "confidence": 0.88,
                "momentum": 8.0,
                "energy": 7.0,
                "risk": 0.1,
                "friction": 0.08,
            },
            "entangled_with": ["WF-03"],
        },
        {
            "step_id": "WF-05",
            "agent": "workflow-ci-fixer",
            "action": "apply automated fixes for stuck workflows",
            "description": "Apply fix patterns for timeout, cache-miss, dep-conflict failures.",
            "physics": {
                "impact": 0.8,
                "confidence": 0.8,
                "momentum": 7.0,
                "energy": 10.0,
                "risk": 0.18,
                "friction": 0.15,
            },
            "entangled_with": ["WF-04"],
        },
    ],
    ImprovementArea.AGENT_CHAINING: [
        {
            "step_id": "CHAIN-01",
            "agent": "agent-orchestrator",
            "action": "implement agent state management for chained executions",
            "description": (
                "Build AgentStateManager: tracks context handoff between chained agents. "
                "Source: AGENT_CHAINING_INTEGRATION_PLANSET.md Phase 1."
            ),
            "physics": {
                "impact": 0.9,
                "confidence": 0.88,
                "momentum": 8.5,
                "energy": 10.0,
                "risk": 0.12,
                "friction": 0.1,
            },
        },
        {
            "step_id": "CHAIN-02",
            "agent": "agent-orchestrator",
            "action": "build orchestrator core with sequential/parallel routing",
            "description": (
                "Implement ChainOrchestrator.route(): sequential_chain, "
                "parallel_fan_out, conditional_routing patterns. Phase 2."
            ),
            "physics": {
                "impact": 0.88,
                "confidence": 0.85,
                "momentum": 8.0,
                "energy": 12.0,
                "risk": 0.15,
                "friction": 0.12,
            },
            "entangled_with": ["CHAIN-01"],
        },
        {
            "step_id": "CHAIN-03",
            "agent": "agent-orchestrator",
            "action": "optimise context compression for long chains",
            "description": "Apply ContextCompressor to reduce token overhead across chain hops.",
            "physics": {
                "impact": 0.78,
                "confidence": 0.82,
                "momentum": 6.5,
                "energy": 8.0,
                "risk": 0.12,
                "friction": 0.1,
            },
            "entangled_with": ["CHAIN-02"],
        },
        {
            "step_id": "CHAIN-04",
            "agent": "workflow-management-agent",
            "action": "wire agent chains into GitHub Actions reusable workflows",
            "description": "Create reusable workflow templates for common agent chain patterns.",
            "physics": {
                "impact": 0.82,
                "confidence": 0.88,
                "momentum": 7.5,
                "energy": 8.0,
                "risk": 0.1,
                "friction": 0.08,
            },
            "entangled_with": ["CHAIN-03"],
        },
        {
            "step_id": "CHAIN-05",
            "agent": "integration-test-runner",
            "action": "run end-to-end chain integration tests",
            "description": "Verify context flows correctly through 3-agent and 5-agent chains.",
            "physics": {
                "impact": 0.75,
                "confidence": 0.90,
                "momentum": 6.0,
                "energy": 10.0,
                "risk": 0.1,
                "friction": 0.1,
            },
            "entangled_with": ["CHAIN-04"],
        },
    ],
}


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class QuantumPlansetEngine:
    """
    Generate, score, collapse, and persist quantum-inspired plansets.

    Parameters
    ----------
    planset_dir:
        Directory where plansets are saved/loaded.
        Defaults to ``.codex/plans/quantum/``.
    decoherence_rate:
        Amplitude decay per deferred session.  Default uses the global
        half-life constant.

    Examples
    --------
    >>> engine = QuantumPlansetEngine()
    >>> planset = engine.generate("SECURITY_REMEDIATION", context={"open_alerts": 42})
    >>> path = engine.collapse(planset)
    >>> [s.step_id for s in path]
    ['SEC-01', 'SEC-02', 'SEC-05', 'SEC-03', 'SEC-04']
    """

    def __init__(
        self,
        planset_dir: Path = Path(".codex/plans/quantum"),
        decoherence_rate: float = _DECOHERENCE_HALF_LIFE_SESSIONS,
    ) -> None:
        self._planset_dir = planset_dir
        self._decoherence_rate = decoherence_rate

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        area: str,
        context: Optional[dict[str, Any]] = None,
        extra_steps: Optional[Sequence[PlanStep]] = None,
    ) -> QuantumPlanset:
        """
        Generate a new planset in superposition for the given improvement area.

        Parameters
        ----------
        area:
            One of the :class:`ImprovementArea` values, or a custom string
            for bespoke plansets supplied via ``extra_steps``.
        context:
            Agent-supplied key/value pairs (e.g. ``{"open_alerts": 42}``).
        extra_steps:
            Additional steps not in the built-in template.

        Returns
        -------
        QuantumPlanset
            Planset in superposition with all viable steps.
        """
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        planset_id = f"{area}-{ts}"

        # Build steps from template + extras
        template_defs = _TEMPLATES.get(area, [])
        steps: list[PlanStep] = []
        for defn in template_defs:
            defn = dict(defn)
            physics_kw = defn.pop("physics", {})
            defn["physics"] = PhysicsParams(**physics_kw)
            defn.setdefault("entangled_with", [])
            defn.setdefault("decoherence_sessions", 0)
            steps.append(PlanStep(**defn))

        if extra_steps:
            steps.extend(list(extra_steps))

        # Build entanglement bonds from step declarations
        bonds: list[EntanglementBond] = []
        seen_bonds: set[Any] = set()
        for step in steps:
            for partner_id in step.entangled_with:
                bond_key = tuple(sorted([step.step_id, partner_id]))
                if bond_key not in seen_bonds:
                    seen_bonds.add(bond_key)
                    bonds.append(
                        EntanglementBond(
                            step_a=step.step_id,
                            step_b=partner_id,
                            coupling_strength=0.9,
                        )
                    )

        # Apply context-driven momentum boost
        if context:
            self._apply_context_momentum(steps, context, area)

        return QuantumPlanset(
            planset_id=planset_id,
            area=area,
            steps=steps,
            entanglement_bonds=bonds,
            context=context or {},
        )

    def score_step(self, step: PlanStep) -> float:
        """Return the effective amplitude of a single step."""
        return step.effective_amplitude()

    def collapse(self, planset: QuantumPlanset) -> list[PlanStep]:
        """
        "Measure" the planset and return a concrete ordered execution path.

        Steps are ordered by effective amplitude (descending).  Entangled
        partners of selected steps are promoted to immediately follow their
        anchor.  Pruned steps (below threshold or already complete/skipped)
        are excluded.

        The planset's ``collapsed_at`` is updated in place.
        """
        planset.collapsed_at = datetime.now(timezone.utc).isoformat()

        viable = [
            s
            for s in planset.steps
            if s.is_viable() and s.status not in (StepStatus.COMPLETE, StepStatus.SKIPPED)
        ]
        if not viable:
            return []

        # Sort by effective amplitude (highest first)
        viable.sort(key=lambda s: s.effective_amplitude(), reverse=True)

        # Build ordered path respecting entanglement
        seen_ids: set[Any] = set()
        path: list[PlanStep] = []

        # Index for fast lookup
        step_by_id: dict[str, PlanStep] = {s.step_id: s for s in planset.steps}

        for step in viable:
            if step.step_id in seen_ids:
                continue
            path.append(step)
            seen_ids.add(step.step_id)

            # Promote entangled partners immediately after anchor
            for partner_id in step.entangled_with:
                if partner_id not in seen_ids and partner_id in step_by_id:
                    partner = step_by_id[partner_id]
                    if partner.is_viable() and partner.status not in (
                        StepStatus.COMPLETE,
                        StepStatus.SKIPPED,
                    ):
                        path.append(partner)
                        seen_ids.add(partner_id)

            if len(path) >= _MAX_PLAN_STEPS:
                break

        return path

    def apply_decoherence(self, planset: QuantumPlanset, sessions: int = 1) -> None:
        """
        Age all pending steps by ``sessions``, increasing their decoherence.

        Steps that fall below the execution threshold after ageing are left in
        the planset but :meth:`PlanStep.is_viable` will return ``False``.
        """
        for step in planset.steps:
            if step.status == StepStatus.PENDING:
                step.decoherence_sessions += sessions

    def interference(
        self,
        planset_a: QuantumPlanset,
        planset_b: QuantumPlanset,
    ) -> QuantumPlanset:
        """
        Combine two plansets via quantum interference.

        * Steps present in both plansets have their amplitudes added
          (constructive interference → promoted).
        * Steps present in only one planset retain their own amplitude.
        * The resulting planset's area is ``"<A>+<B>"``.

        Returns
        -------
        QuantumPlanset
            Merged planset with interference-adjusted amplitudes.
        """
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        merged_area = f"{planset_a.area}+{planset_b.area}"

        # Index B steps by action (semantic key)
        b_by_action: dict[str, PlanStep] = {s.action: s for s in planset_b.steps}

        result_steps: list[PlanStep] = []
        used_b_actions: set[Any] = set()

        for step_a in planset_a.steps:
            if step_a.action in b_by_action:
                # Constructive interference: boost momentum
                step_b = b_by_action[step_a.action]
                boosted = PhysicsParams(
                    impact=max(step_a.physics.impact, step_b.physics.impact),
                    confidence=max(step_a.physics.confidence, step_b.physics.confidence),
                    momentum=step_a.physics.momentum + step_b.physics.momentum,
                    energy=min(step_a.physics.energy, step_b.physics.energy),
                    risk=min(step_a.physics.risk, step_b.physics.risk),
                    friction=min(step_a.physics.friction, step_b.physics.friction),
                )
                merged_step = PlanStep(
                    step_id=step_a.step_id,
                    agent=step_a.agent,
                    action=step_a.action,
                    description=step_a.description,
                    physics=boosted,
                    entangled_with=list(set(step_a.entangled_with + step_b.entangled_with)),
                )
                result_steps.append(merged_step)
                used_b_actions.add(step_a.action)
            else:
                result_steps.append(step_a)

        # Add non-overlapping steps from B
        for step_b in planset_b.steps:
            if step_b.action not in used_b_actions:
                result_steps.append(step_b)

        combined_bonds = planset_a.entanglement_bonds + planset_b.entanglement_bonds
        return QuantumPlanset(
            planset_id=f"{merged_area}-{ts}",
            area=merged_area,
            steps=result_steps,
            entanglement_bonds=combined_bonds,
            context={**planset_a.context, **planset_b.context},
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, planset: QuantumPlanset, path: Optional[Path] = None) -> Path:
        """
        Serialise planset to JSON and write to disk.

        Parameters
        ----------
        planset:
            Planset to save.
        path:
            Destination file.  Defaults to
            ``<planset_dir>/<planset_id>.json``.

        Returns
        -------
        Path
            The file that was written.
        """
        if path is None:
            self._planset_dir.mkdir(parents=True, exist_ok=True)
            path = self._planset_dir / f"{planset.planset_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(planset.to_dict(), indent=2), encoding="utf-8")
        return path

    def load(self, path: Path) -> QuantumPlanset:
        """Load a planset from a JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return QuantumPlanset.from_dict(data)

    def summary(self, planset: QuantumPlanset) -> str:
        """Return a short human-readable summary of the planset."""
        total = len(planset.steps)
        viable = len(planset.viable_steps())
        top = sorted(planset.viable_steps(), key=lambda s: s.effective_amplitude(), reverse=True)
        top_ids = ", ".join(s.step_id for s in top[:3])
        return (
            f"QuantumPlanset [{planset.planset_id}]  "
            f"area={planset.area}  steps={viable}/{total} viable  "
            f"top3=[{top_ids}]  total_amplitude={planset.total_amplitude():.4f}"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_context_momentum(
        steps: list[PlanStep],
        context: dict[str, Any],
        area: str,
    ) -> None:
        """
        Boost momentum for steps based on context signals.

        Rules
        -----
        * ``open_alerts > 50`` → SEC-01, SEC-02 momentum × 1.5
        * ``coverage_pct < 70`` → COV-01, COV-02 momentum × 1.4
        * ``failing_checks > 5`` → CI-01, CI-02 momentum × 1.6
        * ``stale_deps > 10`` → DEP-01, DEP-02 momentum × 1.3
        """
        boosts: dict[str, float] = {}

        if area == ImprovementArea.SECURITY_REMEDIATION:
            if context.get("open_alerts", 0) > 50:
                boosts = {"SEC-01": 1.5, "SEC-02": 1.5}

        elif area == ImprovementArea.COVERAGE_IMPROVEMENT:
            if context.get("coverage_pct", 100) < 70:
                boosts = {"COV-01": 1.4, "COV-02": 1.4}

        elif area == ImprovementArea.CI_SELF_HEALING:
            if context.get("failing_checks", 0) > 5:
                boosts = {"CI-01": 1.6, "CI-02": 1.6}

        elif area == ImprovementArea.DEPENDENCY_MODERNISATION:
            if context.get("stale_deps", 0) > 10:
                boosts = {"DEP-01": 1.3, "DEP-02": 1.3}

        elif area == ImprovementArea.QI_TESTING:
            # Boost baseline + regression-guard steps when pattern accuracy is low
            failing = context.get("failing_patterns", 0)
            if failing >= 2:
                boosts = {"QI-01": 1.5, "QI-06": 1.6}
            elif failing >= 1:
                boosts = {"QI-01": 1.3, "QI-06": 1.4}
            # Extra boost for regression guard when k1 is near limit
            if context.get("k1", 0.0) >= 0.33:
                boosts["QI-06"] = max(boosts.get("QI-06", 1.0), 1.7)

        elif area == ImprovementArea.CACHE_VALIDATION:
            if context.get("cache_failures", 0) > 5:
                boosts = {"CACHE-01": 1.4, "CACHE-04": 1.5}

        elif area == ImprovementArea.TEST_ASSERTION_UPDATE:
            if context.get("stale_assertions", 0) > 20:
                boosts = {"ASSERT-01": 1.4, "ASSERT-03": 1.3}

        elif area == ImprovementArea.RAG_PIPELINE:
            if context.get("phase3_pending", False):
                boosts = {"RAG-01": 1.6, "RAG-02": 1.4}

        elif area == ImprovementArea.ML_PATTERN_FEEDING:
            if context.get("pattern_lag_sessions", 0) > 3:
                boosts = {"ML-01": 1.4, "ML-03": 1.5}

        elif area == ImprovementArea.WORKFLOW_HEALTH:
            if context.get("stuck_workflows", 0) > 0:
                boosts = {"WF-04": 1.6, "WF-05": 1.5}

        elif area == ImprovementArea.AGENT_CHAINING:
            if context.get("chain_depth_needed", 0) >= 3:
                boosts = {"CHAIN-01": 1.4, "CHAIN-02": 1.5}

        for step in steps:
            if step.step_id in boosts:
                step.physics.momentum = min(step.physics.momentum * boosts[step.step_id], 10.0)
