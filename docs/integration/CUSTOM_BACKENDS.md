# Custom Backends Integration Guide

> **Version**: 2.0.0  
> **Last Updated**: 2026-06-20  
> **Scope**: Building custom backends for MCP system  
> **Audience**: Backend developers, platform engineers

---

## Quick Start: Create Your First Backend

### Step 1: Implement Base Interface

```python
from src.mcp.backends import BaseBackend
from typing import List, Optional

class MyBackend(BaseBackend):
    def __init__(self, config: dict):
        self.config = config
        self.storage = {}

    async def store(self, doc_id: str, embedding: List[float]) -> None:
        self.storage[doc_id] = embedding

    async def retrieve(self, doc_id: str) -> Optional[dict]:
        if doc_id in self.storage:
            return {"doc_id": doc_id, "embedding": self.storage[doc_id]}
        return None

    async def search(self, query: List[float], top_k: int = 5):
        results = []
        for doc_id, emb in self.storage.items():
            import numpy as np
            sim = np.dot(query, emb) / (np.linalg.norm(query) * np.linalg.norm(emb) + 1e-10)
            results.append({"doc_id": doc_id, "similarity": float(sim)})
        return sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]

    async def delete(self, doc_id: str) -> None:
        if doc_id in self.storage:
            del self.storage[doc_id]

    async def health_check(self) -> bool:
        return True
```

### Step 2: Use Your Backend

```python
from src.mcp import MCPServer

backend = MyBackend(config={})
server = MCPServer(backend=backend)

import asyncio

async def demo():
    await server.store("doc_1", [0.1, 0.2, 0.3])
    results = await server.search([0.1, 0.2, 0.3], top_k=1)
    print(f"Results: {results}")

asyncio.run(demo())
```

---

## Backend Interface

All custom backends must implement `BaseBackend`:

```python
class BaseBackend(ABC):
    @abstractmethod
    async def store(self, doc_id: str, embedding: List[float]) -> None: ...

    @abstractmethod
    async def retrieve(self, doc_id: str) -> Optional[dict]: ...

    @abstractmethod
    async def search(self, query: List[float], top_k: int = 5) -> List[dict]: ...

    @abstractmethod
    async def delete(self, doc_id: str) -> None: ...

    @abstractmethod
    async def health_check(self) -> bool: ...
```

---

## Production Examples

### SQL Backend

```python
class SQLBackend(BaseBackend):
    def __init__(self, db_url: str):
        self.db_url = db_url
```

### Redis Backend

```python
class RedisBackend(BaseBackend):
    def __init__(self, host: str = "localhost"):
        self.host = host
```

---

## Testing

```python
@pytest.mark.asyncio
async def test_backend():
    backend = MyBackend(config={})
    await backend.store("doc_1", [0.1, 0.2, 0.3])
    result = await backend.retrieve("doc_1")
    assert result["doc_id"] == "doc_1"
```

---

**Last Updated:** 2026-06-20 | **Version:** 2.0.0
