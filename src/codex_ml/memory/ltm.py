"""Long-term memory (LTM) implementation.

Provides persistent storage for important information and supports
search, retrieval, and lifecycle management of stored data.
"""

from __future__ import annotations

from typing import Any

from .schemas import MemoryEntry


class LTMMemory:
    """Long-Term Memory implementation.

    Provides persistent storage for information consolidated from
    short-term memory. Supports search, retrieval, and lifecycle
    management of stored knowledge.

    Characteristics:
    - Persistent storage (no capacity limits enforced)
    - Slower access than STM but for important information
    - Search and query capabilities
    - Lifecycle management (aging, pruning)

    Attributes:
        storage (dict): Persistent storage of entries
        index_counter (int): Counter for generating entry IDs
    """

    def __init__(self) -> None:
        """Initialize long-term memory."""
        self.storage: dict[int, MemoryEntry] = {}
        self.index_counter = 0

    def store(self, data: Any, importance: float = 0.7, metadata: dict[str, Any] | None = None) -> int:
        """Store data in long-term memory.

        Creates a persistent memory entry with an auto-generated ID.

        Args:
            data: Data to store persistently
            importance: Importance score (0.0 to 1.0)
            metadata: Optional metadata dictionary

        Returns:
            ID of the stored entry

        Raises:
            ValueError: If importance is out of valid range
        """
        if not 0.0 <= importance <= 1.0:
            raise ValueError("importance must be between 0.0 and 1.0")

        entry = MemoryEntry(
            data=data,
            importance=importance,
            metadata=metadata or {}
        )
        entry_id = self.index_counter
        self.storage[entry_id] = entry
        self.index_counter += 1
        return entry_id

    def retrieve(self, entry_id: int) -> Any:
        """Retrieve data from long-term memory by ID.

        Args:
            entry_id: ID of the entry to retrieve

        Returns:
            The stored data

        Raises:
            KeyError: If entry_id doesn't exist
        """
        if entry_id not in self.storage:
            raise KeyError(f"Memory entry {entry_id} not found")
        return self.storage[entry_id].data

    def search(self, predicate: callable) -> list[tuple[int, Any]]:
        """Search long-term memory with a predicate function.

        Searches entries matching the predicate function and returns
        matching entries with their IDs.

        Args:
            predicate: Function that takes data and returns bool

        Returns:
            List of (id, data) tuples for matching entries
        """
        results = []
        for entry_id, entry in self.storage.items():
            try:
                if predicate(entry.data):
                    results.append((entry_id, entry.data))
            except Exception:
                # Skip entries that cause predicate to fail
                pass
        return results

    def delete(self, entry_id: int) -> None:
        """Delete an entry from long-term memory.

        Args:
            entry_id: ID of the entry to delete

        Raises:
            KeyError: If entry_id doesn't exist
        """
        if entry_id not in self.storage:
            raise KeyError(f"Memory entry {entry_id} not found")
        del self.storage[entry_id]

    def get_entry_metadata(self, entry_id: int) -> dict[str, Any]:
        """Get metadata for an entry.

        Args:
            entry_id: ID of the entry

        Returns:
            Metadata dictionary for the entry

        Raises:
            KeyError: If entry_id doesn't exist
        """
        if entry_id not in self.storage:
            raise KeyError(f"Memory entry {entry_id} not found")
        return self.storage[entry_id].metadata.copy()

    def update_metadata(self, entry_id: int, metadata: dict[str, Any]) -> None:
        """Update metadata for an entry.

        Args:
            entry_id: ID of the entry
            metadata: New metadata to merge with existing

        Raises:
            KeyError: If entry_id doesn't exist
        """
        if entry_id not in self.storage:
            raise KeyError(f"Memory entry {entry_id} not found")
        self.storage[entry_id].metadata.update(metadata)

    def list_entries(self) -> list[int]:
        """List all entry IDs in long-term memory.

        Returns:
            List of all entry IDs currently stored
        """
        return list(self.storage.keys())

    def get_size(self) -> int:
        """Get total number of entries in LTM.

        Returns:
            Number of stored entries
        """
        return len(self.storage)

    def clear(self) -> None:
        """Clear all entries from long-term memory.

        Returns:
            None
        """
        self.storage.clear()
        self.index_counter = 0

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about long-term memory.

        Returns:
            Dictionary with statistics (size, avg_importance, etc.)
        """
        if not self.storage:
            return {
                "total_entries": 0,
                "average_importance": 0.0,
                "total_metadata_items": 0,
            }

        importances = [e.importance for e in self.storage.values()]
        total_metadata = sum(len(e.metadata) for e in self.storage.values())

        return {
            "total_entries": len(self.storage),
            "average_importance": sum(importances) / len(importances),
            "total_metadata_items": total_metadata,
        }
