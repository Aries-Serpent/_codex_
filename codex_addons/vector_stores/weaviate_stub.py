"""
Module: Weaviate Stub (S-vector)

Light mock for doc-generation. Does not connect to external service.
"""

_STUB_HINT = "Install extras (e.g., codex[vector]) to use the real implementation."


def _stub_error() -> ImportError:
    return ImportError("Weaviate backend not installed/enabled. " + _STUB_HINT)


class WeaviateStore:
    """
    Light mock for doc-generation. Does not connect to external service.

    Provides API-compatible stubs that raise informative errors
    when real backends are not installed.
    """

    def __init__(self, url: str = "http://localhost:8080", api_key: str = ""):
        self.url = url
        self.api_key = api_key

    def connect(self):
        raise _stub_error()

    def upsert(self, items):
        raise _stub_error()

    def query(self, vector, top_k=5):
        raise _stub_error()
