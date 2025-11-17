"""
Module: PGVector Stub (S-vector)

Light mock for doc-generation. Does not connect to external DB.
"""

_STUB_HINT = "Install extras (e.g., codex[vector]) to use the real implementation."


def _stub_error() -> ImportError:
    return ImportError("PGVector backend not installed/enabled. " + _STUB_HINT)


class PGVectorStore:
    """
    Light mock for doc-generation. Does not connect to external DB.

    Provides API-compatible stubs that raise informative errors
    when real backends are not installed.
    """

    def __init__(self, dsn: str = "", table: str = "embeddings"):
        self.dsn = dsn
        self.table = table

    def connect(self):
        raise _stub_error()

    def upsert(self, items):
        raise _stub_error()

    def query(self, vector, top_k=5):
        raise _stub_error()
