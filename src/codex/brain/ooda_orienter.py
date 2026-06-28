"""ORIENT Phase: Inject context from memory, patterns, and precedents.

This module enriches observable state with:
- Relevant patterns from long-term memory (LTM)
- Decision precedents (similar past decisions & outcomes)
- Agent capabilities and success rates
- Risk assessment
- Opportunity detection

Output: Rich context document for decision-maker
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """A reusable pattern from long-term memory."""

    pattern_id: str
    name: str
    category: str  # CI_HEALING, ML_PATTERN_FEEDING, etc.
    description: str
    applicability_score: float  # 0-1, how relevant to current state
    success_rate: float
    usage_count: int
    created_at: datetime
    last_used: Optional[datetime]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PastDecision:
    """A previous decision and its outcome."""

    decision_id: str
    timestamp: datetime
    action: str
    context_similarity: float  # 0-1, how similar to current state
    success: bool
    outcome_quality: float  # 0-1
    impact_score: float
    lessons_learned: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentCapability:
    """Capability of a single agent."""

    agent_id: str
    agent_name: str
    capability: str
    success_rate: float
    avg_latency_ms: float
    cost_estimate: float
    suitability_score: float  # 0-1, for current decision
    availability: str  # available, busy, unavailable


@dataclass
class RiskAssessment:
    """Assessment of risks in current state."""

    overall_risk_level: str  # critical, high, medium, low
    identified_risks: list[str]
    mitigation_strategies: list[str]
    probability: float  # 0-1
    potential_impact: str


@dataclass
class Opportunity:
    """A potential opportunity for action."""

    opportunity_id: str
    description: str
    roi_estimate: float
    difficulty: str  # easy, medium, hard
    time_to_value_hours: float
    required_agents: list[str]
    priority: int  # 1=critical, 5=low


@dataclass
class Orientation:
    """Rich context for decision-maker."""

    timestamp: datetime
    relevant_patterns: list[Pattern]
    decision_precedents: list[PastDecision]
    agent_candidates: list[AgentCapability]
    risk_assessment: RiskAssessment
    opportunities: list[Opportunity]
    context_summary: str
    confidence_baseline: float  # How confident we are in the context


class PatternRetriever:
    """Retrieves relevant patterns from LTM."""

    def __init__(self, pattern_db_path: Path = Path(".codex/patterns")):
        self.pattern_db_path = pattern_db_path

    def retrieve_relevant_patterns(
        self,
        observable_state: Any,
        top_k: int = 10,
        threshold: float = 0.75,
    ) -> list[Pattern]:
        """Retrieve top-k patterns relevant to current state."""
        try:
            # In production, use semantic similarity to rank patterns
            # For now, return representative patterns

            patterns = [
                Pattern(
                    pattern_id="RP-001",
                    name="Import Error Recovery",
                    category="CI_HEALING",
                    description="Resolves missing dependency imports in CI",
                    applicability_score=0.92,
                    success_rate=0.96,
                    usage_count=342,
                    created_at=datetime.now(),
                    last_used=datetime.now(),
                ),
                Pattern(
                    pattern_id="RP-002",
                    name="Test Timeout Mitigation",
                    category="CI_HEALING",
                    description="Handles slow test timeouts gracefully",
                    applicability_score=0.85,
                    success_rate=0.91,
                    usage_count=218,
                    created_at=datetime.now(),
                    last_used=datetime.now(),
                ),
            ]

            # Filter by threshold and return top-k
            filtered = [p for p in patterns if p.applicability_score >= threshold]
            return sorted(
                filtered,
                key=lambda p: p.applicability_score,
                reverse=True,
            )[:top_k]
        except Exception as e:
            logger.error(f"Failed to retrieve patterns: {e}")
            return []


class DecisionPrecedentRetriever:
    """Retrieves relevant past decisions."""

    def __init__(self, audit_trail_path: Path = Path(".codex/decision_history.json")):
        self.audit_trail_path = audit_trail_path

    def retrieve_similar_decisions(
        self,
        current_state: Any,
        top_k: int = 5,
        similarity_threshold: float = 0.8,
    ) -> list[PastDecision]:
        """Retrieve similar past decisions and outcomes."""
        try:
            # In production, use semantic similarity to find past decisions
            # For now, return representative decisions

            decisions = [
                PastDecision(
                    decision_id="dec_001",
                    timestamp=datetime.now(),
                    action="Deploy RP-006 pattern",
                    context_similarity=0.91,
                    success=True,
                    outcome_quality=0.94,
                    impact_score=0.85,
                    lessons_learned="Pattern deployment reduces CI failure rate by 15%",
                ),
                PastDecision(
                    decision_id="dec_002",
                    timestamp=datetime.now(),
                    action="Enable parallel test execution",
                    context_similarity=0.87,
                    success=True,
                    outcome_quality=0.88,
                    impact_score=0.72,
                    lessons_learned="Parallel execution cuts CI time by 40%",
                ),
            ]

            # Filter by similarity and return top-k
            filtered = [d for d in decisions if d.context_similarity >= similarity_threshold]
            return sorted(
                filtered,
                key=lambda d: d.context_similarity,
                reverse=True,
            )[:top_k]
        except Exception as e:
            logger.error(f"Failed to retrieve decision precedents: {e}")
            return []


class AgentCapabilityAnalyzer:
    """Analyzes agent capabilities for current decision."""

    def __init__(self, agent_registry_path: Path = Path(".codex/agent_registry.json")):
        self.agent_registry_path = agent_registry_path

    def get_suitable_agents(
        self,
        observable_state: Any,
        decision_type: str = "general",
    ) -> list[AgentCapability]:
        """Get agents suitable for the current state."""
        try:
            # In production, use semantic matching with agent capabilities
            # For now, return representative agents

            agents = [
                AgentCapability(
                    agent_id="ci_auto_healer",
                    agent_name="CI Auto-Healer",
                    capability="CI/CD pattern healing",
                    success_rate=0.94,
                    avg_latency_ms=127.3,
                    cost_estimate=0.5,
                    suitability_score=0.96,
                    availability="available",
                ),
                AgentCapability(
                    agent_id="semantic_router",
                    agent_name="Semantic Router",
                    capability="Agent routing",
                    success_rate=0.98,
                    avg_latency_ms=23.1,
                    cost_estimate=0.2,
                    suitability_score=0.92,
                    availability="available",
                ),
                AgentCapability(
                    agent_id="test_pattern_guardian",
                    agent_name="Test Pattern Guardian",
                    capability="Test pattern enforcement",
                    success_rate=0.91,
                    avg_latency_ms=45.8,
                    cost_estimate=0.4,
                    suitability_score=0.88,
                    availability="available",
                ),
            ]

            # Sort by suitability
            return sorted(agents, key=lambda a: a.suitability_score, reverse=True)
        except Exception as e:
            logger.error(f"Failed to analyze agent capabilities: {e}")
            return []


class RiskAssessor:
    """Assesses risks in current state."""

    def assess_risks(self, observable_state: Any) -> RiskAssessment:
        """Assess current risks and opportunities."""
        try:
            # In production, use sophisticated risk models
            # For now, return representative assessment

            identified_risks = []
            mitigation_strategies = []

            # Check environment metrics
            if hasattr(observable_state, "environment"):
                env = observable_state.environment
                if env.cpu_percent > 80:
                    identified_risks.append("High CPU usage")
                    mitigation_strategies.append("Scale up infrastructure")
                if env.memory_percent > 85:
                    identified_risks.append("Memory pressure")
                    mitigation_strategies.append("Optimize agent memory usage")

            # Check agent ecosystem
            if hasattr(observable_state, "agents"):
                agents = observable_state.agents
                if agents.failing_agents > 0:
                    identified_risks.append(f"{agents.failing_agents} agents failing")
                    mitigation_strategies.append("Investigate and restart agents")

            overall_risk = "low"
            if identified_risks:
                overall_risk = "high" if len(identified_risks) > 2 else "medium"

            return RiskAssessment(
                overall_risk_level=overall_risk,
                identified_risks=identified_risks,
                mitigation_strategies=mitigation_strategies,
                probability=0.3,
                potential_impact="Moderate CI delay",
            )
        except Exception as e:
            logger.error(f"Failed to assess risks: {e}")
            return RiskAssessment(
                overall_risk_level="unknown",
                identified_risks=[],
                mitigation_strategies=[],
                probability=0.0,
                potential_impact="Unknown",
            )


class OpportunityDetector:
    """Detects opportunities for improvement."""

    def detect_opportunities(
        self,
        observable_state: Any,
        decision_precedents: list[PastDecision],
    ) -> list[Opportunity]:
        """Detect improvement opportunities."""
        try:
            opportunities = []

            # Quick wins: high-ROI, low-effort improvements
            if hasattr(observable_state, "repository"):
                repo = observable_state.repository
                if repo.test_failures > 0:
                    opportunities.append(
                        Opportunity(
                            opportunity_id="opp_001",
                            description="Fix failing tests",
                            roi_estimate=0.9,
                            difficulty="medium",
                            time_to_value_hours=2,
                            required_agents=["test_pattern_guardian", "ci_auto_healer"],
                            priority=1,
                        )
                    )

            # High-impact, medium-effort improvements
            if hasattr(observable_state, "agents"):
                agents = observable_state.agents
                if agents.avg_latency_ms > 100:
                    opportunities.append(
                        Opportunity(
                            opportunity_id="opp_002",
                            description="Optimize agent latency",
                            roi_estimate=0.7,
                            difficulty="hard",
                            time_to_value_hours=8,
                            required_agents=["performance_monitor_agent"],
                            priority=2,
                        )
                    )

            return sorted(opportunities, key=lambda o: o.roi_estimate, reverse=True)
        except Exception as e:
            logger.error(f"Failed to detect opportunities: {e}")
            return []


class OODAOrienter:
    """Main orienter: orchestrates all context injection."""

    def __init__(self) -> None:
        self.pattern_retriever = PatternRetriever()
        self.precedent_retriever = DecisionPrecedentRetriever()
        self.capability_analyzer = AgentCapabilityAnalyzer()
        self.risk_assessor = RiskAssessor()
        self.opportunity_detector = OpportunityDetector()

    def orient(self, observable_state: Any) -> Orientation:
        """Inject rich context into observable state."""
        try:
            # Phase 2 stage 1: Retrieve patterns
            relevant_patterns = self.pattern_retriever.retrieve_relevant_patterns(
                observable_state,
                top_k=10,
            )

            # Phase 2 stage 2: Retrieve decision precedents
            decision_precedents = self.precedent_retriever.retrieve_similar_decisions(
                observable_state,
                top_k=5,
            )

            # Phase 2 stage 3: Get suitable agents
            agent_candidates = self.capability_analyzer.get_suitable_agents(
                observable_state,
            )

            # Phase 2 stage 4: Assess risks
            risk_assessment = self.risk_assessor.assess_risks(observable_state)

            # Phase 2 stage 5: Detect opportunities
            opportunities = self.opportunity_detector.detect_opportunities(
                observable_state,
                decision_precedents,
            )

            # Generate context summary
            pattern_summary = f"{len(relevant_patterns)} relevant patterns"
            precedent_summary = f"{len(decision_precedents)} similar decisions"
            agent_summary = f"{len(agent_candidates)} suitable agents"

            context_summary = (
                f"{pattern_summary}; {precedent_summary}; {agent_summary}; "
                f"Risk: {risk_assessment.overall_risk_level}; "
                f"Opportunities: {len(opportunities)}"
            )

            # Calculate confidence baseline
            # Higher confidence if we have relevant patterns and good precedents
            pattern_confidence = min(0.3, len(relevant_patterns) * 0.05)
            precedent_confidence = min(0.3, len(decision_precedents) * 0.1)
            agent_confidence = min(0.2, len(agent_candidates) * 0.05)
            risk_adjustment = 0.0 if risk_assessment.overall_risk_level == "low" else -0.1

            confidence_baseline = min(
                1.0,
                max(
                    0.0,
                    0.2
                    + pattern_confidence
                    + precedent_confidence
                    + agent_confidence
                    + risk_adjustment,
                ),
            )

            return Orientation(
                timestamp=datetime.now(),
                relevant_patterns=relevant_patterns,
                decision_precedents=decision_precedents,
                agent_candidates=agent_candidates,
                risk_assessment=risk_assessment,
                opportunities=opportunities,
                context_summary=context_summary,
                confidence_baseline=confidence_baseline,
            )
        except Exception as e:
            logger.error(f"Orientation failed: {e}")
            return Orientation(
                timestamp=datetime.now(),
                relevant_patterns=[],
                decision_precedents=[],
                agent_candidates=[],
                risk_assessment=RiskAssessment(
                    overall_risk_level="unknown",
                    identified_risks=[],
                    mitigation_strategies=[],
                    probability=0.0,
                    potential_impact="Unknown",
                ),
                opportunities=[],
                context_summary="Failed to orient",
                confidence_baseline=0.0,
            )
