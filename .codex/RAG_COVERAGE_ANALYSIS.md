# RAG Module Coverage Analysis
*Generated without running tests - static code analysis*
## Executive Summary
### Core Modules Analysis
| Module | Lines | Classes | Functions | Est. Coverage | Status |
|--------|-------|---------|-----------|---------------|--------|
| embeddings | 628 | 5 | 1 | 83% | ✅ Good |
| gpu_utils | 135 | 0 | 5 | 0% | ⚠️ Needs Tests |
| indexer | 756 | 2 | 6 | 75% | ⚠️ Needs Tests |
| monitoring | 539 | 3 | 2 | 100% | ✅ Good |
| postprocess | 173 | 1 | 1 | 100% | ✅ Good |
| prompt | 352 | 2 | 3 | 100% | ✅ Good |
| retriever | 636 | 4 | 0 | 100% | ✅ Good |
| utils | 175 | 1 | 1 | 100% | ✅ Good |

## Detailed Gap Analysis
### Core Modules

#### embeddings.py (628 lines)

**Untested Classes (1):**
- `TfidfEmbeddingProvider` - Priority: HIGH
  - Methods: __init__, encode, get_dimension

#### gpu_utils.py (135 lines)

**Untested Functions (5):**
- `check_cuda_available()` - Priority: MEDIUM
- `get_gpu_memory()` - Priority: MEDIUM
- `select_device()` - Priority: MEDIUM
- `get_optimal_batch_size()` - Priority: MEDIUM
- `try_gpu_index()` - Priority: MEDIUM

#### indexer.py (756 lines)

**Untested Classes (2):**
- `IndexOperation` - Priority: MEDIUM
- `TenantOperationResult` - Priority: MEDIUM

### Sub-Modules

#### analytics/

**dashboard.py** (227 lines)
- Untested classes: AnalyticsDashboard

**metrics_db.py** (230 lines)
- Untested classes: QueryMetric, MetricsDatabase

#### benchmarks/

**e2e_bench.py** (221 lines)
- Untested functions: benchmark_e2e_pipeline, _run_complete_pipeline, benchmark_multi_query_types, _build_e2e_index, _execute_query

**indexing_bench.py** (157 lines)
- Untested functions: benchmark_indexing, _generate_test_corpus, _build_index, benchmark_parallel_vs_sequential

**retrieval_bench.py** (196 lines)
- Untested functions: benchmark_retrieval, _build_test_index, _query_index, _calculate_percentiles, _percentile, _get_latency_percentiles, benchmark_cache_effectiveness

**runner.py** (217 lines)
- Untested classes: BenchmarkResult, BenchmarkRunner

#### cache/

**distributed_cache.py** (474 lines)
- Untested classes: BaseCacheBackend, RedisCacheBackend

#### ingestion/

**chunker.py** (487 lines)
- Untested classes: BaseChunker

#### providers/

**gpt4all_provider.py** (117 lines)
- Untested classes: GPT4AllEmbeddingProvider

**llamacpp_provider.py** (144 lines)
- Untested classes: LlamaCppEmbeddingProvider

**ollama_provider.py** (141 lines)
- Untested classes: OllamaEmbeddingProvider

## Test Creation Recommendations

### Priority 1: Core Functionality (HIGH)

- **embeddings.py**: Test all provider classes (LocalSentenceTransformer, OpenAI, Cached)
  - Test `encode()` with various input sizes
  - Test caching behavior
  - Test error handling for missing models
  
- **indexer.py**: Test index operations
  - Test `chunk_text()` with edge cases
  - Test `embed_chunks()` with different models
  - Test `persist_index()` and `load_index()` roundtrip
  - Test multi-tenant operations
  
- **retriever.py**: Test retrieval logic
  - Test `Retriever.query()` with various k values
  - Test `MultiIndexRetriever` merging logic
  - Test `CachedRetriever` cache behavior

### Priority 2: Monitoring & Utils (MEDIUM)

- **monitoring.py**: Test metrics tracking
  - Test `RAGMetrics` metric recording
  - Test window size configurations
  - Test prometheus/cloudwatch export
  
- **utils.py**: Test utility functions
  - Test `safe_model_load()` with different devices
  - Test `ProvenanceMetadata` creation
  
- **gpu_utils.py**: Test GPU detection and selection
  - Test `check_cuda_available()`
  - Test `select_device()` fallback logic
  - Test `get_optimal_batch_size()`

### Priority 3: Sub-Modules (MEDIUM-LOW)

- **cache/**: Already has comprehensive tests
- **ingestion/**: Already has tests for chunker, pipeline, preprocessor, validator
- **providers/**: Test alternative providers (ollama, llamacpp, gpt4all)
  - Test provider initialization
  - Test encode() methods
  - Test error handling
  
- **analytics/**: Test dashboard and metrics_db
- **benchmarks/**: Test benchmark runners (lower priority)

## Test Coverage Goals

| Module | Current Est. | Target | Gap |
|--------|-------------|--------|-----|
| embeddings.py | 60-70% | 90% | +20-30% |
| indexer.py | 70-80% | 90% | +10-20% |
| retriever.py | 70-80% | 90% | +10-20% |
| monitoring.py | 60-70% | 85% | +15-25% |
| utils.py | 50% | 85% | +35% |
| gpu_utils.py | 30% | 80% | +50% |
| postprocess.py | 60% | 85% | +25% |
| prompt.py | 70% | 85% | +15% |
| **Overall Target** | **~65%** | **88%** | **+23%** |

## Next Steps (Phase 21.2)

1. **Run actual coverage** with pytest-cov to get precise numbers
2. **Create missing tests** following priority order:
   - Start with untested classes in embeddings.py
   - Add error path tests for all core modules
   - Add integration tests for multi-module scenarios
3. **Validate coverage improvement** after each test addition
4. **Document test patterns** for future reference
