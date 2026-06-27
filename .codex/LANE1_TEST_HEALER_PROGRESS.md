# Phase 4, Lane 1 — Test Foundation Hardening
**Status**: IN_PROGRESS
**Timestamp**: 2026-06-27T03:15:47Z
**Agent**: autonomous-test-healer-agent v2.0.0-s228

## Objective
Detect and fix 6 fragile tests in the _codex_ repository:
- 3 subprocess timing tests
- 2 file system race conditions  
- 1 async state leak

## Fragile Tests Identified

### Category 1: Subprocess Timing Tests (3 tests)
1. **test_budget_cap_raises_on_timeout** (`tests/autonomy/test_autonomy_scheduler.py`)
   - Issue: Timer precision on loaded CI runners
   - Current: `@pytest.mark.flaky(reruns=2)` with 0.15s timeout
   - Fix: Add exponential backoff retry loop ✓ (already has retry, needs validation)
   
2. **test_file_cache_expiry** (`tests/space_traversal/test_performance.py`)
   - Issue: TTL precision on loaded CI runners
   - Current: `@pytest.mark.flaky(reruns=2)` with 2.0s sleep
   - Fix: Add deterministic TTL validation with polling

3. **test_file_cache_cleanup_expired** (`tests/space_traversal/test_performance.py`)
   - Issue: TTL precision on loaded CI runners
   - Current: `@pytest.mark.flaky(reruns=2)` 
   - Fix: Add deterministic cleanup validation

### Category 2: File System Race Conditions (2 tests)
4. **test_file_cache_clear** (`tests/space_traversal/test_performance.py`)
   - Issue: Potential race condition during cache clear
   - Current: No locking mechanism
   - Fix: Add atomic file operations or file locks

5. **test_file_cache_invalidate** (`tests/space_traversal/test_performance.py`)
   - Issue: Race condition on file deletion
   - Current: No locking mechanism
   - Fix: Add proper file locking with fcntl

### Category 3: Async State Leak (1 test)
6. **test_concurrent_enqueue_dequeue** (`tests/coverage_phase5/test_async_protocol_handling.py`)
   - Issue: Event loop not properly reset between tests
   - Current: No event loop cleanup
   - Fix: Add fixture to reset event loop state after each test

## Progress Tracking

- [ ] Identify all 6 fragile tests ✓
- [ ] Analyze root causes
- [ ] Apply fixes
- [ ] Validate with 3x pytest runs
- [ ] Create/update FRAGILE_TEST_PATTERNS.md
- [ ] Commit and push changes

## Validation Results

TBD

## Commit Log

TBD
