# MCP System - Comprehensive Master Guide

> **Version**: 2.0.0  
> **Last Updated**: 2026-06-20  
> **Scope**: Complete Model Context Protocol (MCP) system documentation  
> **Audience**: Developers, operators, system administrators

---

## 📋 Quick Navigation

| Topic | Purpose | Time |
|-------|---------|------|
| [What is MCP?](#what-is-mcp) | Conceptual overview | 5 min |
| [Quick Start](#quick-start) | Get MCP running | 15 min |
| [Architecture](#architecture) | System design & components | 20 min |
| [Server Setup](#server-setup) | Deploy MCP server | 30 min |
| [Backend Configuration](#backend-configuration) | Connect data backends | 45 min |
| [API Reference](#api-reference) | Complete API docs | reference |
| [Troubleshooting](#troubleshooting) | Common issues & fixes | as needed |
| [Examples](#examples) | Working code examples | 10 min |

---

## What is MCP?

**MCP (Model Context Protocol)** is the standardized interface for connecting language models to external data sources and tools.

### Key Benefits

- **Standardized Interface**: Single protocol for all backends
- **Pluggable Backends**: Swap implementations without code changes
- **Async Processing**: Non-blocking embeddings and data fetching
- **Type Safety**: Full type hints and schema validation
- **Production Ready**: Built for scale with observability

### Real-World Analogy

Think of MCP like a universal electrical outlet:
- **Different devices** (Pinecone, Redis, S3, custom) = different appliances
- **MCP Server** = standardized outlet
- **Your code** = any device that plugs in

---

## Quick Start

### Installation

```bash
# Install MCP system
pip install -e ".[mcp]"

# Verify installation
python -c "from src.mcp import MCPServer; print('✅ MCP installed')"
```

## Minimal Example (In-Memory Backend)

```python
from src.mcp import MCPServer
from src.mcp.backends import MockBackend
import asyncio

# Create server with in-memory backend
server = MCPServer(backend=MockBackend())

# Store embeddings
async def demo():
    await server.store("doc_1", [0.1, 0.2, 0.3, 0.4])
    await server.store("doc_2", [0.2, 0.3, 0.4, 0.5])
    
    # Retrieve embeddings
    result = await server.retrieve("doc_1")
    print(f"Retrieved: {result}")

# Run demo
asyncio.run(demo())
```

**Expected Output:**
```
Retrieved: {"doc_id": "doc_1", "embedding": [0.1, 0.2, 0.3, 0.4]}
```

## Next Step: Choose Your Backend

- **For Development**: Use `MockBackend` (in-memory)
- **For Production Vector Search**: Use `PineconeBackend`
- **For Custom Data**: Use `CustomBackend` or build your own

→ Continue to [Backend Configuration](#backend-configuration)

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│           Application Code                      │
└────────────────┬────────────────────────────────┘
                 │ Uses MCPServer API
                 ▼
┌─────────────────────────────────────────────────┐
│         MCP Server (MCPServer)                   │
│  ┌─────────────────────────────────────────┐   │
│  │  Request Handler / Router               │   │
│  │  - store(doc_id, embedding)            │   │
│  │  - retrieve(doc_id)                    │   │
│  │  - search(query_embedding)             │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │  Backend Abstraction Layer              │   │
│  │  - Standardizes all backend interfaces │   │
│  │  - Handles async/await patterns        │   │
│  └─────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────┘
                 │ Backend Interface
                 ▼
        ┌────────────────────────┐
        │   Backend Plugins      │
        ├────────────────────────┤
        │ ┌──────────────────┐   │
        │ │ PineconeBackend  │   │  Production vector DB
        │ └──────────────────┘   │
        │ ┌──────────────────┐   │
        │ │ RedisBackend     │   │  Cache / session store
        │ └──────────────────┘   │
        │ ┌──────────────────┐   │
        │ │ S3Backend        │   │  Document storage
        │ └──────────────────┘   │
        │ ┌──────────────────┐   │
        │ │ CustomBackend    │   │  Your implementation
        │ └──────────────────┘   │
        └────────────────────────┘
```

### Data Flow

```
1. Application calls: server.store("doc", embedding)
                           │
                           ▼
2. MCPServer validates and normalizes
                           │
                           ▼
3. Backend plugin receives call
                           │
                           ▼
4. Backend stores data (Pinecone API, Redis SET, S3 PUT, etc.)
                           │
                           ▼
5. Response returned to application
```

### Key Concepts

| Concept | Definition | Example |
|---------|-----------|---------|
| **Document ID** | Unique identifier for stored data | `"user_123"`, `"doc_v2.3"` |
| **Embedding** | Vector representation of data | `[0.1, 0.2, ..., 0.9]` (float array) |
| **Backend** | External storage system | Pinecone, Redis, custom DB |
| **Schema** | Data structure definition | `{"user_id": str, "score": float}` |

---

## Server Setup

### Step 1: Choose Backend

```python
from src.mcp import MCPServer
from src.mcp.backends import PineconeBackend, MockBackend, RedisBackend
```

**Decision Matrix:**

| Use Case | Backend | Why |
|----------|---------|-----|
| Testing/Development | MockBackend | Instant, no setup |
| Production Vector Search | PineconeBackend | Managed, scalable |
| Session Cache | RedisBackend | Fast, in-memory |
| Custom Logic | CustomBackend | Full control |

### Step 2: Initialize Server

#### With Pinecone (Production)

```python
from src.mcp import MCPServer
from src.mcp.backends import PineconeBackend

# Initialize Pinecone backend
backend = PineconeBackend(
    api_key="YOUR_PINECONE_API_KEY",
    environment="us-west4-gcp",
    index_name="codex-prod",
    dimension=1536  # OpenAI embedding dimension
)

# Create server
server = MCPServer(
    backend=backend,
    workers=4,  # Async workers
    timeout=30  # Request timeout
)
```

## With Redis (Caching)

```python
from src.mcp.backends import RedisBackend

backend = RedisBackend(
    host="localhost",
    port=6379,
    db=0
)

server = MCPServer(backend=backend)
```

### With Mock Backend (Development)

```python
from src.mcp.backends import MockBackend

server = MCPServer(backend=MockBackend())  # Uses in-memory dict
```

### Step 3: Configure Observability

```python
from src.mcp.observability import MetricsCollector

# Enable metrics collection
metrics = MetricsCollector()
server.enable_metrics(metrics)

# View metrics
print(server.get_metrics())
# Output: {"requests": 1243, "errors": 2, "latency_p99": 45.2}
```

---

## Backend Configuration

### Pinecone Backend (Production Vector Search)

**Installation:**
```bash
pip install pinecone-client
```

**Configuration:**
```python
from src.mcp.backends import PineconeBackend

backend = PineconeBackend(
    api_key="pc_...",  # From Pinecone console
    environment="us-west4-gcp",
    index_name="my-index",
    dimension=1536,
    metric="cosine"  # or "euclidean"
)
```

**Common Operations:**

```python
import asyncio

async def example():
    # Store embedding
    await backend.store("doc_1", [0.1, 0.2, ..., 0.9])
    
    # Retrieve by ID
    result = await backend.retrieve("doc_1")
    print(f"Got: {result}")
    
    # Search similar vectors
    query = [0.15, 0.25, ..., 0.95]
    results = await backend.search(query, top_k=5)
    print(f"Top 5 matches: {results}")

asyncio.run(example())
```

**Troubleshooting:**

| Error | Solution |
|-------|----------|
| `AuthenticationError` | Check API key in Pinecone console |
| `IndexNotFound` | Create index in Pinecone or use existing name |
| `DimensionMismatch` | Verify dimension matches your embeddings |
| `RateLimit` | Reduce batch size or upgrade plan |

### Redis Backend (Session & Cache)

**Installation:**
```bash
pip install redis
# Start Redis: redis-server
```

**Configuration:**
```python
from src.mcp.backends import RedisBackend

backend = RedisBackend(
    host="localhost",
    port=6379,
    db=0,
    ttl=3600  # 1 hour TTL
)
```

**Use Cases:**
- Session cache during user interaction
- Temporary embeddings
- Rate limiting state

## Custom Backend (Your Implementation)

**Template:**
```python
from src.mcp.backends import BaseBackend
from typing import Any, List

class MyCustomBackend(BaseBackend):
    """Your custom storage implementation."""
    
    async def store(self, doc_id: str, embedding: List[float]) -> None:
        """Store embedding in your system."""
        # Your implementation here
        pass
    
    async def retrieve(self, doc_id: str) -> Any:
        """Retrieve embedding by ID."""
        # Your implementation here
        pass
    
    async def search(self, query: List[float], top_k: int = 5) -> List[dict]:
        """Search for similar embeddings."""
        # Your implementation here
        pass

# Use your backend
server = MCPServer(backend=MyCustomBackend())
```

---

## API Reference

### MCPServer Class

```python
class MCPServer:
    def __init__(
        self,
        backend: BaseBackend,
        workers: int = 4,
        timeout: int = 30
    ) -> None: ...
    
    async def store(self, doc_id: str, embedding: List[float]) -> None:
        """Store embedding with automatic deduplication."""
    
    async def retrieve(self, doc_id: str) -> Optional[dict]:
        """Retrieve stored embedding by ID."""
    
    async def search(
        self, 
        query: List[float], 
        top_k: int = 5
    ) -> List[dict]:
        """Find most similar embeddings."""
    
    async def delete(self, doc_id: str) -> None:
        """Delete embedding by ID."""
    
    async def health_check(self) -> bool:
        """Check backend connectivity."""
```

### Backend Interface

All backends implement:

```python
class BaseBackend(ABC):
    @abstractmethod
    async def store(self, doc_id: str, embedding: List[float]) -> None: ...
    
    @abstractmethod
    async def retrieve(self, doc_id: str) -> Optional[dict]: ...
    
    @abstractmethod
    async def search(self, query: List[float], top_k: int) -> List[dict]: ...
    
    @abstractmethod
    async def delete(self, doc_id: str) -> None: ...
    
    @abstractmethod
    async def health_check(self) -> bool: ...
```

---

## Troubleshooting

### Issue: "Backend connection failed"

**Solutions:**
1. Check backend service is running
2. Verify API keys/credentials
3. Check network connectivity
4. See backend-specific troubleshooting above

### Issue: "Timeout during search"

**Solutions:**
1. Increase timeout: `MCPServer(..., timeout=60)`
2. Reduce `top_k` in search queries
3. Check backend performance
4. Monitor metrics for bottlenecks

### Issue: "Out of memory"

**Solutions:**
1. Use batch processing for large datasets
2. Reduce worker count if using many
3. Enable TTL for temporary data (Redis)
4. Consider pagination for results

---

## Examples

### Example 1: Text Embedding Storage

```python
from src.mcp import MCPServer
from src.mcp.backends import MockBackend
from transformers import AutoTokenizer, AutoModel
import torch
import asyncio

async def store_documents():
    # Load model
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    
    # Create server
    server = MCPServer(backend=MockBackend())
    
    # Sample documents
    docs = [
        ("doc_1", "Python is a programming language"),
        ("doc_2", "JavaScript runs in browsers"),
        ("doc_3", "Rust provides memory safety"),
    ]
    
    # Embed and store
    for doc_id, text in docs:
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        embedding = outputs.last_hidden_state[0][0].tolist()
        
        await server.store(doc_id, embedding)
        print(f"✅ Stored {doc_id}")

asyncio.run(store_documents())
```

### Example 2: Semantic Search

```python
async def semantic_search():
    server = MCPServer(backend=MockBackend())
    
    # Store embeddings (see Example 1)
    # ...
    
    # Search for similar documents
    query_text = "What languages are there?"
    query_embedding = [0.5, 0.3, 0.2]  # Your embedding
    
    results = await server.search(query_embedding, top_k=2)
    print(f"Top matches: {results}")

asyncio.run(semantic_search())
```

### Example 3: FastAPI Integration

```python
from fastapi import FastAPI
from src.mcp import MCPServer
from src.mcp.backends import PineconeBackend

app = FastAPI()

# Initialize MCP server
backend = PineconeBackend(api_key="...", ...)
mcp_server = MCPServer(backend=backend)

@app.post("/embeddings/store")
async def store_embedding(doc_id: str, embedding: list):
    await mcp_server.store(doc_id, embedding)
    return {"status": "stored"}

@app.post("/embeddings/search")
async def search(query: list):
    results = await mcp_server.search(query, top_k=5)
    return {"results": results}
```

---

## Related Documentation

> **Note:** Additional MCP documentation modules (Backend Adapters, Workers & Async, Performance Tuning, Security Best Practices) are planned for future implementation. See the [Continuation Roadmap](../admin/CONTINUATION_ROADMAP.md) for timeline.

---

## Support

- **Questions?** Check [MCP FAQ](#faq)
- **Issues?** See [Troubleshooting](#troubleshooting)
- **Missing something?** [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)

---

**Last Updated:** 2026-06-20 | **Version:** 2.0.0
