"""
Module: Weaviate Stub (S-vector)

Light mock for doc-generation. Does not connect to external service.
"""


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
        raise ImportError(
            "Weaviate backend not installed/enabled. "
            "Install extras (e.g., codex[vector]) and use real implementation."
        )
    
    def upsert(self, items):
        raise ImportError("Weaviate backend unavailable in stub mode.")
    
    def query(self, vector, top_k=5):
        raise ImportError("Weaviate backend unavailable in stub mode.")
