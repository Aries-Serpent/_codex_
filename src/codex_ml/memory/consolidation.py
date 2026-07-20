"""Memory consolidation engine.

Handles the consolidation of short-term memories to long-term storage,
applying importance-based retention policies and pruning strategies.
"""

from __future__ import annotations

from typing import Any

from .ltm import LTMMemory
from .schemas import ConsolidationRecord
from .stm import STMMemory


class MemoryConsolidation:
    """Memory consolidation engine for STM to LTM transfer.

    Manages the transfer of important information from short-term memory
    to long-term storage. Uses importance-based policies to determine
    what gets consolidated and applies pruning strategies to long-term
    memory.

    Attributes:
        stm (STMMemory): Reference to short-term memory
        ltm (LTMMemory): Reference to long-term memory
        consolidation_history (list): History of consolidation operations
    """

    def __init__(self, stm: STMMemory, ltm: LTMMemory) -> None:
        """Initialize the consolidation engine.

        Args:
            stm: Short-term memory instance
            ltm: Long-term memory instance
        """
        self.stm = stm
        self.ltm = ltm
        self.consolidation_history: list[ConsolidationRecord] = []
        self.consolidation_threshold = 0.5

    def consolidate_memory(
        self,
        min_importance: float = 0.5,
        max_consolidations: int | None = None,
    ) -> ConsolidationRecord | None:
        """Consolidate high-importance entries from STM to LTM.

        Transfers entries meeting the importance threshold from STM to LTM,
        applying importance-based retention policies.

        Args:
            min_importance: Minimum importance for consolidation (0.0-1.0)
            max_consolidations: Maximum number of entries to consolidate

        Returns:
            ConsolidationRecord detailing the operation, or None if nothing consolidated

        Raises:
            ValueError: If importance threshold is invalid
        """
        if not 0.0 <= min_importance <= 1.0:
            raise ValueError("min_importance must be between 0.0 and 1.0")

        # Get consolidatable entries from STM, passing the caller's threshold
        entries_to_consolidate = self.stm.consolidate(min_importance=min_importance)

        if not entries_to_consolidate:
            return None

        if max_consolidations:
            entries_to_consolidate = entries_to_consolidate[:max_consolidations]

        if not entries_to_consolidate:
            return None

        # Consolidate to LTM
        ltm_ids = []
        for data, importance in entries_to_consolidate:
            ltm_id = self.ltm.store(data, importance=importance)
            ltm_ids.append(ltm_id)

        # Create consolidation record
        record = ConsolidationRecord(
            source_stm_id=f"stm_batch_{len(self.consolidation_history)}",
            target_ltm_id=f"ltm_batch_{','.join(map(str, ltm_ids))}",
            num_entries=len(ltm_ids),
            importance_threshold=min_importance,
        )

        self.consolidation_history.append(record)

        # Remove consolidated entries from STM
        self._cleanup_stm_entries(entries_to_consolidate)

        return record

    def _cleanup_stm_entries(self, entries_to_remove: list[tuple[Any, float]]) -> None:
        """Remove consolidated entries from STM.

        Args:
            entries_to_remove: List of (data, importance) tuples to remove

        Returns:
            None
        """
        # Build set of entries to remove for efficient lookup
        entries_to_remove_set = set()
        for data, _ in entries_to_remove:
            for i, entry in enumerate(self.stm.entries):
                if entry.data is data or entry.data == data:
                    entries_to_remove_set.add(i)
                    break

        # Remove in reverse order to maintain indices
        for i in sorted(entries_to_remove_set, reverse=True):
            try:
                self.stm.forget(i)
            except IndexError:
                pass

    def prune_ltm(self, importance_threshold: float = 0.3, max_age_seconds: float = 3600.0) -> int:
        """Prune low-importance or aged entries from long-term memory.

        Removes entries below the importance threshold or older than
        max_age_seconds.

        Args:
            importance_threshold: Minimum importance to keep (0.0-1.0)
            max_age_seconds: Maximum age in seconds (entries older are removed)

        Returns:
            Number of entries pruned

        Raises:
            ValueError: If importance_threshold is invalid
        """
        if not 0.0 <= importance_threshold <= 1.0:
            raise ValueError("importance_threshold must be between 0.0 and 1.0")

        entries_to_delete = []

        for entry_id, entry in self.ltm.storage.items():
            # Check importance
            if entry.importance < importance_threshold:
                entries_to_delete.append(entry_id)
                continue

            # Check age
            if entry.get_age_seconds() > max_age_seconds:
                entries_to_delete.append(entry_id)

        # Delete identified entries
        for entry_id in entries_to_delete:
            try:
                self.ltm.delete(entry_id)
            except KeyError:
                pass

        return len(entries_to_delete)

    def get_consolidation_history(self) -> list[ConsolidationRecord]:
        """Get the history of consolidation operations.

        Returns:
            List of consolidation records
        """
        return self.consolidation_history.copy()

    def set_consolidation_threshold(self, threshold: float) -> None:
        """Set the default consolidation threshold.

        Args:
            threshold: New threshold value (0.0-1.0)

        Raises:
            ValueError: If threshold is invalid
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")
        self.consolidation_threshold = threshold

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about consolidation.

        Returns:
            Dictionary with consolidation statistics
        """
        return {
            "consolidations_performed": len(self.consolidation_history),
            "total_consolidated_entries": sum(r.num_entries for r in self.consolidation_history),
            "stm_size": self.stm.get_size(),
            "ltm_size": self.ltm.get_size(),
        }
