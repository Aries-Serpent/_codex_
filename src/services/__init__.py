"""Service orchestration entrypoints for Codex deployments.

This package groups service-layer adapters and runtimes. Modules under
``services.mcp`` and other subpackages provide transport-specific glue
for exposing Codex capabilities to external consumers.

The workflow module provides GitHub Actions workflow inventory and management.
The github module provides GitHub API client functionality.
"""

# Import workflow services (lightweight, no external deps beyond PyYAML/Pydantic)
import logging

from .workflow import WorkflowInventory, WorkflowParser

logger = logging.getLogger(__name__)

__all__: list[str] = [
    "WorkflowInventory",
    "WorkflowParser",
]

# Conditionally import GitHub client (requires httpx)
try:
    from .github import GitHubClient

    __all__.append("GitHubClient")
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    # httpx not installed, skip GitHub client
