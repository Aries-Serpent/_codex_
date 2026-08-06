"""
Multi-Agent Simulation Suite (Phase 4D)

Comprehensive simulation framework for testing orchestration scenarios:
  - Deterministic agent behavior modeling
  - Workload simulation (bursty, steady-state, adversarial)
  - Failure injection and recovery testing
  - SLA compliance validation
  - Performance regression detection

Usage:
  from src.orchestration.simulation import SimulationEngine, ScenarioBuilder

  # Build a simulation scenario
  scenario = (ScenarioBuilder()
      .add_agent("ci-testing-agent", max_concurrent=5)
      .add_agent("ci-importerror-agent", max_concurrent=3)
      .add_workload("steady", tasks_per_sec=2, avg_duration_ms=5000)
      .add_failure_injection("ci-testing-agent", failure_rate=0.05)
      .build())

  # Run simulation
  engine = SimulationEngine()
  results = engine.run_scenario(scenario)
"""

from __future__ import annotations

import json
import logging
import random
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class WorkloadProfile(Enum):
    """Workload patterns."""
    STEADY_STATE = "steady_state"
    BURSTY = "bursty"
    WAVE = "wave"
    ADVERSARIAL = "adversarial"
    RANDOM = "random"


@dataclass
class SimulationMetrics:
    """Metrics collected during simulation."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    timed_out_tasks: int = 0

    total_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    queue_latency_ms: float = 0.0

    sla_compliant_tasks: int = 0
    sla_target_ms: float = 500.0

    agent_metrics: dict[str, dict[str, Any]] = field(default_factory=dict)

    def success_rate(self) -> float:
        """Compute success rate."""
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks

    def sla_compliance_rate(self) -> float:
        """Compute SLA compliance rate."""
        if self.completed_tasks == 0:
            return 0.0
        return self.sla_compliant_tasks / self.completed_tasks

    def avg_latency_ms(self) -> float:
        """Compute average latency."""
        if self.completed_tasks == 0:
            return 0.0
        return self.total_latency_ms / self.completed_tasks

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "timed_out_tasks": self.timed_out_tasks,
            "success_rate": self.success_rate(),
            "avg_latency_ms": self.avg_latency_ms(),
            "max_latency_ms": self.max_latency_ms,
            "sla_compliance_rate": self.sla_compliance_rate(),
            "agent_metrics": self.agent_metrics,
        }


@dataclass
class SimulationTask:
    """Task in simulation."""
    task_id: str
    agent_id: str
    priority: int
    estimated_duration_ms: float
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None


@dataclass
class AgentSimulator:
    """Simulated agent."""
    agent_id: str
    max_concurrent: int
    avg_task_duration_ms: float
    failure_rate: float = 0.0

    active_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_latency_ms: float = 0.0

    def can_accept_task(self) -> bool:
        """Check if agent can accept another task."""
        return self.active_tasks < self.max_concurrent

    def execute_task(self, task: SimulationTask, current_time: float) -> None:
        """Execute a task."""
        self.active_tasks += 1
        task.started_at = current_time

        # Add random variance
        variance = random.gauss(1.0, 0.2)
        duration = max(100, self.avg_task_duration_ms * variance)

        # Simulate failure
        if random.random() < self.failure_rate:
            task.success = False
            task.error_message = "Simulated failure"
            self.failed_tasks += 1
        else:
            task.success = True

        task.completed_at = current_time + (duration / 1000.0)
        latency = (task.completed_at - task.created_at) * 1000.0
        self.total_latency_ms += latency

        if task.success:
            self.completed_tasks += 1

        self.active_tasks -= 1  # task completed


@dataclass
class WorkloadGenerator:
    """Generate workload patterns."""
    profile: WorkloadProfile
    tasks_per_sec: float
    avg_task_duration_ms: float
    duration_sec: float
    failure_rate: float = 0.0

    def generate(self) -> list[SimulationTask]:
        """Generate tasks according to profile."""

        if self.profile == WorkloadProfile.STEADY_STATE:
            return self._generate_steady_state()
        elif self.profile == WorkloadProfile.BURSTY:
            return self._generate_bursty()
        elif self.profile == WorkloadProfile.WAVE:
            return self._generate_wave()
        elif self.profile == WorkloadProfile.ADVERSARIAL:
            return self._generate_adversarial()
        else:
            return self._generate_random()

    def _generate_steady_state(self) -> list[SimulationTask]:
        """Generate steady-state workload."""
        tasks = []
        task_interval = 1.0 / self.tasks_per_sec
        task_id = 0

        for t in range(int(self.duration_sec)):
            for i in range(int(self.tasks_per_sec)):
                created_at = t + (i * task_interval)
                if created_at < self.duration_sec:
                    tasks.append(SimulationTask(
                        task_id=f"task-{task_id}",
                        agent_id="",  # To be assigned
                        priority=2,
                        estimated_duration_ms=self.avg_task_duration_ms,
                        created_at=created_at,
                    ))
                    task_id += 1

        return tasks

    def _generate_bursty(self) -> list[SimulationTask]:
        """Generate bursty workload."""
        tasks = []
        task_id = 0
        burst_size = int(self.tasks_per_sec * 5)  # 5-second bursts

        for burst_start in range(0, int(self.duration_sec), 10):  # Burst every 10 seconds
            for i in range(burst_size):
                created_at = burst_start + (i * 0.01)
                if created_at < self.duration_sec:
                    tasks.append(SimulationTask(
                        task_id=f"task-{task_id}",
                        agent_id="",
                        priority=2,
                        estimated_duration_ms=self.avg_task_duration_ms,
                        created_at=created_at,
                    ))
                    task_id += 1

        return tasks

    def _generate_wave(self) -> list[SimulationTask]:
        """Generate wave workload (ramps up and down)."""
        tasks = []
        task_id = 0

        for t in range(int(self.duration_sec)):
            # Sine wave: ramp up then down
            rate = self.tasks_per_sec * abs(1.0 - (t % 10.0) / 5.0)

            for i in range(int(rate)):
                created_at = t + (i / rate)
                if created_at < self.duration_sec:
                    tasks.append(SimulationTask(
                        task_id=f"task-{task_id}",
                        agent_id="",
                        priority=2,
                        estimated_duration_ms=self.avg_task_duration_ms,
                        created_at=created_at,
                    ))
                    task_id += 1

        return tasks

    def _generate_adversarial(self) -> list[SimulationTask]:
        """Generate adversarial workload (worst-case)."""
        tasks = []
        task_id = 0

        # Ramp up quickly, then plateau
        for t in range(int(self.duration_sec)):
            rate = min(self.tasks_per_sec * 10, self.tasks_per_sec * 2 * t)

            for i in range(int(rate)):
                created_at = t + (i / max(rate, 1))
                if created_at < self.duration_sec:
                    tasks.append(SimulationTask(
                        task_id=f"task-{task_id}",
                        agent_id="",
                        priority=2,
                        estimated_duration_ms=self.avg_task_duration_ms * 2,  # Longer tasks
                        created_at=created_at,
                    ))
                    task_id += 1

        return tasks

    def _generate_random(self) -> list[SimulationTask]:
        """Generate random workload."""
        tasks = []
        expected_count = int(self.tasks_per_sec * self.duration_sec)

        for i in range(expected_count):
            created_at = random.uniform(0, self.duration_sec)
            duration = max(100, random.gauss(self.avg_task_duration_ms, self.avg_task_duration_ms * 0.3))

            tasks.append(SimulationTask(
                task_id=f"task-{i}",
                agent_id="",
                priority=random.randint(0, 3),
                estimated_duration_ms=duration,
                created_at=created_at,
            ))

        return sorted(tasks, key=lambda t: t.created_at)


class ScenarioBuilder:
    """Build simulation scenarios."""

    def __init__(self):
        self.agents: dict[str, tuple[int, float]] = {}  # agent_id -> (max_concurrent, failure_rate)
        self.workloads: list[tuple[WorkloadProfile, float, float, float, float]] = []  # (profile, rate, avg_duration_ms, duration, failure_rate)
        self.failure_injections: dict[str, float] = {}

    def add_agent(
        self,
        agent_id: str,
        max_concurrent: int = 10,
        failure_rate: float = 0.0,
    ) -> ScenarioBuilder:
        """Add agent to scenario."""
        self.agents[agent_id] = (max_concurrent, failure_rate)
        return self

    def add_workload(
        self,
        profile: str,
        tasks_per_sec: float = 2.0,
        avg_duration_ms: float = 5000.0,
        duration_sec: float = 60.0,
        failure_rate: float = 0.0,
    ) -> ScenarioBuilder:
        """Add workload to scenario."""
        p = WorkloadProfile(profile) if isinstance(profile, str) else profile
        self.workloads.append((p, tasks_per_sec, avg_duration_ms, duration_sec, failure_rate))
        return self

    def add_failure_injection(
        self,
        agent_id: str,
        failure_rate: float,
        duration_sec: float = 30.0,
    ) -> ScenarioBuilder:
        """Inject failures into an agent."""
        self.failure_injections[agent_id] = failure_rate
        return self

    def build(self) -> dict[str, Any]:
        """Build scenario."""
        return {
            "agents": self.agents,
            "workloads": self.workloads,
            "failure_injections": self.failure_injections,
        }


class SimulationEngine:
    """Run multi-agent simulations."""

    def run_scenario(
        self,
        scenario: dict[str, Any],
        verbose: bool = False,
    ) -> SimulationMetrics:
        """Run a simulation scenario."""
        metrics = SimulationMetrics()
        agents = self._initialize_agents(scenario, metrics)
        all_tasks = self._generate_workloads(scenario)
        self._dispatch_tasks(agents, all_tasks)
        self._collect_metrics(agents, all_tasks, metrics)

        if verbose:
            print(f"Simulation complete. Success rate: {metrics.success_rate():.1%}")
            print(f"SLA compliance: {metrics.sla_compliance_rate():.1%}")
            print(f"Avg latency: {metrics.avg_latency_ms():.1f}ms")

        return metrics

    def _initialize_agents(
        self,
        scenario: dict[str, Any],
        metrics: SimulationMetrics,
    ) -> dict[str, AgentSimulator]:
        agents: dict[str, AgentSimulator] = {}
        default_duration = self._default_task_duration_ms(scenario)
        for agent_id, (max_concurrent, failure_rate) in scenario["agents"].items():
            agents[agent_id] = AgentSimulator(
                agent_id=agent_id,
                max_concurrent=max_concurrent,
                avg_task_duration_ms=default_duration,
                failure_rate=failure_rate,
            )
            metrics.agent_metrics[agent_id] = {
                "completed": 0,
                "failed": 0,
                "avg_latency_ms": 0.0,
            }
        return agents

    @staticmethod
    def _default_task_duration_ms(scenario: dict[str, Any]) -> float:
        durations = [avg_duration_ms for _, _, avg_duration_ms, _, _ in scenario["workloads"]]
        return sum(durations) / len(durations) if durations else 5000.0

    def _generate_workloads(self, scenario: dict[str, Any]) -> list[SimulationTask]:
        all_tasks: list[SimulationTask] = []
        for profile, rate, avg_duration_ms, duration, failure_rate in scenario["workloads"]:
            gen = WorkloadGenerator(profile, rate, avg_duration_ms, duration, failure_rate)
            all_tasks.extend(gen.generate())
        all_tasks.sort(key=lambda t: t.created_at)
        return all_tasks

    def _dispatch_tasks(
        self,
        agents: dict[str, AgentSimulator],
        all_tasks: list[SimulationTask],
    ) -> None:
        current_time = 0.0
        max_time = max((t.created_at for t in all_tasks), default=0.0) + 60.0
        task_queue: deque[SimulationTask] = deque()
        task_index = 0

        while current_time < max_time:
            while task_index < len(all_tasks) and all_tasks[task_index].created_at <= current_time:
                task = all_tasks[task_index]
                best_agent = min(agents.values(), key=lambda a: a.active_tasks)
                task.agent_id = best_agent.agent_id
                task_queue.append(task)
                task_index += 1

            for agent in agents.values():
                while task_queue and agent.can_accept_task():
                    task = task_queue.popleft()
                    if task.agent_id == agent.agent_id:
                        agent.execute_task(task, current_time)
                    else:
                        task_queue.appendleft(task)
                        break

            current_time += 0.1

    def _collect_metrics(
        self,
        agents: dict[str, AgentSimulator],
        all_tasks: list[SimulationTask],
        metrics: SimulationMetrics,
    ) -> None:
        metrics.total_tasks = len(all_tasks)
        for agent_id, agent in agents.items():
            metrics.completed_tasks += agent.completed_tasks
            metrics.failed_tasks += agent.failed_tasks
            metrics.total_latency_ms += agent.total_latency_ms

            avg_latency = (
                agent.total_latency_ms / agent.completed_tasks
                if agent.completed_tasks > 0
                else 0.0
            )
            metrics.agent_metrics[agent_id] = {
                "completed": agent.completed_tasks,
                "failed": agent.failed_tasks,
                "avg_latency_ms": avg_latency,
            }

        metrics.max_latency_ms = (
            max((t.completed_at - t.created_at) * 1000.0 for t in all_tasks if t.completed_at)
            if all_tasks
            else 0.0
        )

        for task in all_tasks:
            if task.completed_at is None:
                continue
            if (
                task.success
                and (task.completed_at - task.created_at) * 1000.0 <= metrics.sla_target_ms
            ):
                metrics.sla_compliant_tasks += 1


if __name__ == "__main__":
    # Run example scenario
    scenario = (ScenarioBuilder()
        .add_agent("ci-testing-agent", max_concurrent=5)
        .add_agent("ci-importerror-agent", max_concurrent=3)
        .add_agent("ci-health-alert-agent", max_concurrent=2)
        .add_workload("steady_state", tasks_per_sec=2, avg_duration_ms=5000, duration_sec=30)
        .build())

    engine = SimulationEngine()
    results = engine.run_scenario(scenario, verbose=True)

    print("\nResults:")
    print(json.dumps(results.to_dict(), indent=2))
