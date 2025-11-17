# Next Copilot Implementation Prompt

## Context

This prompt continues the "Recommended Combined Path for Options 1 and 2" implementation strategy. The Inference Serving quick win (Phase 1) has been completed. This prompt covers the remaining follow-up PRs.

---

## Executive Summary

Implement remaining capability enhancements following the modular PR strategy:
1. **PR B - Vector Store Integration** (next priority)
2. **PR C - Duplication Ratio & Metrics** (after PR B)
3. **PR D - Inference & Retrieval Optimizations** (optional, after PR C)

Each PR should be small, focused, and independently reviewable. Do NOT combine multiple PRs into one large change.

---

## PR B: Vector Store Integration

### Objective
Add vector-based retrieval capabilities that integrate with the existing inference serving layer.

### Scope (In-Scope)

#### 1. Vector Store Abstraction
- Define base `VectorStore` interface/abstract class with core methods:
  - `add(vectors, metadata)` - Add vectors with metadata
  - `search(query_vector, k, filters)` - Search for similar vectors
  - `delete(ids)` - Delete vectors by ID
  - `get(ids)` - Retrieve vectors by ID
  - `count()` - Get total vector count
  - `clear()` - Clear all vectors
- Document interface contract and expected behavior

#### 2. Indexing Implementation
- Implement indexing for FAISS backend (already registered in factory)
- Support operations:
  - Batch vector insertion with metadata
  - Index persistence (save/load to disk)
  - Index validation and checksum verification
- Add input validation:
  - Dimension consistency checks
  - Batch size limits
  - Metadata schema validation

#### 3. Retrieval Implementation
- Implement k-NN search with configurable k
- Support filtering by metadata fields
- Return results with:
  - Vector IDs
  - Similarity scores
  - Metadata
  - Distance metrics
- Add pagination for large result sets

#### 4. Integration with Inference Server
- Add optional embedding endpoint to inference server:
  - `POST /embed` - Generate embeddings from text
  - Use loaded model to create embeddings
  - Return vectors in standard format
- Wire embeddings to vector store for indexing
- Keep integration loose-coupling (optional feature)

#### 5. Tests
**Unit Tests:**
- Vector store interface compliance
- Indexing: add, batch add, persistence
- Retrieval: search with various k values, filtering
- Edge cases: empty index, dimension mismatch, invalid filters

**Integration Tests:**
- End-to-end: embed text → index → search → retrieve
- Persistence: save index → load index → verify integrity
- Error handling: missing index, corrupted data

Target: 20-25 new tests minimum

#### 6. Documentation
Create `docs/VECTOR_STORE_INTEGRATION_GUIDE.md` covering:
- Vector store interface overview
- Indexing operations with examples
- Search and retrieval patterns
- Integration with inference server
- Performance considerations
- Error handling

### Out of Scope (Future PRs)
- Hybrid search (dense + sparse)
- Advanced filtering (complex queries, joins)
- Distributed indexing
- Real-time index updates
- Vector compression/quantization
- Multiple backend support beyond FAISS
- Caching and optimization

### Acceptance Criteria
- [ ] VectorStore interface defined and documented
- [ ] FAISS implementation complete with indexing and retrieval
- [ ] Integration with inference server (optional embed endpoint)
- [ ] 20+ tests passing with >90% coverage of new code
- [ ] Documentation complete with examples
- [ ] No security vulnerabilities (CodeQL clean)
- [ ] No breaking changes to existing APIs

### Files to Modify/Create
- `src/codex/retrieval/stores/base.py` (new) - VectorStore interface
- `src/codex/retrieval/stores/faiss_store.py` - Enhance with full indexing/retrieval
- `src/codex_ml/serving/inference_server.py` - Add optional /embed endpoint
- `tests/retrieval/test_vector_store_interface.py` (new)
- `tests/retrieval/test_faiss_integration.py` (new)
- `docs/VECTOR_STORE_INTEGRATION_GUIDE.md` (new)

---

## PR C: Duplication Ratio & Metrics

### Objective
Provide visibility into duplication ratio and related code quality metrics.

### Scope (In-Scope)

#### 1. Duplication Detection
- Implement basic duplication detection:
  - Token-based similarity (exact matches)
  - AST-based structural similarity
  - Configurable similarity thresholds
- Support Python files initially
- Generate duplication reports with:
  - Duplicate code blocks
  - Similarity scores
  - File locations and line numbers

#### 2. Ratio Calculation
- Calculate duplication ratio:
  - `duplication_ratio = duplicate_lines / total_lines`
  - Support file-level and project-level ratios
  - Track over time (optional baseline comparison)
- Provide breakdown by:
  - File
  - Directory
  - Module

#### 3. Metrics Pipeline Integration
- Integrate with existing logging/metrics infrastructure
- Store metrics in structured format (JSON/SQLite)
- Support metric queries:
  - Get current duplication ratio
  - Compare against baseline
  - Trend analysis (if historical data available)

#### 4. CLI Command
Add `codex duplication` command:
```bash
# Check duplication in current directory
codex duplication check

# Check specific paths
codex duplication check --path src/

# Generate report
codex duplication report --format json --output duplication.json

# Compare against baseline
codex duplication compare --baseline baseline.json
```

#### 5. Tests
**Unit Tests:**
- Duplication detection (exact, similar, unique cases)
- Ratio calculation with various inputs
- Edge cases: empty files, single file, no duplicates

**Integration Tests:**
- Full pipeline: scan → detect → calculate → report
- CLI commands with various options
- Baseline comparison

Target: 15-20 new tests minimum

#### 6. Documentation
Create `docs/DUPLICATION_METRICS_GUIDE.md` covering:
- What is measured and how
- Running duplication checks
- Interpreting results
- Setting thresholds
- Integration with CI/CD

### Out of Scope (Future PRs)
- Advanced similarity algorithms (ML-based)
- Multi-language support (beyond Python)
- Automated refactoring suggestions
- Duplication trend visualization
- Cross-repository analysis
- Real-time duplication detection

### Acceptance Criteria
- [ ] Duplication detection working for Python files
- [ ] Ratio calculation accurate and tested
- [ ] CLI commands functional and documented
- [ ] 15+ tests passing with >85% coverage
- [ ] Documentation complete with examples
- [ ] No security vulnerabilities (CodeQL clean)
- [ ] Metrics stored in standardized format

### Files to Modify/Create
- `src/codex/metrics/duplication.py` (new) - Core duplication logic
- `src/codex/cli.py` - Add duplication commands
- `tests/metrics/test_duplication.py` (new)
- `tests/cli/test_duplication_commands.py` (new)
- `docs/DUPLICATION_METRICS_GUIDE.md` (new)

---

## PR D: Inference & Retrieval Optimizations (Optional)

### Objective
Refine and optimize the initial Inference Serving and Vector Store implementations.

### Scope (In-Scope)

#### 1. Inference Optimizations
- Add request batching:
  - Batch multiple requests together
  - Configurable batch timeout
  - Improve throughput
- Add response caching:
  - Cache predictions for identical inputs
  - Configurable TTL
  - Memory-bounded cache
- Add basic performance metrics:
  - Latency percentiles (p50, p95, p99)
  - Throughput (requests/sec)
  - Cache hit rate

#### 2. Retrieval Optimizations
- Index optimization:
  - Pre-build index structure
  - Memory-mapped files for large indices
  - Lazy loading
- Search optimization:
  - Result caching for repeated queries
  - Approximate nearest neighbor (ANN) settings
  - Query batching
- Add retrieval metrics:
  - Search latency
  - Index size
  - Query throughput

#### 3. Resilience Improvements
- Add retry logic:
  - Configurable retry attempts
  - Exponential backoff
  - Circuit breaker pattern
- Add graceful degradation:
  - Fallback to cached results
  - Partial results on timeout
  - Health-based routing

#### 4. Integration Tests
- Performance regression tests:
  - Latency benchmarks
  - Throughput benchmarks
  - Memory usage baselines
- Stress tests:
  - High load scenarios
  - Concurrent requests
  - Large batch sizes

Target: 10-15 new tests minimum

#### 5. Documentation
Update existing docs with:
- Performance tuning guide
- Caching strategies
- Resilience patterns
- Benchmarking results

### Out of Scope
- Distributed serving
- GPU optimization
- Model compression
- A/B testing framework
- Auto-scaling

### Acceptance Criteria
- [ ] Batching and caching implemented
- [ ] Performance metrics collection working
- [ ] Resilience patterns in place
- [ ] 10+ tests passing including benchmarks
- [ ] Documentation updated
- [ ] No performance regressions
- [ ] No security vulnerabilities

### Files to Modify/Create
- `src/codex_ml/serving/inference_server.py` - Add batching, caching
- `src/codex/retrieval/stores/faiss_store.py` - Add optimizations
- `src/codex/retrieval/cache.py` (new) - Caching utilities
- `tests/performance/test_inference_benchmarks.py` (new)
- `tests/performance/test_retrieval_benchmarks.py` (new)
- Update `docs/INFERENCE_SERVING_GUIDE.md`
- Update `docs/VECTOR_STORE_INTEGRATION_GUIDE.md`

---

## General Guidelines for All PRs

### Development Process
1. **Start with a plan**: Use `report_progress` to outline the checklist before coding
2. **Make incremental changes**: Commit after each verified unit of work
3. **Test early and often**: Run tests after each change
4. **Document as you go**: Update docs alongside code changes
5. **Security first**: Run `codeql_checker` before finalizing

### Code Quality Standards
- Follow existing code style and patterns
- Add type hints to all new functions
- Write docstrings for public APIs
- Keep functions small and focused (<50 lines)
- Maintain test coverage >85% for new code

### Testing Requirements
- Unit tests for all new functions
- Integration tests for end-to-end workflows
- Error case coverage (happy path + edge cases)
- Performance tests for optimization PRs
- All tests must pass before completion

### Documentation Requirements
- README-style guide for new features
- Code examples for common use cases
- API reference for public interfaces
- Troubleshooting section
- Clear statement of what's NOT included

### Security Requirements
- No secrets in code or config files
- Input validation for all external inputs
- Proper error handling (no info leakage)
- Rate limiting for external-facing APIs
- CodeQL scan must pass (0 vulnerabilities)

---

## Recommended Execution Order

### Immediate Next Step: PR B (Vector Store Integration)
Start with this PR because:
- Builds on completed Inference Serving work
- High value capability enhancement
- Clear scope and deliverables
- Enables future retrieval-based features

### After PR B: PR C (Duplication Ratio & Metrics)
Continue with this PR because:
- Independent of PR B (can be done in parallel)
- Code quality improvement
- Provides visibility into technical debt
- Relatively straightforward implementation

### Optional: PR D (Optimizations)
Only pursue if:
- PRs B and C are complete and merged
- Performance issues are observed
- Time and resources permit
- Clear optimization targets identified

---

## Success Criteria for Full Implementation

### Completion Checklist
- [ ] All 3 PRs completed (or 2 if PR D skipped)
- [ ] 45+ new tests total (20 + 15 + 10)
- [ ] 3 comprehensive documentation guides
- [ ] All security scans passing
- [ ] No breaking changes to existing APIs
- [ ] Repository maturity increased by documented metrics

### Quality Gates
- All tests passing (100% pass rate)
- Code coverage >85% for new code
- No CodeQL vulnerabilities
- Documentation complete and accurate
- PRs independently reviewable and mergeable

---

## Template for Starting Each PR

When starting a new PR, use this template with Copilot:

```
@copilot I'm ready to implement [PR B / PR C / PR D] from the follow-up PR plan.

Objective: [Copy objective from above]

Please:
1. Create an initial plan as a checklist using report_progress
2. Implement the features incrementally with tests
3. Document as you go
4. Run security checks before completion

Scope:
[Copy in-scope items from above]

Out of Scope:
[Copy out-of-scope items from above]

Acceptance Criteria:
[Copy acceptance criteria from above]

Let's start with step 1: creating the implementation plan.
```

---

## Notes

- Each PR should take 1-3 days of focused work
- Keep PRs small (<500 lines of code when possible)
- Request code review after each PR
- Don't start PR C until PR B is merged (unless working in parallel)
- PR D is optional - only do if needed

---

## Questions or Issues?

If you encounter blockers:
1. Check existing documentation and tests
2. Review the repository's AGENTS.md file
3. Ask specific questions about implementation details
4. Request clarification on scope or requirements

Good luck! 🚀
