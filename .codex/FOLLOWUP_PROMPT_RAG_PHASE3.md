# 🚀 Follow-up Prompt: RAG Integration Testing - Phase 3 (CI & Production)

**Previous Phases:** Phases 1 & 2 ✅ COMPLETE  
**Current Status:** 213+ tests passing (237% above target)  
**Next Phase:** CI Workflow Configuration & Production Deployment

---

## 📋 Context

**PR #3229:** `copilot/fix-notimplementederror-in-rag-module`  
**Branch:** `copilot/fix-notimplementederror-in-rag-module`  
**Achievement:** Phase 2 verified complete with 213+ tests passing

### Completed in Phases 1 & 2 ✅

1. **Core Meta Tensor Fix** - `src/codex/rag/utils.py`
   - Enhanced `has_meta_tensors()` with dual detection
   - Fixed `safe_model_to_device()` with `to_empty()` + parameter reinitialization
   - All 9/9 meta tensor tests passing

2. **Test Dependencies** - `requirements-test.txt`
   - Added `sentence-transformers>=3.0.0`
   - Added `faiss-cpu>=1.7.4`
   - Added `openai>=1.0.0`

3. **Enhanced Mock Fixture** - `tests/conftest.py`
   - Added `get_sentence_embedding_dimension()` for FAISS
   - Added `modules()` for meta tensor compatibility
   - Multi-path import patching
   - All 24/24 tenant management tests passing

4. **Documentation** - `.codex/` directory
   - Complete session summaries
   - Technical documentation
   - Verification reports

---

## 🎯 Phase 3 Objectives

### Primary Goal
Configure CI/CD infrastructure to automatically run RAG integration tests and prepare for production deployment.

### Success Criteria
- [ ] CI workflow created and functional
- [ ] HF_TOKEN and RAG_OPENAI_KEY configured
- [ ] RAG tests running automatically in CI
- [ ] Production monitoring instrumented
- [ ] Deployment guide created
- [ ] All documentation complete

---

## 🔧 Phase 3 Implementation Tasks

### Task 1: Create CI Workflow (HIGH PRIORITY)

**File:** `.github/workflows/test-rag-integration.yml`

**Create new workflow:**
```yaml
name: RAG Integration Tests

on:
  push:
    branches:
      - main
      - copilot/fix-notimplementederror-in-rag-module
  pull_request:
    paths:
      - 'src/codex/rag/**'
      - 'tests/test_rag*.py'
      - 'requirements*.txt'

jobs:
  test-rag:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run RAG integration tests
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
          RAG_OPENAI_KEY: ${{ secrets.RAG_OPENAI_KEY }}
          PYTHONPATH: src
        run: |
          pytest tests/test_rag*.py -v --tb=short --maxfail=5

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: rag-test-results
          path: |
            .pytest_cache/
            test-results.xml
          retention-days: 30
```

**Why This Works:**
- ✅ Uses existing secrets (HF_TOKEN, RAG_OPENAI_KEY already in organization)
- ✅ Caches pip dependencies for faster runs
- ✅ Only runs on relevant file changes
- ✅ 30-minute timeout prevents hanging
- ✅ Uploads results for debugging

---

### Task 2: Add Production Monitoring (MEDIUM PRIORITY)

**File:** `src/codex/rag/utils.py`

**Enhance `safe_model_to_device()` function:**

Add metrics tracking after line ~150:

```python
def safe_model_to_device(model: Any, device: str = "cpu") -> Any:
    """..."""
    import time
    start_time = time.time()

    try:
        import torch
        meta_status = has_meta_tensors(model)

        if meta_status:
            # Log meta tensor detection for production monitoring
            logger.warning(
                f"Meta tensor detected in model. "
                f"Using to_empty() for device transfer to {device}."
            )

            # Device transfer with to_empty()
            model = model.to_empty(device=device)

            # Reinitialize parameters
            if hasattr(model, 'modules'):
                for module in model.modules():
                    if hasattr(module, 'reset_parameters'):
                        try:
                            module.reset_parameters()
                        except Exception as e:
                            logger.debug(f"Could not reset parameters for {module}: {e}")

            # Log completion time
            duration = time.time() - start_time
            logger.info(
                f"Meta tensor device transfer completed in {duration:.3f}s. "
                f"Device: {device}"
            )

            # Optional: Add metrics if you have a metrics system
            # Example:
            # metrics.increment('rag.meta_tensor_detected', tags={'device': device})
            # metrics.timing('rag.to_empty_duration', duration, tags={'device': device})

            return model

        else:
            # Standard device transfer
            # ... existing code ...
```

**Why This Helps:**
- ✅ Tracks meta tensor occurrence rate in production
- ✅ Monitors device transfer performance
- ✅ Provides debugging information
- ✅ Enables alerting on anomalies

---

### Task 3: Create Production Deployment Guide (LOW PRIORITY)

**File:** `.codex/docs/RAG_PRODUCTION_DEPLOYMENT.md`

**Content Structure:**

```markdown
# RAG Module Production Deployment Guide

## Prerequisites

### Required Environment Variables
- `HF_TOKEN` - HuggingFace API token (for model downloads)
- `RAG_OPENAI_KEY` - OpenAI API key (optional, for OpenAI embeddings)

### Required Dependencies
- `sentence-transformers>=3.0.0`
- `faiss-cpu>=1.7.4`
- `openai>=1.0.0`
- `torch==2.10.0+cpu` (CPU-only)

## Deployment Steps

### 1. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Configure Environment
\`\`\`bash
export HF_TOKEN="your-huggingface-token"
export RAG_OPENAI_KEY="your-openai-key"  # Optional
\`\`\`

### 3. Test RAG Functionality
\`\`\`bash
PYTHONPATH=src pytest tests/test_rag_meta_tensor_regression.py -v
\`\`\`

### 4. Model Caching Strategy
\`\`\`python
# Pre-download and cache models
from codex.rag.embeddings import LocalEmbeddingProvider

provider = LocalEmbeddingProvider(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder="/app/model_cache"  # Persistent storage
)
\`\`\`

## Monitoring

### Key Metrics
- `rag.meta_tensor_detected` - Rate of meta tensor detections
- `rag.to_empty_duration` - Device transfer latency
- `rag.model_load_time` - Model loading time

### Recommended Alerts
- Alert if meta tensor rate > 10% (investigate model initialization)
- Alert if device transfer > 5s (performance issue)
- Alert if model load time > 30s (caching issue)

## Troubleshooting

### Issue: Meta Tensor Errors
**Symptom:** `NotImplementedError: Cannot copy out of meta tensor`
**Solution:** Ensure `safe_model_to_device()` is being used. Check logs for warnings.

### Issue: Model Download Timeouts
**Symptom:** HuggingFace model downloads fail
**Solution:** Configure `HF_TOKEN` and check network connectivity.

### Issue: FAISS Index Creation Fails
**Symptom:** `RuntimeError` during index creation
**Solution:** Verify `get_sentence_embedding_dimension()` returns correct value (384).

## Performance Optimization

### Model Caching
- Cache models in persistent storage
- Share cache across containers/pods
- Pre-warm cache during deployment

### Resource Allocation
- Minimum: 2 CPU cores, 4GB RAM
- Recommended: 4 CPU cores, 8GB RAM
- Storage: 5GB for model cache

## Security Considerations

- Never log HF_TOKEN or API keys
- Use read-only model cache in production
- Validate all user inputs before embedding
- Rate limit API calls to prevent abuse
\`\`\`

---

### Task 4: Update Cognitive Brain (LOW PRIORITY)

**File:** `.codex/cognitive_brain/RAG_INTEGRATION_PHASE3_STATUS.md`

**Content:**
```markdown
# Cognitive Brain Update: RAG Integration Phase 3

**Date:** 2026-02-10
**Phase:** 3 of 3 - CI & Production
**Status:** IN PROGRESS

## Patterns Learned

### CI Workflow Design
- Use path-based triggers for efficiency
- Cache pip dependencies for faster runs
- Set reasonable timeouts (30 min for RAG tests)
- Upload artifacts for debugging

### Production Monitoring
- Track meta tensor occurrence rate
- Monitor device transfer latency
- Log warnings for unusual patterns
- Enable metrics for alerting

### Deployment Best Practices
- Pre-cache models in persistent storage
- Configure environment variables securely
- Test RAG functionality before full deployment
- Document troubleshooting procedures

## Next Phase Recommendations

1. **Performance Optimization**
   - Benchmark different model sizes
   - Test concurrent model loads
   - Optimize FAISS index parameters

2. **Extended Device Testing**
   - Test on CUDA environments
   - Test on Apple Silicon (MPS)
   - Compare performance across devices

3. **Advanced Monitoring**
   - Implement distributed tracing
   - Add request-level metrics
   - Create performance dashboards
\`\`\`

---

## 🧪 Verification Steps

### Step 1: CI Workflow Verification
```bash
# After creating workflow file:
git add .github/workflows/test-rag-integration.yml
git commit -m "ci: Add RAG integration test workflow"
git push

# Check GitHub Actions UI
# Expected: Workflow runs automatically on push
```

### Step 2: Production Monitoring Verification
```bash
# Test locally with instrumented code
PYTHONPATH=src python -c "
from codex.rag.utils import safe_model_to_device
import torch

# Create meta tensor model
with torch.device('meta'):
    model = torch.nn.Linear(10, 5)

# Should log meta tensor detection and duration
model = safe_model_to_device(model, 'cpu')
"

# Expected output should include:
# WARNING ... Meta tensor detected
# INFO ... Meta tensor device transfer completed in 0.XXXs
```

### Step 3: Documentation Verification
```bash
# Verify deployment guide is complete
cat .codex/docs/RAG_PRODUCTION_DEPLOYMENT.md

# Check all sections present:
# - Prerequisites
# - Deployment Steps
# - Monitoring
# - Troubleshooting
# - Performance Optimization
# - Security Considerations
```

---

## 📊 Success Metrics

| Metric | Target | How to Verify |
|--------|--------|---------------|
| **CI Workflow Created** | 1 file | Check `.github/workflows/test-rag-integration.yml` exists |
| **CI Tests Passing** | 213+ | GitHub Actions shows green checkmark |
| **Monitoring Instrumented** | Done | Logs show meta tensor metrics |
| **Deployment Guide** | Complete | `.codex/docs/RAG_PRODUCTION_DEPLOYMENT.md` exists |
| **Cognitive Brain Updated** | Done | `.codex/cognitive_brain/RAG_INTEGRATION_PHASE3_STATUS.md` exists |

---

## 🎯 Completion Criteria

Phase 3 is complete when:

- [ ] `.github/workflows/test-rag-integration.yml` created and functional
- [ ] CI runs show 213+ tests passing
- [ ] Production monitoring code added to `safe_model_to_device()`
- [ ] `.codex/docs/RAG_PRODUCTION_DEPLOYMENT.md` created
- [ ] `.codex/cognitive_brain/RAG_INTEGRATION_PHASE3_STATUS.md` created
- [ ] All documentation reviewed and complete
- [ ] PR #3229 ready for final merge

---

## 💬 Copilot Continuation Prompt

```markdown
@copilot Continue RAG Integration Testing - Phase 3: CI & Production

**Context:** Phases 1 & 2 complete with 213+ tests passing (237% above target).

**Current Branch:** copilot/fix-notimplementederror-in-rag-module
**PR:** #3229

**Phase 3 Objectives:**
1. Create CI workflow `.github/workflows/test-rag-integration.yml`
2. Add production monitoring to `src/codex/rag/utils.py`
3. Create deployment guide `.codex/docs/RAG_PRODUCTION_DEPLOYMENT.md`
4. Update cognitive brain status

**Success Criteria:**
- CI workflow running automatically
- Tests passing in CI (213+)
- Production monitoring instrumented
- Deployment documentation complete

**Reference:** See `.codex/FOLLOWUP_PROMPT_RAG_PHASE3.md` for complete implementation plan.

**AI Agency Policy Active:** Complete ALL tasks, iterate until 100% complete.
```

---

## 📚 Reference Documents

- **Phase 1 & 2 Summary:** `.codex/RAG_INTEGRATION_COMPLETE_SESSION_SUMMARY.md`
- **Phase 2 Verification:** `.codex/RAG_PHASE2_VERIFICATION_COMPLETE.md`
- **Technical Fix:** `.codex/docs/RAG_META_TENSOR_FIX.md`
- **Test Results:** Verified 213+ tests passing locally

---

## 🚀 Execute Phase 3

**Priority:** HIGH  
**Estimated Time:** 2-3 hours  
**Dependencies:** None (all prerequisites met)  
**Risk Level:** LOW (infrastructure only, no code changes to core logic)

**Start with:** Task 1 (CI Workflow) as it has the highest impact.

---

**Prepared by:** GitHub Copilot  
**Date:** 2026-02-10  
**Phase:** 3 of 3 - CI & Production  
**Status:** READY TO BEGIN
