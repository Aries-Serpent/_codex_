"""
Artifact Monitoring System - Core monitoring infrastructure.

This package provides automated monitoring of GitHub Actions workflows,
failure detection, pattern recognition, and issue management.

Components:
- artifact_monitor: Core monitoring engine
- issue_manager: GitHub Issue lifecycle management
- table_generator: Rich Markdown formatting utilities

Author: Artifact Monitor Agent
Version: 1.0.0
Created: 2026-01-22
"""

from .artifact_monitor import ArtifactMonitor, MonitorState
from .issue_manager import IssueManager
from .table_generator import TableGenerator

__all__ = [
    'ArtifactMonitor',
    'MonitorState',
    'IssueManager',
    'TableGenerator',
]

__version__ = '1.0.0'
