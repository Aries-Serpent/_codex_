"""
Dependency Upgrade Agent - Automated dependency update management.

#AFTERMATH_PATTERN_IDENTIFIED: dependency_upgrade_automation
This agent implements automated dependency monitoring, evaluation, and upgrade.
"""

from .monitor import DependencyMonitor, DependencyUpdate
from .evaluator import DependencyEvaluator, UpgradeEvaluation, BreakingChangeRisk
from .upgrader import DependencyUpgrader, UpgradeResult, UpgradeStrategy
from .tracker import DependencyTracker, UpgradeMetrics

__all__ = [
    "DependencyMonitor",
    "DependencyUpdate",
    "DependencyEvaluator",
    "UpgradeEvaluation",
    "BreakingChangeRisk",
    "DependencyUpgrader",
    "UpgradeResult",
    "UpgradeStrategy",
    "DependencyTracker",
    "UpgradeMetrics",
]
