"""
Codex Verify Module

Behavior comparison and test generation for validating transformations.

Components:
- comparator: Compare baseline vs patched behavior
- test_gen: Generate tests from samples
- snapshot: Manage IO snapshots
"""

from __future__ import annotations

from .comparator import ComparisonResult, compare, generate_tests

__all__ = ["ComparisonResult", "compare", "generate_tests"]
