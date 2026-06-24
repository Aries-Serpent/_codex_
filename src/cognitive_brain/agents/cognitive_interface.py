"""
Cognitive Brain Interface for Autonomous AI Agents (Phase 5)

Provides a high-level decision-making API that wraps QuantumComplianceAssessor
for use in autonomous agent workflows, chain prompting, and multi-turn sessions.

Feature flag: No additional flag — uses CODEX_BAYESIAN_MODE / CODEX_FUZZY_MODE
              from the underlying assessor.

AGENT_INTENT: Primary cognitive decision substrate for autonomous agent pipelines.
DETERMINISTIC: If config seed is fixed, decision chains are reproducible.
AGENT_SAFE: Thread-safe reads; no shared mutable state between sessions.

API:
    brain = CognitiveBrain.create()
    decision = brain.decide(context="compliance_audit", inputs=audit_dict)
    hints  = decision.agent_hints   # workflow guidance
    state  = decision.cognitive_state  # persist / hand off to next agent

Research basis:
    - OpenAI Agent Framework (2024): Cognitive architectures for decision-making
    - DeepMind Multi-Agent Systems (2024): Deterministic handoff protocols
    - LangChain Agent Patterns (2024): Memory-augmented autonomous agents
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Public dataclasses
# ---------------------------------------------------------------------------


@dataclass
class CognitiveDecision:
    """
    Agent-friendly cognitive decision output.

    AGENT_USAGE: Use as the canonical decision format for agent chains.
    """

    decision: str  # ComplianceDecision.value string
    confidence: float  # 0.0–1.0
    reasoning: str  # Human/agent-readable explanation
    coherence: float  # Quantum state quality (≥0.650 = good)
    used_superposition: bool  # Whether quantum path was taken
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    cognitive_state: dict[str, Any] = field(default_factory=dict)
    agent_hints: dict[str, str] = field(default_factory=dict)


@dataclass
class AgentHealthSnapshot:
    """Lightweight cognitive health summary for pre-decision checks."""

    coherence: float  # Latest coherence reading
    decision_count: int  # Total decisions this session
    error_count: int  # Errors encountered this session
    health_status: str  # "healthy" | "degraded" | "critical"


# ---------------------------------------------------------------------------
# CognitiveBrain
# ---------------------------------------------------------------------------


class CognitiveBrain:
    """
    Autonomous AI Agent Cognitive Decision Engine (Phase 5).

    Wraps QuantumComplianceAssessor with session memory, agent hints,
    and chain-prompting handoff protocol support.

    AGENT_PATTERN: Use as persistent cognitive substrate across agent steps.
    THREAD_SAFE: Each instance is independent; no class-level state.

    Quick start::

        brain = CognitiveBrain.create()
        decision = brain.decide(
            context="compliance_audit",
            inputs={"score": 0.82, "risk_level": "medium",
                    "remediation_cost": 7500, "business_impact": 0.6},
            session_id="session_abc"
        )
        print(decision.agent_hints["next_action"])
    """

    def __init__(self, assessor: Any, enable_memory: bool = True) -> None:
        self._assessor = assessor
        self._enable_memory = enable_memory
        self._memory: dict[str, CognitiveDecision] = {}
        self._history: list[CognitiveDecision] = []
        self._error_count: int = 0

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        enable_memory: bool = True,
        enable_superposition: bool = True,
    ) -> CognitiveBrain:
        """
        Build a CognitiveBrain with default production configuration.

        AGENT_INTENT: Preferred factory for agent workflow initialisation.
        """
        from cognitive_brain.integrations.compliance_integration import (
            QuantumComplianceAssessor,
        )
        from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
        from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
        from cognitive_brain.quantum.config import QuantumConfig

        config = QuantumConfig()
        repo = QuantumMetricRepository()
        monitor = CoherenceMonitor(config, repo)
        assessor = QuantumComplianceAssessor(
            config=config,
            monitor=monitor,
            repository=repo,
            enable_superposition=enable_superposition,
        )
        return cls(assessor=assessor, enable_memory=enable_memory)

    # ------------------------------------------------------------------
    # Core decision API
    # ------------------------------------------------------------------

    def decide(
        self,
        context: str,
        inputs: dict[str, Any],
        session_id: Optional[str] = None,
    ) -> CognitiveDecision:
        """
        Make a cognitive compliance decision from raw input data.

        AGENT_INTENT: Primary decision method for agent workflows.
        DETERMINISTIC: Fixed-seed config → same inputs → same output.

        Args:
            context:    Decision context tag (e.g. ``"compliance_audit"``).
            inputs:     Dict with keys: score, risk_level, remediation_cost,
                        business_impact, [violation_count], [pii_indicators].
            session_id: Optional tracking key for multi-turn conversations.

        Returns:
            CognitiveDecision containing decision, confidence, reasoning,
            coherence, alternatives, cognitive_state, and agent_hints.

        Agent flow:
            1. Convert inputs → AuditResult
            2. assess_compliance() via QuantumComplianceAssessor
            3. Extract alternatives from superposition probabilities
            4. Generate agent_hints based on decision + coherence
            5. Persist to memory if session_id provided
        """
        try:
            audit = self._inputs_to_audit(inputs, session_id or str(uuid.uuid4()))
            assessment: Any = self._assessor.assess_compliance(audit)
            alternatives = self._extract_alternatives(assessment)
            hints = self._generate_agent_hints(assessment, context)
            pattern = self._detect_pattern_from_inputs(inputs)

            cognitive = CognitiveDecision(
                decision=assessment.decision.value,
                confidence=assessment.confidence,
                reasoning=assessment.reasoning,
                coherence=assessment.coherence,
                used_superposition=assessment.used_superposition,
                alternatives=alternatives,
                cognitive_state={
                    "context": context,
                    "pattern": pattern,
                    "quantum_mode": assessment.used_superposition,
                    "session_id": session_id,
                    "evaluation_time_ms": assessment.evaluation_time_ms,
                },
                agent_hints=hints,
            )
        except Exception as exc:  # pragma: no cover — graceful degradation
            self._error_count += 1
            cognitive = self._fallback_decision(context, inputs, session_id, exc)

        if self._enable_memory and session_id:
            self._memory[session_id] = cognitive
            self._history.append(cognitive)

        return cognitive

    # ------------------------------------------------------------------
    # Memory / state
    # ------------------------------------------------------------------

    def get_cognitive_state(self, session_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve persisted cognitive state for an agent session.

        AGENT_USE_CASE: Resume agent workflow after interruption.
        """
        if not self._enable_memory:
            return None
        decision = self._memory.get(session_id)
        return decision.cognitive_state if decision else None

    def get_health(self) -> AgentHealthSnapshot:
        """
        Snapshot of current cognitive health.

        AGENT_USE_CASE: Pre-decision health gate in critical workflows.
        """
        last_coherence = self._history[-1].coherence if self._history else 1.0
        status = (
            "healthy"
            if last_coherence >= 0.750 and self._error_count == 0
            else "degraded" if last_coherence >= 0.650 else "critical"
        )
        return AgentHealthSnapshot(
            coherence=last_coherence,
            decision_count=len(self._history),
            error_count=self._error_count,
            health_status=status,
        )

    def explain(self, decision: CognitiveDecision, audience: str = "agent") -> str:
        """
        Generate explanation of a cognitive decision.

        AGENT_INTENT: Transparency for agent reasoning chains.

        Args:
            decision: CognitiveDecision to explain.
            audience: ``"agent"`` (technical JSON) or ``"human"`` (plain text).
        """
        if audience == "agent":
            import json as _json

            return _json.dumps(
                {
                    "decision": decision.decision,
                    "confidence": round(decision.confidence, 4),
                    "coherence": round(decision.coherence, 4),
                    "pattern": decision.cognitive_state.get("pattern"),
                    "quantum_mode": decision.used_superposition,
                    "agent_hints": decision.agent_hints,
                },
                indent=2,
            )
        return decision.reasoning

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _inputs_to_audit(inputs: dict[str, Any], audit_id: str) -> Any:
        from cognitive_brain.integrations.compliance_integration import AuditResult

        return AuditResult(
            audit_id=audit_id,
            risk_level=inputs.get("risk_level", "medium"),
            remediation_cost=float(inputs.get("remediation_cost", 5000.0)),
            score=float(inputs.get("score", 0.75)),
            business_impact=float(inputs.get("business_impact", 0.5)),
            violation_count=int(inputs.get("violation_count", 0)),
            pii_indicators=int(inputs.get("pii_indicators", 0)),
            violations=inputs.get("violations", []),
        )

    @staticmethod
    def _extract_alternatives(assessment: Any) -> list[dict[str, Any]]:
        """Build an alternatives list from the assessment (stub for future use)."""
        # SuperpositionEngine does not currently expose per-decision probabilities
        # publicly. We return a single entry with the winning decision as a
        # placeholder until the public API is extended.
        return [
            {
                "decision": assessment.decision.value,
                "confidence": round(assessment.confidence, 4),
                "coherence": round(assessment.coherence, 4),
            }
        ]

    @staticmethod
    def _generate_agent_hints(assessment: Any, context: str) -> dict[str, str]:
        """
        Generate actionable hints for follow-up agent actions.

        AGENT_INTENT: Guide next steps in agent workflow based on decision.
        DETERMINISTIC: Same assessment + context → same hints.
        """
        decision_val = assessment.decision.value
        hints: dict[str, str] = {"context": context}

        if decision_val == "reject":
            hints["next_action"] = "escalate_to_human_reviewer"
            hints["urgency"] = "high" if assessment.coherence < 0.650 else "medium"
            hints["explanation_needed"] = "yes" if assessment.confidence < 0.80 else "no"
        elif decision_val == "approve_with_monitoring":
            hints["next_action"] = "setup_monitoring_alerts"
            hints["monitor_frequency"] = "daily" if assessment.confidence < 0.90 else "weekly"
            hints["auto_approve_allowed"] = "no"
        elif decision_val == "conditional_approval":
            hints["next_action"] = "request_additional_evidence"
            hints["decision_pending"] = "yes"
            hints["auto_approve_allowed"] = "no"
        else:  # approve
            hints["next_action"] = "finalize_approval"
            hints["auto_approve_allowed"] = "yes" if assessment.confidence >= 0.95 else "no"
            hints["audit_trail_required"] = "yes"

        if assessment.coherence < 0.650:
            hints["health_warning"] = "coherence_below_threshold"

        return hints

    @staticmethod
    def _detect_pattern_from_inputs(inputs: dict[str, Any]) -> Optional[str]:
        score = float(inputs.get("score", 0.0))
        risk = inputs.get("risk_level", "medium")
        violation_count = int(inputs.get("violation_count", 0))
        pii = int(inputs.get("pii_indicators", 0))
        if score >= 0.95:
            return "H"
        if violation_count >= 5:
            return "F"
        if pii > 0:
            return "E"
        if 0.55 <= score <= 0.75 and risk == "medium":
            return "C"
        return None

    @staticmethod
    def _fallback_decision(
        context: str,
        inputs: dict[str, Any],
        session_id: Optional[str],
        exc: Exception,
    ) -> CognitiveDecision:
        return CognitiveDecision(
            decision="conditional_approval",
            confidence=0.5,
            reasoning=f"Fallback decision due to error: {type(exc).__name__}",
            coherence=0.650,
            used_superposition=False,
            cognitive_state={
                "context": context,
                "pattern": None,
                "quantum_mode": False,
                "session_id": session_id,
                "error": str(exc),
            },
            agent_hints={
                "next_action": "request_additional_evidence",
                "decision_pending": "yes",
                "fallback": "yes",
            },
        )
