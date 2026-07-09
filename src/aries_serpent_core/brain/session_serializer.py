"""Session Serializer — Captures and serializes agent session state.

Phase 10.1 Implementation: Complete session state capture and serialization
for checkpoint persistence.

Responsibilities:
- Serialize agent state (ID, metadata, status)
- Capture decision history with confidence scores
- Snapshot memory (STM, LTM, pattern library)
- Record execution progress (tasks, milestones)
- Capture repository and context state
- Support JSON and binary formats
- Apply compression

Usage:
    from codex.brain.session_serializer import SessionSerializer

    serializer = SessionSerializer()

    # Serialize complete session state
    state_dict = serializer.serialize_session_state(
        agent_state=agent,
        memory_snapshot=memory,
        decision_history=decisions,
        execution_progress=progress
    )

    # Convert to JSON
    json_str = serializer.serialize_to_json(state_dict)

    # Or binary format
    binary_data = serializer.serialize_to_binary(state_dict)
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import msgpack

logger = logging.getLogger(__name__)


@dataclass
class AgentStateSnapshot:
    """Snapshot of agent state."""

    agent_id: str
    agent_type: str
    status: str  # running, paused, completed, error
    version: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionSnapshot:
    """Snapshot of a decision made by the agent."""

    decision_id: str
    timestamp: str
    decision_type: str
    description: str
    confidence: float
    outcome: str  # success, pending, failed
    work_items_affected: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class MemorySnapshot:
    """Snapshot of agent memory."""

    short_term_memory: list[dict[str, Any]] = field(default_factory=list)
    long_term_memory: list[dict[str, Any]] = field(default_factory=list)
    total_patterns: int = 0
    memory_usage_bytes: int = 0


@dataclass
class ExecutionProgressSnapshot:
    """Snapshot of execution progress."""

    current_task: Optional[str] = None
    completed_tasks: list[str] = field(default_factory=list)
    pending_tasks: list[str] = field(default_factory=list)
    failed_tasks: list[str] = field(default_factory=list)
    work_items: dict[str, int] = field(
        default_factory=lambda: {"total": 0, "completed": 0, "failed": 0, "pending": 0}
    )
    milestones: dict[str, Any] = field(
        default_factory=lambda: {"completed": [], "current": None, "pending": []}
    )


@dataclass
class RepositoryStateSnapshot:
    """Snapshot of repository state."""

    branch: str
    commit_sha: str
    uncommitted_changes: int = 0
    tracked_files_count: int = 0
    last_commit_time: Optional[str] = None


@dataclass
class ContextSnapshot:
    """Snapshot of execution context."""

    system_prompt_hash: str = ""
    user_context: dict[str, Any] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)


class SessionSerializer:
    """Serializes and deserializes agent session state."""

    SCHEMA_VERSION = 1
    SERIALIZER_VERSION = "1.0.0"

    def __init__(self) -> None:
        """Initialize SessionSerializer."""
        logger.info(f"SessionSerializer initialized: version={self.SERIALIZER_VERSION}")

    def serialize_session_state(
        self,
        agent_state: Optional[AgentStateSnapshot] = None,
        memory_snapshot: Optional[MemorySnapshot] = None,
        decision_history: Optional[list[DecisionSnapshot]] = None,
        execution_progress: Optional[ExecutionProgressSnapshot] = None,
        repository_state: Optional[RepositoryStateSnapshot] = None,
        context_snapshot: Optional[ContextSnapshot] = None,
    ) -> dict[str, Any]:
        """Serialize complete session state.

        Args:
            agent_state: Agent state snapshot
            memory_snapshot: Memory snapshot
            decision_history: List of decision snapshots
            execution_progress: Execution progress snapshot
            repository_state: Repository state snapshot
            context_snapshot: Context snapshot

        Returns:
            Complete session state dict
        """
        return {
            "schema_version": self.SCHEMA_VERSION,
            "serializer_version": self.SERIALIZER_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_state": self._serialize_agent_state(agent_state),
            "decision_history": self._serialize_decision_history(decision_history),
            "memory_snapshot": self._serialize_memory_snapshot(memory_snapshot),
            "execution_progress": self._serialize_execution_progress(execution_progress),
            "repository_state": self._serialize_repository_state(repository_state),
            "context_snapshot": self._serialize_context_snapshot(context_snapshot),
        }

    def serialize_to_json(self, state_dict: dict[str, Any]) -> str:
        """Serialize state dict to JSON string.

        Args:
            state_dict: State dictionary

        Returns:
            JSON string
        """
        try:
            json_str = json.dumps(state_dict, indent=2, default=str)
            logger.debug(f"Serialized to JSON: {len(json_str)} bytes")
            return json_str
        except Exception as e:
            logger.error(f"Failed to serialize to JSON: {e}")
            raise

    def serialize_to_binary(self, state_dict: dict[str, Any]) -> bytes:
        """Serialize state dict to binary (msgpack) format.

        Args:
            state_dict: State dictionary

        Returns:
            Binary data (msgpack encoded)
        """
        try:
            # Convert dataclass instances to dicts if needed
            state_copy = self._prepare_for_msgpack(state_dict)
            binary_data = msgpack.packb(state_copy, use_bin_type=True)
            logger.debug(f"Serialized to binary: {len(binary_data)} bytes")
            return binary_data
        except Exception as e:
            logger.error(f"Failed to serialize to binary: {e}")
            raise

    def deserialize_from_json(self, json_str: str) -> dict[str, Any]:
        """Deserialize state from JSON string.

        Args:
            json_str: JSON string

        Returns:
            State dictionary
        """
        try:
            state_dict = json.loads(json_str)
            logger.debug(f"Deserialized from JSON: {len(json_str)} bytes")
            return state_dict
        except Exception as e:
            logger.error(f"Failed to deserialize from JSON: {e}")
            raise

    def deserialize_from_binary(self, binary_data: bytes) -> dict[str, Any]:
        """Deserialize state from binary (msgpack) format.

        Args:
            binary_data: Binary data (msgpack encoded)

        Returns:
            State dictionary
        """
        try:
            state_dict = msgpack.unpackb(binary_data, raw=False)
            logger.debug(f"Deserialized from binary: {len(binary_data)} bytes")
            return state_dict
        except Exception as e:
            logger.error(f"Failed to deserialize from binary: {e}")
            raise

    def compress_payload(self, data: bytes) -> bytes:
        """Compress payload using gzip.

        Args:
            data: Uncompressed data

        Returns:
            Compressed data
        """
        import gzip

        try:
            compressed = gzip.compress(data, compresslevel=9)
            compression_ratio = len(data) / len(compressed) if compressed else 0
            logger.debug(
                f"Compressed payload: {len(data)} -> {len(compressed)} bytes "
                f"(ratio: {compression_ratio:.2f}x)"
            )
            return compressed
        except Exception as e:
            logger.error(f"Failed to compress payload: {e}")
            raise

    def decompress_payload(self, compressed_data: bytes) -> bytes:
        """Decompress gzip payload.

        Args:
            compressed_data: Compressed data

        Returns:
            Uncompressed data
        """
        import gzip

        try:
            decompressed = gzip.decompress(compressed_data)
            logger.debug(
                f"Decompressed payload: {len(compressed_data)} -> {len(decompressed)} bytes"
            )
            return decompressed
        except Exception as e:
            logger.error(f"Failed to decompress payload: {e}")
            raise

    # Private Methods

    def _serialize_agent_state(self, agent_state: Optional[AgentStateSnapshot]) -> dict[str, Any]:
        """Serialize agent state."""
        if not agent_state:
            return {
                "agent_id": "unknown",
                "agent_type": "unknown",
                "status": "unknown",
                "version": "0.0.0",
                "metadata": {},
            }
        return asdict(agent_state)

    def _serialize_decision_history(
        self, decision_history: Optional[list[DecisionSnapshot]]
    ) -> list[dict[str, Any]]:
        """Serialize decision history."""
        if not decision_history:
            return []
        return [asdict(decision) for decision in decision_history]

    def _serialize_memory_snapshot(
        self, memory_snapshot: Optional[MemorySnapshot]
    ) -> dict[str, Any]:
        """Serialize memory snapshot."""
        if not memory_snapshot:
            return {
                "short_term_memory": [],
                "long_term_memory": [],
                "total_patterns": 0,
                "memory_usage_bytes": 0,
            }
        return asdict(memory_snapshot)

    def _serialize_execution_progress(
        self, execution_progress: Optional[ExecutionProgressSnapshot]
    ) -> dict[str, Any]:
        """Serialize execution progress."""
        if not execution_progress:
            return {
                "current_task": None,
                "completed_tasks": [],
                "pending_tasks": [],
                "failed_tasks": [],
                "work_items": {"total": 0, "completed": 0, "failed": 0, "pending": 0},
                "milestones": {"completed": [], "current": None, "pending": []},
            }
        return asdict(execution_progress)

    def _serialize_repository_state(
        self, repository_state: Optional[RepositoryStateSnapshot]
    ) -> dict[str, Any]:
        """Serialize repository state."""
        if not repository_state:
            return {
                "branch": "unknown",
                "commit_sha": "unknown",
                "uncommitted_changes": 0,
                "tracked_files_count": 0,
                "last_commit_time": None,
            }
        return asdict(repository_state)

    def _serialize_context_snapshot(
        self, context_snapshot: Optional[ContextSnapshot]
    ) -> dict[str, Any]:
        """Serialize context snapshot."""
        if not context_snapshot:
            return {
                "system_prompt_hash": "",
                "user_context": {},
                "configuration": {},
            }
        return asdict(context_snapshot)

    def _prepare_for_msgpack(self, obj: Any) -> Any:
        """Recursively prepare object for msgpack serialization.

        Args:
            obj: Object to prepare

        Returns:
            Msgpack-compatible object
        """
        if isinstance(obj, dict):
            return {k: self._prepare_for_msgpack(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._prepare_for_msgpack(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # Convert to string representation for unsupported types
            return str(obj)


def create_agent_state_snapshot(
    agent_id: str,
    agent_type: str,
    status: str = "running",
    version: str = "1.0.0",
    **metadata,
) -> AgentStateSnapshot:
    """Helper to create AgentStateSnapshot.

    Args:
        agent_id: Agent identifier
        agent_type: Type of agent (custom, builtin, etc.)
        status: Agent status
        version: Agent version
        **metadata: Additional metadata

    Returns:
        AgentStateSnapshot
    """
    return AgentStateSnapshot(
        agent_id=agent_id,
        agent_type=agent_type,
        status=status,
        version=version,
        metadata=metadata,
    )


def create_decision_snapshot(
    decision_id: str,
    decision_type: str,
    description: str,
    confidence: float = 0.9,
    outcome: str = "pending",
    **metrics,
) -> DecisionSnapshot:
    """Helper to create DecisionSnapshot.

    Args:
        decision_id: Decision identifier
        decision_type: Type of decision
        description: Decision description
        confidence: Confidence score (0-1)
        outcome: Decision outcome
        **metrics: Additional metrics

    Returns:
        DecisionSnapshot
    """
    return DecisionSnapshot(
        decision_id=decision_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        decision_type=decision_type,
        description=description,
        confidence=confidence,
        outcome=outcome,
        metrics=metrics,
    )


def create_memory_snapshot(
    short_term_memory: Optional[list[dict[str, Any]]] = None,
    long_term_memory: Optional[list[dict[str, Any]]] = None,
    total_patterns: int = 0,
    memory_usage_bytes: int = 0,
) -> MemorySnapshot:
    """Helper to create MemorySnapshot.

    Args:
        short_term_memory: STM entries
        long_term_memory: LTM entries
        total_patterns: Total number of patterns
        memory_usage_bytes: Total memory used

    Returns:
        MemorySnapshot
    """
    return MemorySnapshot(
        short_term_memory=short_term_memory or [],
        long_term_memory=long_term_memory or [],
        total_patterns=total_patterns,
        memory_usage_bytes=memory_usage_bytes,
    )


def create_execution_progress_snapshot(
    current_task: Optional[str] = None,
    completed_tasks: Optional[list[str]] = None,
    pending_tasks: Optional[list[str]] = None,
    failed_tasks: Optional[list[str]] = None,
) -> ExecutionProgressSnapshot:
    """Helper to create ExecutionProgressSnapshot.

    Args:
        current_task: Current task ID
        completed_tasks: List of completed task IDs
        pending_tasks: List of pending task IDs
        failed_tasks: List of failed task IDs

    Returns:
        ExecutionProgressSnapshot
    """
    return ExecutionProgressSnapshot(
        current_task=current_task,
        completed_tasks=completed_tasks or [],
        pending_tasks=pending_tasks or [],
        failed_tasks=failed_tasks or [],
    )


def create_repository_state_snapshot(
    branch: str,
    commit_sha: str,
    uncommitted_changes: int = 0,
    tracked_files_count: int = 0,
) -> RepositoryStateSnapshot:
    """Helper to create RepositoryStateSnapshot.

    Args:
        branch: Current branch
        commit_sha: Current commit SHA
        uncommitted_changes: Number of uncommitted changes
        tracked_files_count: Total tracked files

    Returns:
        RepositoryStateSnapshot
    """
    return RepositoryStateSnapshot(
        branch=branch,
        commit_sha=commit_sha,
        uncommitted_changes=uncommitted_changes,
        tracked_files_count=tracked_files_count,
        last_commit_time=datetime.now(timezone.utc).isoformat(),
    )


def create_context_snapshot(
    system_prompt_hash: str = "",
    user_context: Optional[dict[str, Any]] = None,
    configuration: Optional[dict[str, Any]] = None,
) -> ContextSnapshot:
    """Helper to create ContextSnapshot.

    Args:
        system_prompt_hash: Hash of system prompt
        user_context: User context dict
        configuration: Configuration dict

    Returns:
        ContextSnapshot
    """
    return ContextSnapshot(
        system_prompt_hash=system_prompt_hash,
        user_context=user_context or {},
        configuration=configuration or {},
    )
