"""
Dependency Evaluator Module - DECIDE Phase

#AFTERMATH_PATTERN_IDENTIFIED: dependency_upgrade_evaluation
Implements compatibility analysis and breaking change risk assessment.
"""

import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

# Add core to path for CognitiveBrain access (acceptable for agent isolation)
# Alternative: Use proper packaging with __init__.py exports
_core_path = str(Path(__file__).parent.parent.parent / "core")
if _core_path not in sys.path:
    sys.path.insert(0, _core_path)
from cognitive_brain import CognitiveBrain  # noqa: E402


class BreakingChangeRisk(Enum):
    """Risk levels for breaking changes."""
    CRITICAL = "critical"  # Major version bump with known breaking changes
    HIGH = "high"          # Major version bump, unclear breaking changes
    MEDIUM = "medium"      # Minor version bump with deprecations
    LOW = "low"            # Patch version or minor without deprecations
    NONE = "none"          # No breaking changes expected


class UpgradePriority(Enum):
    """Priority levels for upgrades."""
    P0 = "p0"  # Security critical - immediate
    P1 = "p1"  # High priority - within 1 week
    P2 = "p2"  # Medium priority - within 1 month
    P3 = "p3"  # Low priority - opportunistic


@dataclass
class UpgradeEvaluation:
    """Evaluation result for a dependency upgrade."""
    package_name: str
    current_version: str
    target_version: str
    breaking_change_risk: BreakingChangeRisk
    priority: UpgradePriority
    compatibility_score: float  # 0.0-1.0
    risk_score: float           # 0.0-1.0
    auto_upgradeable: bool
    requires_testing: bool
    estimated_effort: str
    breaking_changes: List[str]
    migration_steps: List[str]
    rollback_plan: str
    metadata: Dict[str, Any]


class DependencyEvaluator:
    """
    Dependency Evaluator - DECIDE Phase

    #AFTERMATH_PATTERN_IDENTIFIED: upgrade_risk_assessment

    Evaluates dependency updates:
    - Compatibility analysis
    - Breaking change detection
    - Risk assessment
    - Priority calculation
    - Auto-upgrade feasibility
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.brain = CognitiveBrain(Path(".codex/brain.db"))
        self.evaluations: List[UpgradeEvaluation] = []

    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        DECIDE: Evaluate updates and determine upgrade strategy.

        #AFTERMATH_PATTERN_IDENTIFIED: upgrade_decision_making

        Args:
            context: Context from PERCEIVE phase

        Returns:
            Decision with evaluations and priorities
        """
        updates = context.get("available_updates", [])

        # Evaluate each update
        for update in updates:
            evaluation = self._evaluate_update(update, context)
            self.evaluations.append(evaluation)

        # Prioritize by risk and urgency
        prioritized = self._prioritize_updates(self.evaluations)

        # Group by upgrade strategy
        auto_upgrades = [e for e in self.evaluations if e.auto_upgradeable]
        manual_upgrades = [e for e in self.evaluations if not e.auto_upgradeable]

        return {
            "evaluations": self.evaluations,
            "prioritized": prioritized,
            "auto_upgrades": auto_upgrades,
            "manual_upgrades": manual_upgrades,
            "security_critical": [e for e in self.evaluations if e.priority == UpgradePriority.P0],
            "total_evaluated": len(self.evaluations),
            "recommendations": self._generate_recommendations(prioritized)
        }

        #AFTERMATH_METRIC: total_evaluations = len(self.evaluations)
        #AFTERMATH_METRIC: auto_upgradeable = len(auto_upgrades)
        #AFTERMATH_METRIC: security_critical = len(decision["security_critical"])


    def _evaluate_update(self, update: Any, context: Dict[str, Any]) -> UpgradeEvaluation:
        """
        Evaluate individual dependency update.

        #AFTERMATH_PATTERN_IDENTIFIED: single_dependency_evaluation
        """
        # Assess breaking change risk
        breaking_risk = self._assess_breaking_change_risk(update, context)

        # Calculate compatibility score
        compatibility = self._calculate_compatibility(update, context)

        # Calculate risk score
        risk = self._calculate_risk_score(update, breaking_risk, compatibility)

        # Determine priority
        priority = self._determine_priority(update, breaking_risk, risk)

        # Check if auto-upgradeable
        auto_upgradeable = self._is_auto_upgradeable(update, breaking_risk, compatibility)

        # Identify breaking changes
        breaking_changes = self._identify_breaking_changes(update, context)

        # Generate migration steps
        migration_steps = self._generate_migration_steps(update, breaking_changes)

        # Create rollback plan
        rollback_plan = self._create_rollback_plan(update)

        return UpgradeEvaluation(
            package_name=update.package_name,
            current_version=update.current_version,
            target_version=update.latest_version,
            breaking_change_risk=breaking_risk,
            priority=priority,
            compatibility_score=compatibility,
            risk_score=risk,
            auto_upgradeable=auto_upgradeable,
            requires_testing=breaking_risk != BreakingChangeRisk.NONE,
            estimated_effort=self._estimate_effort(breaking_risk, breaking_changes),
            breaking_changes=breaking_changes,
            migration_steps=migration_steps,
            rollback_plan=rollback_plan,
            metadata={"original_update": update}
        )

    def _assess_breaking_change_risk(self, update: Any,
                                     context: Dict[str, Any]) -> BreakingChangeRisk:
        """
        Assess risk of breaking changes.

        #AFTERMATH_PATTERN_IDENTIFIED: breaking_change_detection
        """
        from .monitor import UpdateType

        # Security updates = prioritize despite risk
        if update.update_type == UpdateType.SECURITY:
            return BreakingChangeRisk.MEDIUM  # Lower risk perception for security

        # Major version bump
        if update.update_type == UpdateType.MAJOR:
            changelog_data = context.get("changelog_analysis", {})
            if update.package_name in changelog_data:
                if changelog_data[update.package_name].get("has_breaking_changes"):
                    return BreakingChangeRisk.CRITICAL
            return BreakingChangeRisk.HIGH

        # Minor version bump
        if update.update_type == UpdateType.MINOR:
            return BreakingChangeRisk.LOW

        # Patch version
        return BreakingChangeRisk.NONE

    def _calculate_compatibility(self, update: Any, context: Dict[str, Any]) -> float:
        """
        Calculate compatibility score (0.0-1.0).

        #AFTERMATH_PATTERN_IDENTIFIED: compatibility_scoring
        """
        score = 1.0

        # Reduce score for major updates
        from .monitor import UpdateType
        if update.update_type == UpdateType.MAJOR:
            score *= 0.5
        elif update.update_type == UpdateType.MINOR:
            score *= 0.8

        # Check package health
        health = context.get("package_health", {}).get(update.package_name, {})
        if not health.get("is_maintained", True):
            score *= 0.7

        # Check historical success
        historical = self._query_historical_success(update.package_name)
        score *= historical

        return max(0.0, min(1.0, score))

    def _calculate_risk_score(self, update: Any, breaking_risk: BreakingChangeRisk,
                             compatibility: float) -> float:
        """
        Calculate overall risk score (0.0-1.0).

        #AFTERMATH_PATTERN_IDENTIFIED: risk_calculation
        """
        risk_map = {
            BreakingChangeRisk.CRITICAL: 0.9,
            BreakingChangeRisk.HIGH: 0.7,
            BreakingChangeRisk.MEDIUM: 0.5,
            BreakingChangeRisk.LOW: 0.3,
            BreakingChangeRisk.NONE: 0.1
        }

        base_risk = risk_map.get(breaking_risk, 0.5)
        compatibility_factor = 1.0 - compatibility

        # Security updates reduce perceived risk
        if update.has_vulnerability:
            base_risk *= 0.7

        return (base_risk * 0.7) + (compatibility_factor * 0.3)

    def _determine_priority(self, update: Any, breaking_risk: BreakingChangeRisk,
                           risk: float) -> UpgradePriority:
        """Determine upgrade priority."""
        # Security vulnerabilities = immediate
        if update.has_vulnerability:
            return UpgradePriority.P0

        # Critical breaking changes = lower priority
        if breaking_risk == BreakingChangeRisk.CRITICAL:
            return UpgradePriority.P2

        # High risk = lower priority
        if risk > 0.7:
            return UpgradePriority.P2

        # Medium risk = medium priority
        if risk > 0.4:
            return UpgradePriority.P2

        # Low risk = higher priority (safe to upgrade)
        return UpgradePriority.P1

    def _is_auto_upgradeable(self, update: Any, breaking_risk: BreakingChangeRisk,
                            compatibility: float) -> bool:
        """Determine if update can be auto-upgraded."""
        # Security patches = auto-upgrade if low risk
        if update.has_vulnerability and breaking_risk in [BreakingChangeRisk.LOW, BreakingChangeRisk.NONE]:
            return True

        # Patch updates with high compatibility
        from .monitor import UpdateType
        if update.update_type == UpdateType.PATCH and compatibility > 0.9:
            return True

        # Minor updates with no breaking changes and high compatibility
        if update.update_type == UpdateType.MINOR and breaking_risk == BreakingChangeRisk.NONE and compatibility > 0.8:
            return True

        return False

    def _identify_breaking_changes(self, update: Any,
                                   context: Dict[str, Any]) -> List[str]:
        """Identify specific breaking changes."""
        changes = []

        from .monitor import UpdateType
        if update.update_type == UpdateType.MAJOR:
            changes.append(f"Major version bump from {update.current_version} to {update.latest_version}")

        changelog_data = context.get("changelog_analysis", {}).get(update.package_name, {})
        if changelog_data.get("has_deprecations"):
            changes.append("Contains deprecated API changes")

        return changes

    def _generate_migration_steps(self, update: Any,
                                  breaking_changes: List[str]) -> List[str]:
        """Generate migration steps."""
        steps = []

        if breaking_changes:
            steps.append(f"Review changelog at {update.changelog_url}")
            steps.append("Update code to use new APIs")
            steps.append("Run full test suite")
            steps.append("Test in staging environment")
        else:
            steps.append("Update version in requirements")
            steps.append("Run quick smoke tests")

        return steps

    def _create_rollback_plan(self, update: Any) -> str:
        """Create rollback plan."""
        return f"Revert to {update.current_version} if issues found"

    def _estimate_effort(self, breaking_risk: BreakingChangeRisk,
                        breaking_changes: List[str]) -> str:
        """Estimate upgrade effort."""
        if breaking_risk == BreakingChangeRisk.CRITICAL:
            return "high (4-8 hours)"
        if breaking_risk == BreakingChangeRisk.HIGH:
            return "medium (2-4 hours)"
        if breaking_risk == BreakingChangeRisk.MEDIUM:
            return "low (1-2 hours)"
        return "minimal (<1 hour)"

    def _query_historical_success(self, package: str) -> float:
        """Query historical upgrade success rate."""
        try:
            self.brain.query_patterns(
                pattern_type="dependency_update",
                confidence_threshold=0.5
            )
            # Would filter by package and calculate success rate
            return 0.85  # Default
        except Exception:
            return 0.85

    def _prioritize_updates(self, evaluations: List[UpgradeEvaluation]) -> List[UpgradeEvaluation]:
        """Sort evaluations by priority."""
        priority_order = {
            UpgradePriority.P0: 0,
            UpgradePriority.P1: 1,
            UpgradePriority.P2: 2,
            UpgradePriority.P3: 3
        }
        return sorted(evaluations, key=lambda e: (priority_order[e.priority], e.risk_score))

    def _generate_recommendations(self, prioritized: List[UpgradeEvaluation]) -> List[str]:
        """Generate high-level recommendations."""
        recs = []

        p0_count = sum(1 for e in prioritized if e.priority == UpgradePriority.P0)
        if p0_count > 0:
            recs.append(f"Apply {p0_count} security updates immediately")

        auto_count = sum(1 for e in prioritized if e.auto_upgradeable)
        if auto_count > 0:
            recs.append(f"Auto-upgrade {auto_count} safe updates")

        manual_count = sum(1 for e in prioritized if not e.auto_upgradeable)
        if manual_count > 0:
            recs.append(f"Schedule manual review for {manual_count} complex updates")

        return recs
