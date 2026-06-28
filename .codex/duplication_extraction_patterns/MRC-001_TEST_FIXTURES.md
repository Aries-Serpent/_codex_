# Pattern MRC-001: Test Fixture Boilerplate Consolidation

## Pattern Overview

**Pattern ID:** MRC-001  
**Category:** Tier 1b - Mid-Complexity Refactorings  
**Timeline:** Week 2 of Phase 6 Wave 2  
**LOC Reduction Target:** 480 lines  
**Status:** ✅ EXTRACTED

## Problem Statement

Test fixtures are repeatedly defined across multiple conftest.py files:
- Main conftest: 29 fixtures
- Edge case tests conftest: 13 fixtures
- Regression tests conftest: 9 fixtures
- Other modules: ~10 additional duplicates

Common patterns duplicated:
- Temporary directory/file fixtures
- Environment isolation fixtures
- Mock/config creation fixtures
- Database fixtures
- Mock credentials/authentication fixtures

## Solution

Created `src/codex/consolidation/test_fixtures.py` with:
- **FixtureFactory**: Base factory for reusable fixture patterns
- **DatabaseFixture**: Database-specific fixture utilities
- **MockFixture**: Mock configuration and credentials
- **AsyncFixture**: Async context manager fixtures
- **Pytest fixtures**: Reusable `@pytest.fixture` decorated functions

## Implementation Details

### Core Classes

```python
class FixtureFactory:
    """Base factory for creating reusable test fixtures."""
    - create_temp_dir(): Temporary directory fixture
    - create_temp_file(): Temporary file with content
    - create_isolated_env(): Clean environment dictionary

class DatabaseFixture:
    """Fixture utilities for database testing."""
    - create_test_db_path(): Generate test database paths
    - cleanup_test_db(): Clean up database files

class MockFixture:
    """Fixture utilities for mock/stub object setup."""
    - create_mock_config(): Mock configuration dictionary
    - create_mock_credentials(): Mock credentials for auth testing

class AsyncFixture:
    """Fixture utilities for async testing."""
    - create_async_context_manager(): Reusable async context manager
```

### Pytest Fixtures

- `temp_dir`: Temporary directory for test use
- `temp_file`: Temporary file with optional content
- `isolated_env`: Clean environment dictionary
- `mock_config`: Mock configuration object
- `mock_credentials`: Mock credentials for testing
- `test_db_path`: Test database path with cleanup

## Migration Path

### Before (Duplicated)
```python
# tests/conftest.py
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

# tests/edge_case_boundary_tests/conftest.py
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

# tests/regression/conftest.py
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
```

### After (Consolidated)
```python
# tests/conftest.py (or any test module)
from src.codex.consolidation.test_fixtures import temp_dir

# Direct usage in tests
def test_example(temp_dir):
    # Use consolidated fixture
    (temp_dir / "test_file.txt").write_text("content")
    assert (temp_dir / "test_file.txt").exists()
```

## Metrics

- **Lines Created:** 172 LOC (new consolidation module)
- **Lines to Remove:** 480 LOC (from distributed conftest.py files)
- **Net Reduction:** 308 LOC
- **Exports:** 14 (classes, functions, pytest fixtures)
- **Module Dependencies:** 3 (pathlib, tempfile, pytest)

## Coverage

- ✅ Temporary file/directory fixtures
- ✅ Environment isolation
- ✅ Mock configuration creation
- ✅ Mock credentials creation
- ✅ Database fixture utilities
- ✅ Async context manager templates

## Testing

All new utilities are tested via:
- Import validation (all 14 exports accessible)
- Fixture functionality (pytest fixtures work correctly)
- Factory patterns (all factory methods return expected types)
- Type hints (full type coverage for IDE support)

## Consumers to Update

1. `tests/conftest.py` - Import and use `temp_dir`, `temp_file`, `mock_config`
2. `tests/edge_case_boundary_tests/conftest.py` - Replace duplicate fixtures
3. `tests/regression/conftest.py` - Import and use consolidation fixtures
4. Individual test modules using duplicated fixtures

## Backward Compatibility

✅ All fixtures maintain the same signatures and behavior as original implementations.  
✅ No breaking changes to test code.  
✅ Gradual migration possible (old and new can coexist).

## Rollback Plan

If issues arise:
1. Keep original fixtures in place alongside consolidated versions
2. Test with new consolidation fixtures first
3. Only remove originals after validation passes

## Related Patterns

- **MRC-002** (Config parsing): Works alongside fixture factories
- **MRC-003** (Mocks): Uses MockFixture for test object creation
- **LRC-002** (Validation decorators): Can decorate fixture factories

## Notes

- Async fixture factory support added for future use (MRC-005 related)
- Database fixtures scoped for SQLite/PostgreSQL support
- Credentials fixtures support common auth patterns (OAuth, JWT, API keys)
