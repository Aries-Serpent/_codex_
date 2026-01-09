# RAG Enhancement Plansets & Promptsets

**Created:** 2026-01-08  
**Agent:** GitHub Copilot  
**Status:** 🔄 Execution In Progress  
**Target:** 100% Test Coverage + Production Enhancements

---

## Overview

This document contains comprehensive plansets and promptsets for completing all remaining RAG enhancements, achieving 100% test coverage, and implementing production-ready features.

---

## Planset 1: CI/CD Integration & Performance Validation

### Pre-commit 1-2: CI Environment Test Suite

**Goal:** Execute full test suite in CI-like environment with coverage reporting

**Tasks:**
- [ ] Create CI test configuration file (`.github/workflows/test-rag.yml`)
- [ ] Configure pytest with coverage reporting (XML + HTML)
- [ ] Add coverage badges and gates (fail-under=90)
- [ ] Execute tests in isolated environment
- [ ] Generate and validate coverage report
- [ ] Document CI integration in README

**Success Criteria:**
- [ ] All 70+ tests pass in CI environment
- [ ] Coverage report generated (HTML + XML)
- [ ] Coverage ≥90% maintained
- [ ] No new security issues

**Files to Create/Modify:**
- `.github/workflows/test-rag.yml` (50 lines)
- `tests/conftest.py` (add RAG fixtures, 30 lines)
- `docs/EXPANDED_CONTEXT_RAG.md` (update CI section)

### Pre-commit 3-4: Performance Benchmarking

**Goal:** Establish baseline performance metrics with real corpus

**Tasks:**
- [ ] Create performance benchmark script (`tests/benchmarks/test_rag_performance.py`)
- [ ] Build test corpus (1k, 10k, 100k chunks)
- [ ] Measure indexing throughput
- [ ] Measure query latency (p50, p95, p99)
- [ ] Measure cache hit rates
- [ ] Document performance baselines

**Success Criteria:**
- [ ] Indexing: ≥100 chunks/second
- [ ] Query p95: <50ms for 10k chunks
- [ ] Cache hit rate: ≥90%
- [ ] Results documented with graphs

**Files to Create/Modify:**
- `tests/benchmarks/test_rag_performance.py` (200 lines)
- `tests/benchmarks/generate_test_corpus.py` (100 lines)
- `docs/PERFORMANCE_BENCHMARKS.md` (new file)

### Review, Verify, Commit
- [ ] Tests passing in CI
- [ ] Performance metrics documented
- [ ] Benchmarks reproducible

---

## Planset 2: Path to 100% Test Coverage

### Pre-commit 5-6: Error Handling Tests

**Goal:** Cover all exception paths and edge cases

**Tasks:**
- [ ] Create `tests/test_rag_error_handling.py`
- [ ] Test file I/O errors (permissions, disk full, encoding)
- [ ] Test network errors (OpenAI timeouts, rate limits)
- [ ] Test corruption scenarios (cache, indices)
- [ ] Test import errors (missing dependencies)
- [ ] Test concurrent access patterns
- [ ] Test resource exhaustion scenarios

**Success Criteria:**
- [ ] All error handlers tested
- [ ] Coverage increase: +5-8%
- [ ] Error messages validated
- [ ] Graceful degradation verified

**Files to Create/Modify:**
- `tests/test_rag_error_handling.py` (400 lines)
- `tests/fixtures/corrupt_data.py` (50 lines)

### Pre-commit 7-8: Integration & Multi-Tenant Tests

**Goal:** Complete integration coverage and tenant isolation

**Tasks:**
- [ ] Create `tests/test_rag_integration.py`
- [ ] Test end-to-end pipeline (docs → index → query)
- [ ] Test multi-tenant isolation
- [ ] Test concurrent operations
- [ ] Test index updates and versioning
- [ ] Test cross-module interactions
- [ ] Test cache effectiveness

**Success Criteria:**
- [ ] Full workflow validated
- [ ] Tenant isolation verified
- [ ] Coverage increase: +3-5%
- [ ] No race conditions

**Files to Create/Modify:**
- `tests/test_rag_integration.py` (300 lines)
- `tests/test_rag_multitenant.py` (150 lines)

### Pre-commit 9-10: Edge Cases & Documentation Examples

**Goal:** Cover remaining edge cases and validate all docs examples

**Tasks:**
- [ ] Test extreme parameters (huge top_k, tiny chunks)
- [ ] Test large files (100MB+)
- [ ] Test many small files (10k+)
- [ ] Test malformed metadata
- [ ] Extract and test all code examples from docs
- [ ] Test platform-specific behaviors

**Success Criteria:**
- [ ] Coverage: 98-100%
- [ ] All docs examples validated
- [ ] Edge cases handled gracefully

**Files to Create/Modify:**
- `tests/test_rag_edge_cases.py` (250 lines)
- `tests/test_rag_docs_examples.py` (150 lines)

### Review, Verify, Commit
- [ ] Coverage ≥98% (target: 100%)
- [ ] All branches covered
- [ ] Documentation examples working

---

## Planset 3: Query Enhancement Features

### Pre-commit 11-12: Query Rewriting

**Goal:** Implement query rewriting for improved retrieval accuracy

**Tasks:**
- [ ] Create `src/codex/rag/query_rewriter.py`
- [ ] Implement synonym expansion
- [ ] Implement query expansion with embeddings
- [ ] Implement spell correction
- [ ] Add configuration options
- [ ] Add tests (80%+ coverage)
- [ ] Document usage patterns

**Success Criteria:**
- [ ] Query accuracy improved by 10-15%
- [ ] Configurable on/off
- [ ] Tests comprehensive
- [ ] Documentation complete

**Files to Create/Modify:**
- `src/codex/rag/query_rewriter.py` (300 lines)
- `tests/test_rag_query_rewriter.py` (200 lines)
- `docs/EXPANDED_CONTEXT_RAG.md` (add section)

### Pre-commit 13-14: Cross-Encoder Re-Ranking

**Goal:** Implement re-ranking with cross-encoder for better accuracy

**Tasks:**
- [ ] Create `src/codex/rag/reranker.py`
- [ ] Implement cross-encoder re-ranking
- [ ] Add fallback to embedding similarity
- [ ] Optimize for performance (batch processing)
- [ ] Add caching layer
- [ ] Add tests (80%+ coverage)
- [ ] Document trade-offs

**Success Criteria:**
- [ ] Relevance improved by 20-30%
- [ ] Latency increase <100ms
- [ ] Configurable depth
- [ ] Documentation complete

**Files to Create/Modify:**
- `src/codex/rag/reranker.py` (250 lines)
- `tests/test_rag_reranker.py` (150 lines)
- `pyproject.toml` (add cross-encoder dep)

### Review, Verify, Commit
- [ ] Query accuracy measurably improved
- [ ] Performance acceptable
- [ ] Tests passing

---

## Planset 4: Advanced Features

### Pre-commit 15-16: Hybrid Search (Dense + Sparse)

**Goal:** Implement hybrid search combining dense and sparse retrieval

**Tasks:**
- [ ] Create `src/codex/rag/hybrid_retriever.py`
- [ ] Implement BM25 sparse retrieval
- [ ] Implement fusion algorithm (RRF)
- [ ] Add weighting configuration
- [ ] Optimize for performance
- [ ] Add tests (80%+ coverage)
- [ ] Benchmark against dense-only

**Success Criteria:**
- [ ] Recall improved by 15-25%
- [ ] Configurable weighting
- [ ] Performance acceptable
- [ ] Documentation complete

**Files to Create/Modify:**
- `src/codex/rag/hybrid_retriever.py` (350 lines)
- `src/codex/rag/sparse.py` (200 lines - BM25)
- `tests/test_rag_hybrid.py` (200 lines)

### Pre-commit 17-18: Hierarchical Chunking

**Goal:** Implement hierarchical chunking for better context preservation

**Tasks:**
- [ ] Enhance `src/codex/rag/indexer.py` with hierarchy
- [ ] Implement parent-child chunk relationships
- [ ] Add context expansion on retrieval
- [ ] Update metadata schema
- [ ] Add tests (80%+ coverage)
- [ ] Document strategy

**Success Criteria:**
- [ ] Context preservation improved
- [ ] Backward compatible
- [ ] Tests comprehensive
- [ ] Migration guide provided

**Files to Create/Modify:**
- `src/codex/rag/indexer.py` (add 150 lines)
- `src/codex/rag/hierarchical.py` (200 lines)
- `tests/test_rag_hierarchical.py` (150 lines)

### Review, Verify, Commit
- [ ] Hybrid search functional
- [ ] Hierarchical chunking working
- [ ] Tests passing

---

## Planset 5: Monitoring & Optimization

### Pre-commit 19-20: Query Analytics

**Goal:** Implement query analytics and optimization

**Tasks:**
- [ ] Create `src/codex/rag/analytics.py`
- [ ] Track query patterns
- [ ] Measure retrieval quality
- [ ] Identify optimization opportunities
- [ ] Add dashboard/reporting
- [ ] Add tests (80%+ coverage)
- [ ] Document metrics

**Success Criteria:**
- [ ] Key metrics tracked
- [ ] Reporting functional
- [ ] Actionable insights
- [ ] Documentation complete

**Files to Create/Modify:**
- `src/codex/rag/analytics.py` (300 lines)
- `scripts/rag_analytics_dashboard.py` (200 lines)
- `tests/test_rag_analytics.py` (150 lines)

### Pre-commit 21-22: GPU Acceleration

**Goal:** Add GPU acceleration support (faiss-gpu)

**Tasks:**
- [ ] Add faiss-gpu as optional dependency
- [ ] Create GPU detection utility
- [ ] Add automatic fallback to CPU
- [ ] Update indexer for GPU support
- [ ] Update retriever for GPU support
- [ ] Add tests (with mocks)
- [ ] Document GPU setup

**Success Criteria:**
- [ ] GPU acceleration working
- [ ] Graceful CPU fallback
- [ ] Performance improvement documented
- [ ] Setup guide complete

**Files to Create/Modify:**
- `src/codex/rag/gpu_utils.py` (150 lines)
- `src/codex/rag/indexer.py` (add GPU support)
- `src/codex/rag/retriever.py` (add GPU support)
- `tests/test_rag_gpu.py` (100 lines with mocks)
- `pyproject.toml` (add faiss-gpu optional)
- `docs/GPU_ACCELERATION.md` (new file)

### Review, Verify, Commit
- [ ] Analytics functional
- [ ] GPU support implemented
- [ ] Tests passing

---

## Promptsets for Autonomous Execution

### Promptset 1: CI Integration
```
Execute Planset 1 (CI/CD Integration):

1. Create GitHub Actions workflow at .github/workflows/test-rag.yml:
   - Trigger on push/PR to paths: src/codex/rag/**, tests/test_rag_**
   - Install dependencies: pip install -e ".[rag,test]"
   - Run pytest with coverage: --cov=src/codex/rag --cov-report=xml --cov-report=html
   - Upload coverage to codecov
   - Fail if coverage <90%

2. Create performance benchmarks:
   - Generate test corpus (1k, 10k chunks)
   - Benchmark indexing: chunks/second
   - Benchmark queries: latency percentiles
   - Measure cache hit rates
   - Save results to docs/PERFORMANCE_BENCHMARKS.md

3. Validate:
   - Run tests locally first
   - Ensure all pass
   - Generate coverage report
   - Commit with message: "Add CI integration and performance benchmarks"
```

### Promptset 2: 100% Coverage
```
Execute Planset 2 (Path to 100% Coverage):

1. Create tests/test_rag_error_handling.py:
   - Test all exception paths in indexer, retriever, embeddings
   - Mock file I/O errors (PermissionError, OSError)
   - Mock network errors for OpenAI (TimeoutError, ConnectionError)
   - Test cache corruption scenarios
   - Test import errors (patch sys.modules)
   - Test concurrent access (threading)

2. Create tests/test_rag_integration.py:
   - Full pipeline: create corpus → build index → query → verify provenance
   - Multi-tenant: create 3 tenants, verify isolation
   - Concurrent: build 2 indices simultaneously
   - Updates: modify corpus, rebuild, verify changes

3. Create tests/test_rag_edge_cases.py:
   - Extreme parameters: top_k=10000, chunk_size=10
   - Large files: generate 100MB file, index successfully
   - Many files: 1000 small files
   - Malformed metadata: invalid JSON, missing fields

4. Create tests/test_rag_docs_examples.py:
   - Extract all code examples from docs/EXPANDED_CONTEXT_RAG.md
   - Convert to test functions
   - Add assertions for expected behavior

5. Validate:
   - Run: pytest tests/test_rag_*.py --cov=src/codex/rag --cov-report=term-missing
   - Target: 98-100% coverage
   - Fix any remaining gaps
   - Commit with message: "Achieve 100% test coverage for RAG modules"
```

### Promptset 3: Query Enhancements
```
Execute Planset 3 (Query Enhancement Features):

1. Create src/codex/rag/query_rewriter.py:
   - Class QueryRewriter with methods:
     - expand_synonyms(query) using WordNet/custom dict
     - expand_with_embeddings(query, model, top_k=5)
     - correct_spelling(query) using SymSpell
   - Configuration: enable_synonyms, enable_expansion, enable_spelling
   - Cache expanded queries

2. Create src/codex/rag/reranker.py:
   - Class CrossEncoderReranker:
     - Use cross-encoder/ms-marco-MiniLM-L-6-v2
     - rerank(query, results, top_k) method
     - Batch processing for efficiency
     - Fallback to original scores if model fails
   - Add caching layer for query-result pairs

3. Create tests for both:
   - Query rewriter: test each expansion method
   - Reranker: test ranking improvement, batch processing

4. Update Retriever to use rewriter + reranker:
   - Add optional query_rewriter parameter
   - Add optional reranker parameter
   - Pipeline: rewrite → retrieve → rerank

5. Validate:
   - Test query accuracy improves
   - Measure latency impact
   - Document usage in docs/EXPANDED_CONTEXT_RAG.md
   - Commit with message: "Add query rewriting and cross-encoder re-ranking"
```

### Promptset 4: Advanced Features
```
Execute Planset 4 (Advanced Features):

1. Create src/codex/rag/hybrid_retriever.py:
   - Implement BM25 sparse retrieval (rank_bm25 library)
   - Implement Reciprocal Rank Fusion (RRF)
   - Class HybridRetriever:
     - Combines dense (FAISS) + sparse (BM25)
     - Configurable weights (default: 0.5/0.5)
     - query() returns fused results

2. Create src/codex/rag/hierarchical.py:
   - Implement hierarchical chunking:
     - Parent chunks (2000 chars)
     - Child chunks (500 chars)
     - Store relationships in metadata
   - On retrieval: return child + parent context
   - Update indexer to support hierarchy

3. Create tests:
   - test_rag_hybrid.py: test BM25, RRF, fusion
   - test_rag_hierarchical.py: test parent-child, context expansion

4. Validate:
   - Benchmark hybrid vs dense-only (expect +15% recall)
   - Test hierarchical context preservation
   - Document in docs/EXPANDED_CONTEXT_RAG.md
   - Commit with message: "Add hybrid search and hierarchical chunking"
```

### Promptset 5: Monitoring & GPU
```
Execute Planset 5 (Monitoring & Optimization):

1. Create src/codex/rag/analytics.py:
   - Class RAGAnalytics:
     - Track queries: frequency, latency, results
     - Measure retrieval quality: precision@k, recall@k
     - Store in SQLite: .codex/rag_analytics.db
     - Generate reports: top queries, slow queries, cache stats
   - Add dashboard script: scripts/rag_analytics_dashboard.py

2. Create src/codex/rag/gpu_utils.py:
   - Function detect_gpu(): returns bool
   - Function get_faiss_gpu_resources(): returns GPU config
   - Automatic fallback to CPU if GPU unavailable

3. Update indexer.py and retriever.py:
   - Add use_gpu parameter (default: auto-detect)
   - Use faiss.StandardGpuResources() when available
   - Graceful fallback with logging

4. Create tests:
   - test_rag_analytics.py: test tracking, reporting
   - test_rag_gpu.py: mock GPU, test fallback

5. Create documentation:
   - docs/GPU_ACCELERATION.md: setup guide, benchmarks
   - Update docs/EXPANDED_CONTEXT_RAG.md: analytics section

6. Validate:
   - Test analytics tracking
   - Test GPU detection (mock)
   - Document setup process
   - Commit with message: "Add analytics and GPU acceleration support"
```

---

## Execution Order

Execute plansets in order:

1. **Planset 1** (Pre-commits 1-4): CI & Performance → ~2-3 hours
2. **Planset 2** (Pre-commits 5-10): 100% Coverage → ~3-4 hours
3. **Planset 3** (Pre-commits 11-14): Query Enhancements → ~2-3 hours
4. **Planset 4** (Pre-commits 15-18): Advanced Features → ~3-4 hours
5. **Planset 5** (Pre-commits 19-22): Monitoring & GPU → ~2-3 hours

**Total Estimated**: 11 pre-commit cycles (12-17 hours of development)

---

## Success Criteria

### Completion Checklist
- [ ] All 22 pre-commit cycles completed
- [ ] Test coverage: 100%
- [ ] All tests passing (150+ tests total)
- [ ] CI/CD fully integrated
- [ ] Performance benchmarks documented
- [ ] All features tested and documented
- [ ] Code review passed
- [ ] Security scan clean

### Quality Gates
- [ ] Coverage ≥100%
- [ ] No security issues
- [ ] All linting passes
- [ ] Type hints complete
- [ ] Documentation comprehensive

---

## Status Tracking

Track progress in PR description and comments. Update after each pre-commit cycle.

**Current Status:** 🔄 Ready for Execution  
**Next Action:** Begin Planset 1, Pre-commit 1-2
