"""Top-level package for Codex session logging utilities.

This package also includes the Python Ingestion Pipeline components:
- ingest: Artifact ingestion and manifest handling
- analyze: Static and runtime analysis
- intent: LLM-based intent inference with provenance
- transform: Code transformation and patch generation
- verify: Behavior comparison and test generation
- cli: Command-line interface
"""

from ._version import __version__

__all__ = [
    "__version__",
    "ingest",
    "analyze",
    "intent",
    "transform",
    "verify",
    "cli",
]

# Exported modules or helpers may be added here in the future.
