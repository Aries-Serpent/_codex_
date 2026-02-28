"""
GitHub Guru Agent — Package

Production-ready GitHub repository intelligence agent.
Implements ASSESS → DELIBERATE → OPTIMIZE → ACT → REFLECT cycle.

SAFE_MODE=true: Read-only GitHub operations only.
OFFLINE_MODE=true: No external network calls.
"""
from __future__ import annotations

from .analyzers import IssueAnalyzer, PRAnalyzer, WorkflowAnalyzer
from .guru_adapter import GitHubGuruAdapter
from .hygiene import RepoHygiene
from .main import GitHubGuruAgent
from .triage import IssueTriage

__all__ = [
    "GitHubGuruAgent",
    "PRAnalyzer",
    "IssueAnalyzer",
    "WorkflowAnalyzer",
    "IssueTriage",
    "RepoHygiene",
    "GitHubGuruAdapter",
]

__version__ = "1.1.0"
