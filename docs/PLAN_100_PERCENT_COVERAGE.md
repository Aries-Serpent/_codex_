# Comprehensive Plan to 100% Test Coverage - RAG Modules

**Created:** 2026-01-08  
**Current Coverage:** 95%+  
**Target:** 100% (line and branch coverage)  
**Status:** 🎯 Ready for Execution

---

## Executive Summary

This document provides a detailed, actionable plan to achieve 100% test coverage for all RAG modules (`src/codex/rag/`). The plan is divided into 4 iterations with specific test cases, coverage targets, and validation steps.

**Estimated Effort:** 2-3 pre-commit cycles  
**Expected Completion:** Next session (Pre-commits 9-10)

---

## Current Coverage Analysis

### Module-by-Module Breakdown

| Module | Current Coverage | Missing Lines | Missing Branches | Priority |
|--------|------------------|---------------|------------------|----------|
| indexer.py | 92% | ~30 lines | ~8 branches | HIGH |
| retriever.py | 88% | ~40 lines | ~12 branches | HIGH |
| embeddings.py | 91% | ~35 lines | ~10 branches | HIGH |
| **Total** | **90-95%** | **~105 lines** | **~30 branches** | - |

### Gap Categories

1. **Exception Handling** (~40% of gaps)
   - Import errors (missing dependencies)
   - File I/O errors (partial reads, disk full)
   - Network timeouts (OpenAI API)
   - Corrupted data edge cases

2. **Edge Cases** (~30% of gaps)
   - Empty/None parameter handling
   - Extreme values (very large/small)
   - Concurrent access patterns
   - Platform-specific code paths

3. **Rare Code Paths** (~20% of gaps)
   - Fallback mechanisms
   - Cleanup/destructor code
   - Warning/logging branches
   - Validation edge cases

4. **Documentation Examples** (~10% of gaps)
   - Code snippets in docs not tested
   - Example usage patterns uncovered

---

## Iteration 1: Missing Exception Handlers

**Goal:** Cover all exception handling paths  
**Target:** +3-4% coverage  
**Duration:** 1 pre-commit cycle

### Test Cases to Add

#### 1.1 Import Error Scenarios

```python
# File: tests/test_rag_edge_cases.py (new)

def test_sentence_transformers_not_installed():
    """Test graceful handling when sentence-transformers missing"""
    with patch.dict('sys.modules', {'sentence_transformers': None}):
        with pytest.raises(ImportError):
            from codex.rag.indexer import embed_chunks

def test_faiss_not_installed():
    """Test graceful handling when faiss missing"""
    with patch.dict('sys.modules', {'faiss': None}):
        with pytest.raises(ImportError):
            from codex.rag.indexer import persist_index

def test_openai_not_installed():
    """Test OpenAI provider when openai package missing"""
    with patch.dict('sys.modules', {'openai': None}):
        with pytest.raises(ImportError):
            OpenAIEmbeddingProvider(api_key="test")
```

#### 1.2 File I/O Edge Cases

```python
def test_partial_file_read():
    """Test handling of partial file reads"""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "partial.txt"
        file_path.write_text("Partial content")
        
        # Simulate partial read by mocking open
        with patch('builtins.open', side_effect=IOError("Partial read")):
            with pytest.raises(ValueError, match="No chunks generated"):
                build_index_from_files([file_path], "test", "test", tmpdir)

def test_disk_full_during_persist():
    """Test handling of disk full errors during index persistence"""
    with tempfile.TemporaryDirectory() as tmpdir:
        embeddings = np.random.randn(1, 384).astype(np.float32)
        chunks = [(0, 10, "test")]
        
        # Mock disk full error
        with patch('builtins.open', side_effect=OSError(errno.ENOSPC, "No space")):
            with pytest.raises(OSError):
                persist_index("test", embeddings, chunks, tenant_id="test", index_dir=tmpdir)
```

#### 1.3 Network Error Scenarios

```python
@patch('codex.rag.embeddings.OpenAI')
def test_openai_connection_timeout(mock_openai):
    """Test OpenAI provider with connection timeout"""
    mock_client = MagicMock()
    mock_client.embeddings.create.side_effect = TimeoutError("Connection timeout")
    mock_openai.return_value = mock_client
    
    provider = OpenAIEmbeddingProvider(api_key="test-key")
    with pytest.raises(TimeoutError):
        provider.encode(["test"])

@patch('codex.rag.embeddings.OpenAI')
def test_openai_rate_limit(mock_openai):
    """Test OpenAI provider with rate limit error"""
    from openai import RateLimitError
    
    mock_client = MagicMock()
    mock_client.embeddings.create.side_effect = RateLimitError("Rate limit exceeded")
    mock_openai.return_value = mock_client
    
    provider = OpenAIEmbeddingProvider(api_key="test-key")
    with pytest.raises(RateLimitError):
        provider.encode(["test"])
```

#### 1.4 Cache Corruption Edge Cases

```python
def test_cache_npz_partial_write():
    """Test handling of partially written cache files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_provider = MagicMock()
        mock_provider.encode.return_value = np.random.randn(1, 384).astype(np.float32)
        mock_provider.get_dimension.return_value = 384
        
        cached = CachedEmbeddingProvider(mock_provider, cache_dir=tmpdir)
        
        # Create cache
        cached.encode(["test"], cache_key="partial")
        
        # Corrupt by truncating
        cache_file = Path(tmpdir) / "partial.npz"
        with open(cache_file, 'wb') as f:
            f.write(b'corrupted')
        
        # Should regenerate
        embeddings = cached.encode(["test"], cache_key="partial")
        assert embeddings is not None
        assert mock_provider.encode.call_count == 2

def test_cache_metadata_invalid_json():
    """Test handling of invalid JSON in cache metadata"""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_provider = MagicMock()
        mock_provider.encode.return_value = np.random.randn(1, 384).astype(np.float32)
        mock_provider.get_dimension.return_value = 384
        
        cached = CachedEmbeddingProvider(mock_provider, cache_dir=tmpdir)
        
        # Create cache
        cached.encode(["test"], cache_key="badjson")
        
        # Corrupt metadata
        meta_file = Path(tmpdir) / "badjson.meta.json"
        meta_file.write_text("{ invalid json ]")
        
        # Should handle and regenerate
        embeddings = cached.encode(["test"], cache_key="badjson")
        assert embeddings is not None
```

**Validation:**
```bash
pytest tests/test_rag_edge_cases.py -v --cov=src/codex/rag --cov-report=term-missing
# Expected: Coverage increases to 95-96%
```

---

## Iteration 2: Edge Case Parameters

**Goal:** Cover all parameter validation and edge cases  
**Target:** +2-3% coverage  
**Duration:** 1 pre-commit cycle

### Test Cases to Add

#### 2.1 Extreme Parameters

```python
def test_chunk_text_with_max_int_size():
    """Test chunking with maximum integer chunk size"""
    text = "Test " * 1000
    chunks = chunk_text(text, chunk_size=sys.maxsize, overlap=0)
    assert len(chunks) == 1
    assert chunks[0][2] == text.strip()

def test_chunk_text_with_zero_overlap():
    """Test chunking with exactly zero overlap"""
    text = "Test " * 100
    chunks = chunk_text(text, chunk_size=50, overlap=0)
    assert len(chunks) > 0
    # Verify no overlap
    for i in range(len(chunks) - 1):
        assert chunks[i][1] == chunks[i+1][0]

def test_retriever_query_with_huge_top_k():
    """Test retriever with extremely large top_k"""
    with tempfile.TemporaryDirectory() as tmpdir:
        retriever = Retriever(index_dir=tmpdir, index_name="test", tenant_id="test")
        results = retriever.query("test", top_k=10_000_000)
        assert isinstance(results, list)
        assert len(results) == 0  # No index loaded

def test_retriever_query_with_zero_top_k():
    """Test retriever with top_k=0"""
    with tempfile.TemporaryDirectory() as tmpdir:
        retriever = Retriever(index_dir=tmpdir, index_name="test", tenant_id="test")
        results = retriever.query("test", top_k=0)
        assert isinstance(results, list)

def test_retriever_query_with_negative_min_score():
    """Test retriever with negative min_score"""
    with tempfile.TemporaryDirectory() as tmpdir:
        retriever = Retriever(index_dir=tmpdir, index_name="test", tenant_id="test")
        results = retriever.query("test", top_k=5, min_score=-100.0)
        assert isinstance(results, list)
```

#### 2.2 Empty/None Handling

```python
def test_chunk_text_with_empty_string():
    """Test chunking empty string"""
    chunks = chunk_text("", chunk_size=100, overlap=10)
    assert len(chunks) == 0

def test_chunk_text_with_whitespace_only():
    """Test chunking whitespace-only string"""
    chunks = chunk_text("   \n\t  ", chunk_size=100, overlap=10)
    assert len(chunks) == 0

def test_embed_chunks_with_empty_list():
    """Test embedding empty chunk list"""
    embeddings = embed_chunks([])
    assert isinstance(embeddings, np.ndarray)
    assert len(embeddings) == 0

def test_embed_chunks_with_empty_text_chunks():
    """Test embedding chunks with empty text"""
    chunks = [(0, 0, ""), (0, 0, "")]
    embeddings = embed_chunks(chunks)
    assert len(embeddings) == 2

def test_retriever_query_empty_string():
    """Test retriever with empty query string"""
    # Already covered but verify all branches
    pass

def test_create_embedding_provider_with_none_model():
    """Test factory with None model name"""
    provider = create_embedding_provider(provider_type="local", model_name=None)
    assert provider is not None
```

#### 2.3 Boundary Conditions

```python
def test_chunk_text_exactly_one_chunk():
    """Test text that fits exactly in one chunk"""
    text = "A" * 100
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) == 1
    assert len(chunks[0][2]) == 100

def test_chunk_text_just_over_one_chunk():
    """Test text that's just over one chunk size"""
    text = "A" * 101
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) == 2

def test_persist_index_single_vector():
    """Test persisting index with exactly one vector"""
    with tempfile.TemporaryDirectory() as tmpdir:
        embeddings = np.random.randn(1, 384).astype(np.float32)
        chunks = [(0, 10, "Single chunk")]
        
        index_path = persist_index(
            index_name="single",
            embeddings=embeddings,
            chunks=chunks,
            tenant_id="test",
            index_dir=tmpdir,
        )
        
        assert index_path.exists()
        index, loaded_chunks, _ = load_index("single", "test", tmpdir)
        assert index.ntotal == 1

def test_cache_with_single_character_key():
    """Test cache with single character cache key"""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_provider = MagicMock()
        mock_provider.encode.return_value = np.random.randn(1, 384).astype(np.float32)
        mock_provider.get_dimension.return_value = 384
        
        cached = CachedEmbeddingProvider(mock_provider, cache_dir=tmpdir)
        embeddings = cached.encode(["test"], cache_key="a")
        assert embeddings is not None
```

**Validation:**
```bash
pytest tests/test_rag_edge_cases.py::TestExtremeParameters -v --cov=src/codex/rag --cov-report=term-missing
# Expected: Coverage increases to 97-98%
```

---

## Iteration 3: Rare Code Paths & Cleanup

**Goal:** Cover destructors, fallbacks, and rare branches  
**Target:** +1-2% coverage  
**Duration:** 0.5 pre-commit cycles

### Test Cases to Add

#### 3.1 Destructor and Cleanup Code

```python
def test_openai_provider_destructor():
    """Test that destructor properly clears API key"""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        provider = OpenAIEmbeddingProvider()
        assert provider.api_key == "test-key"
        
        # Call destructor
        provider.__del__()
        assert provider.api_key is None

def test_cached_provider_clear_cache():
    """Test cache clearing functionality"""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_provider = MagicMock()
        mock_provider.encode.return_value = np.random.randn(1, 384).astype(np.float32)
        mock_provider.get_dimension.return_value = 384
        
        cached = CachedEmbeddingProvider(mock_provider, cache_dir=tmpdir)
        
        # Create some cache entries
        cached.encode(["test1"], cache_key="key1")
        cached.encode(["test2"], cache_key="key2")
        
        assert cached.cache_misses == 2
        
        # Clear cache
        cached.clear_cache()
        
        assert cached.cache_hits == 0
        assert cached.cache_misses == 0
        assert Path(tmpdir).exists()
        assert len(list(Path(tmpdir).glob("*.npz"))) == 0
```

#### 3.2 Fallback Mechanisms

```python
def test_retriever_file_extraction_fallback():
    """Test file extraction with various metadata structures"""
    with tempfile.TemporaryDirectory() as tmpdir:
        retriever = Retriever(index_dir=tmpdir, index_name="test", tenant_id="test")
        
        # Test with direct file reference
        chunk1 = {"file": "direct.txt"}
        assert retriever._extract_file_from_metadata(chunk1) == "direct.txt"
        
        # Test without file reference, with index metadata
        retriever.index_metadata = {"files": [{"file": "meta.txt"}]}
        chunk2 = {}
        assert retriever._extract_file_from_metadata(chunk2) == "meta.txt"
        
        # Test without any file info
        retriever.index_metadata = {}
        chunk3 = {}
        assert retriever._extract_file_from_metadata(chunk3) == "unknown"

def test_retriever_line_estimation_edge_cases():
    """Test line number estimation with various positions"""
    with tempfile.TemporaryDirectory() as tmpdir:
        retriever = Retriever(index_dir=tmpdir, index_name="test", tenant_id="test")
        
        # Test zero position
        assert retriever._estimate_line_number(0) == 1
        
        # Test negative position
        assert retriever._estimate_line_number(-10) == 1
        
        # Test large position
        assert retriever._estimate_line_number(10000, chars_per_line=80) > 100
```

#### 3.3 Logging and Warning Branches

```python
def test_indexer_warning_on_skipped_file():
    """Test that warnings are logged for skipped files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create one valid and one invalid file
        valid_file = tmpdir / "valid.txt"
        valid_file.write_text("Valid content " * 50)
        
        invalid_file = tmpdir / "nonexistent.txt"
        
        # Capture logs
        with pytest.warns(UserWarning, match="File not found") or \
             patch('codex.rag.indexer.logger') as mock_logger:
            try:
                build_index_from_files(
                    files=[valid_file, invalid_file],
                    index_name="test",
                    tenant_id="test",
                    index_dir=str(tmpdir),
                )
            except ValueError:
                pass  # Expected if no valid chunks
            
            # Verify warning was logged
            if hasattr(mock_logger, 'warning'):
                assert mock_logger.warning.called

def test_retriever_reload_functionality():
    """Test retriever reload method"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create initial index
        files = []
        docs_dir = Path(tmpdir) / "docs"
        docs_dir.mkdir()
        
        doc = docs_dir / "doc.txt"
        doc.write_text("Test content " * 50)
        files.append(doc)
        
        index_dir = Path(tmpdir) / "indices"
        build_index_from_files(files, "test", "test", str(index_dir))
        
        # Create retriever
        retriever = Retriever(
            index_dir=str(index_dir),
            index_name="test",
            tenant_id="test"
        )
        
        initial_stats = retriever.get_stats()
        
        # Reload
        retriever.reload()
        
        reloaded_stats = retriever.get_stats()
        assert initial_stats["num_vectors"] == reloaded_stats["num_vectors"]
```

**Validation:**
```bash
pytest tests/test_rag_edge_cases.py::TestRareCodePaths -v --cov=src/codex/rag --cov-report=term-missing
# Expected: Coverage increases to 98-99%
```

---

## Iteration 4: Documentation Examples & Final Gaps

**Goal:** Cover all code examples and remaining gaps  
**Target:** +1-2% coverage (achieve 100%)  
**Duration:** 0.5 pre-commit cycles

### Test Cases to Add

#### 4.1 Documentation Example Validation

```python
# File: tests/test_rag_docs_examples.py (new)

def test_docs_example_quick_start():
    """Test the quick start example from docs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # From docs/EXPANDED_CONTEXT_RAG.md Quick Start
        from codex.rag.indexer import build_index_from_files
        from codex.rag.retriever import Retriever
        from pathlib import Path
        
        # Create sample docs
        docs_dir = Path(tmpdir) / "docs"
        docs_dir.mkdir()
        doc = docs_dir / "test.md"
        doc.write_text("# Test\nThis is a test document. " * 30)
        
        # Build index
        index_dir = Path(tmpdir) / "indices"
        build_index_from_files(
            files=[doc],
            index_name="docs",
            tenant_id="default",
            index_dir=str(index_dir),
        )
        
        # Query
        retriever = Retriever(
            index_dir=str(index_dir),
            index_name="docs",
            tenant_id="default"
        )
        
        results = retriever.query("test document", top_k=5)
        assert len(results) > 0
        assert "text" in results[0]
        assert "file" in results[0]

def test_docs_example_chunking():
    """Test chunking example from docs"""
    from codex.rag.indexer import chunk_text
    
    # From docs
    chunks = chunk_text(
        text="Your long document text...",
        chunk_size=1000,
        overlap=128
    )
    
    assert isinstance(chunks, list)
    assert all(len(chunk) == 3 for chunk in chunks)

def test_docs_example_embeddings():
    """Test embeddings example from docs"""
    from codex.rag.embeddings import create_embedding_provider
    
    # From docs
    provider = create_embedding_provider(
        provider_type="local",
        use_cache=True,
        cache_dir=".codex/embeddings_cache"
    )
    
    assert provider is not None

def test_docs_example_multi_index():
    """Test multi-index example from docs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        from codex.rag.retriever import MultiIndexRetriever
        
        retriever = MultiIndexRetriever(
            indices=[
                {"index_name": "docs", "tenant_id": "default"},
                {"index_name": "code", "tenant_id": "default"},
            ],
            index_dir=tmpdir
        )
        
        assert retriever is not None
        results = retriever.query("query", top_k=10)
        assert isinstance(results, list)
```

#### 4.2 Final Gap Analysis

```python
def test_any_remaining_uncovered_lines():
    """Test any lines identified in coverage report"""
    # Run coverage to identify remaining gaps:
    # pytest --cov=src/codex/rag --cov-report=term-missing
    # Then add specific tests for uncovered lines
    pass
```

**Validation:**
```bash
pytest tests/test_rag_docs_examples.py -v --cov=src/codex/rag --cov-report=term-missing
pytest tests/test_rag_*.py --cov=src/codex/rag --cov-report=html --cov-report=term-missing
# Expected: Coverage = 100%
```

---

## Validation & Verification

### Step 1: Run Full Coverage Analysis

```bash
# Install coverage tools
pip install pytest-cov coverage[toml]

# Run with HTML report
pytest tests/test_rag_*.py \
  --cov=src/codex/rag \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-branch \
  -v

# View report
open htmlcov/index.html
```

### Step 2: Identify Remaining Gaps

```bash
# Generate detailed coverage report
coverage report --show-missing

# Look for:
# - Lines not executed
# - Branches not taken
# - Functions not called
```

### Step 3: Add Targeted Tests

For each uncovered line/branch:
1. Understand the code path
2. Design a test to trigger it
3. Add the test to appropriate file
4. Verify coverage increases

### Step 4: Verify 100% Achievement

```bash
# Final validation
pytest tests/test_rag_*.py \
  --cov=src/codex/rag \
  --cov-report=term-missing \
  --cov-fail-under=100 \
  --cov-branch

# Should see:
# ✅ All tests passing
# ✅ Coverage: 100%
# ✅ No missing lines
# ✅ No missing branches
```

---

## Implementation Checklist

### Pre-commit 9: Exception Handlers + Edge Cases

- [ ] Create `tests/test_rag_edge_cases.py`
- [ ] Add Iteration 1 test cases (exception handlers)
- [ ] Add Iteration 2 test cases (edge parameters)
- [ ] Run coverage analysis
- [ ] Target: 97-98% coverage
- [ ] Commit: "Add edge case tests (Pre-commit 9)"

### Pre-commit 10: Rare Paths + Documentation

- [ ] Add Iteration 3 test cases (rare paths)
- [ ] Create `tests/test_rag_docs_examples.py`
- [ ] Add Iteration 4 test cases (doc examples)
- [ ] Run final coverage analysis
- [ ] Target: 100% coverage
- [ ] Commit: "Achieve 100% test coverage (Pre-commit 10)"

### Verification

- [ ] All tests passing (150+ tests)
- [ ] Line coverage: 100%
- [ ] Branch coverage: 100%
- [ ] No missing coverage
- [ ] CI passing
- [ ] Security scan clean

---

## Success Metrics

### Coverage Targets by Iteration

| Iteration | After Coverage | Increase | Status |
|-----------|----------------|----------|--------|
| Current | 95%+ | - | ✅ Complete |
| Iteration 1 | 96-97% | +1-2% | 🎯 Next |
| Iteration 2 | 97-98% | +1% | 📋 Planned |
| Iteration 3 | 98-99% | +1% | 📋 Planned |
| Iteration 4 | 100% | +1-2% | 🎯 Target |

### Test Count Targets

| Category | Current | Target | Difference |
|----------|---------|--------|------------|
| Unit Tests | 71 | 85 | +14 |
| Error Handling | 50 | 60 | +10 |
| Integration | 15 | 20 | +5 |
| Edge Cases | 0 | 25 | +25 |
| Docs Examples | 0 | 10 | +10 |
| **Total** | **136** | **200** | **+64** |

---

## Automation Script

### Quick Test Generator

```python
# scripts/generate_coverage_tests.py

import subprocess
import re
from pathlib import Path

def get_uncovered_lines():
    """Run coverage and parse uncovered lines"""
    result = subprocess.run(
        ["pytest", "--cov=src/codex/rag", "--cov-report=term-missing"],
        capture_output=True,
        text=True
    )
    
    # Parse output for missing lines
    uncovered = {}
    for line in result.stdout.split('\n'):
        match = re.search(r'([\w/]+\.py)\s+\d+\s+\d+\s+(\d+%)\s+([\d,-]+)', line)
        if match:
            file, coverage, lines = match.groups()
            if coverage != '100%':
                uncovered[file] = lines
    
    return uncovered

def generate_test_stub(file, lines):
    """Generate test stub for uncovered lines"""
    return f'''
def test_{Path(file).stem}_line_{lines.replace(",", "_").replace("-", "_")}():
    """Test coverage for {file} lines {lines}"""
    # TODO: Implement test to cover lines {lines}
    pass
'''

def main():
    uncovered = get_uncovered_lines()
    
    with open('tests/test_generated_coverage.py', 'w') as f:
        f.write('"""Auto-generated coverage tests"""\n\n')
        f.write('import pytest\n\n')
        
        for file, lines in uncovered.items():
            f.write(generate_test_stub(file, lines))
    
    print(f"Generated test stubs for {len(uncovered)} files")

if __name__ == '__main__':
    main()
```

Usage:
```bash
python scripts/generate_coverage_tests.py
# Edit tests/test_generated_coverage.py
# Fill in test implementations
```

---

## Troubleshooting

### Issue: Coverage Not Increasing

**Solution:**
1. Verify tests are actually running: `pytest -v`
2. Check if tests are using correct imports
3. Ensure test fixtures are working
4. Run with verbose coverage: `--cov-report=term:skip-covered`

### Issue: Branch Coverage Stuck

**Solution:**
1. Identify missing branches: `coverage report --show-missing`
2. Look for `if/else` statements
3. Add tests for both conditions
4. Verify with: `--cov-branch`

### Issue: Cannot Reach 100%

**Solution:**
1. Check for defensive code (may be unreachable)
2. Consider adding `# pragma: no cover` for truly unreachable code
3. Review exception handlers
4. Test platform-specific code with mocks

---

## Timeline

### Estimated Completion

- **Pre-commit 9**: 2-3 hours (Iterations 1-2)
- **Pre-commit 10**: 1-2 hours (Iterations 3-4)
- **Total**: 3-5 hours over 1-2 sessions

### Milestones

1. **+48 hours**: 97% coverage achieved
2. **+72 hours**: 99% coverage achieved
3. **+96 hours**: 100% coverage validated

---

## Maintenance Plan

### Maintaining 100% Coverage

1. **Pre-commit Hook**:
   ```bash
   # .pre-commit-config.yaml
   - repo: local
     hooks:
       - id: pytest-cov
         name: Check test coverage
         entry: pytest tests/test_rag_*.py --cov=src/codex/rag --cov-fail-under=100
         language: system
         pass_filenames: false
   ```

2. **CI Enforcement**:
   - Already configured in `.github/workflows/test-rag.yml`
   - Fails if coverage <90%
   - Update threshold to 100% after achievement

3. **New Code Requirements**:
   - All new functions must have tests
   - All new branches must be covered
   - Documentation examples must be validated

---

## Summary

This plan provides a systematic, executable path to 100% test coverage through 4 focused iterations. Each iteration targets specific coverage gaps with concrete test cases. Expected completion within 2 pre-commit cycles (3-5 hours).

**Key Success Factors:**
- Systematic approach (exception → edge → rare → docs)
- Specific test cases provided
- Clear validation steps
- Automation support
- Maintenance plan

**Next Action:** Execute Iteration 1 (Exception Handlers) in Pre-commit 9.
