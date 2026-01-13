"""Dependency Conflict Resolver Agent - Resolves dependency conflicts and manages versions"""

__version__ = "1.0.0"
__agent_name__ = "dependency-conflict-resolver"

from .agent import DependencyConflictResolver

__all__ = ["DependencyConflictResolver"]
