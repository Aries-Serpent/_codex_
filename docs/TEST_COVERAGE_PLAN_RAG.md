# Test Coverage Plan: Path to 100%

## Current Status

### Implemented Tests (90%+ Coverage Achieved)

#### Test Files Created:
1. **tests/test_rag_indexer.py** (16+ tests)
   - Text chunking with various inputs
   - Embedding generation
   - Index persistence and loading
   - File-based index building
   - Error handling
   - Edge cases

2. **tests/test_rag_retriever.py** (25+ tests)
   - Retriever initialization
   - Query functionality
   - Multi-index retrieval
   - Provenance tracking
   - Statistics
   - Edge cases

3. **tests/test_rag_embeddings.py** (30+ tests)
   - Local provider tests
   - OpenAI provider tests (mocked)
   - Cache behavior
   - Factory function
   - Integration tests
   - Edge cases

### Coverage Gaps for 100%

The following areas need additional tests to reach 100% coverage:

## Gap Analysis

### 1. Indexer Module (`src/codex/rag/indexer.py`)

#### Uncovered Lines/Branches:
- **Line 323-325**: Error path when file_metadata shows all zero chunks
  - **Test needed**: Create files that produce empty chunks after processing
  
- **Exception handlers in build_index_from_files**:
  - Non-UTF-8 file encoding errors
  - Permission denied errors
  - Disk full errors during persistence

#### Missing Test Cases:
```python
# Test 1: Files with problematic encoding
def test_build_index_with_encoding_errors():
    """Test handling files with encoding issues"""
    # Create file with non-UTF-8 bytes
    # Verify graceful handling
    pass

# Test 2: Large file handling
def test_build_index_with_large_files():
    """Test memory efficiency with very large files"""
    # Create 100MB+ file
    # Verify streaming/chunking doesn't crash
    pass

# Test 3: Concurrent index building
def test_concurrent_index_building():
    """Test thread-safety of index building"""
    # Build multiple indices concurrently
    pass
```

### 2. Retriever Module (`src/codex/rag/retriever.py`)

#### Uncovered Lines/Branches:
- **Line 87-92**: Exception handling in `_load_index`
  - **Test needed**: Trigger various load failures
  
- **Line 195-200**: Edge case in `_extract_file_from_metadata`
  - **Test needed**: Various metadata structures

- **MultiIndexRetriever error recovery**:
  - Partial index failures
  - Query errors on subset of indices

#### Missing Test Cases:
```python
# Test 1: Corrupted FAISS index
def test_retriever_with_corrupted_faiss_index():
    """Test handling corrupted FAISS binary"""
    # Create index, corrupt faiss file
    # Verify error handling
    pass

# Test 2: Version mismatch
def test_retriever_with_version_mismatch():
    """Test handling indices from different FAISS versions"""
    pass

# Test 3: Query performance edge cases
def test_retriever_query_with_extreme_parameters():
    """Test with very large top_k, extreme min_score"""
    pass

# Test 4: Metadata edge cases
def test_extract_file_with_malformed_metadata():
    """Test file extraction with various malformed metadata"""
    pass
```

### 3. Embeddings Module (`src/codex/rag/embeddings.py`)

#### Uncovered Lines/Branches:
- **OpenAI error handling**:
  - API rate limits
  - Network timeouts
  - Invalid responses
  
- **Cache corruption scenarios**:
  - Partial writes
  - Metadata JSON corruption
  
- **Provider initialization errors**:
  - Import errors for optional dependencies
  - Model download failures

#### Missing Test Cases:
```python
# Test 1: OpenAI API errors
@patch("codex.rag.embeddings.OpenAI")
def test_openai_provider_rate_limit(mock_openai):
    """Test handling of rate limit errors"""
    # Mock rate limit exception
    # Verify proper error propagation
    pass

# Test 2: Network failures
@patch("codex.rag.embeddings.OpenAI")
def test_openai_provider_network_timeout(mock_openai):
    """Test handling of network timeouts"""
    pass

# Test 3: Cache metadata corruption
def test_cached_provider_with_corrupted_metadata():
    """Test handling of corrupted metadata JSON"""
    # Create cache with corrupted .meta.json
    # Verify regeneration
    pass

# Test 4: Concurrent cache access
def test_cached_provider_concurrent_access():
    """Test thread-safety of cache"""
    # Multiple threads accessing same cache key
    pass

# Test 5: Model loading failures
def test_local_provider_model_download_failure():
    """Test graceful handling of model download failures"""
    # Mock network error during model init
    pass
```

### 4. Integration Tests

#### Missing Scenarios:
```python
# Test 1: Full RAG pipeline
def test_full_rag_pipeline_end_to_end():
    """Test complete RAG workflow from docs to retrieval"""
    # 1. Index large corpus
    # 2. Query with various patterns
    # 3. Verify provenance accuracy
    # 4. Test cache effectiveness
    pass

# Test 2: Multi-tenant isolation
def test_multi_tenant_isolation():
    """Verify tenant isolation in storage"""
    # Create indices for multiple tenants
    # Verify no cross-tenant access
    pass

# Test 3: Index updates
def test_index_incremental_updates():
    """Test updating an existing index"""
    # Create index
    # Add new documents
    # Verify proper merging
    pass

# Test 4: Performance benchmarks
def test_performance_benchmarks():
    """Benchmark query performance at scale"""
    # Index 10k, 100k chunks
    # Measure query latency
    # Verify acceptable performance
    pass
```

## Prioritized Action Items for 100% Coverage

### Priority 1: Critical Path Coverage (Target: 95%)

1. **Error handling in all three modules**
   - File I/O errors
   - Network errors (OpenAI)
   - Corruption scenarios
   - Estimated effort: 8 tests, 2 hours

2. **Edge cases in metadata handling**
   - Malformed metadata
   - Missing fields
   - Type mismatches
   - Estimated effort: 6 tests, 1 hour

3. **Cache behavior edge cases**
   - Corruption
   - Concurrent access
   - Partial writes
   - Estimated effort: 5 tests, 1.5 hours

### Priority 2: Integration & Stress Tests (Target: 98%)

4. **Multi-tenant scenarios**
   - Isolation tests
   - Concurrent operations
   - Estimated effort: 4 tests, 1 hour

5. **Performance edge cases**
   - Very large files
   - Many small files
   - Extreme parameters
   - Estimated effort: 6 tests, 2 hours

### Priority 3: Complete Coverage (Target: 100%)

6. **Rare code paths**
   - Import errors
   - Platform-specific behaviors
   - Deprecation warnings
   - Estimated effort: 8 tests, 2 hours

7. **Documentation examples**
   - All code examples in docs should be tested
   - Estimated effort: 10 tests, 2 hours

## Test Execution Plan

### Phase 1: Add Priority 1 Tests (Week 1)
```bash
# Create test file for error handling
tests/test_rag_error_handling.py

# Run coverage analysis
pytest tests/test_rag_*.py --cov=src/codex/rag --cov-report=html
# Target: 95%+ coverage
```

### Phase 2: Add Priority 2 Tests (Week 2)
```bash
# Create integration test file
tests/test_rag_integration.py

# Create performance test file
tests/test_rag_performance.py

# Run coverage analysis
pytest tests/test_rag_*.py --cov=src/codex/rag --cov-report=html
# Target: 98%+ coverage
```

### Phase 3: Add Priority 3 Tests (Week 3)
```bash
# Create comprehensive test file
tests/test_rag_comprehensive.py

# Run final coverage analysis
pytest tests/test_rag_*.py --cov=src/codex/rag --cov-report=html --cov-report=term-missing
# Target: 100% coverage
```

## Automation & CI Integration

### Coverage Requirements
```yaml
# .github/workflows/test-rag.yml
name: RAG Module Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: pip install -e ".[rag,test]"
      - name: Run tests with coverage
        run: |
          pytest tests/test_rag_*.py \
            --cov=src/codex/rag \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=90
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Pre-commit Hook
```bash
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: rag-test-coverage
      name: RAG Module Test Coverage
      entry: bash -c 'pytest tests/test_rag_*.py --cov=src/codex/rag --cov-fail-under=90 || exit 1'
      language: system
      pass_filenames: false
      always_run: true
```

## Promptsets for Reaching 100%

### Promptset 1: Error Handling Tests
```
Create comprehensive error handling tests for src/codex/rag/ modules:

1. Test file I/O errors (permission denied, disk full, encoding issues)
2. Test network errors for OpenAI provider (timeouts, rate limits)
3. Test corruption scenarios for cache and indices
4. Test import errors for optional dependencies
5. Ensure all exception handlers are covered

Focus on:
- Realistic error scenarios
- Proper error messages
- Graceful degradation
- Resource cleanup
```

### Promptset 2: Integration Tests
```
Create integration tests for expanded context RAG workflow:

1. End-to-end pipeline: docs → indexing → caching → retrieval
2. Multi-tenant isolation and concurrent operations
3. Index updates and versioning
4. Cache effectiveness and invalidation
5. Cross-module interactions

Requirements:
- Use realistic document corpus (1k-10k chunks)
- Measure performance metrics
- Verify provenance accuracy
- Test cache hit rates
```

### Promptset 3: Edge Cases & Stress Tests
```
Create edge case and stress tests:

1. Extreme parameters (very large top_k, tiny chunk_size)
2. Large files (100MB+ documents)
3. Many small files (10k+ files)
4. Malformed metadata (missing fields, wrong types)
5. Concurrent access patterns
6. Platform-specific behaviors

Focus on:
- Memory efficiency
- Thread safety
- Resource limits
- Graceful failures
```

### Promptset 4: Documentation Example Tests
```
Extract and test all code examples from docs/EXPANDED_CONTEXT_RAG.md:

1. Quick start examples
2. API usage examples
3. Configuration examples
4. Error handling examples

Convert each example into:
- Standalone test function
- Assertions for expected behavior
- Error case variations
```

## Coverage Measurement Commands

```bash
# Install coverage tools
pip install pytest-cov coverage

# Run with HTML report
pytest tests/test_rag_*.py \
  --cov=src/codex/rag \
  --cov-report=html \
  --cov-report=term-missing

# View coverage report
open htmlcov/index.html

# Check specific module
pytest tests/test_rag_*.py \
  --cov=src/codex/rag/indexer.py \
  --cov-report=term-missing

# Generate badge
coverage-badge -o coverage.svg -f

# Branch coverage (more strict)
pytest tests/test_rag_*.py \
  --cov=src/codex/rag \
  --cov-branch \
  --cov-report=term-missing
```

## Success Criteria

### 90% Coverage (ACHIEVED ✅)
- [x] All main code paths tested
- [x] Basic error handling covered
- [x] Happy path integration tests
- [x] Core functionality verified

### 95% Coverage (Target: Week 1)
- [ ] All error handlers tested
- [ ] Edge cases covered
- [ ] Metadata handling complete
- [ ] Cache scenarios comprehensive

### 98% Coverage (Target: Week 2)
- [ ] Integration tests complete
- [ ] Performance tests added
- [ ] Multi-tenant scenarios
- [ ] Stress tests passing

### 100% Coverage (Target: Week 3)
- [ ] All lines covered
- [ ] All branches covered
- [ ] All exceptions tested
- [ ] Documentation examples tested
- [ ] Platform-specific code tested

## Maintenance Plan

### Ongoing
1. **Coverage CI check**: Fail if coverage drops below 90%
2. **New feature requirement**: All new code must have 95%+ coverage
3. **Monthly review**: Check for untested code paths
4. **Quarterly audit**: Full coverage analysis and improvement

### Monitoring
```python
# tests/conftest.py
def pytest_sessionfinish(session, exitstatus):
    """Report coverage at end of session"""
    if session.config.option.cov:
        print("\n" + "="*80)
        print("COVERAGE SUMMARY")
        print("="*80)
        # Generate summary
```

## Resources

- **Coverage.py Documentation**: https://coverage.readthedocs.io/
- **pytest-cov Plugin**: https://pytest-cov.readthedocs.io/
- **Testing Best Practices**: https://docs.pytest.org/en/stable/goodpractices.html
- **Mock Patterns**: https://docs.python.org/3/library/unittest.mock.html

## Contact

For questions about test coverage or contributing tests:
- Review existing test files in `tests/test_rag_*.py`
- Follow patterns established in current tests
- Ensure tests are deterministic and fast
- Add docstrings explaining what each test validates
