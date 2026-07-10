# Agent Brief: Stage 4 - TIER-1 Wave 1 Test Implementation

**Target Agent:** unified-coverage-agent (lead) + autonomous-test-healer-agent (secondary)  
**Priority:** HIGH (builds coverage to ≥70%)  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Timeline:** 8-12 hours (can span 2-3 days with parallelization)  
**Status:** READY FOR DISPATCH (can start during Stage 2, fully after Stage 3)

---

## Mission

Implement 67 TIER-1 Wave 1 test cases across unit, integration, and error path testing to achieve ≥70% coverage on critical modules:
- src/services (7.41% → 70%)
- src/mcp (16.67% → 70%)
- src/tools (20.0% → 70%)
- src/codex_utils (25.0% → 70%)
- src/utils (30.0% → 70%)
- src/security (37.5% → 70%)

---

## Prerequisites

- Python >=3.12 environment with pytest installed
- All Phase 3-5 code merged to main (or 0D_base_ if promotion not complete)
- Phase 6 Wave 1 core documentation available in `.codex/`
- Test templates and patterns in PHASE_6_WAVE_1_TEST_GENERATION_GUIDE.md

---

## Task 4A: Test Environment Setup (~30 min)

**1. Install Test Dependencies:**
```bash
cd /home/runner/work/_codex_/_codex_
pip install pytest pytest-asyncio pytest-mock PyJWT cryptography
pip install --upgrade pytest-cov
# Verify installation
pytest --version
```

**2. Create Test Directory Structure:**
```bash
mkdir -p tests/phase6_wave1/
touch tests/phase6_wave1/__init__.py
# Verify directory can be collected
pytest tests/phase6_wave1/ --collect-only
```

**3. Set Up Coverage Baseline:**
```bash
cd /home/runner/work/_codex_/_codex_
pytest tests/ --cov=src --cov-report=term-missing --co -q 2>/dev/null | tail -1
# Capture baseline metrics for comparison
```

**4. Verify Test Collection:**
```bash
pytest tests/phase6_wave1/ --collect-only
# Expected: 0 errors (new empty directory)
```

---

## Task 4B: Unit Tests Implementation (~3-4 hours, 35 tests)

**Use PHASE_6_WAVE_1_TEST_GENERATION_GUIDE.md as reference for code templates.**

### Day 1-1A: Authentication & Lifecycle Tests (5 tests, ~30 min)

**File:** `tests/phase6_wave1/test_mcp_authentication.py`

**Tests to implement:**
1. `test_mcp_authentication_basic_flow` - Basic auth handshake
2. `test_mcp_session_lifecycle_start` - Session startup
3. `test_mcp_session_lifecycle_end` - Session cleanup
4. `test_credential_handling_secure_storage` - Credential encryption
5. `test_token_refresh_mechanism` - Token refresh flow

**Execution:** `pytest tests/phase6_wave1/test_mcp_authentication.py -v`

### Day 1-1B: Service Initialization (8 tests, ~45 min)

**File:** `tests/phase6_wave1/test_service_initialization.py`

**Tests to implement:**
1. `test_service_startup_default_config` - Default config loading
2. `test_service_startup_custom_config` - Custom config loading
3. `test_service_dependency_injection` - DI container setup
4. `test_service_startup_error_handling` - Error at startup
5. `test_service_config_validation` - Config validation
6. `test_service_logging_initialization` - Logging setup
7. `test_service_resource_cleanup` - Resource cleanup
8. `test_service_health_check` - Health check endpoint

**Execution:** `pytest tests/phase6_wave1/test_service_initialization.py -v`

### Day 1-1C: Utility Functions (8 tests, ~45 min)

**Files:** `tests/phase6_wave1/test_utility_functions.py`, `tests/phase6_wave1/test_codex_codecs.py`

**Tests to implement (test_utility_functions.py):**
1. `test_serialization_json_encoding` - JSON serialization
2. `test_serialization_json_decoding` - JSON deserialization
3. `test_codec_binary_encode` - Binary encoding
4. `test_codec_binary_decode` - Binary decoding
5. `test_validation_input_type_checking` - Type validation
6. `test_conversion_numeric_string` - Numeric conversion
7. `test_conversion_string_numeric` - String to numeric
8. `test_utility_edge_case_empty_input` - Edge case handling

**Execution:** `pytest tests/phase6_wave1/test_utility_functions.py tests/phase6_wave1/test_codex_codecs.py -v`

### Day 1-1D: Security Operations (4 tests, ~25 min)

**File:** `tests/phase6_wave1/test_crypto_operations.py`

**Tests to implement:**
1. `test_crypto_encryption_aes256` - AES-256 encryption
2. `test_crypto_decryption_aes256` - AES-256 decryption
3. `test_crypto_key_generation_secure` - Secure key generation
4. `test_crypto_random_bytes_entropy` - Random bytes quality

**Execution:** `pytest tests/phase6_wave1/test_crypto_operations.py -v`

### Day 1-1E: Additional Utilities (10 tests, ~1 hour)

**File:** `tests/phase6_wave1/test_codex_utilities_extended.py`

**Tests to implement:**
1. `test_string_formatting_unicode` - Unicode handling
2. `test_string_validation_email` - Email validation
3. `test_string_validation_url` - URL validation
4. `test_dict_merge_recursive` - Recursive dict merge
5. `test_list_deduplication_preserves_order` - Dedup with order
6. `test_file_path_normalization` - Path normalization
7. `test_file_path_validation` - Path validation
8. `test_collection_flattening` - List flattening
9. `test_collection_chunking` - List chunking
10. `test_timer_utility_precision` - Timer accuracy

**Execution:** `pytest tests/phase6_wave1/test_codex_utilities_extended.py -v`

### Unit Tests Checkpoint:
```bash
pytest tests/phase6_wave1/test_*_unit.py -v --cov=src --cov-report=term-missing
# Expected: 35 tests passing, ~50-55% coverage on unit tests
```

---

## Task 4C: Integration Tests Implementation (~3-4 hours, 25 tests)

**Use PHASE_6_WAVE_1_TEST_GENERATION_GUIDE.md integration patterns.**

### Day 1-2A: MCP Protocol Handshake (8 tests, ~45 min)

**File:** `tests/phase6_wave1/test_mcp_protocol.py`

**Tests to implement:**
1. `test_mcp_connection_establishment` - TCP connection
2. `test_mcp_connection_ssl_handshake` - SSL/TLS handshake
3. `test_mcp_message_exchange_sequence` - Msg exchange
4. `test_mcp_state_machine_transitions` - State transitions
5. `test_mcp_error_recovery_malformed_msg` - Error handling
6. `test_mcp_timeout_recovery` - Timeout handling
7. `test_mcp_connection_cleanup` - Cleanup on disconnect
8. `test_mcp_protocol_version_negotiation` - Version negotiation

**Execution:** `pytest tests/phase6_wave1/test_mcp_protocol.py -v`

### Day 1-2B: Service Communication (10 tests, ~1 hour)

**Files:** `tests/phase6_wave1/test_service_communication.py`, `tests/phase6_wave1/test_rpc_routing.py`

**Tests to implement (test_service_communication.py):**
1. `test_rpc_request_response_cycle` - Basic RPC
2. `test_rpc_async_request_handling` - Async RPC
3. `test_rpc_error_response_format` - Error response
4. `test_rpc_message_routing_basic` - Basic routing
5. `test_rpc_message_routing_complex` - Complex routing
6. `test_rpc_timeout_handling` - Timeout management
7. `test_rpc_retry_logic` - Retry behavior
8. `test_rpc_connection_pooling` - Connection pooling
9. `test_rpc_load_balancing` - Load balancing
10. `test_rpc_circuit_breaker` - Circuit breaker pattern

**Execution:** `pytest tests/phase6_wave1/test_service_communication.py tests/phase6_wave1/test_rpc_routing.py -v`

### Day 1-2C: Tool Execution Pipeline (7 tests, ~40 min)

**File:** `tests/phase6_wave1/test_tool_execution.py`

**Tests to implement:**
1. `test_tool_registry_registration` - Tool registration
2. `test_tool_registry_lookup` - Tool lookup
3. `test_tool_execution_basic` - Basic execution
4. `test_tool_execution_with_params` - With parameters
5. `test_tool_parameter_validation` - Param validation
6. `test_tool_result_handling` - Result handling
7. `test_tool_execution_error_propagation` - Error propagation

**Execution:** `pytest tests/phase6_wave1/test_tool_execution.py -v`

### Integration Tests Checkpoint:
```bash
pytest tests/phase6_wave1/test_*_integration.py -v --cov=src --cov-report=term-missing
# Expected: 25 tests passing, additional 15-20% coverage
```

---

## Task 4D: Error Path Tests (~1.5 hours, 7 tests)

**Use PHASE_6_WAVE_1_TEST_GENERATION_GUIDE.md error patterns.**

### Day 2-3A: Malformed Messages (4 tests, ~25 min)

**File:** `tests/phase6_wave1/test_mcp_errors.py`

**Tests to implement:**
1. `test_error_handling_malformed_json` - Invalid JSON
2. `test_error_handling_truncated_message` - Truncated msg
3. `test_error_handling_type_mismatch` - Type mismatch
4. `test_error_handling_missing_fields` - Missing fields

**Execution:** `pytest tests/phase6_wave1/test_mcp_errors.py -v`

### Day 2-3B: Timeout Handling (3 tests, ~20 min)

**File:** `tests/phase6_wave1/test_service_errors.py`

**Tests to implement:**
1. `test_error_connection_timeout` - Connection timeout
2. `test_error_request_timeout` - Request timeout
3. `test_error_resource_cleanup_on_timeout` - Cleanup

**Execution:** `pytest tests/phase6_wave1/test_service_errors.py -v`

### Error Path Tests Checkpoint:
```bash
pytest tests/phase6_wave1/test_*_error.py -v --cov=src --cov-report=term-missing
# Expected: 7 tests passing, completing coverage to ≥70%
```

---

## Task 4E: Wave 1 Validation & Reporting (~1 hour)

**1. Run Full Wave 1 Test Suite:**
```bash
pytest tests/phase6_wave1/ -v --cov=src --cov-config=.coveragerc \
  --cov-report=html --cov-report=term-missing
# Expected execution time: ~5-7 min
```

**2. Capture Coverage Metrics:**
```bash
# Extract coverage summary
pytest tests/phase6_wave1/ --cov=src --cov-report=term | grep "TOTAL"
# Document metrics by module (create CSV/table)
```

**3. Generate Coverage Report:**
- HTML report: `htmlcov/index.html`
- Module breakdown with % coverage
- Identify any gaps <70%

**4. Identify Regression:**
```bash
# Run existing tests to verify no breakage
pytest tests/ --ignore=tests/phase6_wave1/ -x -q
# Expected: All existing tests still passing
```

**5. Update Checkpoint Document:**
Save to `.codex/PHASE_6_WAVE_1_STAGE4_COMPLETION_REPORT.md` with:
- 67 tests implemented and passing
- Coverage metrics by TIER-1 module
- No regressions detected
- Status: READY for Stage 5 delegation

---

## Success Criteria

- ✅ 67 TIER-1 tests implemented and passing
- ✅ Coverage ≥70% on all TIER-1 modules:
  - src/services, src/mcp, src/tools, src/codex_utils, src/utils, src/security
- ✅ All error paths covered
- ✅ Coverage report generated with module breakdown
- ✅ No regression in existing tests
- ✅ Completion report committed to `.codex/`

---

## Parallelization Strategy

To achieve 8-12 hour timeline across 2-3 days:
- **Day 1 Morning:** 4A (setup) + 4B (35 unit tests) = ~4 hours
- **Day 1 Afternoon:** 4C (25 integration tests) = ~4 hours  
- **Day 2 Morning:** 4D (7 error tests) = ~1.5 hours
- **Day 2 Afternoon:** 4E (validation) = ~1 hour

Or, for faster execution (single day):
- Parallelize 4B, 4C, 4D across multiple test runner instances
- Estimated: 8-10 hours continuous

---

## Output Artifacts

**Committed to Repository:**
- `tests/phase6_wave1/test_*.py` (all 67 test files)
- `.codex/PHASE_6_WAVE_1_STAGE4_COMPLETION_REPORT.md` (metrics & status)
- Updated `.codex/PHASE_6_WAVE_1_EXECUTION_TRACKING.md`
- Updated `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` (session tracking)

---

## Dependencies

- Stage 3 completion (promotion merged to main)
- All Phase 3-5 code available in main branch
- Phase 6 Wave 1 test guide and templates ready

---

**Authority:** @mbaetiong - all steps pre-approved  
**Mode:** Autonomous GO CONTINUE - proceed at all decision points  
**Dispatch Status:** AWAITING STAGE 3 COMPLETION SIGNAL (can start during Stage 2)
