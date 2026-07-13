"""
Phase 6: Cohort Routing

Routes decisions into risk cohorts for differential treatment in canary deployment.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CohortRisk(Enum):
    """Decision cohort risk level"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class CohortClassification:
    """Classification of a decision into a risk cohort"""

    decision_id: str
    cohort: CohortRisk
    risk_score: float  # 0.0 to 1.0
    reasoning: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CohortRoutes:
    """Result of cohort routing analysis"""

    routing_id: str
    total_decisions: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    low_risk_decisions: list[str]
    medium_risk_decisions: list[str]
    high_risk_decisions: list[str]
    classifications: dict[str, CohortClassification] = field(
        default_factory=dict
    )


class CohortRouter:
    """Routes decisions into risk cohorts for Phase 6 canary deployment"""

    def __init__(self):
        self._classifications: dict[str, CohortClassification] = {}
        self._routing_history: list[CohortRoutes] = []

    def classify_decision(
        self,
        decision_id: str,
        risk_indicators: dict[str, float],
        domain: str = "general",
        metadata: dict[str, Any] | None = None,
    ) -> CohortClassification:
        """Classify a decision into a risk cohort"""

        risk_score = self._calculate_risk_score(risk_indicators)

        if risk_score < 0.33:
            cohort = CohortRisk.LOW
            reasoning = "Low risk indicators, suitable for early hybrid evaluation"
        elif risk_score < 0.67:
            cohort = CohortRisk.MEDIUM
            reasoning = "Medium risk - hybrid deployment after staged validation"
        else:
            cohort = CohortRisk.HIGH
            reasoning = "High risk - keep with classical solver until proven safe"

        classification = CohortClassification(
            decision_id=decision_id,
            cohort=cohort,
            risk_score=risk_score,
            reasoning=reasoning,
            metadata={
                "domain": domain,
                "risk_indicators": risk_indicators,
                **(metadata or {}),
            },
        )

        self._classifications[decision_id] = classification
        logger.debug(
            f"Classified {decision_id}: {cohort.value} cohort "
            f"(risk_score={risk_score:.3f})"
        )

        return classification

    def generate_routes(self) -> CohortRoutes:
        """Generate cohort routes from classified decisions"""

        routing_id = f"routes_{len(self._routing_history)}"
        
        low_risk = [
            d for d, c in self._classifications.items()
            if c.cohort == CohortRisk.LOW
        ]
        medium_risk = [
            d for d, c in self._classifications.items()
            if c.cohort == CohortRisk.MEDIUM
        ]
        high_risk = [
            d for d, c in self._classifications.items()
            if c.cohort == CohortRisk.HIGH
        ]

        routes = CohortRoutes(
            routing_id=routing_id,
            total_decisions=len(self._classifications),
            low_risk_count=len(low_risk),
            medium_risk_count=len(medium_risk),
            high_risk_count=len(high_risk),
            low_risk_decisions=low_risk,
            medium_risk_decisions=medium_risk,
            high_risk_decisions=high_risk,
            classifications=self._classifications.copy(),
        )

        self._routing_history.append(routes)
        logger.info(
            f"Generated cohort routes: {len(low_risk)} low, "
            f"{len(medium_risk)} medium, {len(high_risk)} high risk"
        )

        return routes

    def _calculate_risk_score(self, indicators: dict[str, float]) -> float:
        """Calculate aggregate risk score from indicators"""

        if not indicators:
            return 0.5  # Default to medium risk if no indicators

        # Weighted average of indicators
        weights = {
            "financial_impact": 0.3,
            "user_impact": 0.25,
            "operational_criticality": 0.25,
            "reversibility": -0.2,  # Negative = lower risk
        }

        total_weight = 0.0
        weighted_sum = 0.0

        for key, value in indicators.items():
            weight = weights.get(key, 1.0)
            total_weight += abs(weight)
            weighted_sum += value * weight

        return min(1.0, max(0.0, weighted_sum / total_weight)) if total_weight > 0 else 0.5

    def get_routing_history(self) -> list[CohortRoutes]:
        """Get history of routing operations"""
        return self._routing_history.copy()

    def get_latest_routes(self) -> CohortRoutes | None:
        """Get most recent routing result"""
        return self._routing_history[-1] if self._routing_history else None
