# Type stubs for codex_engine Rust module
#
# This file provides type hints for the Rust-implemented codex_engine module
# to enable proper IDE support and type checking for Python code.

from typing import Optional

__version__: str
__doc__: str  # type: ignore[no-redef]

class SwarmState:
    """
    Thread-safe shared state for agent coordination.

    This class provides concurrent access to agent state without GIL contention.
    Multiple threads can read/write simultaneously using lock-free data structures.
    """

    def __init__(self) -> None:
        """Create a new SwarmState instance."""

    def register_agent(self, agent_id: str) -> None:
        """
        Register a new agent with the swarm.

        Args:
            agent_id: Unique identifier for the agent
        """

    def get_agent_count(self) -> int:
        """Get the current count of registered agents."""

    def set_agent_status(self, agent_id: str, status: str, message: Optional[str] = None) -> None:
        """
        Update an agent's status.

        Args:
            agent_id: Unique identifier for the agent
            status: New status ("idle", "working", "complete", "failed")
            message: Optional message (required for "working" and "failed")
        """

    def get_agent_status(self, agent_id: str) -> tuple[str, str]:
        """
        Get an agent's current status.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            Tuple of (status_str, message)
        """

    def unregister_agent(self, agent_id: str) -> None:
        """Remove an agent from the swarm."""

    def list_agents(self) -> list[str]:
        """Get all agent IDs currently registered."""

class Orchestrator:
    """
    High-performance async orchestrator for agent coordination.

    The Orchestrator runs a Tokio runtime that manages agent tasks independently
    of Python's GIL, enabling true parallelism across all CPU cores.
    """

    def __init__(self, state: SwarmState) -> None:
        """
        Create a new Orchestrator instance.

        Args:
            state: SwarmState instance to manage
        """

    def start(self) -> None:
        """
        Start the orchestration loop.

        Spawns an async task that runs the orchestrator event loop at 10 Hz.
        """

    def stop(self) -> None:
        """Stop the orchestration loop."""

    def is_running(self) -> bool:
        """Check if the orchestrator is currently running."""

class Task:
    """
    A task to be executed by an agent.

    Tasks contain all necessary information for an agent to execute
    a specific operation.
    """

    id: str
    task_type: str
    data: str

    def __init__(self, id: str, task_type: str, data: str) -> None:
        """
        Create a new Task.

        Args:
            id: Unique task identifier
            task_type: Type of task to execute
            data: JSON-encoded task parameters
        """

class TaskQueue:
    """
    High-performance task queue for agent coordination.

    Uses Tokio's unbounded MPSC channels for lock-free task submission.
    Capable of handling 10,000+ tasks per second with sub-millisecond latency.
    """

    def __init__(self) -> None:
        """Create a new TaskQueue."""

    def submit(self, task: Task) -> None:
        """
        Submit a task to the queue (lock-free operation).

        Args:
            task: Task to submit
        """

    def receive(self) -> Optional[Task]:
        """
        Receive the next task from the queue (non-blocking).

        Returns:
            Task if available, None if queue is empty
        """

    def size(self) -> int:
        """
        Get the approximate number of tasks in the queue.

        Note: This is an estimate due to concurrent access.
        """
