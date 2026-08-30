"""
Multi-Agent Orchestrator for _codex_
Coordinates multiple autonomous agents with shared resources

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Rate limiting across all agents
- Input validation on task parameters
- Bounded queue size
- Defensive error handling
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from codex.clients import CodexOpenAIClient, ExecutionResult
from codex_ml.safety.moderation import ModerationAdapter, ModerationRejection, ModerationSettings

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds checking constants
MAX_AGENTS = 100
MAX_QUEUE_SIZE = 10000
MAX_CAPABILITIES_PER_AGENT = 50


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class Agent:
    """Represents a registered agent."""

    id: str
    capabilities: list[str]
    status: AgentStatus = AgentStatus.IDLE
    tasks_completed: int = 0
    total_tokens_used: int = 0


@dataclass
class RateLimiter:
    """Rate limiter for API requests."""

    requests_per_minute: int = 60
    tokens_per_minute: int = 150000
    current_requests: int = 0
    current_tokens: int = 0
    window_start: float = 0.0


class AgentOrchestrator:
    """
    Orchestrates multiple autonomous agents with shared OpenAI resources.

    Features:
    - Agent registration and capability matching
    - Rate limiting across all agents
    - Task queue management
    - Resource pooling

    Safeguards:
    - Bounded agent registration
    - Bounded queue size
    - Rate limiting enforcement
    - Input validation
    """

    def __init__(self) -> None:
        """Initialize the orchestrator."""
        self.client = CodexOpenAIClient()
        self.agents: dict[str, Agent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
        self.rate_limiter = RateLimiter()
        self._lock = asyncio.Lock()

    def register_agent(self, agent_id: str, capabilities: list[str]) -> Agent | None:
        """
        Register a new agent with the orchestrator.

        Args:
            agent_id: Unique identifier for the agent
            capabilities: List of task types the agent can handle

        Returns:
            The registered Agent instance or None if registration fails

        Safeguards:
        - Validates agent_id is non-empty string
        - Bounds check on number of agents
        - Bounds check on capabilities list
        """
        # Input validation (safeguard)
        if not agent_id or not isinstance(agent_id, str):
            logger.warning("Invalid agent_id provided")
            return None

        # Bounds check on agents (safeguard)
        if len(self.agents) >= MAX_AGENTS:
            logger.warning(f"Maximum agents reached: {MAX_AGENTS}")
            return None

        # Bounds check on capabilities (safeguard)
        if len(capabilities) > MAX_CAPABILITIES_PER_AGENT:
            logger.warning(f"Capabilities exceed limit, truncating to {MAX_CAPABILITIES_PER_AGENT}")
            capabilities = capabilities[:MAX_CAPABILITIES_PER_AGENT]

        agent = Agent(id=agent_id, capabilities=capabilities)
        self.agents[agent_id] = agent
        logger.info(f"Registered agent: {agent_id} with {len(capabilities)} capabilities")
        return agent

    def select_agent_for_task(self, task_type: str) -> Agent | None:
        """
        Select the best available agent for a task.

        Args:
            task_type: Type of task to execute

        Returns:
            Selected agent or None if no suitable agent available
        """
        for agent in self.agents.values():
            if agent.status == AgentStatus.IDLE and task_type in agent.capabilities:
                return agent

        # Fallback: any idle agent
        for agent in self.agents.values():
            if agent.status == AgentStatus.IDLE:
                return agent

        return None

    async def delegate_task(
        self,
        prompt: str,
        task_type: str = "general",
        **kwargs: Any,
    ) -> ExecutionResult:
        """
        Delegate a task to an available agent.

        Args:
            prompt: The task prompt
            task_type: Type of task
            **kwargs: Additional arguments for task execution

        Returns:
            ExecutionResult from the agent
        """
        agent = self.select_agent_for_task(task_type)

        if not agent:
            # Check queue size before adding (safeguard)
            if self.task_queue.full():
                return ExecutionResult(
                    success=False,
                    model="",
                    error="Task queue is full. Cannot queue task.",
                )

            # Queue the task for later
            try:
                self.task_queue.put_nowait((prompt, task_type, kwargs))
            except asyncio.QueueFull:
                logger.debug("Exception caught, returning", exc_info=True)
                return ExecutionResult(
                    success=False,
                    model="",
                    error="Task queue is full.",
                )

            return ExecutionResult(
                success=False,
                model="",
                error="No available agents. Task queued.",
            )

        async with self._lock:
            agent.status = AgentStatus.BUSY

        try:
            # Gap 27: mandatory pre-dispatch moderation (fail-closed)
            _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
            _mod.enforce(prompt, stage="input")
        except ModerationRejection:
            logger.warning("Moderation rejected orchestrator task prompt for agent %s", agent.id)
            async with self._lock:
                agent.status = AgentStatus.IDLE
            return ExecutionResult(
                success=False,
                model="",
                error="Request rejected by content policy.",
            )

        try:
            # Apply rate limiting
            await self._enforce_rate_limits(prompt)

            # Select model
            model = self.client.select_model()

            # In production, this would execute the actual task
            # For now, return a placeholder result
            result = ExecutionResult(
                success=True,
                model=model,
                response=f"[ORCHESTRATED] Task delegated to agent {agent.id}",
                usage={
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150,
                },
                duration_ms=100,
                estimated_cost=0.0,
            )

            # Update agent stats
            async with self._lock:
                agent.tasks_completed += 1
                if result.usage:
                    agent.total_tokens_used += result.usage.get("total_tokens", 0)
                agent.status = AgentStatus.IDLE

            return result

        except (ValueError, TypeError, RuntimeError) as e:
            logger.debug(f"Exception: {type(e).__name__}")
            async with self._lock:
                agent.status = AgentStatus.ERROR

            logger.error(f"Agent {agent.id} encountered error: {e}")

            return ExecutionResult(
                success=False,
                model="",
                error=str(e),
            )

    async def _enforce_rate_limits(self, prompt: str) -> None:
        """Enforce rate limits before making a request (thread-safe with async lock)."""
        # Estimate tokens (rough approximation)
        estimated_tokens = int(len(prompt.split()) * 1.3)

        # Acquire lock for atomic rate limit check and update
        async with self._lock:
            current_time = time.time()

            # Reset counters if minute has passed (fully atomic under lock)
            if current_time - self.rate_limiter.window_start > 60:
                self.rate_limiter.current_requests = 0
                self.rate_limiter.current_tokens = 0
                self.rate_limiter.window_start = current_time

            # Check if we need to wait
            needs_wait = (
                self.rate_limiter.current_requests >= self.rate_limiter.requests_per_minute
                or self.rate_limiter.current_tokens + estimated_tokens
                > self.rate_limiter.tokens_per_minute
            )

            if needs_wait:
                # Calculate wait time while still holding lock
                wait_time = 60 - (current_time - self.rate_limiter.window_start)
                # Clamp to positive value
                wait_time = max(0, wait_time)
            else:
                # Increment counters atomically before releasing lock
                self.rate_limiter.current_requests += 1
                self.rate_limiter.current_tokens += estimated_tokens
                wait_time = 0

        # Sleep outside the lock to allow other tasks to proceed
        if wait_time > 0:
            logger.info(f"⏳ Rate limit approaching, waiting {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)

            # After wait, atomically reset and increment counters for this request
            async with self._lock:
                current_time = time.time()
                self.rate_limiter.current_requests = 1
                self.rate_limiter.current_tokens = estimated_tokens
                self.rate_limiter.window_start = current_time

    def get_orchestrator_status(self) -> dict[str, Any]:
        """Get the current status of the orchestrator."""
        return {
            "registered_agents": len(self.agents),
            "agents": {
                agent_id: {
                    "status": agent.status.value,
                    "capabilities": agent.capabilities,
                    "tasks_completed": agent.tasks_completed,
                    "tokens_used": agent.total_tokens_used,
                }
                for agent_id, agent in self.agents.items()
            },
            "queued_tasks": self.task_queue.qsize(),
            "rate_limiter": {
                "requests_used": self.rate_limiter.current_requests,
                "tokens_used": self.rate_limiter.current_tokens,
            },
            "client_usage": self.client.get_usage_summary(),
        }


__all__ = [
    "Agent",
    "AgentOrchestrator",
    "AgentStatus",
    "RateLimiter",
]
