# Follow-up Prompt: RAG Meta Tensor Fix - Integration & Production Readiness

**Previous Session:** fix-notimplementederror-in-rag-module  
**Status:** Core fix ✅ COMPLETE  
**Next Phase:** Integration testing & production deployment

---

## 🎯 Objectives for Next Session

### Phase 1: Integration Test Environment Setup (HIGH PRIORITY)

**Task:** Configure CI environment to support RAG integration tests

**Actions Required:**
1. **HuggingFace Token Configuration**
   ```bash
   # Add HF_TOKEN to GitHub Secrets
   # Update workflow to expose token in test environment
   ```

2. **Pre-cache Common Models**
   ```bash
   # Download and cache in CI:
   # - sentence-transformers/all-MiniLM-L6-v2
   # - sentence-transformers/all-mpnet-base-v2
   ```

3. **Install Optional Dependencies**
   ```bash
   # Add to requirements-test.txt:
   # - faiss-cpu>=1.7.4
   # - openai>=1.0.0
   ```

**Validation:**
- Run full RAG test suite: `pytest tests/test_rag*.py -v`
- Target: 90+ tests passing (currently 31/98 due to missing deps)

---

### Phase 2: Extended Device Testing (MEDIUM PRIORITY)

**Task:** Verify meta tensor fix works across different devices

**Test Matrix:**
| Device | PyTorch Version | Expected Result |
|--------|----------------|-----------------|
| CPU | 2.0+ | ✅ Pass |
| CPU | 1.13 | ✅ Pass (fallback) |
| CUDA | 2.0+ | ✅ Pass |
| MPS (Apple Silicon) | 2.0+ | ⚠️ Test needed |

**Actions:**
1. Create device-specific test suite
2. Test with different model sizes (small, medium, large)
3. Test concurrent model loads
4. Benchmark performance impact of parameter reinitialization

---

### Phase 3: Production Monitoring (MEDIUM PRIORITY)

**Task:** Add observability for meta tensor occurrences in production

**Instrumentation:**
```python
# Add to safe_model_to_device()
if meta_status:
    # Log metric
    metrics.increment('rag.meta_tensor_detected')
    metrics.timing('rag.to_empty_duration', duration)

    # Alert if frequent
    if rate > threshold:
        alert('High meta tensor rate detected')
```

**Dashboards:**
- Meta tensor detection rate over time
- Device transfer latency (p50, p95, p99)
- Failed transfers with stack traces

---

### Phase 4: Performance Optimization (LOW PRIORITY)

**Task:** Minimize overhead of parameter reinitialization

**Investigation Areas:**
1. **Lazy Initialization:** Can we defer reset_parameters()?
2. **Selective Reset:** Which modules actually need reinitialization?
3. **Batch Operations:** Can we reset multiple modules in parallel?

**Benchmarks to Run:**
```python
# Measure overhead
time_without_reset = benchmark(to_empty_only)
time_with_reset = benchmark(to_empty_plus_reset)
overhead = time_with_reset - time_without_reset

# Target: < 10% overhead for typical models
```

---

### Phase 5: Documentation & Training (LOW PRIORITY)

**Task:** Share knowledge about meta tensor handling

**Deliverables:**
1. **Developer Guide:** "Working with Meta Tensors in RAG"
2. **Troubleshooting Doc:** Common meta tensor issues
3. **Best Practices:** Model loading patterns
4. **Team Training:** 30-min session on meta tensors

---

## 🚀 Immediate Next Steps (Priority Order)

1. **CRITICAL:** Set up HF_TOKEN in CI environment
2. **CRITICAL:** Install faiss-cpu and openai in test dependencies
3. **HIGH:** Run full RAG test suite and fix any remaining failures
4. **HIGH:** Create device-specific test matrix
5. **MEDIUM:** Add production monitoring/metrics
6. **LOW:** Optimize parameter reinitialization if needed
7. **LOW:** Create developer documentation

---

## 📊 Success Criteria for Next Session

**Must Have (Critical):**
- [ ] 90+ RAG tests passing (up from 31/98)
- [ ] Integration tests running in CI
- [ ] No new meta tensor errors

**Should Have (High):**
- [ ] Device matrix tests (CPU, CUDA, MPS)
- [ ] Performance benchmarks documented
- [ ] Production metrics configured

**Nice to Have (Medium):**
- [ ] Optimization implemented (if overhead > 10%)
- [ ] Developer guide published

---

## 🔗 References

**Current PR:** copilot/fix-notimplementederror-in-rag-module  
**Documentation:** `.codex/docs/RAG_META_TENSOR_FIX.md`  
**Code:** `src/codex/rag/utils.py`  
**Tests:** `tests/test_rag_*.py`

---

## 💡 Prompt for Next Agent

```markdown
@copilot Continue from PR #[NUMBER] - RAG Meta Tensor Fix Integration Phase

I need to complete integration testing and production readiness for the RAG meta tensor fix.

**Context:**
- Core fix is complete and tested (31/31 unit tests passing)
- Integration tests are failing due to missing HuggingFace models and dependencies
- See `.codex/FOLLOWUP_PROMPT_RAG_META_TENSOR.md` for full context

**Priority Tasks:**
1. Configure HF_TOKEN in CI for model downloads
2. Add faiss-cpu and openai to requirements-test.txt
3. Run full RAG test suite: `pytest tests/test_rag*.py -v`
4. Fix any remaining failures
5. Add production metrics for meta tensor detection

**Expected Outcome:**
- 90+ tests passing (currently 31/98)
- All RAG integration tests running in CI
- Production monitoring in place

**AI Agency Policy Active:** Complete ALL tasks, leave codebase better than found.
```

---

**Prepared by:** GitHub Copilot  
**Date:** 2026-02-10  
**Ready for:** Next agent session
