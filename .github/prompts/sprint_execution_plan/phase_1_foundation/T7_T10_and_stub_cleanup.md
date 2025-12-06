# T7-T10 & Additional Tasks - Comprehensive Autonomous Prompts

This file contains condensed prompts for the remaining high-priority tasks and scaffolding for all 298 stubs.

## T7: Health/Readiness Probes

🎯 **COPILOT INSTRUCTION:** @workspace Implement health checks

**Context:** No health endpoints (deployment maturity gap)

**Implementation:**
```python
# File: src/codex_ml/serving/health.py
from fastapi import APIRouter
import psutil

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "healthy", "timestamp": time.time()}

@router.get("/ready")
def readiness():
    # Check model loaded, disk space, etc.
    return {"ready": True, "checks": {...}}
```

**Docker:** Add HEALTHCHECK instruction
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

**Validation:** `curl localhost:8000/health`

---

## T8: Prometheus Metrics Export

🎯 **COPILOT INSTRUCTION:** @workspace Add metrics endpoint

**Implementation:**
```python
# File: src/codex_ml/monitoring/metrics.py
from prometheus_client import Counter, Histogram, generate_latest

requests = Counter('requests_total', 'Total requests')
latency = Histogram('request_latency_seconds', 'Request latency')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

**Validation:** `curl localhost:8000/metrics | grep requests_total`

---

## T9: Security Scans in CI

🎯 **COPILOT INSTRUCTION:** @workspace Wire security tools to CI

**Implementation:**
```yaml
# .github/workflows/security.yml
name: Security Scans
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run bandit
        run: |
          pip install bandit
          bandit -r src/ -ll -f json -o bandit-report.json
      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit --require-hashes
      - name: Run detect-secrets
        run: |
          pip install detect-secrets
          detect-secrets scan --baseline .secrets.baseline
```

---

## T10: SBOM Generation

🎯 **COPILOT INSTRUCTION:** @workspace Generate SBOMs

**Implementation:**
```bash
# Install tools
pip install cyclonedx-bom

# Generate SBOM
cyclonedx-py -o sbom.json

# Add to release process
python setup.py bdist_wheel
cyclonedx-py -o dist/sbom.json
```

---

## Stub Cleanup Campaign (298 stubs)

🎯 **COPILOT INSTRUCTION:** @workspace Systematically resolve all stubs

### Priority P0 Stubs (15 items)

**Blocking stubs that break functionality:**

1. `src/codex_ml/serving/inference_server.py:255` - NotImplementedError("FastAPI not installed")
   - **Fix:** Add FastAPI to requirements or graceful fallback

2. `src/codex_ml/metrics/writers.py:101` - NotImplementedError
   - **Fix:** Implement abstract method or remove from registry

3-15. [Additional P0 stubs - implement similarly]

### Priority P1 Stubs (45 items)

**High-impact TODOs:**

1. `src/codex_ml/training/functional_training.py:98` - TODO: wire scheduler resume
   - **Fix:** Implement scheduler state save/restore

2. `training/engine_hf_trainer.py:835` - TODO: DDP/FSDP hooks
   - **Fix:** Add distributed training support

[Continue for all P1 items]

### Batch Resolution Strategy

**Auto-generate sub-prompts for each capability domain:**

```yaml
tokenization_stubs:
  - prompt: "Resolve 12 TODOs in tokenization module"
  - files: [tokenization/pipeline.py, tokenization/train_tokenizer.py]
  - strategy: "Implement missing features, add tests, update docs"

training_stubs:
  - prompt: "Resolve 23 TODOs in training module"
  - files: [training/engine_hf_trainer.py, training/functional_training.py]
  - strategy: "Complete distributed training, scheduler resume, timeout guards"

[... Continue for all 18 capability domains]
```

---

## Master Stub Resolution Prompt

🎯 **COPILOT INSTRUCTION: COMPREHENSIVE STUB CLEANUP**

@workspace Execute systematic stub cleanup across all 298 items

### Phase 1: Categorize (Auto-detect)
```python
stub_categories = {
    "NotImplementedError": 127,
    "TODO": 82,
    "FIXME": 18,
    "pass-only": 34,
    "STUB": 15,
    "ellipsis": 22
}
```

### Phase 2: Prioritize by Impact
- P0: Breaks functionality (15 items) → Fix Week 1
- P1: High value (45 items) → Fix Weeks 2-4  
- P2: Medium value (128 items) → Fix Weeks 5-12
- P3: Low impact (110 items) → Fix opportunistically

### Phase 3: Auto-Resolution Strategies

**For NotImplementedError:**
```python
# Pattern 1: Optional dependency
if condition_not_met:
    raise NotImplementedError("Feature requires X")

# Fix: Add graceful fallback
if condition_not_met:
    logger.warning("Feature unavailable, using fallback")
    return fallback_implementation()
```

**For TODO/FIXME:**
```python
# TODO: Implement feature X
pass

# Fix: Research → Implement → Test → Document
def feature_x():
    # Implementation based on requirements
    ...
```

**For pass-only functions:**
```python
except Exception:
    pass  # STUB

# Fix: Add proper error handling
except Exception as e:
    logger.error(f"Error: {e}")
    if critical:
        raise
```

### Phase 4: Validation
- [ ] No NotImplementedError in hot paths
- [ ] All TODOs have tickets or implementations
- [ ] All pass-only blocks have logging
- [ ] Test coverage >70% for resolved areas

### Phase 5: Progress Tracking
```yaml
stubs_remaining: 298 → 0
completion_rate: 0% → 100%
timeline: 16 weeks
effort: 2-3 engineers
```

---

## Autonomous Expansion Protocol

🎯 **For any blocking stub, Copilot auto-generates:**

1. **Research sub-prompt:** Understand requirements
2. **Design sub-prompt:** Plan implementation approach
3. **Implementation sub-prompt:** Code the solution
4. **Testing sub-prompt:** Write comprehensive tests
5. **Documentation sub-prompt:** Update docs

**Example for complex stub:**
```
Stub: src/codex_ml/training/distributed.py:45 - TODO: DDP support

Auto-generates:
├─ Research: "Survey PyTorch DDP best practices"
├─ Design: "Design DDP integration for CodexTrainer"
├─ Implement: "Add DDP wrapper with auto-device placement"
├─ Test: "Create DDP integration tests (multi-GPU)"
└─ Document: "Add DDP usage guide to training docs"
```

🤖 **Copilot:** Execute stub cleanup incrementally, reporting progress after each batch
