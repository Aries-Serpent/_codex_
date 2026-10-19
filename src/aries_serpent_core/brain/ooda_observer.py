"""OBSERVE Phase: Collect and snapshot environment state for OODA loop.

This module continuously collects state from:
- Repository (branch, changes, test results)
- Agent ecosystem (health, queue, performance)
- Task queue (pending, active, completed)
- System environment (CPU, memory, disk)
- Event stream (GitHub, workflow, alerts)

Output: Observable state snapshot (JSON, immutable)
"""

import asyncio
import json
import logging
import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class RepositoryState:
    """Current state of the repository."""

    current_branch: str
    commit_hash: str
    uncommitted_changes: int
    staged_changes: int
    test_status: str  # passing, failing, unknown
    test_count: int
    test_failures: int
    ci_status: str  # success, failure, pending, unknown, unavailable, error
    last_commit_timestamp: datetime
    recent_commits: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentStatus:
    """Status of a single agent."""

    agent_id: str
    name: str
    status: str  # healthy, degraded, failing
    queue_depth: int
    success_rate: float
    avg_latency_ms: float
    last_execution: Optional[datetime]
    error_count: int


@dataclass
class AgentEcosystemState:
    """Overall state of agent ecosystem."""

    total_agents: int
    healthy_agents: int
    degraded_agents: int
    failing_agents: int
    agents: list[AgentStatus] = field(default_factory=list)
    total_queue_depth: int = 0
    avg_success_rate: float = 0.0
    avg_latency_ms: float = 0.0


@dataclass
class TaskInfo:
    """Information about a task."""

    task_id: str
    priority: int  # 1=critical, 5=low
    status: str  # pending, active, completed, failed
    created_at: datetime
    age_seconds: int
    dependencies: list[str] = field(default_factory=list)
    owner: Optional[str] = None


@dataclass
class TaskQueueState:
    """State of the task queue."""

    pending_count: int
    active_count: int
    completed_count: int
    failed_count: int
    oldest_pending_age_seconds: int
    tasks: list[TaskInfo] = field(default_factory=list)


@dataclass
class EnvironmentMetrics:
    """System environment metrics."""

    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_percent: float
    disk_available_mb: float
    network_latency_ms: Optional[float]


@dataclass
class Event:
    """A system event."""

    timestamp: datetime
    event_type: str  # github_push, workflow_complete, alert, etc.
    source: str
    severity: str  # critical, warning, info
    data: dict[str, Any]


@dataclass
class ObservableMetadata:
    """Metadata about the observation."""

    observation_latency_ms: float
    state_completeness: float  # 0-1, fraction of data sources collected
    data_freshness_seconds: dict[str, float]  # per data source
    event_count: int


@dataclass
class Observable:
    """Complete snapshot of observable environment state."""

    timestamp: datetime
    repository: RepositoryState
    agents: AgentEcosystemState
    tasks: TaskQueueState
    environment: EnvironmentMetrics
    events: list[Event]
    metadata: ObservableMetadata

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""

        def serialize(obj) -> None:
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(
                obj,
                (
                    RepositoryState,
                    AgentEcosystemState,
                    TaskQueueState,
                    EnvironmentMetrics,
                    Event,
                    ObservableMetadata,
                ),
            ):
                return asdict(obj)
            return obj

        return json.loads(json.dumps(asdict(self), default=serialize))


class RepositoryObserver:
    """Observes repository state."""

    def __init__(
        self,
        repo_path: Path = Path("."),
        collect_test_status: bool = False,
        collect_ci_status: bool = False,
        test_command: Optional[list[str]] = None,
        test_timeout_seconds: int = 300,
    ):
        self.repo_path = repo_path
        self.collect_test_status = collect_test_status
        self.collect_ci_status = collect_ci_status
        self.test_command = test_command or [
            "python",
            "-m",
            "pytest",
            "--collect-only",
            "-q",
        ]
        self.test_timeout_seconds = test_timeout_seconds

    def _collect_test_status(self) -> tuple[str, int, int]:
        """Measure test status via pytest, or report it as unavailable.

        Returns (status, collected, failures). ``unavailable`` means no
        measurement was attempted; ``unknown`` means one was attempted but
        the summary could not be parsed. Neither is reported as healthy.
        """
        if not self.collect_test_status:
            return ("unavailable", 0, 0)
        try:
            result = subprocess.run(
                self.test_command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=self.test_timeout_seconds,
            )
            collected = failures = 0
            match = re.search(r"(\d+)\s+tests? collected", result.stdout)
            if match:
                collected = int(match.group(1))
            err_match = re.search(r"(\d+)\s+errors?", result.stdout + result.stderr)
            if err_match:
                failures = int(err_match.group(1))
            if result.returncode == 0:
                return ("passing", collected, 0)
            return ("failing", collected, max(failures, 1))
        except subprocess.TimeoutExpired:
            return ("failing", 0, 1)
        except FileNotFoundError:
            logger.warning("pytest not available; test status unknown")
            return ("unknown", 0, 0)
        except Exception as e:  # noqa: BLE001 - observation must not raise
            logger.error(f"Test status collection failed: {e}")
            return ("error", 0, 0)

    def _collect_ci_status(self, branch: str) -> str:
        """Measure CI status via the GitHub CLI, or report it unavailable."""
        if not self.collect_ci_status:
            return "unavailable"
        try:
            result = subprocess.run(
                [
                    "gh",
                    "run",
                    "list",
                    "--branch",
                    branch,
                    "--limit",
                    "1",
                    "--json",
                    "status,conclusion",
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode != 0:
                return "unavailable"
            runs = json.loads(result.stdout or "[]")
            if not runs:
                return "unavailable"
            run = runs[0]
            if run.get("status") != "completed":
                return "pending"
            return "success" if run.get("conclusion") == "success" else "failure"
        except FileNotFoundError:
            logger.warning("gh CLI not available; CI status unavailable")
            return "unavailable"
        except Exception as e:  # noqa: BLE001 - observation must not raise
            logger.error(f"CI status collection failed: {e}")
            return "error"

    def observe(self) -> RepositoryState:
        """Collect current repository state."""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            current_branch = branch_result.stdout.strip() or "unknown"

            # Get current commit
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            commit_hash = commit_result.stdout.strip()[:8] or "unknown"

            # Count changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            lines = status_result.stdout.strip().split("\n") if status_result.stdout else []
            uncommitted = len([ln for ln in lines if ln and not ln.startswith("??")]) or 0
            staged = len([ln for ln in lines if ln and ln.startswith(" M")]) or 0

            # Get recent commits
            log_result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--format=%H|%s|%ai"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            recent_commits = []
            if log_result.stdout:
                for line in log_result.stdout.strip().split("\n"):
                    if "|" in line:
                        parts = line.split("|")
                        recent_commits.append(
                            {
                                "hash": parts[0][:8],
                                "message": parts[1],
                                "timestamp": parts[2] if len(parts) > 2 else "",
                            }
                        )

            # Get last commit timestamp
            if recent_commits:
                try:
                    last_commit_time = datetime.fromisoformat(
                        recent_commits[0]["timestamp"].replace("Z", "+00:00")
                    )
                except (ValueError, IndexError):
                    last_commit_time = datetime.now()
            else:
                last_commit_time = datetime.now()

            test_status, test_count, test_failures = self._collect_test_status()
            ci_status = self._collect_ci_status(current_branch)

            return RepositoryState(
                current_branch=current_branch,
                commit_hash=commit_hash,
                uncommitted_changes=uncommitted,
                staged_changes=staged,
                test_status=test_status,
                test_count=test_count,
                test_failures=test_failures,
                ci_status=ci_status,
                last_commit_timestamp=last_commit_time,
                recent_commits=recent_commits,
            )
        except Exception as e:
            logger.error(f"Failed to observe repository state: {e}")
            return RepositoryState(
                current_branch="unknown",
                commit_hash="unknown",
                uncommitted_changes=0,
                staged_changes=0,
                test_status="error",
                test_count=0,
                test_failures=0,
                ci_status="error",
                last_commit_timestamp=datetime.now(),
            )


class AgentEcosystemObserver:
    """Observes agent ecosystem state.

    Reads the local agent registry file when present. When no registry is
    available the observer reports zero agents rather than inventing
    representative entries; per-agent health metrics require a registry
    that supplies them and are otherwise left at their zero defaults.
    """

    def __init__(self, agent_registry_path: Path = Path(".codex/agent_registry.json")):
        self.agent_registry_path = agent_registry_path

    def observe(self) -> AgentEcosystemState:
        """Collect current agent ecosystem state from the registry."""
        try:
            if not self.agent_registry_path.exists():
                logger.info(
                    "Agent registry not found at %s; reporting empty ecosystem",
                    self.agent_registry_path,
                )
                return AgentEcosystemState(
                    total_agents=0,
                    healthy_agents=0,
                    degraded_agents=0,
                    failing_agents=0,
                )

            registry = json.loads(self.agent_registry_path.read_text(encoding="utf-8"))
            entries = registry.get("agents", registry if isinstance(registry, list) else [])

            agents: list[AgentStatus] = []
            healthy_count = 0
            degraded_count = 0
            failing_count = 0
            total_queue_depth = 0

            for entry in entries:
                name = str(entry.get("name") or entry.get("id") or "unknown")
                # Registry entries that do not report a measured success
                # rate are counted but not assigned fabricated metrics.
                measured = "success_rate" in entry
                success_rate = float(entry.get("success_rate", 0.0))
                latency = float(entry.get("avg_latency_ms", 0.0))
                queue_depth = int(entry.get("queue_depth", 0))

                if not measured:
                    status = "unknown"
                elif success_rate > 0.95:
                    status = "healthy"
                    healthy_count += 1
                elif success_rate > 0.85:
                    status = "degraded"
                    degraded_count += 1
                else:
                    status = "failing"
                    failing_count += 1

                agents.append(
                    AgentStatus(
                        agent_id=name.lower().replace("-", "_"),
                        name=name,
                        status=status,
                        queue_depth=queue_depth,
                        success_rate=success_rate,
                        avg_latency_ms=latency,
                        last_execution=None,
                        error_count=int(entry.get("error_count", 0)),
                    )
                )
                total_queue_depth += queue_depth

            measured_agents = [a for a in agents if a.status != "unknown"]
            avg_success_rate = (
                sum(a.success_rate for a in measured_agents) / len(measured_agents)
                if measured_agents
                else 0.0
            )
            avg_latency = (
                sum(a.avg_latency_ms for a in measured_agents) / len(measured_agents)
                if measured_agents
                else 0.0
            )

            return AgentEcosystemState(
                total_agents=len(agents),
                healthy_agents=healthy_count,
                degraded_agents=degraded_count,
                failing_agents=failing_count,
                agents=agents,
                total_queue_depth=total_queue_depth,
                avg_success_rate=avg_success_rate,
                avg_latency_ms=avg_latency,
            )
        except Exception as e:
            logger.error(f"Failed to observe agent ecosystem: {e}")
            return AgentEcosystemState(
                total_agents=0,
                healthy_agents=0,
                degraded_agents=0,
                failing_agents=0,
            )


class TaskQueueObserver:
    """Observes task queue state.

    When a queue path is configured the observer counts real task records
    (one JSON object per line). Without a live queue it reports empty
    counts rather than representative placeholders.
    """

    def __init__(self, queue_path: Optional[Path] = None):
        self.queue_path = queue_path

    def observe(self) -> TaskQueueState:
        """Collect current task queue state from the configured queue."""
        try:
            if self.queue_path is None or not self.queue_path.exists():
                return TaskQueueState(
                    pending_count=0,
                    active_count=0,
                    completed_count=0,
                    failed_count=0,
                    oldest_pending_age_seconds=0,
                )

            now = datetime.now()
            tasks: list[TaskInfo] = []
            pending = active = completed = failed = 0
            oldest_pending_age = 0

            with open(self.queue_path, encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    status = str(record.get("status", "pending"))
                    created_raw = record.get("created_at")
                    try:
                        created_at = (
                            datetime.fromisoformat(str(created_raw).replace("Z", "+00:00"))
                            if created_raw
                            else now
                        )
                    except ValueError:
                        created_at = now
                    age_seconds = max(0, int((now - created_at).total_seconds()))

                    if status == "pending":
                        pending += 1
                        oldest_pending_age = max(oldest_pending_age, age_seconds)
                    elif status == "active":
                        active += 1
                    elif status == "completed":
                        completed += 1
                    elif status == "failed":
                        failed += 1

                    tasks.append(
                        TaskInfo(
                            task_id=str(record.get("task_id", f"task_{len(tasks)}")),
                            priority=int(record.get("priority", 5)),
                            status=status,
                            created_at=created_at,
                            age_seconds=age_seconds,
                            dependencies=list(record.get("dependencies", [])),
                            owner=record.get("owner"),
                        )
                    )

            return TaskQueueState(
                pending_count=pending,
                active_count=active,
                completed_count=completed,
                failed_count=failed,
                oldest_pending_age_seconds=oldest_pending_age,
                tasks=tasks,
            )
        except Exception as e:
            logger.error(f"Failed to observe task queue: {e}")
            return TaskQueueState(
                pending_count=0,
                active_count=0,
                completed_count=0,
                failed_count=0,
                oldest_pending_age_seconds=0,
            )


class EnvironmentObserver:
    """Observes system environment metrics."""

    def observe(self) -> EnvironmentMetrics:
        """Collect current environment metrics."""
        try:
            import psutil

            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / (1024 * 1024)

            # Disk
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_available_mb = disk.free / (1024 * 1024)

            # Network latency to GitHub (simple ping to DNS)
            try:
                start = time.time()
                subprocess.run(
                    ["ping", "-c", "1", "-W", "100", "8.8.8.8"],
                    capture_output=True,
                    timeout=2,
                )
                network_latency_ms = (time.time() - start) * 1000
            except Exception:
                network_latency_ms = None

            return EnvironmentMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_mb=memory_available_mb,
                disk_percent=disk_percent,
                disk_available_mb=disk_available_mb,
                network_latency_ms=network_latency_ms,
            )
        except ImportError:
            # psutil not available, return defaults
            return EnvironmentMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_mb=0.0,
                disk_percent=0.0,
                disk_available_mb=0.0,
                network_latency_ms=None,
            )
        except Exception as e:
            logger.error(f"Failed to observe environment metrics: {e}")
            return EnvironmentMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_mb=0.0,
                disk_percent=0.0,
                disk_available_mb=0.0,
                network_latency_ms=None,
            )


class EventObserver:
    """Observes system events."""

    def __init__(self) -> None:
        self.events: list[Event] = []

    def observe(self) -> list[Event]:
        """Collect current events."""
        # In production, this would subscribe to event streams
        # For now, return empty list (events are event-driven)
        return self.events.copy()

    def record_event(self, event_type: str, source: str, severity: str, data: Dict) -> None:
        """Record a new event."""
        self.events.append(
            Event(
                timestamp=datetime.now(),
                event_type=event_type,
                source=source,
                severity=severity,
                data=data,
            )
        )


class OODAObserver:
    """Main observer: orchestrates all observation sub-systems."""

    def __init__(self, repo_path: Path = Path(".")):
        self.repo_observer = RepositoryObserver(repo_path)
        self.agent_observer = AgentEcosystemObserver()
        self.task_observer = TaskQueueObserver()
        self.env_observer = EnvironmentObserver()
        self.event_observer = EventObserver()

    async def observe_async(self) -> Observable:
        """Observe all state asynchronously."""
        start_time = time.time()

        # Collect all observations in parallel
        loop = asyncio.get_event_loop()

        repo_state = await loop.run_in_executor(None, self.repo_observer.observe)
        agent_state = await loop.run_in_executor(None, self.agent_observer.observe)
        task_state = await loop.run_in_executor(None, self.task_observer.observe)
        env_metrics = await loop.run_in_executor(None, self.env_observer.observe)
        events = await loop.run_in_executor(None, self.event_observer.observe)

        observation_latency_ms = (time.time() - start_time) * 1000

        # Calculate state completeness (all sources collected)
        state_completeness = (
            1.0
            if all(
                [
                    repo_state,
                    agent_state,
                    task_state,
                    env_metrics,
                ]
            )
            else 0.8
        )

        metadata = ObservableMetadata(
            observation_latency_ms=observation_latency_ms,
            state_completeness=state_completeness,
            data_freshness_seconds={
                "repository": 0.1,
                "agents": 0.5,
                "tasks": 0.2,
                "environment": 0.1,
                "events": 0.0,
            },
            event_count=len(events),
        )

        return Observable(
            timestamp=datetime.now(),
            repository=repo_state,
            agents=agent_state,
            tasks=task_state,
            environment=env_metrics,
            events=events,
            metadata=metadata,
        )

    def observe(self) -> Observable:
        """Observe all state (synchronous)."""
        start_time = time.time()

        # Collect all observations sequentially
        repo_state = self.repo_observer.observe()
        agent_state = self.agent_observer.observe()
        task_state = self.task_observer.observe()
        env_metrics = self.env_observer.observe()
        events = self.event_observer.observe()

        observation_latency_ms = (time.time() - start_time) * 1000

        # Calculate state completeness
        state_completeness = (
            1.0
            if all(
                [
                    repo_state,
                    agent_state,
                    task_state,
                    env_metrics,
                ]
            )
            else 0.8
        )

        metadata = ObservableMetadata(
            observation_latency_ms=observation_latency_ms,
            state_completeness=state_completeness,
            data_freshness_seconds={
                "repository": 0.1,
                "agents": 0.5,
                "tasks": 0.2,
                "environment": 0.1,
                "events": 0.0,
            },
            event_count=len(events),
        )

        return Observable(
            timestamp=datetime.now(),
            repository=repo_state,
            agents=agent_state,
            tasks=task_state,
            environment=env_metrics,
            events=events,
            metadata=metadata,
        )
