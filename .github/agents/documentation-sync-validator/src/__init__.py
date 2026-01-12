"""Documentation Sync Validator Agent Package"""

__version__ = "1.0.0"
__author__ = "Copilot Autonomous Agent System"
__description__ = "Validates documentation synchronization with codebase"

from .agent import (
    DocumentationSyncValidator,
    DocumentationIssue,
    FreshnessReport,
    SemanticDriftReport,
    DriftSeverity,
    FreshnessStatus,
)

__all__ = [
    'DocumentationSyncValidator',
    'DocumentationIssue',
    'FreshnessReport',
    'SemanticDriftReport',
    'DriftSeverity',
    'FreshnessStatus',
]
