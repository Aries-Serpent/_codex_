"""AST delta analysis for detecting changes."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from codex.ast.baseline import BaselineManager

logger = logging.getLogger(__name__)


@dataclass
class DeltaResult:
    """Result of delta analysis."""

    added: list[str]
    removed: list[str]
    modified: list[str]
    unchanged: list[str]

    def summary(self) -> str:
        """Get summary string."""
        return (
            f"Added: {len(self.added)}, "
            f"Removed: {len(self.removed)}, "
            f"Modified: {len(self.modified)}, "
            f"Unchanged: {len(self.unchanged)}"
        )

    def has_changes(self) -> bool:
        """Check if any changes detected."""
        return bool(self.added or self.removed or self.modified)

    def total_changes(self) -> int:
        """Get total number of changed files."""
        return len(self.added) + len(self.removed) + len(self.modified)


class DeltaAnalyzer:
    """Analyzes differences between AST baselines and current state."""

    def __init__(self, baseline_manager: BaselineManager) -> None:
        """Initialize delta analyzer.

        Args:
            baseline_manager: BaselineManager instance
        """
        self.baseline_manager = baseline_manager

    def analyze(self, current_files: dict[str, dict[str, Any]]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {b["file_path"]: b for b in self.baseline_manager.list_baselines()}
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def analyze_file(self, file_path: str, current_data: dict[str, Any]) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "modified"

        return "unchanged"


__all__ = ["DeltaAnalyzer", "DeltaResult"]
