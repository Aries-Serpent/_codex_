"""DECIDE Phase: Autonomous decision-making with confidence scoring.

This module makes autonomous decisions using:
- Observable state + oriented context
- Semantic router for action candidates
- Confidence scoring and authority validation
- Guardrail checks
- Audit trail logging

Output: Decision directive with confidence scores
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions the OODA loop can make."""

    DEPLOY_PATTERN = "deploy_pattern"
    RUN_TEST = "run_test"
    HEAL_FAILURE = "heal_failure"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    SCALE_RESOURCE = "scale_resource"
    ALERT_HUMAN = "alert_human"


@dataclass
class Action:
    """A possible action to take."""

    action_id: str
    action_type: DecisionType
    description: str
    target: str  # What to act on
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class RankedAction:
    """An action ranked by suitability."""

    action: Action
    confidence_score: float  # 0-1
    success_probability: float  # 0-1 historical
    risk_level: str  # low, medium, high, critical
    estimated_impact: float  # 0-1
    required_resources: list[str] = field(default_factory=list)


@dataclass
class GuardrailCheck:
    """A guardrail validation result."""

    check_name: str
    passed: bool
    description: str
    severity: str  # info, warning, error, critical


@dataclass
class DecisionDirective:
    """A decision to execute."""

    decision_id: str
    timestamp: datetime
    action: Action
    candidates: list[RankedAction]
    confidence: float  # Overall confidence (0-1)
    assigned_agents: list[str]  # Agent IDs to execute
    parallel_execution: bool
    guardrail_checks: list[GuardrailCheck]
    audit_id: str
    decision_rationale: str
    requires_approval: bool  # True if confidence < threshold
    approved: bool = False
    approver: Optional[str] = None


class ConfidenceScorer:
    """Scores confidence of decisions."""

    def __init__(self) -> None:
        self.min_confidence_threshold = 0.70
        self.auto_approve_threshold = 0.85

    def score_decision(
        self,
        action: Action,
        historical_success_rate: float,
        pattern_match_strength: float,
        risk_level: str,
        agent_availability: float,
        resource_constraints: float,
    ) -> float:
        """Score confidence for a decision."""
        try:
            # Base confidence from historical success
            base_confidence = 0.5

            # Add historical success component
            base_confidence += historical_success_rate * 0.2

            # Add pattern match strength
            base_confidence += pattern_match_strength * 0.15

            # Add agent availability component
            base_confidence += agent_availability * 0.1

            # Adjust for risk
            risk_adjustment = {
                "low": 0.0,
                "medium": -0.05,
                "high": -0.15,
                "critical": -0.3,
            }.get(risk_level, -0.1)
            base_confidence += risk_adjustment

            # Adjust for resource constraints
            base_confidence -= (1 - resource_constraints) * 0.1

            # Clamp to [0, 1]
            return max(0.0, min(1.0, base_confidence))
        except Exception as e:
            logger.error(f"Failed to score decision: {e}")
            return 0.5


class GuardrailValidator:
    """Validates decisions against guardrails."""

    def __init__(self, guardrail_path: Path = Path(".codex/guardrails.md")):
        self.guardrail_path = guardrail_path

    def validate_decision(
        self,
        decision: Action,
        confidence: float,
        agent_availability: float,
    ) -> list[GuardrailCheck]:
        """Validate decision against guardrails."""
        checks = []

        # Check 1: No destructive operations
        destructive_keywords = ["rm ", "drop ", "delete", "truncate", "flush"]
        if any(kw in decision.description.lower() for kw in destructive_keywords):
            checks.append(
                GuardrailCheck(
                    check_name="destructive_operation_check",
                    passed=False,
                    description="Destructive operations require explicit approval",
                    severity="critical",
                )
            )
        else:
            checks.append(
                GuardrailCheck(
                    check_name="destructive_operation_check",
                    passed=True,
                    description="No destructive operations detected",
                    severity="info",
                )
            )

        # Check 2: Sufficient confidence
        if confidence < 0.70:
            checks.append(
                GuardrailCheck(
                    check_name="confidence_threshold_check",
                    passed=False,
                    description=f"Confidence {confidence:.2f} below threshold 0.70",
                    severity="warning",
                )
            )
        else:
            checks.append(
                GuardrailCheck(
                    check_name="confidence_threshold_check",
                    passed=True,
                    description=f"Confidence {confidence:.2f} meets threshold",
                    severity="info",
                )
            )

        # Check 3: Agent availability
        if agent_availability < 0.5:
            checks.append(
                GuardrailCheck(
                    check_name="agent_availability_check",
                    passed=False,
                    description="Insufficient agent availability",
                    severity="warning",
                )
            )
        else:
            checks.append(
                GuardrailCheck(
                    check_name="agent_availability_check",
                    passed=True,
                    description="Sufficient agents available",
                    severity="info",
                )
            )

        # Check 4: No privileged operations (without D-mode)
        privileged_keywords = ["sudo ", "deploy to production", "release"]
        if any(kw in decision.description.lower() for kw in privileged_keywords):
            checks.append(
                GuardrailCheck(
                    check_name="privilege_level_check",
                    passed=False,
                    description="Privileged operations require D-mode authority",
                    severity="error",
                )
            )
        else:
            checks.append(
                GuardrailCheck(
                    check_name="privilege_level_check",
                    passed=True,
                    description="Operation within standard privilege level",
                    severity="info",
                )
            )

        return checks


class SemanticActionSelector:
    """Selects actions using semantic similarity."""

    def select_candidates(
        self,
        observable_state: Any,
        oriented_context: Any,
        candidate_count: int = 5,
    ) -> list[Action]:
        """Select candidate actions based on state and context."""
        try:
            # In production, use semantic similarity to rank actions
            # For now, return representative actions

            actions = [
                Action(
                    action_id="act_001",
                    action_type=DecisionType.HEAL_FAILURE,
                    description="Deploy CI healing pattern RP-006",
                    target="CI workflow",
                    parameters={"pattern_id": "RP-006", "auto_deploy": True},
                ),
                Action(
                    action_id="act_002",
                    action_type=DecisionType.RUN_TEST,
                    description="Run high-priority test suite",
                    target="test_suite",
                    parameters={"priority": 1, "parallel": True},
                ),
                Action(
                    action_id="act_003",
                    action_type=DecisionType.OPTIMIZE_PERFORMANCE,
                    description="Optimize cache hit rate",
                    target="cache_system",
                    parameters={"strategy": "adaptive", "ttl_seconds": 3600},
                ),
            ]

            return actions[:candidate_count]
        except Exception as e:
            logger.error(f"Failed to select action candidates: {e}")
            return []


class OODADecider:
    """Main decider: orchestrates autonomous decision-making."""

    def __init__(self) -> None:
        self.confidence_scorer = ConfidenceScorer()
        self.guardrail_validator = GuardrailValidator()
        self.action_selector = SemanticActionSelector()
        self.audit_trail: list[DecisionDirective] = []

    def decide(
        self,
        observable_state: Any,
        oriented_context: Any,
        require_approval_for_confidence: float = 0.80,
        d_mode_authority: bool = False,
    ) -> DecisionDirective:
        """Make autonomous decision."""
        try:
            decision_id = str(uuid.uuid4())[:8]
            audit_id = str(uuid.uuid4())

            # Phase 3 stage 1: Select action candidates
            candidates = self.action_selector.select_candidates(
                observable_state,
                oriented_context,
                candidate_count=5,
            )

            if not candidates:
                logger.warning("No action candidates found")
                return self._create_null_decision(decision_id, audit_id)

            # Phase 3 stage 2: Score each candidate
            ranked_candidates = []
            for action in candidates:
                # In production, use sophisticated scoring
                base_confidence = 0.7
                if hasattr(oriented_context, "confidence_baseline"):
                    base_confidence = oriented_context.confidence_baseline

                # Score based on agent suitability
                agent_suitability = 0.85
                if hasattr(oriented_context, "agent_candidates"):
                    agent_suitability = (
                        max([a.suitability_score for a in oriented_context.agent_candidates])
                        if oriented_context.agent_candidates
                        else 0.0
                    )

                confidence = self.confidence_scorer.score_decision(
                    action=action,
                    historical_success_rate=0.85,
                    pattern_match_strength=base_confidence,
                    risk_level="low",
                    agent_availability=agent_suitability,
                    resource_constraints=0.9,
                )

                ranked_candidates.append(
                    RankedAction(
                        action=action,
                        confidence_score=confidence,
                        success_probability=0.85,
                        risk_level="low",
                        estimated_impact=0.75,
                        required_resources=["ci_auto_healer"],
                    )
                )

            # Sort by confidence
            ranked_candidates.sort(key=lambda a: a.confidence_score, reverse=True)

            # Phase 3 stage 3: Select best action
            best_candidate = ranked_candidates[0]
            best_action = best_candidate.action
            best_confidence = best_candidate.confidence_score

            # Phase 3 stage 4: Validate against guardrails
            guardrail_checks = self.guardrail_validator.validate_decision(
                best_action,
                best_confidence,
                agent_suitability,
            )

            # All guardrails must pass
            guardrails_passed = all(check.passed for check in guardrail_checks)

            # Phase 3 stage 5: Determine if approval required
            requires_approval = False
            if not guardrails_passed:
                requires_approval = True
            elif best_confidence < require_approval_for_confidence:
                requires_approval = True
            elif best_candidate.risk_level == "critical":
                requires_approval = True

            # Get suitable agents
            assigned_agents = ["ci_auto_healer"]
            if hasattr(oriented_context, "agent_candidates"):
                assigned_agents = [a.agent_id for a in oriented_context.agent_candidates[:3]]

            # Create decision directive
            decision = DecisionDirective(
                decision_id=decision_id,
                timestamp=datetime.now(),
                action=best_action,
                candidates=ranked_candidates,
                confidence=best_confidence,
                assigned_agents=assigned_agents,
                parallel_execution=True,
                guardrail_checks=guardrail_checks,
                audit_id=audit_id,
                decision_rationale=(
                    f"Action: {best_action.description}; "
                    f"Confidence: {best_confidence:.2%}; "
                    f"Candidates: {len(ranked_candidates)}; "
                    f"Guardrails: {'✓' if guardrails_passed else '✗'}"
                ),
                requires_approval=requires_approval,
                approved=(
                    (best_confidence >= 0.95 and d_mode_authority) if guardrails_passed else False
                ),
            )

            # Log to audit trail
            self.audit_trail.append(decision)

            return decision

        except Exception as e:
            logger.error(f"Decision making failed: {e}")
            decision_id = str(uuid.uuid4())[:8]
            audit_id = str(uuid.uuid4())
            return self._create_null_decision(decision_id, audit_id)

    def _create_null_decision(self, decision_id: str, audit_id: str) -> DecisionDirective:
        """Create a null decision (no action)."""
        return DecisionDirective(
            decision_id=decision_id,
            timestamp=datetime.now(),
            action=Action(
                action_id="null",
                action_type=DecisionType.ALERT_HUMAN,
                description="No suitable action found",
                target="human_review",
            ),
            candidates=[],
            confidence=0.0,
            assigned_agents=[],
            parallel_execution=False,
            guardrail_checks=[],
            audit_id=audit_id,
            decision_rationale="Decision making failed; requires human review",
            requires_approval=True,
        )

    def get_audit_trail(self, limit: int = 100) -> list[DecisionDirective]:
        """Get recent decisions from audit trail."""
        return self.audit_trail[-limit:]
