"""
Dependency Upgrade Agent - Automated dependency update management.

#AFTERMATH_PATTERN_IDENTIFIED: dependency_upgrade_automation
This agent implements automated dependency monitoring, evaluation, and upgrade.
"""

from .evaluator import BreakingChangeRisk, DependencyEvaluator, UpgradeEvaluation
from .monitor import DependencyMonitor, DependencyUpdate
from .tracker import DependencyTracker, UpgradeMetrics
from .upgrader import DependencyUpgrader, UpgradeResult, UpgradeStrategy

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
