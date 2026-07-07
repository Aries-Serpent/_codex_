# PHASE 13 TRACK 13.2: GUARD RAIL INTEGRATION CHECKLIST

**Session**: phase-13-track-13-2-deployment  
**Date**: 2026-07-06T05:43:52Z  
**Mode**: ADVISORY (Pre-Implementation Planning)  
**Target Audience**: Implementation Team (Days 3-7)

---

## INTEGRATION PLANNING CHECKLIST

This checklist provides step-by-step integration guidance for deploying the 4 guard rails across the RAG subsystem. Designed for implementation phase (Days 3-7).

---

## GUARD RAIL 1: INITIALIZATION HARDENING

### File: src/codex/rag/guards.py (NEW)

```python
# Step 1: Create guards.py module
class InitializationHardeningGuard:
    def validate(self) -> None:
        """Validate environment before model loading."""
        # TODO: Step 2.1 - Check PYTORCH_CUDA_ALLOC_CONF
        # TODO: Step 2.2 - Check TRANSFORMERS_OFFLINE
        # TODO: Step 2.3 - Check torch version
        # TODO: Step 2.4 - Set memory limits
        # TODO: Step 2.5 - Log environment state
```

### Integration Checklist

- [ ] **Step 1.1**: Create `src/codex/rag/guards.py` module
- [ ] **Step 1.2**: Implement `InitializationHardeningGuard` class
- [ ] **Step 1.3**: Add PYTORCH_CUDA_ALLOC_CONF validation
  - [ ] Check variable exists
  - [ ] Check value format (max_split_size_mb=128)
  - [ ] Log if missing or invalid
- [ ] **Step 1.4**: Add TRANSFORMERS_OFFLINE validation
  - [ ] Check variable exists
  - [ ] Check value is 0 or 1
  - [ ] Log state
- [ ] **Step 1.5**: Add torch version check
  - [ ] Import torch (with fallback)
  - [ ] Check version >= 2.0
  - [ ] Log version for debugging
- [ ] **Step 1.6**: Add memory limit enforcement
  - [ ] Set soft limit: 80% of available
  - [ ] Set hard limit: 100% of available
  - [ ] Log limits
- [ ] **Step 1.7**: Add comprehensive logging
- [ ] **Step 1.8**: Write 10 unit tests
  - [ ] Test missing PYTORCH_CUDA_ALLOC_CONF
  - [ ] Test missing TRANSFORMERS_OFFLINE
  - [ ] Test incompatible torch version
  - [ ] Test valid environment
  - [ ] Test memory limit setup
  - [ ] (5 more edge cases)

### Integration Points

**In embeddings.py: LocalSentenceTransformerProvider._load_model()**
```python
# BEFORE:
self.model = safe_load_sentence_transformer(self.model_name, self.cache_dir)

# AFTER:
guard = InitializationHardeningGuard()
guard.validate()  # Raises RuntimeError if env invalid
self.model = safe_load_sentence_transformer(self.model_name, self.cache_dir)
```

**In retriever.py: Retriever._load_model()**
```python
# BEFORE:
self.model = safe_load_sentence_transformer(self.model_name, self.cache_dir)

# AFTER:
guard = InitializationHardeningGuard()
guard.validate()  # Raises RuntimeError if env invalid
self.model = safe_load_sentence_transformer(self.model_name, self.cache_dir)
```

### Testing Points

- [ ] Unit test: environment variable validation
- [ ] Unit test: torch version checking
- [ ] Unit test: memory limit enforcement
- [ ] Unit test: error handling (missing variables)
- [ ] Integration test: embeddings.py guard call
- [ ] Integration test: retriever.py guard call

---

## GUARD RAIL 2: MATERIALIZATION DETECTION

### File: src/codex/rag/guards.py (ADDITION)

```python
class MaterializationDetectionGuard:
    def check_and_materialize(self, model: Any) -> Any:
        """Check for meta tensors and materialize if needed."""
        # TODO: Step 2.1 - Check for meta tensors (params + buffers)
        # TODO: Step 2.2 - If found: apply to_empty() with reinit
        # TODO: Step 2.3 - If not found: return model as-is
        # TODO: Step 2.4 - Log all findings with detail
        # TODO: Step 2.5 - Raise RuntimeError if materialization fails
```

### Integration Checklist

- [ ] **Step 2.1**: Implement meta tensor detection
  - [ ] Check all parameters for meta tensors
  - [ ] Check all buffers for meta tensors (CRITICAL!)
  - [ ] Use both `is_meta` attribute and `device.type` check
- [ ] **Step 2.2**: Implement to_empty() materialization
  - [ ] Check if model has `to_empty()` method
  - [ ] Call `model.to_empty(device='cpu')`
  - [ ] Re-initialize parameters if needed
- [ ] **Step 2.3**: Add verification after materialization
  - [ ] Re-check for remaining meta tensors
  - [ ] Raise RuntimeError if any remain
- [ ] **Step 2.4**: Add comprehensive logging
  - [ ] Log meta tensor names found
  - [ ] Log materialization attempts
  - [ ] Log success/failure with detail
- [ ] **Step 2.5**: Integrate with safe_load_sentence_transformer
  - [ ] Call within _model_utils.py after SentenceTransformer init
- [ ] **Step 2.6**: Write 15 unit tests
  - [ ] Test parameter meta tensor detection
  - [ ] Test buffer meta tensor detection
  - [ ] Test no meta tensors case
  - [ ] Test to_empty() materialization
  - [ ] Test post-materialization verification
  - [ ] Test error handling (to_empty() missing)
  - [ ] Test logging output
  - [ ] (8 more edge cases and failure modes)

### Integration Points

**In _model_utils.py: safe_load_sentence_transformer()**
```python
# EXISTING CODE:
model = SentenceTransformer(model_name, device="cpu", ...)

# ADD AFTER:
guard = MaterializationDetectionGuard()
model = guard.check_and_materialize(model)

# Keep existing safe_model_to_device call:
model = safe_model_to_device(model, "cpu")
```

### Testing Points

- [ ] Unit test: parameter meta tensor detection
- [ ] Unit test: buffer meta tensor detection
- [ ] Unit test: to_empty() materialization
- [ ] Unit test: post-materialization verification
- [ ] Unit test: error cases (to_empty() missing)
- [ ] Stress test: 200+ meta tensor scenarios

---

## GUARD RAIL 3: OOM PROTECTION & ROLLBACK

### File: src/codex/rag/guards.py (ADDITION)

```python
class OOMProtectionGuard:
    def load_with_protection(self, 
                             model_name: str, 
                             cache_dir: str,
                             memory_limit_mb: int = 2048) -> Any:
        """Load model with memory protection and fallback."""
        # TODO: Step 3.1 - Set memory limits (soft/hard)
        # TODO: Step 3.2 - Attempt primary model load
        # TODO: Step 3.3 - If OOM: catch, log, try fallback
        # TODO: Step 3.4 - Return whichever succeeds
        # TODO: Step 3.5 - Collect telemetry
```

### Integration Checklist

- [ ] **Step 3.1**: Implement memory limit enforcement
  - [ ] Set soft limit (80% of available)
  - [ ] Set hard limit (100% of available)
  - [ ] Use resource.setrlimit() or equivalent
- [ ] **Step 3.2**: Implement primary model load attempt
  - [ ] Call safe_load_sentence_transformer()
  - [ ] Catch MemoryError and RuntimeError (CUDA OOM)
- [ ] **Step 3.3**: Implement fallback strategy
  - [ ] Fallback model: "sentence-transformers/all-MiniLM-L6-v2"
  - [ ] Load fallback with same memory limits
  - [ ] Log fallback trigger with detail
- [ ] **Step 3.4**: Add error handling
  - [ ] If primary fails: log with stacktrace
  - [ ] If fallback fails: raise MemoryError
  - [ ] Distinguish between OOM and other errors
- [ ] **Step 3.5**: Add telemetry collection
  - [ ] Memory before/after
  - [ ] Memory peak
  - [ ] Which model was used (primary/fallback)
  - [ ] Load time
- [ ] **Step 3.6**: Write 12 unit tests
  - [ ] Test memory limit setting
  - [ ] Test successful primary load
  - [ ] Test OOM detection and handling
  - [ ] Test fallback load success
  - [ ] Test fallback load failure
  - [ ] Test memory telemetry collection
  - [ ] (6 more edge cases)

### Integration Points

**Create new function in embeddings.py**
```python
# In LocalSentenceTransformerProvider._load_model()
from codex.rag.guards import OOMProtectionGuard

guard = OOMProtectionGuard()
self.model = guard.load_with_protection(
    self.model_name, 
    self.cache_dir,
    memory_limit_mb=2048
)
```

### Testing Points

- [ ] Unit test: memory limit enforcement
- [ ] Unit test: OOM detection
- [ ] Unit test: fallback model loading
- [ ] Unit test: fallback failure handling
- [ ] Unit test: telemetry collection
- [ ] Stress test: 300+ memory stress scenarios

---

## GUARD RAIL 4: VERIFICATION & CORRECTNESS

### File: src/codex/rag/guards.py (ADDITION)

```python
@dataclass
class VerificationResult:
    passed: bool
    errors: list[str]
    warnings: list[str]
    meta_parameters: list[str]
    meta_buffers: list[str]
    device_consistency: bool
    timestamp: datetime

class VerificationGuard:
    def verify(self, model: Any) -> VerificationResult:
        """Verify model is fully materialized and correct."""
        # TODO: Step 4.1 - Check all parameters for meta tensors
        # TODO: Step 4.2 - Check all buffers for meta tensors
        # TODO: Step 4.3 - Verify device consistency
        # TODO: Step 4.4 - Test model usability (optional)
        # TODO: Step 4.5 - Return detailed result
```

### Integration Checklist

- [ ] **Step 4.1**: Implement parameter verification
  - [ ] Iterate all parameters via `named_parameters()`
  - [ ] Check `is_meta` attribute
  - [ ] Check `device.type == 'meta'`
  - [ ] Collect meta parameter names
- [ ] **Step 4.2**: Implement buffer verification
  - [ ] Iterate all buffers via `named_buffers()`
  - [ ] Check `is_meta` attribute (CRITICAL!)
  - [ ] Check `device.type == 'meta'`
  - [ ] Collect meta buffer names
- [ ] **Step 4.3**: Implement device consistency check
  - [ ] Get device from first parameter
  - [ ] Verify all parameters on same device
  - [ ] Verify all buffers on same device
  - [ ] Report any mismatches
- [ ] **Step 4.4**: Implement result composition
  - [ ] Create VerificationResult dataclass
  - [ ] Set passed=True only if all checks pass
  - [ ] Collect errors and warnings
  - [ ] Add timestamp
- [ ] **Step 4.5**: Implement optional forward pass test
  - [ ] Create dummy input
  - [ ] Call model.forward() if safe
  - [ ] Catch exceptions, log as warning
  - [ ] Don't fail verification on forward pass error
- [ ] **Step 4.6**: Add comprehensive logging
- [ ] **Step 4.7**: Write 15 unit tests
  - [ ] Test parameter verification
  - [ ] Test buffer verification
  - [ ] Test device consistency check
  - [ ] Test all checks pass case
  - [ ] Test meta parameters detected
  - [ ] Test meta buffers detected (IMPORTANT!)
  - [ ] Test device mismatch detected
  - [ ] (8 more edge cases)

### Integration Points

**Call in safe_load_sentence_transformer() after Guard 2**
```python
# In _model_utils.py
guard2 = MaterializationDetectionGuard()
model = guard2.check_and_materialize(model)

guard4 = VerificationGuard()
result = guard4.verify(model)
if not result.passed:
    raise RuntimeError(f"Model verification failed: {result.errors}")

return model
```

### Testing Points

- [ ] Unit test: parameter verification
- [ ] Unit test: buffer verification
- [ ] Unit test: device consistency
- [ ] Unit test: meta tensor detection (params)
- [ ] Unit test: meta tensor detection (buffers)
- [ ] Unit test: verification result composition
- [ ] Stress test: 250+ verification scenarios

---

## INTEGRATION WITH EXISTING MODULES

### Module: src/codex/rag/_model_utils.py

**File Changes**:
```python
# At top of safe_load_sentence_transformer():
from codex.rag.guards import (
    InitializationHardeningGuard,
    MaterializationDetectionGuard,
    VerificationGuard,
)

def safe_load_sentence_transformer(model_name, cache_dir, ...):
    # Add Guard 1 validation
    guard1 = InitializationHardeningGuard()
    guard1.validate()
    
    # Keep existing code...
    model = SentenceTransformer(...)
    
    # Add Guard 2 materialization check
    guard2 = MaterializationDetectionGuard()
    model = guard2.check_and_materialize(model)
    
    # Keep existing safe_model_to_device call
    model = safe_model_to_device(model, "cpu")
    
    # Add Guard 4 verification
    guard4 = VerificationGuard()
    result = guard4.verify(model)
    if not result.passed:
        raise RuntimeError(f"Verification failed: {result.errors}")
    
    model.eval()
    return model
```

**Integration Checklist**:
- [ ] Add imports from guards.py
- [ ] Add Guard 1 call before model creation
- [ ] Add Guard 2 call after SentenceTransformer init
- [ ] Keep Guard 3 call within OOMProtectionGuard
- [ ] Add Guard 4 call before model.eval()
- [ ] Update docstring to document guards

### Module: src/codex/rag/embeddings.py

**File Changes**:
```python
# In LocalSentenceTransformerProvider._load_model():
from codex.rag.guards import OOMProtectionGuard

def _load_model(self) -> None:
    try:
        from codex.rag.guards import OOMProtectionGuard
        guard = OOMProtectionGuard()
        
        logger.info(f"Loading local embedding model: {self.model_name}")
        self.model = guard.load_with_protection(
            self.model_name, 
            self.cache_dir,
            memory_limit_mb=2048
        )
        
        logger.info("Local embedding model loaded successfully on CPU")
    except ImportError:
        logger.error("sentence-transformers not installed...")
        raise
```

**Integration Checklist**:
- [ ] Add OOMProtectionGuard import
- [ ] Wrap model loading in OOMProtectionGuard.load_with_protection()
- [ ] Update error handling for OOM fallback
- [ ] Update logging to reflect fallback model (if used)
- [ ] Test integration

### Module: src/codex/rag/retriever.py

**File Changes**:
```python
# In Retriever._load_model():
from codex.rag.guards import OOMProtectionGuard

def _load_model(self) -> None:
    if SentenceTransformer is None:
        logger.error("sentence-transformers not installed...")
        raise ImportError("sentence-transformers not installed")
    
    try:
        from codex.rag.guards import OOMProtectionGuard
        guard = OOMProtectionGuard()
        
        logger.info(f"Loading query embedding model: {self.model_name}")
        self.model = guard.load_with_protection(
            self.model_name,
            self.cache_dir,
            memory_limit_mb=2048
        )
    except MemoryError:
        logger.error("Failed to load model (OOM even with fallback)")
        raise
```

**Integration Checklist**:
- [ ] Add OOMProtectionGuard import
- [ ] Wrap model loading in guard
- [ ] Update error handling for fallback scenarios
- [ ] Update logging
- [ ] Test integration

---

## TESTING INTEGRATION CHECKLIST

### Unit Tests (52 total)

- [ ] **Guard 1 Tests** (10 tests)
  - [ ] test_validate_pytorch_cuda_alloc_conf_present
  - [ ] test_validate_pytorch_cuda_alloc_conf_missing
  - [ ] test_validate_transformers_offline_present
  - [ ] test_validate_transformers_offline_missing
  - [ ] test_torch_version_check_compatible
  - [ ] test_torch_version_check_incompatible
  - [ ] test_memory_limit_enforcement
  - [ ] test_valid_environment_setup
  - [ ] test_logging_output
  - [ ] test_error_handling

- [ ] **Guard 2 Tests** (15 tests)
  - [ ] test_detect_parameter_meta_tensor
  - [ ] test_detect_buffer_meta_tensor
  - [ ] test_no_meta_tensors_present
  - [ ] test_materialize_via_to_empty
  - [ ] test_post_materialization_verification
  - [ ] test_to_empty_method_missing
  - [ ] test_logging_meta_tensor_names
  - [ ] test_logging_materialization_process
  - [ ] test_error_on_failed_materialization
  - [ ] test_multiple_meta_tensors
  - [ ] test_mixed_meta_and_normal_tensors
  - [ ] (5 more edge cases)

- [ ] **Guard 3 Tests** (12 tests)
  - [ ] test_memory_limit_setup
  - [ ] test_primary_model_load_success
  - [ ] test_oom_detection_memoryerror
  - [ ] test_oom_detection_cuda_oom
  - [ ] test_fallback_model_load_success
  - [ ] test_fallback_model_load_failure
  - [ ] test_memory_telemetry_collection
  - [ ] test_logging_fallback_trigger
  - [ ] test_error_distinction
  - [ ] (3 more edge cases)

- [ ] **Guard 4 Tests** (15 tests)
  - [ ] test_verify_all_parameters_no_meta
  - [ ] test_verify_detects_parameter_meta
  - [ ] test_verify_all_buffers_no_meta
  - [ ] test_verify_detects_buffer_meta
  - [ ] test_verify_device_consistency_passed
  - [ ] test_verify_device_consistency_failed
  - [ ] test_verify_result_composition
  - [ ] test_verify_logging_output
  - [ ] test_verify_multiple_meta_tensors
  - [ ] (5 more edge cases)

### Integration Tests (15 total)

- [ ] **embeddings.py Integration** (5 tests)
  - [ ] test_local_provider_guard_chain
  - [ ] test_local_provider_oom_fallback
  - [ ] test_local_provider_verification
  - [ ] test_local_provider_error_handling
  - [ ] test_local_provider_logging

- [ ] **indexer.py Integration** (5 tests)
  - [ ] test_embed_chunks_guard_chain
  - [ ] test_embed_chunks_provider_guards
  - [ ] test_embed_chunks_error_propagation
  - [ ] test_embed_chunks_logging
  - [ ] test_embed_chunks_performance

- [ ] **retriever.py Integration** (5 tests)
  - [ ] test_retriever_guard_chain
  - [ ] test_retriever_oom_fallback
  - [ ] test_retriever_verification
  - [ ] test_retriever_error_handling
  - [ ] test_retriever_logging

### Stress Tests (1000+ operations)

- [ ] **Initialization Stress** (200 ops)
  - [ ] Rapid load/unload cycles
  - [ ] Memory leak detection
  - [ ] Guard overhead measurement

- [ ] **Memory Stress** (300 ops)
  - [ ] Large batch encoding
  - [ ] OOM injection scenarios
  - [ ] Fallback model usage

- [ ] **Concurrency Stress** (200 ops)
  - [ ] Parallel model loads
  - [ ] Race condition detection
  - [ ] Thread safety validation

- [ ] **Failure Injection** (200 ops)
  - [ ] Meta tensor injection
  - [ ] OOM injection
  - [ ] Device error injection

- [ ] **Recovery Stress** (100 ops)
  - [ ] Fallback model cycles
  - [ ] Recovery time measurement
  - [ ] Graceful degradation validation

---

## CI/CD INTEGRATION CHECKLIST

### Workflow Files

- [ ] **test-rag-guards.yml** (NEW)
  - [ ] Run 52 unit tests
  - [ ] Run 15 integration tests
  - [ ] Collect coverage metrics
  - [ ] Report to PR

- [ ] **stress-test-rag.yml** (NEW)
  - [ ] Run 1000+ stress ops
  - [ ] Collect performance metrics
  - [ ] Report results to PR
  - [ ] Gate on stress test pass

- **Existing Workflows**:
  - [ ] Update test-comprehensive.yml to run guard tests
  - [ ] Update coverage reports to include guards
  - [ ] Add guard metrics to dashboard

### Coverage Requirements

- [ ] Unit test coverage: >95%
- [ ] Integration test coverage: 100%
- [ ] Guard rail code coverage: 100%
- [ ] Total RAG coverage: >90% (with guards)

---

## ROLLOUT TIMELINE

### Day 3 (2026-07-08)
- [ ] Implement Guard 1 (Initialization Hardening)
- [ ] Write & test 10 unit tests
- [ ] Integrate with _model_utils.py

### Day 4 (2026-07-09)
- [ ] Implement Guard 2 (Materialization Detection)
- [ ] Write & test 15 unit tests
- [ ] Integrate with safe_load_sentence_transformer()

### Day 5 (2026-07-10)
- [ ] Implement Guard 3 (OOM Protection)
- [ ] Write & test 12 unit tests
- [ ] Integrate with embeddings.py & retriever.py

### Day 6 (2026-07-11)
- [ ] Implement Guard 4 (Verification)
- [ ] Write & test 15 unit tests
- [ ] Final integration & smoke tests

### Day 7 (2026-07-12)
- [ ] Run 1000+ stress tests
- [ ] Validate all 4 guards working together
- [ ] CI/CD integration
- [ ] Documentation & runbooks

---

## SIGN-OFF CHECKLIST

### Pre-Implementation (Advisory Phase)

- [x] Architecture designed and documented
- [x] Integration points identified
- [x] Test strategy defined
- [x] Risk assessment completed
- [ ] Design review approval (PENDING)

### Post-Implementation (Full Execution)

- [ ] All code implemented
- [ ] All tests passing (52 unit + 15 integration)
- [ ] All stress tests passing (1000+ ops)
- [ ] CI/CD integration complete
- [ ] Documentation complete
- [ ] Performance metrics validated
- [ ] Ready for production deployment

---

**Document Status**: ✅ COMPLETE (Advisory Phase)  
**Last Updated**: 2026-07-06  
**Next Steps**: Await Track 12.3 clearance for full implementation
