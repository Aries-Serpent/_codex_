#!/usr/bin/env python3
"""
Checkpoint Manager for State Persistence and Recovery

Manages the lifecycle of execution state checkpoints:
- Create: Persist full canonical state
- Load: Restore state from checkpoint
- Resume: Rehydrate execution loop from checkpoint
- Rollback: Recover from failed validation

REQUIREMENTS:
- Deterministic state recreation
- No data loss (fix STM 100% loss issue)
- Linked state lineage (previous_state_id)
- Crash recovery support
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class CheckpointStorageConfig:
    """Configuration for checkpoint storage."""
    
    # Default storage location
    DEFAULT_CHECKPOINT_DIR = "docs-data/runtime/checkpoints"
    
    # Metadata storage
    DEFAULT_METADATA_DIR = "docs-data/runtime/checkpoint_metadata"
    
    # Max checkpoints per track
    MAX_CHECKPOINTS_PER_TRACK = 100
    
    # Checkpoint retention policy
    RETAIN_FAILED_CHECKPOINTS = True
    RETAIN_ROLLBACK_HISTORY = True


class CheckpointMetadata:
    """Metadata about a checkpoint."""
    
    def __init__(self, state_id: str, checkpoint_id: str):
        self.state_id = state_id
        self.checkpoint_id = checkpoint_id
        self.created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.accessed_at = self.created_at
        self.restore_count = 0
        self.validation_status = ""
        self.tags: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "state_id": self.state_id,
            "checkpoint_id": self.checkpoint_id,
            "created_at": self.created_at,
            "accessed_at": self.accessed_at,
            "restore_count": self.restore_count,
            "validation_status": self.validation_status,
            "tags": self.tags
        }


class CheckpointManager:
    """Manages creation, loading, and recovery of state checkpoints."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize checkpoint manager.
        
        Args:
            storage_dir: Root directory for checkpoint storage
        """
        self.storage_dir = Path(
            storage_dir or CheckpointStorageConfig.DEFAULT_CHECKPOINT_DIR
        )
        self.metadata_dir = Path(
            storage_dir or CheckpointStorageConfig.DEFAULT_METADATA_DIR
        )
        
        # Ensure directories exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Track state lineage
        self.state_lineage: Dict[str, str] = {}
    
    def create_checkpoint(self, state: Dict[str, Any]) -> str:
        """
        Create a checkpoint from a canonical state.
        
        Persists full state to JSON file with metadata tracking.
        Enforces state lineage for recovery and auditing.
        
        Args:
            state: The canonical execution state
            
        Returns:
            Checkpoint ID (filename without extension)
        """
        state_id = state.get("state_id")
        if not state_id:
            raise ValueError("State must have state_id")
        
        # Generate checkpoint ID
        checkpoint_id = str(uuid.uuid4())
        
        # Prepare checkpoint data
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "state": state,
            "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "format_version": "1.0"
        }
        
        # Write checkpoint file
        checkpoint_file = self.storage_dir / f"{checkpoint_id}.json"
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2)
        
        # Create metadata
        metadata = CheckpointMetadata(state_id, checkpoint_id)
        self._write_metadata(metadata)
        
        # Track lineage
        previous_state_id = state.get("previous_state_id")
        if previous_state_id and previous_state_id != "null":
            self.state_lineage[state_id] = previous_state_id
        
        return checkpoint_id
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a checkpoint by ID.
        
        Restores the complete state from checkpoint storage.
        
        Args:
            checkpoint_id: The checkpoint ID to load
            
        Returns:
            The canonical state dict, or None if checkpoint not found
        """
        checkpoint_file = self.storage_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file, "r") as f:
                checkpoint_data = json.load(f)
            
            # Update metadata access time
            metadata = self._read_metadata(checkpoint_id)
            if metadata:
                metadata.accessed_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                metadata.restore_count += 1
                self._write_metadata(metadata)
            
            return checkpoint_data.get("state")
        
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading checkpoint {checkpoint_id}: {e}")
            return None
    
    def resume_execution(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Resume execution from a checkpoint.
        
        Rehydrates the execution loop with all context, decisions, and
        dependency information intact.
        
        Args:
            checkpoint_id: The checkpoint to resume from
            
        Returns:
            Rehydrated state ready for next execution step
        """
        state = self.load_checkpoint(checkpoint_id)
        if state is None:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        # Mark state as resumed
        state["_checkpoint_source"] = checkpoint_id
        state["_resumed_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # If the execution was paused, may need to update execution_step
        # based on validation results
        validation_results = state.get("validation_results", {})
        if validation_results.get("valid"):
            # State was validated, move to next step
            current_step = state.get("execution_step", "validate")
            next_steps = {
                "observe": "context",
                "context": "decide",
                "decide": "act",
                "act": "validate",
                "validate": "persist",
                "persist": "handoff",
                "handoff": "complete",
                "complete": "complete"
            }
            state["execution_step"] = next_steps.get(current_step, "complete")
        
        return state
    
    def rollback_to_previous(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Rollback to previous state.
        
        Recovery function when validation fails. Restores to the state
        immediately before the failed action.
        
        Args:
            state: Current failed state
            
        Returns:
            Previous state dict, or None if no previous state exists
        """
        previous_state_id = state.get("previous_state_id")
        
        if previous_state_id is None or previous_state_id == "null":
            return None
        
        # Find checkpoint with this state_id
        checkpoint_id = self._find_checkpoint_by_state_id(previous_state_id)
        if checkpoint_id:
            return self.load_checkpoint(checkpoint_id)
        
        return None
    
    def get_checkpoint_lineage(self, checkpoint_id: str) -> List[Dict[str, Any]]:
        """
        Get the complete lineage of a checkpoint.
        
        Returns the chain of states leading up to this checkpoint
        for auditing and recovery.
        
        Args:
            checkpoint_id: The checkpoint to trace
            
        Returns:
            List of states in lineage order (oldest first)
        """
        lineage: List[Dict[str, Any]] = []
        current_id = checkpoint_id
        visited = set()
        
        while current_id and current_id not in visited:
            state = self.load_checkpoint(current_id)
            if state is None:
                break
            
            visited.add(current_id)
            lineage.append({
                "checkpoint_id": current_id,
                "state_id": state.get("state_id"),
                "status": state.get("status"),
                "execution_step": state.get("execution_step"),
                "timestamp": state.get("timestamp")
            })
            
            # Move to previous
            previous_id = state.get("previous_state_id")
            if previous_id and previous_id != "null":
                current_id = self._find_checkpoint_by_state_id(previous_id)
            else:
                break
        
        # Reverse to get chronological order (oldest first)
        return list(reversed(lineage))
    
    def cleanup_checkpoints(self, track_id: Optional[str] = None,
                          older_than_seconds: Optional[int] = None) -> int:
        """
        Clean up old checkpoints.
        
        Maintains checkpoint storage by removing old or orphaned
        checkpoints while preserving lineage for recovery.
        
        Args:
            track_id: Optional track ID to clean up only that track
            older_than_seconds: Remove checkpoints older than this (None = keep all)
            
        Returns:
            Number of checkpoints deleted
        """
        deleted_count = 0
        now_timestamp = datetime.utcnow()
        
        for checkpoint_file in self.storage_dir.glob("*.json"):
            try:
                # Skip if not a checkpoint file
                if not checkpoint_file.name.endswith(".json"):
                    continue
                
                # Check file age if specified
                if older_than_seconds:
                    file_mtime = datetime.fromtimestamp(checkpoint_file.stat().st_mtime)
                    age_seconds = (now_timestamp - file_mtime).total_seconds()
                    
                    if age_seconds < older_than_seconds:
                        continue
                
                # Load checkpoint to check track_id if filtering
                if track_id:
                    with open(checkpoint_file, "r") as f:
                        data = json.load(f)
                    
                    if data.get("state", {}).get("track_id") != track_id:
                        continue
                
                # Delete checkpoint
                checkpoint_file.unlink()
                deleted_count += 1
                
                # Delete associated metadata
                checkpoint_id = checkpoint_file.stem
                metadata_file = self.metadata_dir / f"{checkpoint_id}.json"
                if metadata_file.exists():
                    metadata_file.unlink()
            
            except Exception as e:
                print(f"Error cleaning up checkpoint {checkpoint_file}: {e}")
                continue
        
        return deleted_count
    
    def _write_metadata(self, metadata: CheckpointMetadata) -> None:
        """Write checkpoint metadata to file."""
        metadata_file = self.metadata_dir / f"{metadata.checkpoint_id}.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)
    
    def _read_metadata(self, checkpoint_id: str) -> Optional[CheckpointMetadata]:
        """Read checkpoint metadata from file."""
        metadata_file = self.metadata_dir / f"{checkpoint_id}.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, "r") as f:
                data = json.load(f)
            
            metadata = CheckpointMetadata(data["state_id"], checkpoint_id)
            metadata.created_at = data.get("created_at", metadata.created_at)
            metadata.accessed_at = data.get("accessed_at", metadata.accessed_at)
            metadata.restore_count = data.get("restore_count", 0)
            metadata.validation_status = data.get("validation_status", "")
            metadata.tags = data.get("tags", [])
            
            return metadata
        
        except (json.JSONDecodeError, IOError):
            return None
    
    def _find_checkpoint_by_state_id(self, state_id: str) -> Optional[str]:
        """Find a checkpoint ID by state_id."""
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, "r") as f:
                    data = json.load(f)
                
                if data.get("state_id") == state_id:
                    return data.get("checkpoint_id")
            
            except (json.JSONDecodeError, IOError):
                continue
        
        return None
    
    def get_checkpoint_stats(self) -> Dict[str, Any]:
        """
        Get statistics about checkpoint storage.
        
        Returns:
            Stats about checkpoint usage and storage
        """
        checkpoint_count = len(list(self.storage_dir.glob("*.json")))
        metadata_count = len(list(self.metadata_dir.glob("*.json")))
        
        total_size = sum(
            f.stat().st_size for f in self.storage_dir.glob("*.json")
        )
        
        return {
            "total_checkpoints": checkpoint_count,
            "total_metadata": metadata_count,
            "total_storage_bytes": total_size,
            "storage_dir": str(self.storage_dir),
            "metadata_dir": str(self.metadata_dir)
        }


def create_checkpoint(state: Dict[str, Any], storage_dir: Optional[str] = None) -> str:
    """
    Convenience function to create a checkpoint.
    
    Args:
        state: The state to checkpoint
        storage_dir: Optional storage directory override
        
    Returns:
        Checkpoint ID
    """
    manager = CheckpointManager(storage_dir)
    return manager.create_checkpoint(state)


def load_checkpoint(checkpoint_id: str, storage_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to load a checkpoint.
    
    Args:
        checkpoint_id: The checkpoint ID
        storage_dir: Optional storage directory override
        
    Returns:
        The state dict or None
    """
    manager = CheckpointManager(storage_dir)
    return manager.load_checkpoint(checkpoint_id)


def resume_execution(checkpoint_id: str, storage_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to resume execution from checkpoint.
    
    Args:
        checkpoint_id: The checkpoint ID
        storage_dir: Optional storage directory override
        
    Returns:
        Rehydrated state
    """
    manager = CheckpointManager(storage_dir)
    return manager.resume_execution(checkpoint_id)
