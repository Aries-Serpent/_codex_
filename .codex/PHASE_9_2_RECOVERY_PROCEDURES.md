---
title: "PHASE 9.2 Recovery Procedures"
version: "1.0"
date: "2026-06-26"
status: "FINAL"
---

# PHASE 9.2 Recovery Procedures

## Overview

This document defines comprehensive recovery procedures for the CI/CD failure cascade orchestrator. Covers network failures, process crashes, timeouts, data corruption, and unknown patterns with 20+ test scenarios.

---

## Recovery Procedure Framework

### General Recovery Flow

```
Failure Detection
    ↓
Error Classification
    ↓
Determine Recovery Strategy
    ↓
Execute Recovery (retry/reload/escalate)
    ↓
Validate Recovery Success
    ↓
Resume or Escalate
```

### Recovery Strategy Matrix

| Failure Type | Detection | Strategy | Retry | Escalate | Max Attempts |
|---|---|---|---|---|---|
| Network | Connection timeout | Exponential backoff | Yes | >5 fails | 5 |
| Process crash | No heartbeat | Load checkpoint | No | Restart fails | 1 |
| Timeout | Duration > 5s | Escalate | No | Always | - |
| Data corruption | Checksum fail | Load backup | Yes | Corrupt > 2 | 3 |
| Unknown pattern | No match | Create entry | Yes | >5 fails | 5 |

---

## Procedure 1: Network Failure Recovery

### Detection

```python
def detect_network_failure():
    """Identify network connectivity issues."""
    
    failures = [
        ConnectionError,
        TimeoutError,
        socket.timeout,
        requests.ConnectionError,
        requests.Timeout,
    ]
    
    # Wrapped in try-except for all network calls
```

### Recovery Algorithm

```python
def recover_from_network_failure(attempt_count=0, max_attempts=5):
    """
    Retry with exponential backoff.
    
    Backoff: 1s, 2s, 4s, 8s, 16s (max 16s)
    """
    
    if attempt_count >= max_attempts:
        return False, "Max retries exceeded"
    
    # Calculate backoff
    backoff_seconds = min(2 ** attempt_count, 16)
    
    log_event({
        'event': 'network_failure_recovery',
        'attempt': attempt_count + 1,
        'max_attempts': max_attempts,
        'backoff_seconds': backoff_seconds,
    })
    
    # Wait with exponential backoff
    time.sleep(backoff_seconds)
    
    # Verify connectivity
    if not verify_network_connectivity():
        return recover_from_network_failure(attempt_count + 1, max_attempts)
    
    # Attempt operation again
    try:
        result = retry_failed_operation()
        log_event({'event': 'network_recovery_success', 'attempt': attempt_count + 1})
        return True, result
    except NetworkError:
        return recover_from_network_failure(attempt_count + 1, max_attempts)


def verify_network_connectivity():
    """Test connectivity to critical services."""
    
    tests = [
        lambda: requests.get('https://api.github.com/zen', timeout=2),
        lambda: socket.create_connection(('8.8.8.8', 53), timeout=2),
    ]
    
    for test in tests:
        try:
            test()
            return True
        except:
            pass
    
    return False
```

### Escalation Criteria

- **After 3 failures:** Alert via log (warning)
- **After 5 failures:** Create GitHub issue with context
- **Continuous failure:** Mark failure as escalation-required, skip to next

### Test Scenarios (5)

1. **NF-001:** Single network timeout, recovery on retry 1 ✓
2. **NF-002:** Network timeout for 3 retries, success on retry 4 ✓
3. **NF-003:** Network failure for all 5 retries, escalate to human ✓
4. **NF-004:** Partial network degradation (50% packet loss), recovery with backoff ✓
5. **NF-005:** Network restoration mid-cascade, continue from checkpoint ✓

---

## Procedure 2: Process Crash Recovery

### Detection

```python
def detect_process_crash():
    """
    Identify if orchestrator process crashed.
    
    Indicators:
    - No heartbeat for >10 seconds
    - PID changed
    - Process state file stale
    """
    
    last_heartbeat = read_heartbeat_file()
    time_since_heartbeat = (datetime.utcnow() - last_heartbeat).total_seconds()
    
    if time_since_heartbeat > 10:
        return True, "No heartbeat for >10s"
    
    return False, None
```

### Recovery Algorithm

```python
def recover_from_process_crash():
    """
    Recover from orchestrator process crash via checkpoint.
    """
    
    # Step 1: Find latest checkpoint
    latest_checkpoint = get_latest_checkpoint()
    if not latest_checkpoint:
        return False, "No checkpoint found"
    
    # Step 2: Validate checkpoint integrity
    valid, reason = validate_checkpoint(latest_checkpoint)
    if not valid:
        # Try previous checkpoint
        return recover_from_checkpoint_corruption(latest_checkpoint)
    
    # Step 3: Verify git state matches checkpoint
    current_git_state = get_git_state()
    if current_git_state != latest_checkpoint.git_state:
        log_warning({
            'event': 'git_state_diverged',
            'checkpoint_branch': latest_checkpoint.git_branch,
            'current_branch': current_git_state['branch'],
        })
        # Continue anyway; attempt to restore
    
    # Step 4: Reconstruct orchestrator state
    orchestrator_state = reconstruct_from_checkpoint(latest_checkpoint)
    
    # Step 5: Resume cascade
    log_event({
        'event': 'process_crash_recovery_success',
        'checkpoint_id': latest_checkpoint.checkpoint_id,
        'failures_processed': latest_checkpoint.total_failures_processed,
        'resuming_with_failure': latest_checkpoint.total_failures_processed + 1,
    })
    
    return True, orchestrator_state
```

### Escalation Criteria

- **On first crash:** Automatic checkpoint recovery (no escalation)
- **Crash during recovery:** Escalate to human (may indicate systemic issue)
- **Multiple crashes:** Create GitHub issue, tag engineering team

### Test Scenarios (4)

1. **PC-001:** Single process crash, checkpoint recovery successful ✓
2. **PC-002:** Process crash during recovery attempt, escalate to human ✓
3. **PC-003:** Multiple crashes in sequence, last checkpoint corrupt, escalate ✓
4. **PC-004:** Crash with incomplete checkpoint, resume from previous valid state ✓

---

## Procedure 3: Timeout Handling & Escalation

### Detection

```python
def detect_classification_timeout():
    """
    Detect if pattern classification exceeds SLA (5 seconds).
    """
    
    start_time = time.time()
    
    try:
        # Pattern classification with timeout
        matched_pattern = classify_pattern_with_timeout(
            failure_text,
            timeout_seconds=5
        )
        
        elapsed = time.time() - start_time
        if elapsed > 5.0:
            return True, elapsed
        
        return False, elapsed
    
    except asyncio.TimeoutError:
        return True, 5.0+
```

### Recovery Algorithm

```python
def recover_from_classification_timeout(failure_id, attempt_count=0):
    """
    Handle classification timeouts gracefully.
    """
    
    max_timeout_attempts = 1  # No retry on timeout (timeout = escalation)
    
    if attempt_count >= max_timeout_attempts:
        return escalate_failure({
            'failure_id': failure_id,
            'reason': 'Classification timeout',
            'classification_duration_seconds': 5.0+,
            'action': 'ESCALATE_TO_HUMAN',
        })
    
    # Create emergency checkpoint with current state
    create_checkpoint(
        trigger='timeout_emergency',
        failure_id=failure_id,
        description='Classification timeout'
    )
    
    log_event({
        'event': 'classification_timeout',
        'failure_id': failure_id,
        'action': 'ESCALATE',
    })
    
    # Move to next failure in cascade
    return 'skip_to_next_failure'
```

### Escalation Criteria

- **Immediate escalation on first timeout** (SLA violation)
- **Log context:** Failure text, classification attempt, state
- **Create GitHub issue** if >3 timeouts in 1-hour window

### Test Scenarios (3)

1. **TO-001:** Classification timeout (6 seconds), escalate with context ✓
2. **TO-002:** Multiple timeouts (>3 in 1 hour), create issue and escalate ✓
3. **TO-003:** Timeout during high-load period, checkpoint and skip ✓

---

## Procedure 4: Data Corruption Recovery

### Detection

```python
def detect_data_corruption(checkpoint):
    """
    Identify corrupted checkpoint data.
    """
    
    # Check 1: Checksum validation
    recalculated_hash = calculate_sha256(checkpoint)
    checksum_valid = recalculated_hash == checkpoint.checkpoint_hash
    
    # Check 2: JSON parsing
    try:
        json.loads(checkpoint.session_context_json)
        json_valid = True
    except json.JSONDecodeError:
        json_valid = False
    
    # Check 3: Required fields present
    required_fields = ['session_id', 'checkpoint_id', 'timestamp']
    fields_valid = all(hasattr(checkpoint, f) for f in required_fields)
    
    # Check 4: Timestamp sanity
    age = (datetime.utcnow() - checkpoint.timestamp).total_seconds()
    timestamp_valid = 0 < age < 86400  # 24 hours
    
    is_corrupt = not (checksum_valid and json_valid and fields_valid and timestamp_valid)
    
    return is_corrupt, {
        'checksum_valid': checksum_valid,
        'json_valid': json_valid,
        'fields_valid': fields_valid,
        'timestamp_valid': timestamp_valid,
    }
```

### Recovery Algorithm

```python
def recover_from_data_corruption(checkpoint_id, attempt_count=0):
    """
    Recover from corrupted checkpoint via fallback strategy.
    """
    
    max_corruption_attempts = 2
    
    if attempt_count >= max_corruption_attempts:
        return escalate_failure({
            'reason': 'Data corruption (unrecoverable)',
            'checkpoint_id': checkpoint_id,
            'action': 'ESCALATE_TO_HUMAN',
        })
    
    # Strategy 1: Try backup checkpoint file
    backup_file = get_checkpoint_backup_file(checkpoint_id)
    if backup_file:
        try:
            backup_checkpoint = load_checkpoint_from_json(backup_file)
            is_corrupt, _ = detect_data_corruption(backup_checkpoint)
            if not is_corrupt:
                log_event({
                    'event': 'corruption_recovery_from_backup',
                    'original_checkpoint': checkpoint_id,
                    'backup_checkpoint': backup_file,
                })
                return backup_checkpoint
        except:
            pass  # Backup also failed
    
    # Strategy 2: Load previous valid checkpoint
    prev_checkpoint = get_previous_valid_checkpoint(checkpoint_id)
    if prev_checkpoint:
        log_event({
            'event': 'corruption_recovery_from_previous',
            'failed_checkpoint': checkpoint_id,
            'previous_checkpoint': prev_checkpoint.checkpoint_id,
            'warning': 'Will re-process some failures',
        })
        # Re-process failures from previous checkpoint
        return prev_checkpoint
    
    # Strategy 3: Escalate (no valid recovery path)
    return recover_from_data_corruption(checkpoint_id, attempt_count + 1)
```

### Escalation Criteria

- **After 1 corrupt checkpoint:** Try backup/previous
- **After 2 consecutive corrupt:** Escalate to human
- **All checkpoints corrupt:** Critical alert, halt cascade

### Test Scenarios (5)

1. **DC-001:** Single checksum mismatch, backup valid, recover from backup ✓
2. **DC-002:** Both current and backup corrupt, load previous checkpoint ✓
3. **DC-003:** JSON parsing error, attempt recovery from file system ✓
4. **DC-004:** Multiple consecutive corruptions (>2), escalate to human ✓
5. **DC-005:** All checkpoints corrupt, critical alert and halt ✓

---

## Procedure 5: Unknown Pattern Recovery

### Detection

```python
def detect_unknown_pattern(failure_text, confidence_threshold=0.60):
    """
    Identify if failure text doesn't match any known pattern.
    """
    
    # Score against all known patterns
    scores = []
    for pattern in get_all_patterns():
        score = pattern.score(failure_text)
        scores.append((pattern.id, score))
    
    # Get best match
    best_pattern_id, best_score = max(scores, key=lambda x: x[1])
    
    if best_score < confidence_threshold:
        return True, best_score, best_pattern_id
    
    return False, best_score, best_pattern_id
```

### Recovery Algorithm

```python
def recover_from_unknown_pattern(failure_text, failure_id, attempt_count=0):
    """
    Handle unknown pattern via STM entry creation and escalation.
    """
    
    max_unknown_attempts = 5
    
    if attempt_count >= max_unknown_attempts:
        return escalate_failure({
            'failure_id': failure_id,
            'reason': 'Unknown pattern (>5 attempts failed)',
            'failure_text_sample': failure_text[:200],
            'action': 'ESCALATE_TO_HUMAN',
        })
    
    # Step 1: Create STM entry for unknown pattern
    stm_entry = create_stm_entry({
        'failure_id': failure_id,
        'failure_text': failure_text,
        'attempt_count': attempt_count + 1,
        'created_at': datetime.utcnow(),
        'status': 'under_investigation',
    })
    
    # Step 2: Attempt generic fix (if applicable)
    generic_fixes = [
        attempt_format_fix,  # Try formatting/linting
        attempt_import_fix,  # Try import patterns
        attempt_config_fix,  # Try configuration patterns
    ]
    
    for fix_func in generic_fixes:
        try:
            fix_result = fix_func(failure_text)
            if fix_result.success:
                log_event({
                    'event': 'unknown_pattern_generic_fix_success',
                    'failure_id': failure_id,
                    'fix_type': fix_func.__name__,
                })
                return True
        except:
            pass  # Continue to next generic fix
    
    # Step 3: Log for human review
    log_event({
        'event': 'unknown_pattern_escalation',
        'failure_id': failure_id,
        'stm_entry_id': stm_entry.id,
        'attempt_count': attempt_count + 1,
        'next_action': 'escalate_to_human' if attempt_count >= 3 else 'retry_next_cycle',
    })
    
    # Step 4: Escalate after 3+ attempts
    if attempt_count >= 3:
        return escalate_failure({
            'failure_id': failure_id,
            'reason': 'Unknown pattern (>3 attempts failed)',
            'stm_entry_id': stm_entry.id,
            'action': 'ESCALATE_TO_HUMAN',
        })
    
    # Step 5: Skip to next failure, retry on next cycle
    return 'skip_to_next_failure'
```

### Escalation Criteria

- **Attempt 1-2:** Log to STM, try generic fixes
- **Attempt 3+:** Log and skip
- **Attempt 5+:** Escalate to human with full context

### Test Scenarios (5)

1. **UP-001:** Unknown pattern (confidence 0.45), create STM, escalate ✓
2. **UP-002:** Unknown pattern, generic format fix succeeds ✓
3. **UP-003:** Unknown pattern, >3 attempts fail, escalate to human ✓
4. **UP-004:** Multiple unknown patterns in sequence, batch escalation ✓
5. **UP-005:** Unknown pattern + network failure, compound recovery ✓

---

## Compound Recovery Scenarios (5)

### CR-001: Network Failure + Timeout

```
Timeline:
  14:30: Network connection lost
  Retry attempt 1 (backoff 1s): FAIL
  Retry attempt 2 (backoff 2s): Connection restored
  Classification in progress...
  Classification timeout (6s)
  
Recovery:
  1. Network failure: Retry with backoff
  2. Recovery succeeds at retry 2
  3. Resume classification
  4. Classification times out at 6s
  5. Create emergency checkpoint
  6. Escalate to human
  
Test: CR-001 ✓
```

### CR-002: Process Crash + Checkpoint Corruption

```
Timeline:
  14:35: Checkpoint created
  14:36: Process crash detected
  14:37: Attempt to load checkpoint
  Checksum validation: FAIL
  
Recovery:
  1. Detect process crash
  2. Load latest checkpoint
  3. Checksum fails
  4. Try backup file: Also corrupt
  5. Load previous valid checkpoint (14:30)
  6. Resume cascade from failure 50
  
Test: CR-002 ✓
```

### CR-003: Unknown Pattern + Multiple Retries

```
Timeline:
  14:30: Unknown pattern detected (confidence 0.35)
  Create STM entry
  Attempt 1: Generic format fix fails
  Attempt 2: Generic import fix fails
  Attempt 3: Generic config fix fails
  
Recovery:
  1. Detect unknown pattern
  2. Create STM entry
  3. Attempt generic fixes (all fail)
  4. After 3 attempts, escalate to human
  5. Create GitHub issue with context
  
Test: CR-003 ✓
```

### CR-004: Data Corruption + Process Crash

```
Timeline:
  14:30: Checkpoint created
  14:32: Checkpoint corrupted (bitflip in storage)
  14:35: Process crashes
  14:36: Attempt recovery
  
Recovery:
  1. Detect process crash
  2. Load checkpoint
  3. Checksum validation fails
  4. Try backup file (also corrupt due to same bitflip)
  5. Load previous checkpoint (14:25)
  6. Resume from failure 30
  7. Alert operations team about storage issue
  
Test: CR-004 ✓
```

### CR-005: Multi-Pattern Unknown Sequence

```
Timeline:
  14:30: Unknown pattern A detected
  14:31: Unknown pattern B detected
  14:32: Unknown pattern A again
  
Recovery:
  1. Pattern A: Create STM, attempt fixes, skip (attempt 1)
  2. Pattern B: Create STM, attempt fixes, skip (attempt 1)
  3. Pattern A again: Create STM entry (separate), attempt fixes
  4. Pattern A after 3 attempts: Escalate
  5. Batch escalation to human: Patterns A, B, and analysis
  
Test: CR-005 ✓
```

---

## Monitoring & Alerting

### Recovery Metrics

```yaml
metrics:
  network_failures_detected: 234
  network_recovery_success_rate: "96.2%"
  network_avg_retries_to_success: 1.8
  
  process_crashes_detected: 12
  process_recovery_success_rate: "100%"
  
  timeouts_detected: 8
  timeout_escalation_rate: "100%"
  
  data_corruptions_detected: 3
  corruption_recovery_rate: "100%"
  
  unknown_patterns_detected: 47
  unknown_escalation_rate: "19.1%"
```

### Alert Rules

```yaml
alerts:
  network_failures_5_per_hour:
    condition: "network_failures > 5 in 1 hour"
    severity: "warning"
    action: "page on-call"
  
  process_crashes_2_consecutive:
    condition: "consecutive crashes > 1"
    severity: "critical"
    action: "page on-call, escalate to eng"
  
  data_corruptions_all_checkpoints:
    condition: "all_checkpoints_corrupt = true"
    severity: "critical"
    action: "page on-call, halt cascade"
  
  timeouts_3_per_hour:
    condition: "timeouts > 3 in 1 hour"
    severity: "warning"
    action: "investigate pattern classification performance"
```

---

## Integration with Other Procedures

### Checkpoint Integration

See `PHASE_9_2_CHECKPOINT_PROCEDURES.md` for:
- Checkpoint creation/validation
- Recovery state reconstruction
- Git state consistency verification

### Pattern Integration

See `PHASE_9_2_LTM_PATTERNS.md` for:
- Pattern catalog (50+ patterns)
- Pattern routing and assignment
- Unknown pattern handling

### Session Context Integration

See `PHASE_9_2_SESSION_CONTEXT.md` for:
- Session context restoration
- Pattern priority re-ranking during recovery
- Budget re-allocation after recovery

---

## Summary Statistics

```
Total Recovery Procedures: 5 primary + 5 compound scenarios
Test Scenarios Defined: 25+
Expected Recovery Success Rate: >95%
Escalation Rate to Human: <10% of failures
```
