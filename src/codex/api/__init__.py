"""RAG API Module"""

# Guard against missing optional dependency 'slowapi' so that importing this
# package does not crash in environments where slowapi is not installed.
try:
    from .rag_api import app
except ImportError:  # pragma: no cover — slowapi missing in lightweight envs
    app = None  # type: ignore[assignment]

__all__ = ["app"]
