"""Strategy Generator Module — Generate repair strategies for incidents.

This module:
- Takes incident reports as input
- Generates ranked repair strategies
- Scores strategies by success probability
- Prioritizes actions by risk/benefit
- Returns action plan for executor
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from orchestration.healing.incident_detection import (
    FailureType,
    IncidentReport,
)

logger = logging.getLogger(__name__)


class StrategyType(str, Enum):
    """Type of repair strategy."""

    RERUN = "rerun"
    FIX_IMPORT = "fix_import"
    FIX_ASSERTION = "fix_assertion"
    ADD_TIMEOUT = "add_timeout"
    MOCK_RESOURCE = "mock_resource"
    FIX_CONFTEST = "fix_conftest"
    APPLY_SECURITY_PATCH = "apply_security_patch"
    ROLLBACK = "rollback"
    NOTIFY_OWNER = "notify_owner"
    ESCALATE = "escalate"
    SKIP_FLAKY = "skip_flaky"


@dataclass
class Action:
    """Single action to execute."""

    action_type: StrategyType
    description: str
    target: str  # File or test name
    changes: Dict[str, Any]
    estimated_duration_sec: float
    rollback_command: Optional[str] = None


@dataclass
class RepairStrategy:
    """Complete repair strategy for an incident."""

    strategy_id: str
    incident_id: str
    strategy_type: StrategyType
    description: str
    actions: List[Action]
    success_probability: float  # 0.0-1.0
    risk_score: float  # 0.0-1.0
    estimated_mttr_sec: float
    requires_approval: bool
    approval_tier: str  # T0-T3
    evidence: List[str] = field(default_factory=list)
    related_incidents: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategy_id": self.strategy_id,
            "incident_id": self.incident_id,
            "strategy_type": self.strategy_type.value,
            "description": self.description,
            "actions": [
                {
                    "action_type": a.action_type.value,
                    "description": a.description,
                    "target": a.target,
                    "changes": a.changes,
                    "estimated_duration_sec": a.estimated_duration_sec,
                    "rollback_command": a.rollback_command,
                }
                for a in self.actions
            ],
            "success_probability": self.success_probability,
            "risk_score": self.risk_score,
            "estimated_mttr_sec": self.estimated_mttr_sec,
            "requires_approval": self.requires_approval,
            "approval_tier": self.approval_tier,
            "evidence": self.evidence,
            "related_incidents": self.related_incidents,
        }


class StrategyGenerator:
    """Generates repair strategies for incidents."""

    @classmethod
    def generate_strategies(
        cls,
        report: IncidentReport,
        max_strategies: int = 5,
    ) -> List[RepairStrategy]:
        """Generate ranked repair strategies.

        Args:
            report: IncidentReport from detector
            max_strategies: Maximum strategies to generate

        Returns:
            List of RepairStrategy sorted by success probability
        """

        strategies = []

        # Generate strategies based on failure type
        if report.failure_type == FailureType.IMPORT_ERROR:
            strategies.extend(cls._strategies_for_import_error(report))

        elif report.failure_type == FailureType.ASSERTION_ERROR:
            strategies.extend(cls._strategies_for_assertion_error(report))

        elif report.failure_type == FailureType.TIMEOUT:
            strategies.extend(cls._strategies_for_timeout(report))

        elif report.failure_type == FailureType.RESOURCE_EXHAUSTION:
            strategies.extend(cls._strategies_for_resource_exhaustion(report))

        elif report.failure_type == FailureType.CASCADING_FAILURE:
            strategies.extend(cls._strategies_for_cascading_failure(report))

        elif report.failure_type == FailureType.FLAKY_TEST:
            strategies.extend(cls._strategies_for_flaky_test(report))

        elif report.failure_type == FailureType.SECURITY_FINDING:
            strategies.extend(cls._strategies_for_security_finding(report))

        else:
            strategies.extend(cls._strategies_for_generic_failure(report))

        # Add fallback strategies
        strategies.extend(cls._fallback_strategies(report))

        # Sort by success probability (descending)
        strategies.sort(
            key=lambda s: (s.success_probability, -s.risk_score), reverse=True
        )

        # Limit and assign IDs
        for i, strategy in enumerate(strategies[:max_strategies]):
            strategy.strategy_id = f"strat_{report.incident_id}_{i}"

        logger.info(
            f"Generated {len(strategies[:max_strategies])} strategies "
            f"for incident {report.incident_id}"
        )

        return strategies[:max_strategies]

    @classmethod
    def _strategies_for_import_error(cls, report: IncidentReport) -> List[RepairStrategy]:
        """Strategies for import errors."""
        strategies = []

        # Strategy 1: Fix import path
        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.FIX_IMPORT,
                description="Add missing import or fix import path",
                actions=[
                    Action(
                        action_type=StrategyType.FIX_IMPORT,
                        description="Add import statement to test file",
                        target=report.affected_tests[0] if report.affected_tests else "unknown",
                        changes={
                            "import_line": "# Auto-added by healer",
                        },
                        estimated_duration_sec=5.0,
                    )
                ],
                success_probability=0.85,
                risk_score=0.1,
                estimated_mttr_sec=30.0,
                requires_approval=False,
                approval_tier="T0",
                evidence=report.root_cause_hypotheses[0].evidence,
            )
        )

        # Strategy 2: P19 shadow import fix
        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.RERUN,
                description="Reinstall package to resolve shadow import (P19)",
                actions=[
                    Action(
                        action_type=StrategyType.RERUN,
                        description="Run pip install --force-reinstall --no-deps -e .",
                        target="package",
                        changes={"command": "pip install --force-reinstall --no-deps -e ."},
                        estimated_duration_sec=30.0,
                    )
                ],
                success_probability=0.7,
                risk_score=0.3,
                estimated_mttr_sec=60.0,
                requires_approval=False,
                approval_tier="T1",
                evidence=["P19 shadow import hypothesis"],
            )
        )

        # Strategy 3: Simple rerun
        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.RERUN,
                description="Rerun failed test (may be transient)",
                actions=[
                    Action(
                        action_type=StrategyType.RERUN,
                        description="Rerun test",
                        target=report.affected_tests[0] if report.affected_tests else "test",
                        changes={"reruns": 1},
                        estimated_duration_sec=10.0,
                    )
                ],
                success_probability=0.4,
                risk_score=0.0,
                estimated_mttr_sec=15.0,
                requires_approval=False,
                approval_tier="T0",
                evidence=["May be transient failure"],
            )
        )

        return strategies

    @classmethod
    def _strategies_for_assertion_error(cls, report: IncidentReport) -> List[RepairStrategy]:
        """Strategies for assertion errors."""
        strategies = []

        # Strategy 1: Fix assertion
        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.FIX_ASSERTION,
                description="Fix test assertion to match implementation",
                actions=[
                    Action(
                        action_type=StrategyType.FIX_ASSERTION,
                        description="Update assertion in test",
                        target=report.affected_tests[0] if report.affected_tests else "test",
                        changes={"assertion": "# Review and fix"},
                        estimated_duration_sec=15.0,
                    )
                ],
                success_probability=0.75,
                risk_score=0.2,
                estimated_mttr_sec=60.0,
                requires_approval=True,
                approval_tier="T1",
                evidence=report.root_cause_hypotheses[0].evidence,
            )
        )

        # Strategy 2: Rerun
        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.RERUN,
                description="Rerun to check if transient",
                actions=[
                    Action(
                        action_type=StrategyType.RERUN,
                        description="Rerun test",
                        target=report.affected_tests[0] if report.affected_tests else "test",
                        changes={"reruns": 1},
                        estimated_duration_sec=10.0,
                    )
                ],
                success_probability=0.3,
                risk_score=0.0,
                estimated_mttr_sec=15.0,
                requires_approval=False,
                approval_tier="T0",
            )
        )

        return strategies

    @classmethod
    def _strategies_for_timeout(cls, report: IncidentReport) -> List[RepairStrategy]:
        """Strategies for timeout failures."""
        strategies = []

        # Strategy 1: Add timeout decorator
        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.ADD_TIMEOUT,
                description="Add pytest timeout marker to prevent hanging",
                actions=[
                    Action(
                        action_type=StrategyType.ADD_TIMEOUT,
                        description="Add @pytest.mark.timeout(30) decorator",
                        target=report.affected_tests[0] if report.affected_tests else "test",
                        changes={"timeout": 30},
                        estimated_duration_sec=5.0,
                    )
                ],
                success_probability=0.65,
                risk_score=0.1,
                estimated_mttr_sec=30.0,
                requires_approval=False,
                approval_tier="T0",
            )
        )

        # Strategy 2: Mock resources
        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.MOCK_RESOURCE,
                description="Mock expensive/async operations",
                actions=[
                    Action(
                        action_type=StrategyType.MOCK_RESOURCE,
                        description="Add mocks for slow operations",
                        target=report.affected_tests[0] if report.affected_tests else "test",
                        changes={"mocks": ["external_api", "database"]},
                        estimated_duration_sec=20.0,
                    )
                ],
                success_probability=0.7,
                risk_score=0.2,
                estimated_mttr_sec=60.0,
                requires_approval=True,
                approval_tier="T1",
            )
        )

        return strategies

    @classmethod
    def _strategies_for_resource_exhaustion(cls, report: IncidentReport) -> List[RepairStrategy]:
        """Strategies for resource exhaustion."""
        strategies = []

        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.MOCK_RESOURCE,
                description="Mock resource-intensive operations",
                actions=[
                    Action(
                        action_type=StrategyType.MOCK_RESOURCE,
                        description="Mock memory-intensive operations",
                        target=report.affected_tests[0] if report.affected_tests else "test",
                        changes={"mocks": ["data_loading", "model_init"]},
                        estimated_duration_sec=15.0,
                    )
                ],
                success_probability=0.8,
                risk_score=0.2,
                estimated_mttr_sec=45.0,
                requires_approval=True,
                approval_tier="T1",
            )
        )

        return strategies

    @classmethod
    def _strategies_for_cascading_failure(
        cls, report: IncidentReport
    ) -> List[RepairStrategy]:
        """Strategies for cascading failures."""
        strategies = []

        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.FIX_CONFTEST,
                description="Fix conftest.py setup/fixture issues",
                actions=[
                    Action(
                        action_type=StrategyType.FIX_CONFTEST,
                        description="Debug and fix conftest fixtures",
                        target="conftest.py",
                        changes={"fixture": "# Review fixture"},
                        estimated_duration_sec=30.0,
                    )
                ],
                success_probability=0.75,
                risk_score=0.4,
                estimated_mttr_sec=120.0,
                requires_approval=True,
                approval_tier="T2",
            )
        )

        return strategies

    @classmethod
    def _strategies_for_flaky_test(cls, report: IncidentReport) -> List[RepairStrategy]:
        """Strategies for flaky tests."""
        strategies = []

        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.SKIP_FLAKY,
                description="Skip or mark test as expected failure",
                actions=[
                    Action(
                        action_type=StrategyType.SKIP_FLAKY,
                        description="Add @pytest.mark.xfail or skip marker",
                        target=report.affected_tests[0] if report.affected_tests else "test",
                        changes={"marker": "xfail"},
                        estimated_duration_sec=5.0,
                    )
                ],
                success_probability=0.9,
                risk_score=0.3,
                estimated_mttr_sec=15.0,
                requires_approval=False,
                approval_tier="T0",
            )
        )

        return strategies

    @classmethod
    def _strategies_for_security_finding(
        cls, report: IncidentReport
    ) -> List[RepairStrategy]:
        """Strategies for security findings."""
        strategies = []

        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.APPLY_SECURITY_PATCH,
                description="Apply security patch",
                actions=[
                    Action(
                        action_type=StrategyType.APPLY_SECURITY_PATCH,
                        description="Apply security fix",
                        target="security",
                        changes={"patch": "# Security fix"},
                        estimated_duration_sec=60.0,
                    )
                ],
                success_probability=0.9,
                risk_score=0.4,
                estimated_mttr_sec=180.0,
                requires_approval=True,
                approval_tier="T2",
            )
        )

        return strategies

    @classmethod
    def _strategies_for_generic_failure(cls, report: IncidentReport) -> List[RepairStrategy]:
        """Strategies for generic/unknown failures."""
        strategies = []

        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.RERUN,
                description="Rerun to check if transient",
                actions=[
                    Action(
                        action_type=StrategyType.RERUN,
                        description="Rerun test",
                        target=report.affected_tests[0] if report.affected_tests else "test",
                        changes={"reruns": 2},
                        estimated_duration_sec=20.0,
                    )
                ],
                success_probability=0.5,
                risk_score=0.0,
                estimated_mttr_sec=30.0,
                requires_approval=False,
                approval_tier="T0",
            )
        )

        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.NOTIFY_OWNER,
                description="Notify owner for manual investigation",
                actions=[
                    Action(
                        action_type=StrategyType.NOTIFY_OWNER,
                        description="Notify owner",
                        target="owner",
                        changes={"notification": "Manual investigation required"},
                        estimated_duration_sec=5.0,
                    )
                ],
                success_probability=0.3,
                risk_score=0.0,
                estimated_mttr_sec=600.0,
                requires_approval=False,
                approval_tier="T0",
            )
        )

        return strategies

    @classmethod
    def _fallback_strategies(cls, report: IncidentReport) -> List[RepairStrategy]:
        """Generate fallback strategies."""
        strategies = []

        # Escalate if all else fails
        strategies.append(
            RepairStrategy(
                strategy_id="",
                incident_id=report.incident_id,
                strategy_type=StrategyType.ESCALATE,
                description="Escalate to human reviewer",
                actions=[
                    Action(
                        action_type=StrategyType.ESCALATE,
                        description="Escalate incident",
                        target="governance",
                        changes={"escalation": "unknown_pattern"},
                        estimated_duration_sec=0.0,
                    )
                ],
                success_probability=0.1,
                risk_score=0.5,
                estimated_mttr_sec=3600.0,
                requires_approval=False,
                approval_tier="T3",
            )
        )

        return strategies
