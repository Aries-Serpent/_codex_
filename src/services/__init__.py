"""Service orchestration entrypoints for Codex deployments.

This package groups service-layer adapters and runtimes. Modules under
``services.mcp`` and other subpackages provide transport-specific glue
for exposing Codex capabilities to external consumers.

The workflow module provides GitHub Actions workflow inventory and management.
The github module provides GitHub API client functionality.
"""

from __future__ import annotations

import logging
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_ROOT_SERVICES = _ROOT / "services"
if _ROOT_SERVICES.exists():
    __path__ = [str(Path(__file__).resolve().parent), str(_ROOT_SERVICES)]

# Import workflow services (lightweight, no external deps beyond PyYAML/Pydantic)
from .workflow import (
    WorkflowDependency,
    WorkflowInput,
    WorkflowInventory,
    WorkflowJob,
    WorkflowMetadata,
    WorkflowParser,
    WorkflowTrigger,
)

logger = logging.getLogger(__name__)

__all__: list[str] = [
    "WorkflowDependency",
    "WorkflowInput",
    "WorkflowInventory",
    "WorkflowJob",
    "WorkflowMetadata",
    "WorkflowParser",
    "WorkflowTrigger",
]

# Conditionally import GitHub client (requires httpx)
try:
    from .github import GitHubClient

    __all__.append("GitHubClient")
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: %s", error_type)
    logger.warning("ImportError: %s", error_type, exc_info=True)
    # httpx not installed, skip GitHub client
