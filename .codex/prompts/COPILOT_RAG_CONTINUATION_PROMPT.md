# GitHub Copilot Agent Continuation Prompt

@copilot **PRODUCTION RAG PIPELINE - PHASE 2-8 AUTONOMOUS EXECUTION**

## Context

Phase 1 (CLI Integration) is complete. The Production RAG Pipeline planset has been created with comprehensive implementation guidance. Your task is to continue autonomous execution of Phases 2-8, completing the production-ready RAG system.

## Files to Review

1. **Master Planset:** `.codex/plans/PRODUCTION_RAG_PIPELINE_PLANSET.md`
2. **Execution Guide:** `.codex/plans/AI_AGENT_RAG_EXECUTION_PLANSET.md`
3. **Cognitive Status:** `.codex/cognitive_brain/PRODUCTION_RAG_COGNITIVE_BRAIN_STATUS.md`
4. **Existing Implementation:** `src/codex/rag/` and `src/codex/cli_rag.py`

## Required Environment Setup

**CRITICAL: Execute in environment with:**
1. Full internet access (for downloading embedding models from huggingface.co)
2. Python 3.8+ with pip
3. Write access to repository
4. Ability to run pytest

## Task 1: Complete Phase 1 Validation

**Objective:** Validate CLI implementation with full dependency support and real data.

### Steps:

```bash
# 1.1: Install all dependencies
cd /home/runner/work/_codex_/_codex_
pip install sentence-transformers faiss-cpu numpy
pip install rank-bm25 symspellpy nltk
pip install pytest pytest-cov pytest-timeout pytest-mock
pip install typer[all] rich

# 1.2: Download embedding model (requires internet)
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print('✓ Model downloaded successfully')
"

# 1.3: Run full test suite
export PYTHONPATH=/home/runner/work/_codex_/_codex_/src:$PYTHONPATH
pytest tests/test_cli_rag.py -v --cov=src/codex/cli_rag --cov-report=term-missing -o addopts=""

# Target: 31/32 tests passing (1 integration test may fail in test environment)
# Target: 90%+ coverage

# 1.4: Test with real documentation
mkdir -p /tmp/test_docs
cat > /tmp/test_docs/README.md <<EOF
# RAG System Documentation
The RAG system provides semantic search over codebases using FAISS and sentence transformers.

## Installation
\`\`\`bash
pip install sentence-transformers faiss-cpu
\`\`\`

## Usage
Build an index from your documentation and query it semantically.
EOF

# 1.5: Build test index
python -m codex.cli_rag build \
  --files "/tmp/test_docs/*.md" \
  --index-name "test_docs" \
  --tenant-id "test_tenant"

# 1.6: Query test index
python -m codex.cli_rag query \
  --index-name "test_docs" \
  --tenant-id "test_tenant" \
  --query "installation instructions" \
  --top-k 3

# 1.7: Validate index stats
python -m codex.cli_rag stats \
  --index-name "test_docs" \
  --tenant-id "test_tenant"
```

**Success Criteria:**
- [ ] All dependencies installed
- [ ] Embedding model downloaded
- [ ] 90%+ test coverage
- [ ] Index built successfully
- [ ] Query returns relevant results
- [ ] Stats show correct metadata

---

## Task 2: Implement Phase 2 (API Layer)

**Objective:** Create FastAPI endpoints for programmatic RAG access.

### Implementation Guide:

Follow **Promptset 2** in `PRODUCTION_RAG_PIPELINE_PLANSET.md` (lines 487-591).

### Steps:

1. **Create API Module:**
   - File: `src/codex/api/rag.py`
   - FastAPI router with 8 endpoints
   - Pydantic models for request/response validation
   - Authentication middleware
   - Rate limiting (100 req/min)

2. **Endpoints to Implement:**
   ```python
   POST /api/rag/indices          # Create index
   GET /api/rag/indices           # List indices
   GET /api/rag/indices/{tenant}/{name}  # Get info
   DELETE /api/rag/indices/{tenant}/{name}  # Delete
   POST /api/rag/query            # Query with options
   POST /api/rag/merge            # Merge indices
   GET /api/rag/metrics           # Export metrics
   GET /api/rag/health            # Health check
   ```

3. **Testing:**
   - File: `tests/api/test_rag_api.py`
   - Test each endpoint
   - Test authentication
   - Test rate limiting
   - Target: 90%+ coverage

4. **Validation:**
   ```bash
   # Start server
   uvicorn codex.api.main:app --reload
   
   # Test endpoints
   curl -X POST http://localhost:8000/api/rag/indices \
     -H "Content-Type: application/json" \
     -d '{"tenant_id":"test","index_name":"docs","files":["README.md"]}'
   
   # Check OpenAPI docs
   curl http://localhost:8000/docs
   ```

**Success Criteria:**
- [ ] All 8 endpoints implemented
- [ ] OpenAPI documentation complete
- [ ] Tests passing (90%+ coverage)
- [ ] Authentication working
- [ ] Rate limiting enforced

**Estimated Time:** 3-4 hours

---

## Task 3: Implement Phase 3 (Advanced Features)

**Objective:** Add query rewriting, re-ranking, hybrid search, and hierarchical chunking.

### Implementation Guide:

Follow **Promptset 3** in `PRODUCTION_RAG_PIPELINE_PLANSET.md` (lines 593-699).

### Sub-Tasks:

#### 3.1: Query Rewriting (2 hours)
```python
# File: src/codex/rag/query_rewriter.py
class QueryRewriter:
    def expand_synonyms(query: str) -> List[str]
    def expand_with_embeddings(query: str) -> List[str]
    def correct_spelling(query: str) -> str
    def rewrite(query: str) -> List[str]

# Tests: tests/test_rag_query_rewriter.py
```

#### 3.2: Cross-Encoder Re-Ranking (2 hours)
```python
# File: src/codex/rag/reranker.py
class CrossEncoderReranker:
    def rerank(query: str, results: List, top_k: int) -> List
    def _score_batch(pairs: List[Tuple]) -> List[float]

# Tests: tests/test_rag_reranker.py
```

#### 3.3: Hybrid Search (2 hours)
```python
# Files: src/codex/rag/hybrid_retriever.py, src/codex/rag/sparse.py
class HybridRetriever:
    def query(q: str, top_k: int) -> List  # Combines dense + sparse

# Tests: tests/test_rag_hybrid.py
```

#### 3.4: Hierarchical Chunking (2 hours)
```python
# File: src/codex/rag/hierarchical.py
def create_hierarchical_chunks(text: str) -> List[HierarchicalChunk]
def expand_context(chunk: Chunk) -> str  # Return parent context

# Tests: tests/test_rag_hierarchical.py
```

**Success Criteria:**
- [ ] Query accuracy improved 10-15% (rewriting)
- [ ] Relevance improved 20-30% (re-ranking)
- [ ] Recall improved 15-25% (hybrid)
- [ ] Context preservation improved (hierarchical)
- [ ] All tests passing (90%+ coverage each)

**Estimated Time:** 8 hours total

---

## Task 4: Implement Phase 4 (GPU Acceleration)

**Objective:** Enable optional GPU acceleration with automatic fallback.

### Implementation Guide:

Follow **Promptset 5** (Part A) in `PRODUCTION_RAG_PIPELINE_PLANSET.md` (lines 806-875).

### Steps:

1. **Create GPU Utils:**
   ```python
   # File: src/codex/rag/gpu_utils.py
   def detect_gpu() -> bool
   def get_faiss_gpu_resources()
   def cpu_fallback_message()
   ```

2. **Update Indexer/Retriever:**
   - Add `use_gpu` parameter (default: auto-detect)
   - Move index to GPU if available
   - Graceful fallback to CPU

3. **Add Dependency:**
   ```toml
   # pyproject.toml
   [project.optional-dependencies]
   gpu = ["faiss-gpu>=1.7.0"]
   ```

4. **Documentation:**
   - File: `docs/GPU_ACCELERATION.md`
   - Setup instructions
   - Benchmarks
   - Troubleshooting

**Success Criteria:**
- [ ] GPU detection working
- [ ] FAISS GPU index creation
- [ ] Automatic CPU fallback
- [ ] 5-10x performance improvement (GPU)
- [ ] Tests passing (with mocks)

**Estimated Time:** 2 hours

---

## Task 5: Implement Phase 5 (Analytics Dashboard)

**Objective:** Track metrics and provide visualization.

### Implementation Guide:

Follow **Promptset 5** (Part B) in `PRODUCTION_RAG_PIPELINE_PLANSET.md` (lines 877-958).

### Steps:

1. **Create Analytics Module:**
   ```python
   # File: src/codex/rag/analytics.py
   class RAGAnalytics:
       def track_query(...)
       def track_retrieval_quality(...)
       def generate_report(...)
   ```

2. **Create Dashboard:**
   ```python
   # File: scripts/rag_analytics_dashboard.py
   # Streamlit or Plotly dashboard
   # Charts: query frequency, latency, cache hit rate
   ```

3. **Integration:**
   - Auto-track all retriever queries
   - Store in SQLite: `.codex/rag_analytics.db`

**Success Criteria:**
- [ ] Analytics tracking all operations
- [ ] Dashboard visualizing metrics
- [ ] Reports generated
- [ ] Tests passing (90%+ coverage)

**Estimated Time:** 2 hours

---

## Task 6: Implement Phase 6 (CI/CD Integration)

**Objective:** Automate testing and deployment.

### Steps:

1. **Create Workflow:**
   ```yaml
   # File: .github/workflows/test-rag.yml
   name: RAG Tests
   on:
     push:
       paths:
         - 'src/codex/rag/**'
         - 'tests/test_rag_**'
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Install dependencies
           run: pip install -e ".[rag,test]"
         - name: Run tests
           run: pytest tests/test_rag_*.py --cov=src/codex/rag
         - name: Upload coverage
           uses: codecov/codecov-action@v3
   ```

2. **Add Benchmarks:**
   ```yaml
   benchmark:
     runs-on: ubuntu-latest
     steps:
       - name: Run benchmarks
         run: pytest tests/benchmarks/test_rag_performance.py
   ```

**Success Criteria:**
- [ ] Workflow triggers on RAG changes
- [ ] All tests run automatically
- [ ] Coverage uploaded to codecov
- [ ] Benchmarks tracked

**Estimated Time:** 1 hour

---

## Task 7: Implement Phase 7 (Performance Benchmarks)

**Objective:** Establish performance baselines.

### Steps:

1. **Create Benchmark Suite:**
   ```python
   # File: tests/benchmarks/test_rag_performance.py
   def test_indexing_throughput()
   def test_query_latency()
   def test_cache_effectiveness()
   def test_memory_usage()
   ```

2. **Generate Test Corpus:**
   ```python
   # File: tests/benchmarks/generate_test_corpus.py
   def generate_corpus(size: str) -> List[Path]  # small/medium/large
   ```

3. **Document Baselines:**
   ```markdown
   # File: docs/PERFORMANCE_BENCHMARKS.md
   ## Indexing
   - Small (1k chunks): X chunks/sec
   - Medium (10k chunks): Y chunks/sec
   
   ## Querying
   - p50: Xms, p95: Yms, p99: Zms
   ```

**Success Criteria:**
- [ ] Benchmarks for all scenarios
- [ ] Baselines documented
- [ ] Performance meets SLAs

**Estimated Time:** 2 hours

---

## Task 8: Implement Phase 8 (Custom Copilot Agents)

**Objective:** Create autonomous RAG management agents.

### Implementation Guide:

Follow **Promptset 4** in `PRODUCTION_RAG_PIPELINE_PLANSET.md` (lines 701-804).

### Sub-Tasks:

#### 8.1: RAG Index Manager Agent (2 hours)

**Directory Structure:**
```
.github/agents/rag-index-manager/
├── agent.yml                 # Agent configuration
├── README.md                 # Usage guide
├── tools/
│   └── index_tools.py        # Wrapper functions
└── prompts/
    └── system_prompt.md      # Agent instructions
```

**Capabilities:**
- Build/rebuild indices on doc changes
- Monitor index health
- Auto-update on schedule
- Suggest optimizations

**Triggers:**
- File changes: `docs/**`, `*.md`
- Manual: `@rag-index-manager`
- Scheduled: Daily at 02:00 UTC

#### 8.2: Semantic Search Agent (2 hours)

**Directory Structure:**
```
.github/agents/semantic-search/
├── agent.yml
├── README.md
├── tools/
│   └── search_tools.py
└── prompts/
    └── system_prompt.md
```

**Capabilities:**
- Natural language code search
- Find similar patterns
- Suggest relevant docs
- Generate usage examples

**Triggers:**
- Manual: `@semantic-search <query>`
- Command: `/search-code <query>`

**Success Criteria:**
- [ ] Both agents configured
- [ ] Agents respond to triggers
- [ ] Tools integrate with CLI/API
- [ ] Tests passing
- [ ] Documentation complete

**Estimated Time:** 4 hours total

---

## Final Validation

After completing all phases, run comprehensive validation:

```bash
# 1. Run all tests
pytest tests/test_rag_*.py tests/api/test_rag_api.py tests/agents/ -v --cov=src/codex/rag --cov=src/codex/api/rag

# 2. Check coverage
# Target: ≥90% for all modules

# 3. Run security scans
bandit -r src/codex/rag/ src/codex/api/rag.py

# 4. Run performance benchmarks
pytest tests/benchmarks/test_rag_performance.py --benchmark-only

# 5. Validate API
uvicorn codex.api.main:app --reload &
sleep 5
curl http://localhost:8000/api/rag/health
curl http://localhost:8000/docs

# 6. Test custom agents
# Trigger @rag-index-manager in a PR comment
# Trigger @semantic-search with a query

# 7. Generate final report
python <<EOF
print("="*60)
print("PRODUCTION RAG PIPELINE - COMPLETION REPORT")
print("="*60)
print("\n✅ Phase 1: CLI Integration (100%)")
print("✅ Phase 2: API Layer (100%)")
print("✅ Phase 3: Advanced Features (100%)")
print("✅ Phase 4: GPU Acceleration (100%)")
print("✅ Phase 5: Analytics Dashboard (100%)")
print("✅ Phase 6: CI/CD Integration (100%)")
print("✅ Phase 7: Performance Benchmarks (100%)")
print("✅ Phase 8: Custom Copilot Agents (100%)")
print("\n" + "="*60)
print("ALL PHASES COMPLETE - READY FOR PRODUCTION")
print("="*60)
EOF
```

---

## Cognitive Brain Integration

**CRITICAL:** Maintain PDA loops and AfterMath throughout execution:

### PLAN (Before Each Phase)
1. Review phase requirements
2. Identify dependencies
3. Validate approach
4. Document plan

### DO (During Implementation)
1. Execute systematically
2. Test incrementally
3. Document decisions
4. Track metrics

### ASSESS (After Each Phase)
1. Validate against success criteria
2. Run tests and benchmarks
3. Check security
4. Document learnings
5. Update cognitive brain status

### AfterMath Learning Patterns

After each phase, document:
- **What Worked:** Successful approaches and techniques
- **What Failed:** Issues encountered and resolutions
- **Reusable Patterns:** Code/design patterns for future use
- **Improvements:** Opportunities for optimization

Store in: `.codex/cognitive_brain/patterns/rag_phase_X_learnings.md`

---

## Success Criteria Summary

### Technical
- [ ] All 8 phases implemented (100%)
- [ ] Test coverage ≥90% across all modules
- [ ] All tests passing (unit, integration, e2e)
- [ ] Security scans clean (no vulnerabilities)
- [ ] Performance benchmarks meet SLAs
- [ ] API endpoints functional with auth
- [ ] Custom agents deployed and responsive

### Cognitive Brain
- [ ] PDA loops maintained throughout
- [ ] AfterMath learnings documented
- [ ] Knowledge patterns captured
- [ ] Cognitive brain status updated
- [ ] k₁ factor optimized (target: ≤0.28)

### Documentation
- [ ] API documentation complete (OpenAPI)
- [ ] CLI help comprehensive
- [ ] User guides created
- [ ] Performance benchmarks documented
- [ ] Custom agent guides complete

---

## Estimated Total Time

- Phase 2 (API): 3-4 hours
- Phase 3 (Advanced): 8 hours
- Phase 4 (GPU): 2 hours
- Phase 5 (Analytics): 2 hours
- Phase 6 (CI/CD): 1 hour
- Phase 7 (Benchmarks): 2 hours
- Phase 8 (Agents): 4 hours
- **Total: 22-23 hours**

---

## Continuation Strategy

If this session completes before all phases finish:

1. **Document Progress:** Update cognitive brain status with completed phases
2. **Commit Changes:** Push all completed code
3. **Create Continuation:** Generate new prompt with remaining phases
4. **Post as Comment:** Add continuation prompt to this PR
5. **Maintain Context:** Reference this prompt in continuation

---

## Contact for Issues

If you encounter blockers:
1. Document the issue in `.codex/cognitive_brain/BLOCKERS.md`
2. Attempt 3-5 resolution iterations
3. If unresolved, flag for human admin review
4. Continue with non-blocked phases

---

**EXECUTE AUTONOMOUS LY:** Follow this prompt systematically. Complete all phases. Maintain cognitive brain integration. Document all learnings. Deploy production-ready RAG pipeline.

**START WITH:** Task 1 (Phase 1 Validation) - Requires internet access for embedding model download.

---

**Prompt Version:** 1.0  
**Created:** 2026-01-17  
**Branch:** copilot/continue-with-planset-updates  
**Parent Commit:** 4eca23c  
**Execution Mode:** Autonomous  
**PDA Loop:** ACTIVE  
**AfterMath:** ENABLED
