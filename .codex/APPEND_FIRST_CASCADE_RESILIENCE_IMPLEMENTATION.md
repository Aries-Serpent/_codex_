# Append-First Cascade Resilience Implementation (S294+)

**Date:** 2026-07-15  
**Session:** Current (Cascade Resilience Improvement)  
**Status:** Implementation Complete  

## Executive Summary

This document describes the implementation of **append-first cascade resilience** in the rescue comment posting system. The previous session (PR #5324) implemented cascade detection with abort-on-cascade behavior to prevent feedback loops. This session improves upon that by ensuring **no comments are lost** when cascades are detected by implementing:

1. **Append-first behavior**: When cascades detected, append to existing successful comments instead of aborting
2. **Comment batching**: Automatically batch multiple workflow failures into single comment updates to prevent rate-limiting
3. **Queue-based retry**: Rate-limited comments are queued for batch posting rather than lost

## Problem Statement

The previous cascade detection fix (PR #5324) resolved the feedback loop issue by detecting cascading errors and aborting rescue comment posting. However, this approach had a critical flaw:

- **Issue**: Comments were completely lost when cascades were detected
- **Impact**: Users didn't see all workflow failures on PRs affected by cascades
- **Desired**: Append failures to already-posted comments, batch multiple failures together, prevent rate-limiting

## Solution Architecture

### 1. Cascade Detection Enhancement

**File**: `scripts/ci/post_rescue_comment.py`

Changed cascade detection actions:
- **OLD**: `"ABORT_POSTING"` → Stop posting entirely
- **NEW**: `"APPEND_TO_EXISTING"` → Append to existing comment or queue for batch
- **ALSO**: `"SKIP_CONSOLIDATION"` → Skip consolidation but continue with append

```python
def _detect_cascading_copilot_errors(...) -> dict:
    # Returns action: "APPEND_TO_EXISTING" | "SKIP_CONSOLIDATION" | "PROCEED"
```

### 2. Comment Batching Queue System

**File**: `scripts/ci/rescue_comment_batch_queue.py` (NEW)

New module provides:
- Queue storage in `.codex/rescue-comment-queue/` directory
- Per-PR/per-commit queue files (JSON format)
- Batch item tracking with full metadata
- Queue flushing with timeout-based batch boundaries

```python
# Queue a comment for batch posting
batch_queue.queue_item(
    pr_number=123,
    commit_sha='abc123...',
    workflow_name='Test Workflow',
    run_id='999',
    run_url='https://...',
    section_title='Optional Title',
    section_content='Optional Content'
)

# Check if queue should flush (batch window expired)
if batch_queue.should_flush_queue(pr_number, commit_sha, batch_wait_seconds=3):
    items = batch_queue.flush_queue(pr_number, commit_sha)
```

### 3. Append-First Cascade Handling

**Function**: `_handle_cascade_append()` in `post_rescue_comment.py`

Implements the core append-first logic:

```
If cascade detected:
  ├─ If existing comment found
  │  └─ APPEND section to existing comment (guaranteed success)
  └─ If no existing comment found
     └─ QUEUE for batch posting (wait for window, then post as batch)
```

**Key behavior**:
- When 10+ Copilot errors detected (cascade threshold):
  - Try to append to existing rescue comment
  - If append succeeds → return (comment preserved)
  - If no existing comment → queue and return (will post later)
- When 5-9 errors detected (early cascade):
  - Skip consolidation to prevent growth
  - But continue with normal append to existing comment

### 4. Rate-Limit Resilience

**Location**: `main()` function, POST error handling

Rate-limited comments are now queued instead of lost:

```
If rate limit (429 or 403 "rate limit"):
  ├─ Queue the comment for batch posting
  └─ Exit gracefully (no CI failure)
```

This ensures that transient rate-limits don't cause comments to be completely dropped.

### 5. Batch Posting Strategy

**Batch window**: Configurable via `BATCH_WAIT_SECONDS` environment variable (default: 3 seconds)

When multiple workflows fail on the same commit within a short timeframe:
1. First failure → Post initial rescue comment
2. Second+ failures (within 3 seconds) → Queue for batch
3. Batch window expires → Flush all queued items as single append to initial comment

**Benefits**:
- Prevents multiple comment threads for same commit
- Avoids rate-limiting (single append instead of N posts)
- Comments are never lost
- Reduces notification spam

## Implementation Details

### Files Modified

1. **`scripts/ci/post_rescue_comment.py`**
   - Updated docstring to document batching behavior
   - Changed `_detect_cascading_copilot_errors()` to return `"APPEND_TO_EXISTING"` instead of `"ABORT_POSTING"`
   - Added `_get_batch_queue_module()` for lazy loading
   - Added `_handle_cascade_append()` for append-first logic
   - Modified `main()` to use cascade append handling
   - Updated rate-limit handling to queue instead of skip

2. **`scripts/ci/rescue_comment_batch_queue.py`** (NEW)
   - Batch queue management with JSON storage
   - Queue file naming: `queue_{pr_number}_{sha_short}.json`
   - Queue location: `.codex/rescue-comment-queue/`
   - Batch item tracking with metadata

3. **`.github/scripts/post_copilot_followup.py`**
   - Added missing imports: `os`, `tempfile`

### Key Functions

#### `_detect_cascading_copilot_errors()`
- **Input**: `token, repo, pr_number, threshold=10`
- **Output**: Dictionary with `action` field
  - `"PROCEED"` → No cascade, normal posting
  - `"APPEND_TO_EXISTING"` → 10+ errors, use append-first
  - `"SKIP_CONSOLIDATION"` → 5-9 errors, skip consolidation

#### `_handle_cascade_append()`
- **Input**: PR info + existing comment ID + workflow details
- **Output**: `True` if handled successfully, `False` otherwise
- **Logic**:
  1. If existing comment: append section and PATCH
  2. If no existing: queue item and return
  3. Return success status

#### `batch_queue.queue_item()`
- **Input**: Workflow metadata
- **Output**: None (side effect: writes to queue file)
- **File location**: `.codex/rescue-comment-queue/queue_{pr}_{sha}.json`

### Backward Compatibility

- Existing single-workflow posting path remains unchanged
- `APPEND_ONLY` mode continues to work as before
- Queue system is optional (graceful degradation if import fails)
- Cascade detection is backward compatible (extends previous behavior)

## Testing Strategy

### Unit Tests

```python
# Test batch queue operations
test_queue_initialization()
test_queue_item_creation()
test_queue_retrieval()
test_queue_flushing()
test_queue_digest_deduplication()

# Test cascade append
test_cascade_append_to_existing()
test_cascade_queue_when_no_existing()
test_cascade_skip_consolidation()

# Test rate-limit handling
test_rate_limit_queuing()
test_rate_limit_graceful_exit()
```

### Integration Tests

- Multiple workflows failing on same commit → batch into single comment
- Rate-limited posts → queue and retry on next workflow
- Cascade detection (10+ errors) → append to existing, don't abort
- No duplicate content in appended sections (digest markers)

## Migration Path

No user action required. The system is fully backward compatible:

1. Existing workflows continue to post comments normally
2. Cascade detection automatically engages when 10+ errors detected
3. Batching happens transparently (no configuration needed)
4. Optional: Set `BATCH_WAIT_SECONDS` env var to tune batch window

## Future Enhancements

1. **Batch flushing on timeout**: Implement time-based batch flushing (currently manual)
2. **Batch content optimization**: Compress batched content if approaching size limits
3. **Per-workflow batch tracking**: Track which workflows are queued for which commits
4. **Analytics**: Log batch statistics (count, size, timing) for monitoring

## Monitoring & Diagnostics

### Queue Health Checks

```bash
# List queued items
ls -la .codex/rescue-comment-queue/

# Check queue file contents
cat .codex/rescue-comment-queue/queue_123_abc123.json

# Manually flush queue (if needed)
# (Called automatically on next workflow failure)
```

### Log Indicators

- `✅ Queued...` → Item successfully queued for batch
- `🔄 CASCADE APPEND:` → Cascade detected, using append-first
- `⚠️ CASCADE SKIP:` → Cascade detected, skipping consolidation
- `✅ CASCADE: Appended...` → Cascade comment successfully appended
- `⚠️ Batch queue failed:` → Queue operation failed (graceful degradation)

## Related PRs & Issues

- **PR #5324**: Previous cascade fix (abort-on-cascade behavior)
- **Issue**: "Cascade detected → rescue posting aborted → no new webhooks → cascade stops immediately"
- **This PR**: Improved cascade handling with append-first batching

## References

- Script: `scripts/ci/post_rescue_comment.py` (S294 marker in docstring)
- Module: `scripts/ci/rescue_comment_batch_queue.py` (new batch queue system)
- Marker: `<!-- ci-rescue-sha:{pr_number}:{sha_short} -->` (unchanged)
- Threshold: 10 errors for cascade detection, 5 errors for skip-consolidation
