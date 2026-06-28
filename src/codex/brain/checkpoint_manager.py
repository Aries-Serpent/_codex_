"""Checkpoint Manager — Manages agent session state checkpoints.

Phase 10.1 Implementation: Core checkpoint lifecycle management for
autonomous agent session persistence and recovery.

Responsibilities:
- Detect checkpoint trigger conditions (commits, time, events)
- Coordinate state capture via SessionSerializer
- Write checkpoint files with integrity verification
- Maintain checkpoint registry and metadata
- Cleanup old checkpoints based on retention policy
- Verify checkpoint integrity via SHA256

Usage:
    from codex.brain.checkpoint_manager import CheckpointManager

    manager = CheckpointManager()

    # Automatic checkpoint on triggers
    manager.maybe_checkpoint()

    # Force immediate checkpoint
    checkpoint_id = manager.create_checkpoint(label="before_deployment")

    # Inspect checkpoints
    latest = manager.get_latest_checkpoint()
    all_checkpoints = manager.list_checkpoints()
"""

from __future__ import annotations

import gzip
import hashlib
import json
import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CheckpointMetadata:
    """Metadata for a checkpoint."""

    checkpoint_id: str
    session_id: str
    timestamp: str
    created_by_version: str
    schema_version: int
    sha256: str
    compressed: bool
    compressed_size_bytes: int
    uncompressed_size_bytes: int
    repository_commit: str
    agent_id: str
    label: Optional[str] = None


class CheckpointManager:
    """Manages checkpoint lifecycle for agent sessions."""

    # Configuration defaults
    DEFAULT_CHECKPOINT_DIR = Path(".codex/checkpoints")
    DEFAULT_SCHEMA_VERSION = 1
    DEFAULT_RETENTION_COUNT = 10
    DEFAULT_COMMIT_INTERVAL = 5  # Every N commits
    DEFAULT_TIME_INTERVAL_SECONDS = 1800  # Every 30 minutes

    MANAGER_VERSION = "1.0.0"

    def __init__(
        self,
        checkpoint_dir: Optional[Path] = None,
        schema_version: int = DEFAULT_SCHEMA_VERSION,
        retention_count: int = DEFAULT_RETENTION_COUNT,
        commit_interval: int = DEFAULT_COMMIT_INTERVAL,
        time_interval_seconds: int = DEFAULT_TIME_INTERVAL_SECONDS,
    ):
        """Initialize CheckpointManager.

        Args:
            checkpoint_dir: Directory to store checkpoints (default: .codex/checkpoints)
            schema_version: Checkpoint schema version (default: 1)
            retention_count: Number of checkpoints to keep (default: 10)
            commit_interval: Create checkpoint every N commits (default: 5)
            time_interval_seconds: Create checkpoint every T seconds (default: 1800)
        """
        self.checkpoint_dir = Path(checkpoint_dir or self.DEFAULT_CHECKPOINT_DIR)
        self.schema_version = schema_version
        self.retention_count = retention_count
        self.commit_interval = commit_interval
        self.time_interval_seconds = time_interval_seconds

        # Ensure checkpoint directory exists
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        (self.checkpoint_dir / "v1").mkdir(parents=True, exist_ok=True)
        (self.checkpoint_dir / "metadata").mkdir(parents=True, exist_ok=True)

        # Track state for time-based triggers
        self._last_checkpoint_time = time.time()
        self._last_checkpoint_commit_count = 0
        self._commit_count_since_checkpoint = 0

        logger.info(
            f"CheckpointManager initialized: dir={self.checkpoint_dir}, "
            f"retention={retention_count}, schema_v{schema_version}"
        )

    def maybe_checkpoint(self, commit_count_delta: int = 0, force: bool = False) -> Optional[str]:
        """Check if checkpoint should be created based on triggers.

        Args:
            commit_count_delta: Number of commits since last checkpoint
            force: Force checkpoint creation regardless of triggers

        Returns:
            Checkpoint ID if created, None otherwise
        """
        if force:
            logger.info("Forcing checkpoint creation")
            return self.create_checkpoint(label="forced")

        self._commit_count_since_checkpoint += commit_count_delta

        # Check commit-based trigger
        if self._commit_count_since_checkpoint >= self.commit_interval:
            logger.info(
                f"Commit trigger reached: {self._commit_count_since_checkpoint} >= {self.commit_interval}"  # noqa: E501
            )
            return self.create_checkpoint(label="commit_triggered")

        # Check time-based trigger
        time_since_checkpoint = time.time() - self._last_checkpoint_time
        if time_since_checkpoint >= self.time_interval_seconds:
            logger.info(
                f"Time trigger reached: {time_since_checkpoint}s >= {self.time_interval_seconds}s"
            )
            return self.create_checkpoint(label="time_triggered")

        return None

    def create_checkpoint(
        self,
        session_state: Optional[dict[str, Any]] = None,
        session_id: str = "unknown",
        agent_id: str = "unknown",
        repository_commit: str = "unknown",
        label: Optional[str] = None,
    ) -> str:
        """Create a checkpoint of current session state.

        Args:
            session_state: Complete session state dict (from SessionSerializer)
            session_id: Session identifier
            agent_id: Agent identifier
            repository_commit: Current repository commit SHA
            label: Optional checkpoint label

        Returns:
            Checkpoint ID
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        checkpoint_id = self._generate_checkpoint_id(session_id)

        # Build checkpoint payload
        checkpoint_payload = {
            "schema_version": self.schema_version,
            "checkpoint_id": checkpoint_id,
            "timestamp": timestamp,
            "session_id": session_id,
            "agent_id": agent_id,
            "repository_commit": repository_commit,
            "label": label,
            "session_state": session_state or {},
        }

        # Serialize to JSON
        json_str = json.dumps(checkpoint_payload, indent=2, default=str)
        uncompressed_size = len(json_str.encode("utf-8"))

        # Compress with gzip
        compressed_data = gzip.compress(json_str.encode("utf-8"), compresslevel=9)
        compressed_size = len(compressed_data)

        # Calculate SHA256 checksum
        sha256_hash = hashlib.sha256(compressed_data).hexdigest()

        # Write checkpoint file
        checkpoint_file = self.checkpoint_dir / "v1" / f"{checkpoint_id}.json.gz"
        try:
            checkpoint_file.write_bytes(compressed_data)
            # Make checkpoint immutable
            os.chmod(checkpoint_file, 0o444)
            logger.info(
                f"Checkpoint created: {checkpoint_id} (compressed: {compressed_size}B, "
                f"original: {uncompressed_size}B, sha256: {sha256_hash[:16]}...)"
            )
        except Exception as e:
            logger.error(f"Failed to write checkpoint {checkpoint_id}: {e}")
            raise

        # Create metadata entry
        metadata = CheckpointMetadata(
            checkpoint_id=checkpoint_id,
            session_id=session_id,
            timestamp=timestamp,
            created_by_version=self.MANAGER_VERSION,
            schema_version=self.schema_version,
            sha256=sha256_hash,
            compressed=True,
            compressed_size_bytes=compressed_size,
            uncompressed_size_bytes=uncompressed_size,
            repository_commit=repository_commit,
            agent_id=agent_id,
            label=label,
        )

        # Write metadata
        self._write_metadata(metadata)

        # Update checkpoint state
        self._last_checkpoint_time = time.time()
        self._commit_count_since_checkpoint = 0

        # Cleanup old checkpoints
        self._cleanup_old_checkpoints()

        return checkpoint_id

    def list_checkpoints(self) -> list[dict[str, Any]]:
        """List all available checkpoints.

        Returns:
            List of checkpoint metadata dicts, sorted by timestamp (newest first)
        """
        manifest_file = self.checkpoint_dir / "manifest.json"
        checkpoints = []

        if manifest_file.exists():
            try:
                manifest = json.loads(manifest_file.read_text())
                for checkpoint_id, metadata_dict in manifest.items():
                    try:
                        metadata = CheckpointMetadata(**metadata_dict)
                        checkpoints.append(asdict(metadata))
                    except Exception as e:
                        logger.warning(f"Failed to parse metadata for {checkpoint_id}: {e}")
            except Exception as e:
                logger.warning(f"Failed to read manifest: {e}")

        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
        return checkpoints

    def get_latest_checkpoint(self) -> Optional[str]:
        """Get the most recent checkpoint ID.

        Returns:
            Latest checkpoint ID or None if no checkpoints exist
        """
        checkpoints = self.list_checkpoints()
        if checkpoints:
            return checkpoints[0]["checkpoint_id"]
        return None

    def verify_checkpoint_integrity(self, checkpoint_id: str) -> bool:
        """Verify checkpoint integrity via SHA256.

        Args:
            checkpoint_id: ID of checkpoint to verify

        Returns:
            True if checkpoint is valid, False otherwise
        """
        checkpoint_file = self.checkpoint_dir / "v1" / f"{checkpoint_id}.json.gz"

        if not checkpoint_file.exists():
            logger.error(f"Checkpoint file not found: {checkpoint_id}")
            return False

        try:
            # Read checkpoint file
            compressed_data = checkpoint_file.read_bytes()

            # Calculate current SHA256
            current_sha256 = hashlib.sha256(compressed_data).hexdigest()

            # Read metadata
            metadata = self._read_metadata_for_file(checkpoint_id)
            if not metadata:
                logger.error(f"Metadata not found for checkpoint: {checkpoint_id}")
                return False

            # Compare checksums
            if current_sha256 != metadata.sha256:
                logger.error(
                    f"Checkpoint integrity check failed: {checkpoint_id} "
                    f"(expected {metadata.sha256[:16]}..., got {current_sha256[:16]}...)"
                )
                return False

            logger.info(f"Checkpoint integrity verified: {checkpoint_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to verify checkpoint {checkpoint_id}: {e}")
            return False

    def get_checkpoint_content(self, checkpoint_id: str) -> Optional[dict[str, Any]]:
        """Load and decompress checkpoint content.

        Args:
            checkpoint_id: ID of checkpoint to load

        Returns:
            Checkpoint content dict or None on error
        """
        checkpoint_file = self.checkpoint_dir / "v1" / f"{checkpoint_id}.json.gz"

        if not checkpoint_file.exists():
            logger.error(f"Checkpoint file not found: {checkpoint_id}")
            return None

        if not self.verify_checkpoint_integrity(checkpoint_id):
            logger.error(f"Checkpoint integrity check failed: {checkpoint_id}")
            return None

        try:
            compressed_data = checkpoint_file.read_bytes()
            json_str = gzip.decompress(compressed_data).decode("utf-8")
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")
            return None

    def get_checkpoint_metadata(self, checkpoint_id: str) -> Optional[CheckpointMetadata]:
        """Get metadata for a checkpoint.

        Args:
            checkpoint_id: ID of checkpoint

        Returns:
            CheckpointMetadata or None if not found
        """
        return self._read_metadata_for_file(checkpoint_id)

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        checkpoint_file = self.checkpoint_dir / "v1" / f"{checkpoint_id}.json.gz"

        try:
            if checkpoint_file.exists():
                # Make file writable (was immutable after creation)
                os.chmod(
                    checkpoint_file, 0o600
                )  # nosemgrep: semgrep.insecure-file-permissions - Temp permission change before deletion  # noqa: E501
                checkpoint_file.unlink()
                logger.info(f"Checkpoint deleted: {checkpoint_id}")
                return True
            else:
                logger.warning(f"Checkpoint not found: {checkpoint_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete checkpoint {checkpoint_id}: {e}")
            return False

    # Private Methods

    def _generate_checkpoint_id(self, session_id: str) -> str:
        """Generate a unique checkpoint ID.

        Args:
            session_id: Session identifier

        Returns:
            Checkpoint ID
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        counter = len(list((self.checkpoint_dir / "v1").glob("*.json.gz"))) + 1
        return f"cp_{timestamp}_{counter:03d}_{session_id}"

    def _write_metadata(self, metadata: CheckpointMetadata) -> None:
        """Write checkpoint metadata to registry.

        Args:
            metadata: Checkpoint metadata
        """
        manifest_file = self.checkpoint_dir / "manifest.json"
        manifest = {}

        if manifest_file.exists():
            try:
                manifest = json.loads(manifest_file.read_text())
            except Exception as e:
                logger.warning(f"Failed to read manifest: {e}")

        manifest[metadata.checkpoint_id] = asdict(metadata)

        try:
            manifest_file.write_text(json.dumps(manifest, indent=2, default=str))
        except Exception as e:
            logger.error(f"Failed to write manifest: {e}")

        # Also write to immutable jsonl log
        log_file = self.checkpoint_dir / "metadata" / "checkpoint_hashes.jsonl"
        try:
            with log_file.open("a") as f:
                f.write(json.dumps(asdict(metadata), default=str) + "\n")
        except Exception as e:
            logger.error(f"Failed to write hash log: {e}")

    def _read_metadata_for_file(self, checkpoint_id: str) -> Optional[CheckpointMetadata]:
        """Read metadata for a specific checkpoint.

        Args:
            checkpoint_id: ID of checkpoint

        Returns:
            CheckpointMetadata or None
        """
        manifest_file = self.checkpoint_dir / "manifest.json"

        if not manifest_file.exists():
            return None

        try:
            manifest = json.loads(manifest_file.read_text())
            if checkpoint_id in manifest:
                metadata_dict = manifest[checkpoint_id]
                return CheckpointMetadata(**metadata_dict)
        except Exception as e:
            logger.warning(f"Failed to read metadata for {checkpoint_id}: {e}")

        return None

    def _cleanup_old_checkpoints(self) -> None:
        """Remove old checkpoints, keeping only retention_count most recent."""
        checkpoints = self.list_checkpoints()

        if len(checkpoints) > self.retention_count:
            # Delete oldest checkpoints
            for checkpoint in checkpoints[self.retention_count :]:
                cp_id = checkpoint["checkpoint_id"]
                cp_file = self.checkpoint_dir / "v1" / f"{cp_id}.json.gz"

                # Only delete if file exists
                if cp_file.exists():
                    try:
                        os.chmod(
                            cp_file, 0o600
                        )  # nosemgrep: semgrep.insecure-file-permissions - Temp permission change before deletion  # noqa: E501
                        cp_file.unlink()
                        logger.info(f"Cleaned up old checkpoint: {cp_id}")
                    except Exception as e:
                        logger.error(f"Failed to delete checkpoint {cp_id}: {e}")

                # Also remove from manifest
                manifest_file = self.checkpoint_dir / "manifest.json"
                if manifest_file.exists():
                    try:
                        manifest = json.loads(manifest_file.read_text())
                        if cp_id in manifest:
                            del manifest[cp_id]
                            manifest_file.write_text(json.dumps(manifest, indent=2, default=str))
                    except Exception as e:
                        logger.warning(f"Failed to update manifest for {cp_id}: {e}")
