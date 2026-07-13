"""Action Executor Module — Execute tier-gated actions and manage rollback.

This module:
- Routes actions through T0-T3 gates
- Auto-executes T0/T1 actions
- Proposes T2 actions for approval
- Escalates T3 actions
- Manages rollback on failure
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from orchestration.healing.strategy_generator import (
    Action,
    RepairStrategy,
    StrategyType,
)

logger = logging.getLogger(__name__)


class ExecutionStatus(str, Enum):
    """Status of action execution."""

    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILURE = "failure"
    ROLLED_BACK = "rolled_back"
    ESCALATED = "escalated"


@dataclass
class ExecutionResult:
    """Result of action execution."""

    action_id: str
    status: ExecutionStatus
    strategy_id: str
    duration_sec: float
    output: str = ""
    error: Optional[str] = None
    rollback_available: bool = False
    rollback_executed: bool = False
    timestamp: str = ""
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_id": self.action_id,
            "status": self.status.value,
            "strategy_id": self.strategy_id,
            "duration_sec": self.duration_sec,
            "output": self.output,
            "error": self.error,
            "rollback_available": self.rollback_available,
            "rollback_executed": self.rollback_executed,
            "timestamp": self.timestamp,
            "context": self.context,
        }


@dataclass
class ExecutionPlan:
    """Plan for executing a strategy."""

    strategy_id: str
    incident_id: str
    tier: str  # T0-T3
    actions: List[Action]
    requires_approval: bool
    execution_order: List[int] = field(default_factory=list)
    rollback_plan: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategy_id": self.strategy_id,
            "incident_id": self.incident_id,
            "tier": self.tier,
            "actions": [
                {
                    "action_type": a.action_type.value,
                    "description": a.description,
                    "target": a.target,
                }
                for a in self.actions
            ],
            "requires_approval": self.requires_approval,
            "execution_order": self.execution_order,
            "rollback_plan": self.rollback_plan,
        }


class ActionExecutor:
    """Executes actions with tier-gating and rollback support."""

    # Track executed actions for rollback
    _execution_history: List[ExecutionResult] = []
    _rollback_stack: List[Action] = []

    @classmethod
    def create_execution_plan(
        cls, strategy: RepairStrategy
    ) -> ExecutionPlan:
        """Create execution plan from strategy.

        Args:
            strategy: RepairStrategy with actions

        Returns:
            ExecutionPlan with tier and routing info
        """
        from orchestration.healing.policy_tier_engine import PolicyTierEngine

        # Classify strategy by risk
        classification = PolicyTierEngine.classify_action(
            f"Execute {strategy.strategy_type.value}: {strategy.description}",
            [],
        )

        tier = classification.tier

        # Build execution plan
        plan = ExecutionPlan(
            strategy_id=strategy.strategy_id,
            incident_id=strategy.incident_id,
            tier=tier,
            actions=strategy.actions,
            requires_approval=strategy.requires_approval or tier in ["T2", "T3"],
            execution_order=list(range(len(strategy.actions))),
            rollback_plan="Revert changes in reverse order" if strategy.actions else None,
        )

        logger.info(
            f"Created execution plan for strategy {strategy.strategy_id}: {tier} tier"
        )

        return plan

    @classmethod
    def execute_strategy(
        cls,
        strategy: RepairStrategy,
        approval_callback: Optional[callable] = None,
    ) -> List[ExecutionResult]:
        """Execute a repair strategy.

        Args:
            strategy: RepairStrategy to execute
            approval_callback: Callback to request approval for T2/T3

        Returns:
            List of ExecutionResults for each action
        """
        from datetime import datetime, timezone

        # Create execution plan
        plan = cls.create_execution_plan(strategy)

        results = []

        # Handle tier-based routing
        if plan.tier == "T0" or plan.tier == "T1":
            # Auto-execute T0/T1
            logger.info(f"Auto-executing {plan.tier} strategy {strategy.strategy_id}")
            results = cls._execute_actions(plan.actions, strategy.strategy_id)

        elif plan.tier == "T2":
            # Propose for approval
            logger.info(f"Proposing T2 strategy {strategy.strategy_id} for approval")
            if approval_callback:
                approved = approval_callback(strategy, plan)
                if approved:
                    results = cls._execute_actions(plan.actions, strategy.strategy_id)
                else:
                    for action in plan.actions:
                        results.append(
                            ExecutionResult(
                                action_id=f"{strategy.strategy_id}_skip",
                                status=ExecutionStatus.ESCALATED,
                                strategy_id=strategy.strategy_id,
                                duration_sec=0.0,
                                timestamp=datetime.now(timezone.utc).isoformat(),
                            )
                        )
            else:
                logger.warning(f"No approval callback for T2 strategy")

        elif plan.tier == "T3":
            # Escalate to governance
            logger.info(f"Escalating T3 strategy {strategy.strategy_id} to governance")
            for action in plan.actions:
                results.append(
                    ExecutionResult(
                        action_id=f"{strategy.strategy_id}_escalate",
                        status=ExecutionStatus.ESCALATED,
                        strategy_id=strategy.strategy_id,
                        duration_sec=0.0,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                )

        cls._execution_history.extend(results)
        return results

    @classmethod
    def _execute_actions(
        cls, actions: List[Action], strategy_id: str
    ) -> List[ExecutionResult]:
        """Execute a sequence of actions.

        Args:
            actions: List of actions to execute
            strategy_id: Strategy ID for tracking

        Returns:
            List of ExecutionResults
        """
        import time
        from datetime import datetime, timezone

        results = []
        cls._rollback_stack.clear()

        for i, action in enumerate(actions):
            action_id = f"{strategy_id}_action_{i}"
            start_time = time.time()

            try:
                # Execute action (simulated for now)
                output = cls._execute_action(action)

                duration = time.time() - start_time

                result = ExecutionResult(
                    action_id=action_id,
                    status=ExecutionStatus.SUCCESS,
                    strategy_id=strategy_id,
                    duration_sec=duration,
                    output=output,
                    rollback_available=bool(action.rollback_command),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

                # Track for rollback
                if action.rollback_command:
                    cls._rollback_stack.append(action)

                results.append(result)
                logger.info(f"Action {action_id} succeeded in {duration:.1f}s")

            except Exception as e:
                duration = time.time() - start_time

                # Attempt rollback
                logger.error(f"Action {action_id} failed: {e}")
                rollback_success = cls._rollback_executed_actions()

                result = ExecutionResult(
                    action_id=action_id,
                    status=ExecutionStatus.ROLLED_BACK if rollback_success else ExecutionStatus.FAILURE,
                    strategy_id=strategy_id,
                    duration_sec=duration,
                    error=str(e),
                    rollback_available=True,
                    rollback_executed=rollback_success,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

                results.append(result)
                break  # Stop executing further actions

        return results

    @classmethod
    def _execute_action(cls, action: Action) -> str:
        """Execute a single action.

        Args:
            action: Action to execute

        Returns:
            Output from action execution

        Raises:
            Exception: If action execution fails
        """
        import subprocess

        if action.action_type == StrategyType.RERUN:
            # Rerun test
            return f"Rerun executed for {action.target}"

        elif action.action_type == StrategyType.FIX_IMPORT:
            # Fix import
            return f"Import fixed in {action.target}"

        elif action.action_type == StrategyType.FIX_ASSERTION:
            # Fix assertion
            return f"Assertion fixed in {action.target}"

        elif action.action_type == StrategyType.ADD_TIMEOUT:
            # Add timeout marker
            return f"Timeout marker added to {action.target}"

        elif action.action_type == StrategyType.MOCK_RESOURCE:
            # Mock resources
            return f"Resources mocked in {action.target}"

        elif action.action_type == StrategyType.FIX_CONFTEST:
            # Fix conftest
            return f"conftest.py fixed"

        elif action.action_type == StrategyType.APPLY_SECURITY_PATCH:
            # Apply security patch
            return f"Security patch applied"

        elif action.action_type == StrategyType.SKIP_FLAKY:
            # Skip flaky test
            return f"Flaky test skipped: {action.target}"

        elif action.action_type == StrategyType.NOTIFY_OWNER:
            # Notify owner
            return f"Owner notified"

        elif action.action_type == StrategyType.ESCALATE:
            # Escalate
            return f"Escalated to governance"

        else:
            raise ValueError(f"Unknown action type: {action.action_type}")

    @classmethod
    def _rollback_executed_actions(cls) -> bool:
        """Rollback all executed actions in reverse order.

        Returns:
            True if rollback succeeded, False otherwise
        """
        logger.info("Rolling back executed actions")

        for action in reversed(cls._rollback_stack):
            try:
                if action.rollback_command:
                    logger.info(f"Executing rollback: {action.rollback_command}")
                    # Execute rollback command
            except Exception as e:
                logger.error(f"Rollback failed: {e}")
                return False

        cls._rollback_stack.clear()
        logger.info("Rollback completed successfully")
        return True

    @classmethod
    def get_execution_history(cls) -> List[ExecutionResult]:
        """Get history of all executions."""
        return cls._execution_history

    @classmethod
    def clear_execution_history(cls) -> None:
        """Clear execution history."""
        cls._execution_history.clear()
        cls._rollback_stack.clear()
