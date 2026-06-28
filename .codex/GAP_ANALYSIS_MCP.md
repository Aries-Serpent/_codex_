# DETAILED GAP ANALYSIS — MCP Module

**Date:** 2026-06-27  
**Module:** mcp (16.7% → 80% target)  
**Priority:** 4 (MEDIUM)  

---

## Critical Gaps (MUST CLOSE FIRST)

### 1. auth.py (8 functions, 3 classes) — AUTHENTICATION FLOW

**Status:** <15% coverage

**Testable Items:**
```
auth.py:
├── Public Functions (7):
│   ├── authenticate() — main auth entry
│   ├── get_token() — token retrieval
│   ├── refresh_token() — token refresh
│   ├── validate_token() — token validation
│   ├── revoke_token() — token revocation
│   ├── get_permissions() — permission checking
│   └── has_permission() — single permission check
├── Private Functions (1):
│   └── _cache_token() — token caching
└── Classes (3):
    ├── AuthManager (main interface)
    ├── TokenError (exception)
    └── PermissionDenied (exception)
```

**Critical Gaps:**
- Token expiration handling
- Multi-method auth (token, oauth, API key)
- Permission validation logic
- Token revocation cascading
- Concurrent auth requests

**Test Requirements (6 tests):**
1. `test_auth_authenticate_with_token()` — token auth success
2. `test_auth_authenticate_invalid_token()` — token auth failure
3. `test_auth_refresh_token_success()` — token refresh
4. `test_auth_refresh_token_expired()` — expired token handling
5. `test_auth_validate_permissions()` — permission checking
6. `test_auth_revoke_token()` — token revocation

**Coverage Impact:** +5-7%

---

### 2. lifecycle.py (12 functions, 5 classes) — PROTOCOL LIFECYCLE

**Status:** <20% coverage

**Critical Gaps:**
- State machine transitions (initialize → ready → active → shutdown)
- Error recovery and retry logic
- Graceful shutdown procedures
- Concurrent lifecycle operations
- Resource cleanup

**Test Requirements (7 tests):**
1. `test_lifecycle_initialize_success()` — successful init
2. `test_lifecycle_initialize_timeout()` — init timeout
3. `test_lifecycle_ready_state_transition()` — state machine
4. `test_lifecycle_active_to_shutdown()` — shutdown sequence
5. `test_lifecycle_error_recovery()` — error recovery
6. `test_lifecycle_concurrent_operations()` — concurrency safety
7. `test_lifecycle_resource_cleanup()` — cleanup verification

**Coverage Impact:** +6-8%

---

### 3. embeddings/batcher.py + deduplication (5 functions, 1 class) — DATA PIPELINE

**Status:** <10% coverage

**Critical Gaps:**
- Batch size optimization
- Deduplication logic (hash collisions)
- Memory efficiency with large datasets
- Error handling in batch processing

**Test Requirements (5 tests):**
1. `test_embeddings_batch_exact_size()` — batch size control
2. `test_embeddings_batch_overflow()` — partial batches
3. `test_embeddings_dedupe_duplicates()` — deduplication
4. `test_embeddings_dedupe_hash_collision()` — hash handling
5. `test_embeddings_batch_memory_efficiency()` — memory usage

**Coverage Impact:** +4-6%

---

### 4. server/http.py (18 functions, 9 public) — HTTP ROUTES

**Status:** <15% coverage

**Critical Gaps:**
- Route handlers not tested
- Request validation missing
- Response formatting untested
- Error status codes not validated
- Content negotiation (JSON vs YAML)

**Test Requirements (8 tests):**
1. `test_http_route_health_check()` — health endpoint
2. `test_http_route_list_embeddings()` — GET endpoints
3. `test_http_route_create_embedding()` — POST endpoints
4. `test_http_route_invalid_request()` — validation errors
5. `test_http_route_500_error()` — server error
6. `test_http_route_timeout()` — timeout handling
7. `test_http_response_format_json()` — JSON response
8. `test_http_response_format_yaml()` — YAML response

**Coverage Impact:** +6-8%

---

### 5. adapters/ (5 adapters × 3-6 functions) — PLUGGABLE BACKENDS

**Status:** <20% coverage across adapters

**Tested Items per adapter:**
- mock_adapter.py (6 functions) — 30% coverage
- zendesk_adapter.py (4 functions) — 15% coverage
- pinecone_adapter.py (3 functions) — 10% coverage
- Others (similar coverage)

**Test Requirements (8 tests):**
1. `test_mock_adapter_search()` — mock search
2. `test_zendesk_adapter_connect()` — zendesk connection
3. `test_zendesk_adapter_search()` — zendesk search
4. `test_pinecone_adapter_index()` — pinecone indexing
5. `test_adapter_error_handling()` — error cases
6. `test_adapter_concurrent_requests()` — concurrency
7. `test_adapter_timeout_fallback()` — timeout handling
8. `test_adapter_rate_limit_backoff()` — rate limit handling

**Coverage Impact:** +6-8%

---

## High-Priority Gaps

### 6. rate_limit_middleware.py (10 functions, 7 public)

**Status:** <20% coverage

**Gap:** Rate limit enforcement, backoff strategy untested

**Test Requirements (4 tests):**
1. `test_rate_limit_exceeded()` — limit enforcement
2. `test_rate_limit_backoff()` — exponential backoff
3. `test_rate_limit_reset()` — window reset
4. `test_rate_limit_multiple_clients()` — client isolation

**Coverage Impact:** +4-5%

---

## Execution Order (Phase 4 + 5)

### Phase 4A (Target: 25% coverage)
1. auth.py (6 tests) → +5-7%
2. lifecycle.py (7 tests) → +6-8%
3. **Subtotal:** +11-15% (current 16.7% → 27.7-31.7%)

### Phase 4B (Target: 40% coverage)
1. embeddings/ (5 tests) → +4-6%
2. server/http.py (8 tests) → +6-8%
3. rate_limit_middleware.py (4 tests) → +4-5%
4. **Subtotal:** +14-19% (27.7% → 41.7-46.7%)

### Phase 5A (Target: 55% coverage)
1. adapters/ (8 tests) → +6-8%
2. Other modules (misc) → +4-6%
3. **Subtotal:** +10-14% (41.7% → 51.7-55.7%)

### Phase 5B+ (Target: 70-80% coverage)
- Edge cases and advanced scenarios
- Integration tests
- Performance assertions

---

## Success Criteria

- [ ] All 6 auth.py tests passing (Phase 4A)
- [ ] All 7 lifecycle.py tests passing (Phase 4A)
- [ ] All embeddings tests passing (Phase 4B)
- [ ] All 8 http.py tests passing (Phase 4B)
- [ ] Coverage: 16.7% → 25% (Phase 4A), 25% → 40% (Phase 4B)
- [ ] No test isolation issues
- [ ] CI time budget maintained

