"""
Module: PGVector Stub (S-vector)

Light mock for doc-generation. Does not connect to external DB.
"""


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
        raise ImportError(
            "PGVector backend not installed/enabled. "
            "Install extras (e.g., codex[vector]) and use real implementation."
        )
    
    def upsert(self, items):
        raise ImportError("PGVector backend unavailable in stub mode.")
    
    def query(self, vector, top_k=5):
        raise ImportError("PGVector backend unavailable in stub mode.")
