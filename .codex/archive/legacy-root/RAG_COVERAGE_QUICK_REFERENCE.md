# RAG Coverage Analysis - Quick Reference

## 🎯 Executive Summary

- **Current Coverage:** ~58% (estimated)
- **Target Coverage:** 80%
- **Total Lines:** 8,470
- **Gap:** ~3,500 lines (+22%)

## 🚨 Priority 1: CRITICAL (Must Fix)

### 1. gpu_utils.py - 0% coverage
- **Lines:** 135
- **Functions:** 5 (all untested)
- **Impact:** Core GPU functionality
- **Action:** Create `tests/test_rag_gpu_utils.py`

### 2. utils.py - 40% coverage
- **Gap:** ~105 lines
- **Functions:** `safe_model_load()`, `ProvenanceMetadata`
- **Impact:** Used by all providers
- **Action:** Create `tests/test_rag_utils_comprehensive.py`

### 3. TfidfEmbeddingProvider - 0% coverage
- **Gap:** ~100 lines
- **Impact:** Alternative embedding method
- **Action:** Extend `tests/test_rag_embeddings.py`

**Total P1 Impact:** ~340 lines, +8-10% coverage

## ⚠️ Priority 2: HIGH (Should Fix)

### 4. monitoring.py exports - 70% coverage
- **Gap:** ~100 lines
- **Functions:** `export_prometheus()`, `export_cloudwatch()`
- **Impact:** Production monitoring
- **Action:** Extend `tests/test_rag_monitoring.py`

### 5. providers/ - 10% coverage
- **Gap:** ~360 lines
- **Modules:** ollama, llamacpp, gpt4all
- **Impact:** Alternative backends
- **Action:** Create `tests/rag/providers/test_*.py`

**Total P2 Impact:** ~460 lines, +10-12% coverage

## 📊 Module Coverage Summary

| Module | Lines | Coverage | Priority |
|--------|-------|----------|----------|
| embeddings.py | 628 | 80% | HIGH |
| indexer.py | 756 | 85% | MEDIUM |
| retriever.py | 636 | 90% | LOW |
| monitoring.py | 539 | 70% | HIGH |
| utils.py | 175 | 40% | **CRITICAL** |
| gpu_utils.py | 135 | 0% | **CRITICAL** |
| postprocess.py | 173 | 85% | LOW |
| prompt.py | 352 | 85% | LOW |

## 📝 Test Files to Create

### New Files
- ✅ `tests/test_rag_gpu_utils.py` (P1)
- ✅ `tests/test_rag_utils_comprehensive.py` (P1)
- ✅ `tests/rag/providers/test_ollama_provider.py` (P2)
- ✅ `tests/rag/providers/test_llamacpp_provider.py` (P2)
- ✅ `tests/rag/providers/test_gpt4all_provider.py` (P2)

### Files to Extend
- 📝 `tests/test_rag_embeddings.py` - Add TfidfProvider
- 📝 `tests/test_rag_monitoring.py` - Add exports

## ⏱️ Time Estimate

- **Day 1:** gpu_utils + utils tests (8h) → +5%
- **Day 2:** Tfidf + monitoring (6h) → +7% (total: 70%)
- **Day 3:** Providers (8h) → +8% (total: 78%)
- **Day 4:** Edge cases + polish (8h) → +2% (total: 80%)

## ✅ Success Criteria

**Must Achieve:**
- gpu_utils.py: 80%+
- utils.py: 85%+
- TfidfEmbeddingProvider: 90%+

**Should Achieve:**
- monitoring.py: 88%+
- providers/: 75%+
- Overall: 75%+

**Stretch Goal:**
- Overall: 80%+

## 🔍 Key Test Scenarios

### gpu_utils.py
```python
- test_cuda_available_when_present()
- test_cuda_unavailable_fallback()
- test_prefer_gpu_when_available()
- test_fallback_to_cpu()
- test_optimal_batch_size()
```

### utils.py
```python
- test_safe_model_load_to_cpu()
- test_safe_model_load_to_gpu()
- test_handle_meta_device_tensors()
- test_provenance_metadata_creation()
- test_metadata_serialization()
```

### TfidfEmbeddingProvider
```python
- test_fit_corpus()
- test_encode_after_fit()
- test_unknown_words_handling()
- test_dimension_consistency()
```

## 📈 Coverage Validation

```bash
# Run RAG coverage
pytest tests/rag/ tests/test_rag*.py \
    --cov=src/codex/rag \
    --cov-report=term \
    --cov-report=html

# Check specific module
pytest tests/test_rag_gpu_utils.py \
    --cov=src/codex/rag/gpu_utils.py \
    --cov-fail-under=80
```

## 📚 Full Reports

- Detailed Analysis: `RAG_COVERAGE_ANALYSIS_PHASE_21_1.md`
- Gap Analysis: `RAG_COVERAGE_GAP_ANALYSIS_DETAILED.md`
- Static Analysis: `RAG_COVERAGE_ANALYSIS.md`

---

**Phase 21.1 Complete** ✅  
**Ready for Phase 21.2 Test Generation** 🚀
