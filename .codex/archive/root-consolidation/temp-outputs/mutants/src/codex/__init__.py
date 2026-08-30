"""Top-level package for Codex session logging utilities.

This package also includes the Python Ingestion Pipeline components:
- ingest: Artifact ingestion and manifest handling
- analyze: Static and runtime analysis
- intent: LLM-based intent inference with provenance
- transform: Code transformation and patch generation
- verify: Behavior comparison and test generation
- cli: Command-line interface
"""

__all__ = [
    "__version__",
    "ingest",
    "analyze",
    "intent",
    "transform",
    "verify",
    "cli",
]

_SUBMODULES = {
    "analyze",
    "archive",
    "cli",
    "github",
    "ingest",
    "intent",
    "transform",
    "verify",
}


# Lazy-load __version__ to avoid cyclic import
def __getattr__(name: str) -> object:
    if name == "__version__":
        from ._version import __version__

        return __version__
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f".{name}", __name__)
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
