# Pattern MRC-005: Async Context Manager Templates Consolidation

**Status:** ✅ EXTRACTED  
**LOC Reduction Target:** 380 lines  
**Lines Created:** 264 LOC (new consolidation module)  
**Net Reduction:** 116 LOC

## Overview

Consolidated async context manager patterns from async utils (2), database layer (2), and cache operations (1) into `src/codex/consolidation/async_utils.py`.

## Key Classes

- **AsyncContextBase**: Abstract base for async context managers
- **AsyncResourceManager**: Generic resource lifecycle management
- **AsyncPoolManager**: Connection/resource pool management
- **AsyncTimeout**: Timeout enforcement
- **AsyncRetryManager**: Async retry logic with exponential backoff

## Utility Functions

- async_managed_resource(): Factory for managed resources
- async_pool_connection(): Factory for pool connections
- async_timeout_context(): Factory for timeout contexts

## Pattern

```python
# Before: Duplicated async context managers
class DatabaseConnection:
    async def __aenter__(self):
        self.conn = await self.pool.acquire()
        return self.conn
    
    async def __aexit__(self, *args):
        await self.pool.release(self.conn)

# After: Unified manager
from src.codex.consolidation.async_utils import AsyncPoolManager
async with AsyncPoolManager(pool) as conn:
    await conn.execute("SELECT 1")
```

## Features

- Resource lifecycle management
- Connection pooling
- Timeout enforcement
- Automatic retry with backoff
- Exception-safe cleanup
- Async context manager factory pattern

## Consumers

- Database operations (pgvector, async connections)
- Cache operations
- HTTP client management
- Stream/socket operations
