"""
Codex Verify Module

Behavior comparison and test generation for validating transformations.

Components:
- comparator: Compare baseline vs patched behavior
- test_gen: Generate tests from samples
- snapshot: Manage IO snapshots
"""

from __future__ import annotations

__all__ = ["compare", "ComparisonResult", "generate_tests"]
