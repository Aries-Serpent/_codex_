"""Search provider plugin architecture for codex."""

from .providers import (
    ExternalWebSearch,
    InternalRepoSearch,
    SearchProvider,
    SearchRegistry,
)

__all__ = [
    "ExternalWebSearch",
    "InternalRepoSearch",
    "SearchProvider",
    "SearchRegistry",
]
