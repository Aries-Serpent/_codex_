# Phase 7 Integration Test Plan and Checklist

**Document Version:** 1.0.0  
**Created:** 2026-07-06  
**Execution Timeline:** Phase 7 (2026-07-08T10:00Z, 2 days post-merge)  
**Status:** GROUNDWORK PREPARED (Ready for Phase 7 Execution)  

---

## Overview

This document defines the comprehensive test plan for Phase 7 Local Development Environment Validation. It outlines all integration tests, validation steps, and success criteria for the 8 environment variables deployed in Phase 6.2.

---

## Phase 7 Test Strategy

### Testing Pyramid

```
                    ▲
                   ╱ ╲
                  ╱   ╲  End-to-End Integration Tests
                 ╱     ╲ (Validate all 8 variables together)
                ╱───────╲
               ╱         ╲
              ╱           ╲ Integration Tests
             ╱             ╲ (Test variable interaction)
            ╱───────────────╲
           ╱                 ╲
          ╱                   ╲ Unit Tests
         ╱                     ╲ (Test individual variables)
        ╱─────────────────────────╲

From bottom to top:
1. Unit Tests (8 variables × 3 scenarios = 24 tests)
2. Integration Tests (8 variables × 2 scenarios = 16 tests)
3. End-to-End Tests (All 8 variables = 4 tests)
```

---

## Part 1: Unit Tests

Each environment variable gets 3 unit test scenarios:

### Test Set 1: Default Value Behavior

**Test**: Verify each variable has a sensible default when unset

```python
# tests/test_phase_7_unit_variable_defaults.py

class TestVariableDefaults:
    """Verify all 8 variables have sensible defaults."""
    
    def test_redis_host_default(self, monkeypatch):
        """CODEX_REDIS_HOST defaults to 'localhost'"""
        monkeypatch.delenv("CODEX_REDIS_HOST", raising=False)
        # Import and verify default
        
    def test_ollama_host_default(self, monkeypatch):
        """CODEX_OLLAMA_HOST defaults to 'http://localhost:11434'"""
        monkeypatch.delenv("CODEX_OLLAMA_HOST", raising=False)
        
    def test_master_addr_default(self, monkeypatch):
        """CODEX_MASTER_ADDR defaults to 'localhost'"""
        monkeypatch.delenv("CODEX_MASTER_ADDR", raising=False)
        
    def test_master_port_default(self, monkeypatch):
        """CODEX_MASTER_PORT defaults to '29500'"""
        monkeypatch.delenv("CODEX_MASTER_PORT", raising=False)
        
    def test_inference_host_default(self, monkeypatch):
        """CODEX_INFERENCE_SERVICE_HOST defaults to '127.0.0.1'"""
        monkeypatch.delenv("CODEX_INFERENCE_SERVICE_HOST", raising=False)
        
    def test_inference_port_default(self, monkeypatch):
        """CODEX_INFERENCE_SERVICE_PORT defaults to '8000'"""
        monkeypatch.delenv("CODEX_INFERENCE_SERVICE_PORT", raising=False)
        
    def test_trusted_hosts_default(self, monkeypatch):
        """CODEX_TRUSTED_HOSTS defaults to 'localhost,127.0.0.1,testserver'"""
        monkeypatch.delenv("CODEX_TRUSTED_HOSTS", raising=False)
        
    def test_local_loopback_default(self, monkeypatch):
        """CODEX_LOCAL_LOOPBACK defaults to 'true'"""
        monkeypatch.delenv("CODEX_LOCAL_LOOPBACK", raising=False)
```

**Expected Results:** ✅ 8/8 tests pass (one default for each variable)

### Test Set 2: Override Behavior

**Test**: Verify each variable can be overridden via environment

```python
# tests/test_phase_7_unit_variable_overrides.py

class TestVariableOverrides:
    """Verify all 8 variables can be overridden."""
    
    def test_redis_host_override(self, monkeypatch):
        """CODEX_REDIS_HOST can be set to custom value"""
        monkeypatch.setenv("CODEX_REDIS_HOST", "custom-redis.local")
        # Verify custom value is used
        
    def test_ollama_host_override(self, monkeypatch):
        """CODEX_OLLAMA_HOST can be set to custom value"""
        monkeypatch.setenv("CODEX_OLLAMA_HOST", "http://custom-ollama:11434")
        
    # ... (6 more tests for other variables)
```

**Expected Results:** ✅ 8/8 tests pass (one override for each variable)

### Test Set 3: Type Validation

**Test**: Verify each variable has correct type/format

```python
# tests/test_phase_7_unit_variable_validation.py

class TestVariableValidation:
    """Verify all 8 variables validate correctly."""
    
    def test_redis_host_is_string(self):
        """CODEX_REDIS_HOST must be a string (hostname)"""
        
    def test_ollama_host_is_url(self):
        """CODEX_OLLAMA_HOST must be a valid URL"""
        
    def test_master_port_is_valid_port(self):
        """CODEX_MASTER_PORT must be 1-65535"""
        
    def test_inference_port_is_valid_port(self):
        """CODEX_INFERENCE_SERVICE_PORT must be 1-65535"""
        
    def test_trusted_hosts_is_comma_separated(self):
        """CODEX_TRUSTED_HOSTS must be comma-separated list"""
        
    def test_local_loopback_is_boolean_string(self):
        """CODEX_LOCAL_LOOPBACK must be 'true' or 'false'"""
```

**Expected Results:** ✅ 8/8 tests pass (one validation for each variable)

**Total Unit Tests:** 24 ✅

---

## Part 2: Integration Tests

### Test Set 4: Cross-Variable Interaction

**Test**: Verify variables work together correctly

```python
# tests/test_phase_7_integration_variable_interaction.py

class TestVariableInteraction:
    """Verify all 8 variables work together."""
    
    def test_master_addr_and_port_together(self, monkeypatch):
        """CODEX_MASTER_ADDR and CODEX_MASTER_PORT work as pair"""
        monkeypatch.setenv("CODEX_MASTER_ADDR", "master.local")
        monkeypatch.setenv("CODEX_MASTER_PORT", "29501")
        # Verify distributed training uses both
        
    def test_inference_host_and_port_together(self, monkeypatch):
        """CODEX_INFERENCE_SERVICE_HOST and PORT work as pair"""
        monkeypatch.setenv("CODEX_INFERENCE_SERVICE_HOST", "0.0.0.0")
        monkeypatch.setenv("CODEX_INFERENCE_SERVICE_PORT", "9000")
        # Verify server binds to both
        
    def test_trusted_hosts_with_local_loopback(self, monkeypatch):
        """CODEX_TRUSTED_HOSTS respects CODEX_LOCAL_LOOPBACK"""
        monkeypatch.setenv("CODEX_LOCAL_LOOPBACK", "false")
        monkeypatch.setenv("CODEX_TRUSTED_HOSTS", "example.com")
        # Verify strict host validation when feature gate off
        
    def test_redis_and_ollama_both_accessible(self, monkeypatch):
        """CODEX_REDIS_HOST and CODEX_OLLAMA_HOST both reachable"""
        # This may require Docker containers running
        monkeypatch.setenv("CODEX_REDIS_HOST", "localhost")
        monkeypatch.setenv("CODEX_OLLAMA_HOST", "http://localhost:11434")
```

**Expected Results:** ✅ 4/4 tests pass

### Test Set 5: Environment-Specific Configurations

**Test**: Verify configuration for each environment type

```python
# tests/test_phase_7_integration_env_configs.py

class TestEnvironmentConfigurations:
    """Verify each environment configuration is valid."""
    
    def test_localhost_configuration(self, monkeypatch):
        """Local development configuration works"""
        config = {
            'CODEX_REDIS_HOST': 'localhost',
            'CODEX_OLLAMA_HOST': 'http://localhost:11434',
            'CODEX_MASTER_ADDR': 'localhost',
            'CODEX_MASTER_PORT': '29500',
            'CODEX_INFERENCE_SERVICE_HOST': '127.0.0.1',
            'CODEX_INFERENCE_SERVICE_PORT': '8000',
            'CODEX_TRUSTED_HOSTS': 'localhost,127.0.0.1,testserver',
            'CODEX_LOCAL_LOOPBACK': 'true',
        }
        # Apply and verify
        
    def test_docker_configuration(self, monkeypatch):
        """Docker Compose configuration works"""
        config = {
            'CODEX_REDIS_HOST': 'redis',
            'CODEX_OLLAMA_HOST': 'http://ollama:11434',
            'CODEX_MASTER_ADDR': 'training-master',
            'CODEX_INFERENCE_SERVICE_HOST': '0.0.0.0',
            'CODEX_TRUSTED_HOSTS': 'localhost,127.0.0.1,inference-api',
            'CODEX_LOCAL_LOOPBACK': 'true',
        }
        
    def test_kubernetes_staging_configuration(self, monkeypatch):
        """Kubernetes staging configuration works"""
        config = {
            'CODEX_REDIS_HOST': 'redis-staging.codex.svc.cluster.local',
            'CODEX_TRUSTED_HOSTS': '*.staging.codex.svc.cluster.local',
            'CODEX_LOCAL_LOOPBACK': 'false',
        }
        
    def test_kubernetes_production_configuration(self, monkeypatch):
        """Kubernetes production configuration works"""
        config = {
            'CODEX_REDIS_HOST': 'redis-primary.codex.svc.cluster.local',
            'CODEX_TRUSTED_HOSTS': '*.codex.svc.cluster.local,codex.prod',
            'CODEX_LOCAL_LOOPBACK': 'false',
        }
```

**Expected Results:** ✅ 4/4 tests pass

**Total Integration Tests:** 8 ✅

---

## Part 3: End-to-End Tests

### Test Set 6: Full Pipeline Validation

**Test**: Run complete workflows with each configuration

```python
# tests/test_phase_7_e2e_full_pipeline.py

class TestFullPipelineWithEnvironmentVariables:
    """Verify complete pipelines work with all 8 variables."""
    
    def test_rag_pipeline_with_redis_and_ollama(self, monkeypatch):
        """RAG pipeline works with CODEX_REDIS_HOST and CODEX_OLLAMA_HOST"""
        # 1. Set variables
        # 2. Initialize RAG components
        # 3. Run embedding pipeline
        # 4. Verify Redis caching works
        # 5. Verify Ollama embeddings work
        
    def test_distributed_training_with_master_config(self, monkeypatch):
        """Distributed training works with CODEX_MASTER_ADDR/PORT"""
        # 1. Set CODEX_MASTER_ADDR and CODEX_MASTER_PORT
        # 2. Initialize distributed config
        # 3. Verify NCCL/DDP bootstrap
        # 4. Verify master node communication
        
    def test_inference_api_with_host_validation(self, monkeypatch):
        """Inference API respects CODEX_TRUSTED_HOSTS and CODEX_LOCAL_LOOPBACK"""
        # 1. Set CODEX_INFERENCE_SERVICE_HOST and PORT
        # 2. Set CODEX_TRUSTED_HOSTS and CODEX_LOCAL_LOOPBACK
        # 3. Start inference server
        # 4. Test allowed hosts (should pass)
        # 5. Test blocked hosts (should fail with strict gate)
        
    def test_all_eight_variables_together(self, monkeypatch):
        """All 8 variables work together in production configuration"""
        # Set all 8 variables to production values
        # Run comprehensive integration test
        # Verify all subsystems initialized correctly
```

**Expected Results:** ✅ 4/4 tests pass

**Total End-to-End Tests:** 4 ✅

---

## Summary of All Tests

| Category | Tests | File(s) |
|----------|-------|---------|
| Unit: Defaults | 8 | `test_phase_7_unit_variable_defaults.py` |
| Unit: Overrides | 8 | `test_phase_7_unit_variable_overrides.py` |
| Unit: Validation | 8 | `test_phase_7_unit_variable_validation.py` |
| Integration: Interaction | 4 | `test_phase_7_integration_variable_interaction.py` |
| Integration: Env Configs | 4 | `test_phase_7_integration_env_configs.py` |
| End-to-End: Pipeline | 4 | `test_phase_7_e2e_full_pipeline.py` |
| **Total** | **36** | **6 test files** |

---

## Phase 7 Execution Checklist

### Pre-Phase 7 (Now - Phase 6.2)

- [ ] **Validation script created:** `.codex/validate_local_env.sh`
- [ ] **Environment template created:** `.env.example`
- [ ] **Setup guide created:** `docs/LOCAL_DEV_ENV_SETUP.md`
- [ ] **Test plan created:** This document
- [ ] **All groundwork reviewed and tested locally**

### Phase 7 Activation (2026-07-08T10:00Z)

- [ ] **All 8 variables live in GitHub Settings**
- [ ] **Validation script runs:**
  ```bash
  bash .codex/validate_local_env.sh
  # Expected: 8/8 tests PASSED
  ```

- [ ] **Unit tests run:**
  ```bash
  pytest tests/test_phase_7_unit_variable_defaults.py -v
  pytest tests/test_phase_7_unit_variable_overrides.py -v
  pytest tests/test_phase_7_unit_variable_validation.py -v
  # Expected: 24/24 tests PASSED
  ```

- [ ] **Integration tests run:**
  ```bash
  pytest tests/test_phase_7_integration_variable_interaction.py -v
  pytest tests/test_phase_7_integration_env_configs.py -v
  # Expected: 8/8 tests PASSED
  ```

- [ ] **End-to-end tests run:**
  ```bash
  pytest tests/test_phase_7_e2e_full_pipeline.py -v
  # Expected: 4/4 tests PASSED
  ```

### Phase 7 Success Criteria

✅ **All Validation Passed:**
- Validation script: 8/8 ✓
- Unit tests: 24/24 ✓
- Integration tests: 8/8 ✓
- End-to-end tests: 4/4 ✓
- **Total: 44/44 tests PASSED**

✅ **All Variables Functional:**
- CODEX_REDIS_HOST ✓
- CODEX_OLLAMA_HOST ✓
- CODEX_MASTER_ADDR ✓
- CODEX_MASTER_PORT ✓
- CODEX_INFERENCE_SERVICE_HOST ✓
- CODEX_INFERENCE_SERVICE_PORT ✓
- CODEX_TRUSTED_HOSTS ✓
- CODEX_LOCAL_LOOPBACK ✓

✅ **All Environment Configurations Work:**
- Local development ✓
- Docker Compose ✓
- Kubernetes staging ✓
- Kubernetes production ✓

### Phase 7 Completion

- [ ] **Phase 7 validation report generated**
- [ ] **All tests documented in Phase 7 summary**
- [ ] **Ready to proceed to Phase 8 (CI/CD integration)**

---

## Test Execution Commands (Phase 7)

```bash
# Run validation script
bash .codex/validate_local_env.sh

# Run all Phase 7 tests
pytest tests/test_phase_7_*.py -v --tb=short

# Run specific test category
pytest tests/test_phase_7_unit_*.py -v           # Unit tests
pytest tests/test_phase_7_integration_*.py -v    # Integration tests
pytest tests/test_phase_7_e2e_*.py -v            # End-to-end tests

# Run with coverage
pytest tests/test_phase_7_*.py -v --cov=src.codex --cov=src.codex_ml

# Run with custom environment
CODEX_REDIS_HOST=custom pytest tests/test_phase_7_*.py -v
```

---

## Troubleshooting Test Failures

### Issue: Unit tests fail with "Variable not found"

**Cause**: Variable not yet set in GitHub Settings  
**Solution**: Check GitHub Settings > Variables at merge time

### Issue: Integration tests fail with "Connection refused"

**Cause**: Redis/Ollama not running  
**Solution**: Start services locally for testing
```bash
redis-server &
ollama serve &
pytest tests/test_phase_7_*.py -v
```

### Issue: E2E tests timeout

**Cause**: Services slow to initialize  
**Solution**: Increase timeout in test config
```python
@pytest.mark.timeout(30)  # 30 second timeout
def test_slow_pipeline():
    pass
```

---

## Reference Documents

- **Phase 6.2 Implementation:** `.codex/ENV_VARS_IMPLEMENTATION_SPECIFICATION.md`
- **Variable Inventory:** `.codex/ENVIRONMENT_VARIABLES_ANALYSIS_TABLE.md`
- **Existing Phase 6.2 Tests:** `tests/test_phase_6_2_b_env_vars.py`
- **Config Tests:** `tests/config/test_env_vars_comprehensive.py`

---

**Status**: Phase 7 Groundwork COMPLETE (Ready for 2026-07-08 Execution)  
**Created**: 2026-07-06  
**Last Updated**: 2026-07-06
