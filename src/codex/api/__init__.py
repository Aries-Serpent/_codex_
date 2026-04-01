"""RAG API Module"""

# Guard against missing optional dependency 'slowapi' so that importing this
# package does not crash in environments where slowapi is not installed.
try:
    from .rag_api import app
except ImportError as exc:  # pragma: no cover — slowapi missing in lightweight envs
    if getattr(exc, "name", None) == "slowapi":
        app = None
    else:
        raise

__all__ = ["app"]
