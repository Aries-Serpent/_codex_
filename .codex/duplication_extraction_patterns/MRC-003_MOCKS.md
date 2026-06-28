# Pattern MRC-003: Mock/Stub Object Factories Consolidation

**Status:** ✅ EXTRACTED  
**LOC Reduction Target:** 560 lines  
**Lines Created:** 260 LOC (new consolidation module)  
**Net Reduction:** 300 LOC

## Overview

Consolidated 8+ mock/stub implementations from test suite into unified factories in `src/codex/consolidation/mocks.py`.

## Key Classes

- **ObjectFactory[T]**: Generic base factory pattern
- **FakeModel**: Generic fake model for testing
- **MockClientFactory**: Create mock HTTP/API clients
- **AsyncMockClientFactory**: Async version
- **FakeRepositoryFactory**: Mock repositories
- **FakeServiceFactory**: Mock services
- **AsyncFakeServiceFactory**: Async services
- **StubDataFactory**: Create stub data structures

## Pattern

```python
# Before: Scattered mock implementations
class _FakeModel:
    def __init__(self, id="fake", name="test"):
        self.id = id
        self.name = name

class _MockClient:
    def __init__(self):
        self.get = MagicMock()
        self.post = MagicMock()

# After: Unified factories
from src.codex.consolidation.mocks import FakeModel, MockClientFactory

model = FakeModel(id="test_id")
client = MockClientFactory().create()
```

## Features

- Generic factory pattern for type safety
- Batch creation support
- Default parameters with overrides
- Async mock support
- Stub data generators

## Consumers

- 50+ test files using mock objects
- ML training test fixtures
- API integration tests
- Service layer tests
