"""Search provider plugin architecture for codex."""

from .providers import (
    ExternalWebSearch,
    InternalRepoSearch,
    SearchProvider,
    SearchRegistry,
)

__all__ = [
    "SearchProvider",
    "InternalRepoSearch",
    "ExternalWebSearch",
    "SearchRegistry",
]
