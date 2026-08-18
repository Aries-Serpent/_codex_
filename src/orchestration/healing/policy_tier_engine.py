"""Policy Tier Classification Engine — T0-T3 automatic action classification.

Implements automatic classification of actions into policy tiers:
- T0: Metadata-only changes (logging, config)
- T1: Low-risk operational (tests <5 lines, docs)
- T2: Code-level changes (security patches, APIs)
- T3: Governance changes (tier system, approval chains)
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PolicyTierError(Exception):
    """Raised when policy tier classification fails."""

    pass


@dataclass
class TierClassification:
    """Result of action classification to policy tier."""

    action_description: str
    tier: str
    justification: str
    required_gates: List[int] = field(default_factory=list)
    required_approvers: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    confidence: float = 1.0
    escalation_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "action_description": self.action_description,
            "tier": self.tier,
            "justification": self.justification,
            "required_gates": self.required_gates,
            "required_approvers": self.required_approvers,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "escalation_reason": self.escalation_reason,
        }


class PolicyTierEngine:
    """T0-T3 automatic classification engine."""

    TIER_DEFINITIONS = {
        "T0": {
            "name": "Metadata-only",
            "description": "Configuration and logging changes with no code impact",
            "examples": ["Update logging config", "Add README entry"],
            "required_gates": [1],
            "required_approvers": [],
        },
        "T1": {
            "name": "Low-risk operational",
            "description": "Small, low-risk changes (tests, docs, minor fixes)",
            "examples": ["Add 3-line test", "Update documentation"],
            "required_gates": [1, 2],
            "required_approvers": [],
        },
        "T2": {
            "name": "Code-level changes",
            "description": "Significant code changes (security patches, API changes)",
            "examples": ["Security patch", "API refactor"],
            "required_gates": [1, 2, 3, 4, 5, 6],
            "required_approvers": ["security-reviewer", "code-owner"],
        },
        "T3": {
            "name": "Governance changes",
            "description": "Changes to system governance (tier system, approval chains)",
            "examples": ["Modify tier system", "Change approval workflow"],
            "required_gates": [1, 2, 3, 4, 5, 6, 7, 8],
            "required_approvers": ["@mbaetiong", "stakeholder_1", "stakeholder_2"],
        },
    }

    # Keywords that indicate each tier
    TIER_0_KEYWORDS = {
        "logging",
        "config",
        "README",
        "documentation metadata",
        "comments only",
        "format",
        ".md",
        ".yaml config",
    }

    TIER_1_KEYWORDS = {
        "test",
        "unit test",
        "doc",
        "documentation",
        "example",
        "minor fix",
        "typo",
    }

    TIER_2_KEYWORDS = {
        "security",
        "patch",
        "API",
        "refactor",
        "algorithm",
        "data structure",
        "database",
        "performance",
        "vulnerability",
    }

    TIER_3_KEYWORDS = {
        "governance",
        "approval",
        "tier",
        "policy",
        "workflow",
        "authorization",
        "authentication",
        "access control",
    }

    # Risk assessment thresholds
    RISK_THRESHOLDS = {
        "T0": {"max_score": 10.0, "escalate_above": 10.0},
        "T1": {"max_score": 30.0, "escalate_above": 35.0},
        "T2": {"max_score": 60.0, "escalate_above": 65.0},
        "T3": {"max_score": 100.0, "escalate_above": 100.0},
    }

    @classmethod
    def _calculate_risk_score(
        cls, action_description: str, affected_modules: List[str]
    ) -> float:
        """Calculate risk score based on action and modules.

        Args:
            action_description: Description of the action
            affected_modules: List of affected module names

        Returns:
            Risk score (0-100)
        """
        score = 0.0

        # Check description keywords for risk indicators
        desc_lower = action_description.lower()

        if any(kw in desc_lower for kw in ["delete", "drop", "remove critical"]):
            score += 30.0
        if any(kw in desc_lower for kw in ["security", "vulnerability", "exploit"]):
            score += 25.0
        if any(kw in desc_lower for kw in ["breaking change", "deprecate"]):
            score += 20.0
        if any(kw in desc_lower for kw in ["refactor", "rewrite"]):
            score += 15.0

        # Add score based on number of affected modules
        score += len(affected_modules) * 3.0

        # Cap at 100
        return min(score, 100.0)

    @classmethod
    def classify_action(
        cls, action_description: str, affected_modules: Optional[List[str]] = None
    ) -> TierClassification:
        """Classify action to T0-T3 tier.

        Args:
            action_description: Description of the action
            affected_modules: List of affected module names (optional)

        Returns:
            TierClassification with tier, justification, and requirements

        Raises:
            PolicyTierError: If classification fails
        """
        if affected_modules is None:
            affected_modules = []

        try:
            desc_lower = action_description.lower()
            risk_score = cls._calculate_risk_score(action_description, affected_modules)

            # Initial tier determination based on keywords
            if any(kw in desc_lower for kw in cls.TIER_3_KEYWORDS):
                initial_tier = "T3"
            elif any(kw in desc_lower for kw in cls.TIER_2_KEYWORDS):
                initial_tier = "T2"
            elif any(kw in desc_lower for kw in cls.TIER_1_KEYWORDS):
                initial_tier = "T1"
            else:
                initial_tier = "T0"

            # Check for escalation
            tier_config = cls.TIER_DEFINITIONS[initial_tier]
            escalation_reason = None

            if risk_score > cls.RISK_THRESHOLDS[initial_tier]["escalate_above"]:
                # Escalate to next tier
                tier_order = ["T0", "T1", "T2", "T3"]
                current_idx = tier_order.index(initial_tier)
                if current_idx < len(tier_order) - 1:
                    escalation_reason = f"Risk score {risk_score} exceeds threshold"
                    final_tier = tier_order[current_idx + 1]
                    tier_config = cls.TIER_DEFINITIONS[final_tier]
                else:
                    final_tier = initial_tier
            else:
                final_tier = initial_tier

            # Calculate confidence (higher risk = lower confidence)
            confidence = max(0.5, 1.0 - (risk_score / 100.0 * 0.5))

            justification = (
                f"Classified as {final_tier} ({tier_config['name']}). "
                f"Risk score: {risk_score:.1f}. "
                f"Affected modules: {len(affected_modules)}."
            )

            if escalation_reason:
                justification += f" Escalated: {escalation_reason}"

            classification = TierClassification(
                action_description=action_description,
                tier=final_tier,
                justification=justification,
                required_gates=list(tier_config["required_gates"]),  # type: ignore[arg-type]
                required_approvers=list(tier_config["required_approvers"]),  # type: ignore[arg-type]
                risk_score=risk_score,
                confidence=confidence,
                escalation_reason=escalation_reason,
            )

            logger.info(
                f"Action classified as {final_tier}: {action_description} "
                f"(risk: {risk_score:.1f})"
            )

            return classification
        except Exception as e:
            raise PolicyTierError(f"Failed to classify action: {e}")

    @classmethod
    def get_tier_requirements(cls, tier: str) -> Dict[str, Any]:
        """Get requirements for a specific tier.

        Args:
            tier: Tier name (T0-T3)

        Returns:
            Dictionary with tier requirements

        Raises:
            PolicyTierError: If tier is invalid
        """
        if tier not in cls.TIER_DEFINITIONS:
            raise PolicyTierError(f"Invalid tier: {tier}")

        tier_def = cls.TIER_DEFINITIONS[tier]
        return {
            "tier": tier,
            "name": tier_def["name"],
            "description": tier_def["description"],
            "examples": tier_def["examples"],
            "required_gates": tier_def["required_gates"],
            "required_approvers": tier_def["required_approvers"],
            "gate_count": len(tier_def["required_gates"]),
            "approver_count": len(tier_def["required_approvers"]),
        }

    @classmethod
    def batch_classify(
        cls, actions: List[Dict[str, Any]]
    ) -> List[TierClassification]:
        """Classify multiple actions at once.

        Args:
            actions: List of action dicts with 'description' and optional 'affected_modules'

        Returns:
            List of TierClassification results
        """
        classifications = []
        for action in actions:
            classification = cls.classify_action(
                action.get("description", ""),
                action.get("affected_modules", []),
            )
            classifications.append(classification)
        return classifications
