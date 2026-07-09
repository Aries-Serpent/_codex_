"""ACT Phase: Execute decided actions through parallel agent orchestration.

This module:
- Translates decisions into agent tasks
- Dispatches to semantic router
- Monitors 3-5 agents in parallel
- Collects results
- Validates outcomes
- Generates execution reports

Output: Execution report with results and metrics
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from a single agent execution."""

    agent_id: str
    agent_name: str
    task_id: str
    status: str  # success, failure, timeout, error
    output: dict[str, Any]
    duration_ms: float
    error_message: Optional[str] = None
    side_effects: list[str] = field(default_factory=list)


@dataclass
class SideEffect:
    """Unintended side effect from action execution."""

    effect_type: str
    description: str
    severity: str  # info, warning, error, critical
    affected_component: str


@dataclass
class ExecutionReport:
    """Report on action execution."""

    timestamp: datetime
    decision_id: str
    agents_executed: list[str]
    results: list[AgentResult]
    outcomes_matched: bool
    side_effects: list[SideEffect]
    duration_ms: float
    success_rate: float
    impact_score: float  # 0-1, how much impact the action had
    next_observable_delta: dict[str, Any]  # Changes to feed into next observe


class AgentDispatcher:
    """Dispatches tasks to agents."""

    def __init__(self) -> None:
        self.available_agents = {
            "ci_auto_healer": {"latency": 127, "success_rate": 0.94},
            "semantic_router": {"latency": 23, "success_rate": 0.98},
            "test_pattern_guardian": {"latency": 45, "success_rate": 0.91},
        }

    def select_agents(
        self,
        candidate_agents: list[str],
        count: int = 3,
        strategy: str = "round_robin",
    ) -> list[str]:
        """Select best agents for execution."""
        try:
            # Filter to available agents
            available = [a for a in candidate_agents if a in self.available_agents]

            if not available:
                # Fall back to any available agent
                available = list(self.available_agents.keys())[:count]

            # Sort by success rate (descending)
            sorted_agents = sorted(
                available,
                key=lambda a: self.available_agents[a]["success_rate"],
                reverse=True,
            )

            return sorted_agents[:count]
        except Exception as e:
            logger.error(f"Failed to select agents: {e}")
            return list(self.available_agents.keys())[:count]

    async def dispatch_async(self, agent_id: str, task: dict[str, Any]) -> AgentResult:
        """Dispatch task to agent asynchronously."""
        try:
            task_id = str(uuid.uuid4())[:8]
            start_time = time.time()

            # In production, make actual RPC call to agent
            # For now, simulate agent execution
            await asyncio.sleep(0.05)  # Simulate latency

            duration_ms = (time.time() - start_time) * 1000

            return AgentResult(
                agent_id=agent_id,
                agent_name=agent_id.replace("_", " ").title(),
                task_id=task_id,
                status="success",
                output={"result": "Task completed successfully", "processed": True},
                duration_ms=duration_ms,
                side_effects=[],
            )
        except Exception as e:
            logger.error(f"Agent dispatch failed for {agent_id}: {e}")
            return AgentResult(
                agent_id=agent_id,
                agent_name=agent_id.replace("_", " ").title(),
                task_id="",
                status="error",
                output={},
                duration_ms=0,
                error_message=str(e),
                side_effects=[],
            )


class OutcomeValidator:
    """Validates action outcomes against expectations."""

    def validate_outcomes(
        self,
        results: list[AgentResult],
        success_criteria: list[str],
    ) -> bool:
        """Validate that outcomes match expectations."""
        try:
            # All results must be successful
            if not all(r.status == "success" for r in results):
                return False

            # For now, consider all successful results as matched
            # In production, would check against specific criteria
            return len(results) > 0
        except Exception as e:
            logger.error(f"Outcome validation failed: {e}")
            return False

    def detect_side_effects(self, results: list[AgentResult]) -> list[SideEffect]:
        """Detect unintended side effects from execution."""
        side_effects = []

        for result in results:
            # Check for errors in output
            if result.status != "success":
                side_effects.append(
                    SideEffect(
                        effect_type="agent_failure",
                        description=f"Agent {result.agent_name} failed: {result.error_message}",
                        severity="warning",
                        affected_component=result.agent_id,
                    )
                )

            # Check for long execution times (potential performance impact)
            if result.duration_ms > 500:
                side_effects.append(
                    SideEffect(
                        effect_type="slow_execution",
                        description=f"Agent {result.agent_name} took {result.duration_ms:.0f}ms",
                        severity="info",
                        affected_component=result.agent_id,
                    )
                )

            # Check for explicit side effects reported by agent
            if result.side_effects:
                for effect in result.side_effects:
                    side_effects.append(
                        SideEffect(
                            effect_type="reported_side_effect",
                            description=effect,
                            severity="warning",
                            affected_component=result.agent_id,
                        )
                    )

        return side_effects


class OODAactor:
    """Main actor: orchestrates action execution."""

    def __init__(self) -> None:
        self.dispatcher = AgentDispatcher()
        self.validator = OutcomeValidator()

    async def act_async(
        self,
        decision_directive: Any,
        timeout_seconds: int = 60,
    ) -> ExecutionReport:
        """Execute action asynchronously."""
        try:
            start_time = time.time()

            # Prepare task
            task = {
                "action": decision_directive.action.description,
                "target": decision_directive.action.target,
                "parameters": decision_directive.action.parameters,
                "timeout": timeout_seconds,
            }

            # Select agents
            agents = self.dispatcher.select_agents(
                decision_directive.assigned_agents,
                count=min(3, len(decision_directive.assigned_agents)),
            )

            # Dispatch to agents in parallel
            agent_tasks = [self.dispatcher.dispatch_async(agent_id, task) for agent_id in agents]

            # Wait for all agents to complete (with timeout)
            results = await asyncio.wait_for(
                asyncio.gather(*agent_tasks, return_exceptions=False),
                timeout=timeout_seconds,
            )

            # Validate outcomes
            outcomes_matched = self.validator.validate_outcomes(
                results,
                success_criteria=["task_completed"],
            )

            # Detect side effects
            side_effects = self.validator.detect_side_effects(results)

            # Calculate metrics
            duration_ms = (time.time() - start_time) * 1000
            successful_results = [r for r in results if r.status == "success"]
            success_rate = len(successful_results) / len(results) if results else 0

            # Calculate impact score (0-1)
            impact_score = min(1.0, success_rate * 0.9 + (1 - len(side_effects) * 0.05))

            # Generate next observable delta
            next_observable_delta = {
                "agents_affected": agents,
                "actions_executed": len(results),
                "success_count": len(successful_results),
                "side_effects": len(side_effects),
            }

            return ExecutionReport(
                timestamp=datetime.now(),
                decision_id=decision_directive.decision_id,
                agents_executed=agents,
                results=results,
                outcomes_matched=outcomes_matched,
                side_effects=side_effects,
                duration_ms=duration_ms,
                success_rate=success_rate,
                impact_score=impact_score,
                next_observable_delta=next_observable_delta,
            )

        except asyncio.TimeoutError:
            logger.error("Action execution timed out")
            return self._create_timeout_report(decision_directive, start_time)
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return self._create_error_report(decision_directive, start_time, str(e))

    def act(
        self,
        decision_directive: Any,
        timeout_seconds: int = 60,
    ) -> ExecutionReport:
        """Execute action (synchronous wrapper)."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.act_async(decision_directive, timeout_seconds))
        finally:
            loop.close()

    def _create_timeout_report(
        self,
        decision_directive: Any,
        start_time: float,
    ) -> ExecutionReport:
        """Create report for timeout scenario."""
        return ExecutionReport(
            timestamp=datetime.now(),
            decision_id=decision_directive.decision_id,
            agents_executed=[],
            results=[],
            outcomes_matched=False,
            side_effects=[
                SideEffect(
                    effect_type="timeout",
                    description="Action execution exceeded timeout",
                    severity="error",
                    affected_component="orchestrator",
                )
            ],
            duration_ms=(time.time() - start_time) * 1000,
            success_rate=0.0,
            impact_score=0.0,
            next_observable_delta={"error": "timeout"},
        )

    def _create_error_report(
        self,
        decision_directive: Any,
        start_time: float,
        error_msg: str,
    ) -> ExecutionReport:
        """Create report for error scenario."""
        return ExecutionReport(
            timestamp=datetime.now(),
            decision_id=decision_directive.decision_id,
            agents_executed=[],
            results=[],
            outcomes_matched=False,
            side_effects=[
                SideEffect(
                    effect_type="execution_error",
                    description=f"Action execution error: {error_msg}",
                    severity="error",
                    affected_component="orchestrator",
                )
            ],
            duration_ms=(time.time() - start_time) * 1000,
            success_rate=0.0,
            impact_score=0.0,
            next_observable_delta={"error": error_msg},
        )
