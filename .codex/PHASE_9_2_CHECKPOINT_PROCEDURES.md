---
title: "PHASE 9.2 Checkpoint Procedures"
version: "1.0"
date: "2026-06-26"
status: "FINAL"
---

# PHASE 9.2 Checkpoint Procedures

## Overview

This document defines **state checkpointing** procedures for the CI/CD failure cascade orchestrator. Checkpoints preserve orchestrator state, progress, and validation results to enable robust recovery from network failures, process crashes, or timeouts.

---

## Checkpoint Strategy

### Frequency

**Trigger:** Either condition (whichever occurs first)
- Every **50 failures processed**
- Every **5 minutes** (wall-clock time)

```python
def should_checkpoint(failure_count_since_last_checkpoint, time_since_last_checkpoint):
    """Determine if checkpoint needed."""
    return (
        failure_count_since_last_checkpoint >= 50 or
        time_since_last_checkpoint >= 300  # 5 minutes
    )
```

### Checkpoint Storage

**Location:** `.codex/checkpoints/cascade_<session_id>_<timestamp>.json`

**Storage Strategy:**
1. **Primary:** SQLite database (`.codex/cascade_checkpoints.db`)
2. **Backup:** JSON files (`.codex/checkpoints/`)
3. **Archive:** Git commits (immutable record, optional)

**Retention:** Keep last 10 checkpoints per session; delete older checkpoints after 7 days

---

## Checkpoint Contents

### Data Structure

```python
@dataclass
class CascadeCheckpoint:
    """State to preserve at checkpoint."""
    
    # Metadata
    session_id: str
    checkpoint_id: str  # Unique ID (UUID)
    timestamp: datetime
    checkpoint_trigger: str  # "failure_count_threshold" or "time_threshold"
    
    # Processing state
    total_failures_processed: int
    current_failure_id: str  # Failure being processed
    current_pattern_match: str  # Pattern matched (e.g., "RP-001")
    current_attempt_count: int  # Attempt # for current failure
    
    # Session context
    session_context: SessionContext
    patterns_in_use: List[str]  # Pattern IDs active in session
    routing_decisions: Dict[str, str]  # failure_id → agent_id
    
    # Progress tracking
    fix_attempts: List[FixAttempt]  # All attempted fixes
    validation_results: List[ValidationResult]  # Test/lint results
    escalations: List[EscalationRecord]  # Issues escalated to human
    
    # Git state
    git_branch: str
    git_commit_hash: str
    git_working_dir_clean: bool
    git_staged_changes: List[str]
    
    # Failure recovery state
    rollback_history: List[RollbackRecord]  # Previous rollbacks
    recovery_attempted: int  # Number of recovery attempts
    last_successful_fix_timestamp: datetime
    
    # Integrity checks
    checkpoint_hash: str  # SHA256 of checkpoint contents
    checksum_validation: bool  # Verified checksum on load
```

---

## Checkpoint Lifecycle

### Phase 1: Creation

```python
def create_checkpoint(orchestrator_state):
    """Create and persist checkpoint."""
    
    checkpoint = CascadeCheckpoint(
        session_id=orchestrator_state.session_id,
        checkpoint_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        checkpoint_trigger=determine_trigger(),
        
        # Copy state
        total_failures_processed=orchestrator_state.failure_count,
        current_failure_id=orchestrator_state.current_failure['id'],
        current_pattern_match=orchestrator_state.matched_pattern,
        current_attempt_count=orchestrator_state.attempt_count,
        
        # Session snapshot
        session_context=deepcopy(orchestrator_state.session_context),
        patterns_in_use=[p.id for p in orchestrator_state.patterns],
        routing_decisions=orchestrator_state.routing_decisions.copy(),
        
        # Progress snapshot
        fix_attempts=orchestrator_state.fix_attempts.copy(),
        validation_results=orchestrator_state.validation_results.copy(),
        escalations=orchestrator_state.escalations.copy(),
        
        # Git state snapshot
        git_branch=get_git_branch(),
        git_commit_hash=get_git_head(),
        git_working_dir_clean=is_git_working_dir_clean(),
        git_staged_changes=get_staged_files(),
        
        # Recovery state
        rollback_history=orchestrator_state.rollback_history.copy(),
        recovery_attempted=orchestrator_state.recovery_count,
        last_successful_fix_timestamp=orchestrator_state.last_success_time,
    )
    
    # Calculate checksum
    checkpoint.checkpoint_hash = calculate_sha256(checkpoint)
    
    # Persist checkpoint
    save_checkpoint_to_sqlite(checkpoint)
    save_checkpoint_to_json(checkpoint)
    
    log_event({
        'event': 'checkpoint_created',
        'checkpoint_id': checkpoint.checkpoint_id,
        'timestamp': checkpoint.timestamp,
        'failures_processed': checkpoint.total_failures_processed,
    })
    
    return checkpoint
```

### Phase 2: Persistence

```python
def save_checkpoint_to_sqlite(checkpoint):
    """Save checkpoint to SQLite database."""
    
    sql = """
    INSERT INTO checkpoints (
        checkpoint_id, session_id, timestamp, trigger,
        total_failures, current_failure, current_pattern, attempt_count,
        session_context_json, routing_decisions_json, git_branch, git_commit,
        checkpoint_hash, checksum_valid
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    db.execute(sql, (
        checkpoint.checkpoint_id,
        checkpoint.session_id,
        checkpoint.timestamp.isoformat(),
        checkpoint.checkpoint_trigger,
        checkpoint.total_failures_processed,
        checkpoint.current_failure_id,
        checkpoint.current_pattern_match,
        checkpoint.current_attempt_count,
        json.dumps(checkpoint.session_context, default=str),
        json.dumps(checkpoint.routing_decisions),
        checkpoint.git_branch,
        checkpoint.git_commit_hash,
        checkpoint.checkpoint_hash,
        True  # checksum_valid on creation
    ))
    
    db.commit()


def save_checkpoint_to_json(checkpoint):
    """Save checkpoint as JSON file for portability."""
    
    filename = (
        f".codex/checkpoints/"
        f"cascade_{checkpoint.session_id}_{checkpoint.timestamp.isoformat()}.json"
    )
    
    with open(filename, 'w') as f:
        json.dump(
            {
                'checkpoint': asdict(checkpoint),
                'metadata': {
                    'created_by': 'cascade_orchestrator',
                    'version': '1.0',
                    'python_version': sys.version,
                }
            },
            f,
            indent=2,
            default=str
        )
```

### Phase 3: Validation

```python
def validate_checkpoint(checkpoint):
    """Verify checkpoint integrity."""
    
    # Check 1: Checksum validation
    recalculated_hash = calculate_sha256(checkpoint)
    if recalculated_hash != checkpoint.checkpoint_hash:
        return False, "Checksum mismatch"
    
    # Check 2: Git state consistency
    current_git_state = get_git_state()
    if (current_git_state['branch'] != checkpoint.git_branch and
        current_git_state['commit'] != checkpoint.git_commit_hash):
        return False, "Git state diverged"
    
    # Check 3: Pattern IDs validity
    for pattern_id in checkpoint.patterns_in_use:
        if not pattern_exists_in_ltm(pattern_id):
            return False, f"Pattern {pattern_id} not found in LTM"
    
    # Check 4: Attempt count sanity
    if checkpoint.current_attempt_count > 10:  # Max retries
        return False, "Attempt count exceeded"
    
    # Check 5: Timestamp sanity
    age = (datetime.utcnow() - checkpoint.timestamp).total_seconds()
    if age > 86400:  # 24 hours
        return False, "Checkpoint too old (>24 hours)"
    
    return True, "Checkpoint valid"
```

### Phase 4: Recovery (on process restart)

```python
def load_and_recover_from_checkpoint(checkpoint_id):
    """Load checkpoint and resume cascade."""
    
    # Step 1: Load checkpoint
    checkpoint = load_checkpoint_from_sqlite(checkpoint_id)
    if not checkpoint:
        return None, "Checkpoint not found"
    
    # Step 2: Validate checkpoint
    valid, reason = validate_checkpoint(checkpoint)
    if not valid:
        return None, f"Checkpoint invalid: {reason}"
    
    # Step 3: Verify git state
    if not checkpoint.git_working_dir_clean:
        # Attempt to restore staged changes
        restore_staged_changes(checkpoint.git_staged_changes)
    
    # Step 4: Reconstruct orchestrator state
    orchestrator_state = OrchestratorState(
        session_id=checkpoint.session_id,
        failure_count=checkpoint.total_failures_processed,
        matched_pattern=checkpoint.current_pattern_match,
        attempt_count=checkpoint.current_attempt_count,
        session_context=checkpoint.session_context,
        patterns=load_patterns(checkpoint.patterns_in_use),
        routing_decisions=checkpoint.routing_decisions,
        fix_attempts=checkpoint.fix_attempts,
        validation_results=checkpoint.validation_results,
        escalations=checkpoint.escalations,
        rollback_history=checkpoint.rollback_history,
        recovery_count=checkpoint.recovery_attempted + 1,
        last_success_time=checkpoint.last_successful_fix_timestamp,
    )
    
    # Step 5: Determine next action
    next_action = determine_next_action(checkpoint)
    
    # Step 6: Resume cascade
    return orchestrator_state, next_action
```

---

## Consistency Validation

### Pre-Recovery Checks

```python
def validate_consistency_before_recovery(checkpoint):
    """Multi-level consistency validation."""
    
    checks = {
        'checksum': validate_checksum(checkpoint),
        'git_state': validate_git_state(checkpoint),
        'pattern_catalog': validate_pattern_catalog(checkpoint),
        'ltm_freshness': validate_ltm_patterns_fresh(checkpoint),
        'session_context': validate_session_context(checkpoint),
    }
    
    all_passed = all(checks.values())
    
    if not all_passed:
        log_warning({
            'event': 'consistency_checks_failed',
            'checkpoint_id': checkpoint.checkpoint_id,
            'failed_checks': [k for k, v in checks.items() if not v],
        })
    
    return all_passed, checks
```

### Pattern Catalog Reconciliation

```python
def reconcile_pattern_catalog(checkpoint):
    """Verify pattern list matches current LTM; update confidence if needed."""
    
    mismatches = []
    
    for pattern_id in checkpoint.patterns_in_use:
        ltm_pattern = get_ltm_pattern(pattern_id)
        checkpoint_pattern = checkpoint.session_context.patterns[pattern_id]
        
        # Check 1: Existence
        if not ltm_pattern:
            mismatches.append({
                'type': 'not_found',
                'pattern_id': pattern_id,
                'action': 'remove_from_session'
            })
            continue
        
        # Check 2: Confidence drift
        if abs(ltm_pattern.confidence - checkpoint_pattern.confidence) > 0.10:
            mismatches.append({
                'type': 'confidence_drift',
                'pattern_id': pattern_id,
                'old_confidence': checkpoint_pattern.confidence,
                'new_confidence': ltm_pattern.confidence,
                'action': 'update_confidence'
            })
        
        # Check 3: Success rate change
        if ltm_pattern.success_rate != checkpoint_pattern.success_rate:
            mismatches.append({
                'type': 'success_rate_changed',
                'pattern_id': pattern_id,
                'action': 'update_success_rate'
            })
    
    # Apply reconciliations
    for mismatch in mismatches:
        if mismatch['action'] == 'remove_from_session':
            checkpoint.session_context.patterns.pop(mismatch['pattern_id'])
        elif mismatch['action'] == 'update_confidence':
            checkpoint.session_context.patterns[mismatch['pattern_id']].confidence = (
                get_ltm_pattern(mismatch['pattern_id']).confidence
            )
    
    return mismatches
```

---

## Failure Recovery Scenarios

### Scenario 1: Clean Recovery (Normal Path)

```python
# Checkpoint created at 14:30:00 UTC
# Orchestrator running, processing failures
# No errors, cascade completes successfully
# Final checkpoint saved with summary

checkpoint_summary = {
    'total_failures_processed': 247,
    'total_patterns_used': 12,
    'total_fixes_attempted': 289,
    'successful_fixes': 254,
    'success_rate': '87.9%',
    'final_status': 'CASCADE_COMPLETED',
}
```

### Scenario 2: Process Crash Recovery

```python
# Checkpoint saved at 14:35:00 UTC after 50 failures
# Process crashes at 14:36:45 UTC
# On restart:
#   1. Load checkpoint from SQLite
#   2. Validate integrity (checksum OK)
#   3. Verify git state (clean, matches checkpoint)
#   4. Restore session context (20 patterns loaded)
#   5. Skip already-processed failures (first 50)
#   6. Resume with failure #51
# Cascade continues from interruption point

recovery_path = "process_crash → load_checkpoint → validate → resume_from_failure_51"
```

### Scenario 3: Network Failure Recovery

```python
# Checkpoint saved at 14:35:00 UTC
# Network disconnection at 14:36:30 UTC during fix attempt
# Retry logic: Exponential backoff (1s, 2s, 4s, 8s, 16s)
#   Attempt 1: Wait 1s, retry (success)
#   or
#   Attempt 1-5: All fail
#   → Escalate to human with context

recovery_path = "network_fail → retry_exponential → success_or_escalate"
```

### Scenario 4: Data Corruption Recovery

```python
# Checkpoint saved normally at 14:35:00 UTC
# Checkpoint file corrupted (bitflip in storage) at 14:50:00 UTC
# On recovery:
#   1. Load checkpoint from SQLite
#   2. Checksum validation FAILS
#   3. Try loading backup from JSON file
#   4. JSON also fails (same corruption)
#   5. Load previous valid checkpoint (from 14:30:00)
#   6. Re-process failures 50-100 (may have duplicates)

recovery_path = "corruption → checksum_fail → try_backup → load_previous_valid → reprocess"
```

### Scenario 5: Timeout During Classification

```python
# Pattern matching takes >5 seconds (SLA breach)
# Classification stuck in infinite loop or resource contention
# On timeout:
#   1. Log timeout event with context
#   2. Create emergency checkpoint
#   3. Mark failure as "escalation_required"
#   4. Skip to next failure
#   5. Continue cascade

recovery_path = "timeout → emergency_checkpoint → escalate_failure → continue"
```

---

## Cleanup & Retention

### Periodic Cleanup

```python
def cleanup_old_checkpoints():
    """Remove stale checkpoints per retention policy."""
    
    cutoff_age_days = 7
    max_checkpoints_per_session = 10
    
    for session_id in list_session_ids():
        checkpoints = list_checkpoints_for_session(session_id)
        
        # Sort by timestamp (oldest first)
        checkpoints.sort(key=lambda c: c.timestamp)
        
        # Remove old checkpoints
        for checkpoint in checkpoints:
            age = (datetime.utcnow() - checkpoint.timestamp).days
            if age > cutoff_age_days:
                delete_checkpoint(checkpoint.checkpoint_id)
        
        # Keep only last N checkpoints
        remaining = list_checkpoints_for_session(session_id)
        if len(remaining) > max_checkpoints_per_session:
            to_delete = remaining[:-max_checkpoints_per_session]
            for checkpoint in to_delete:
                delete_checkpoint(checkpoint.checkpoint_id)
```

### Archive Old Checkpoints

```python
def archive_checkpoint_to_git(checkpoint):
    """Create immutable record via git commit."""
    
    archive_file = (
        f".codex/archive/checkpoints/"
        f"{checkpoint.session_id}_{checkpoint.timestamp.isoformat()}.json"
    )
    
    # Write archive file
    with open(archive_file, 'w') as f:
        json.dump(asdict(checkpoint), f, indent=2, default=str)
    
    # Commit to git
    run_cmd(f"git add {archive_file}")
    run_cmd(
        f"git commit -m 'Archive checkpoint {checkpoint.checkpoint_id}' "
        f"--no-verify"
    )
```

---

## Integration with Recovery Procedures

See `PHASE_9_2_RECOVERY_PROCEDURES.md` for:
- Network failure recovery (retry with backoff)
- Process crash detection and recovery
- Timeout handling and escalation
- Data corruption detection and rollback
- Unknown pattern handling

---

## Monitoring & Metrics

### Checkpoint Health

```yaml
metrics:
  checkpoints_created_24h: 1247
  checkpoints_recovered_successfully: 1189
  recovery_success_rate: "95.4%"
  avg_checkpoint_size_kb: 42.3
  avg_recovery_time_seconds: 1.2
  
alerts:
  recovery_success_rate_below_90: true  # Warning threshold
  checkpoint_size_above_100kb: false
  recovery_time_above_5s: false
```

### Checkpoint Validation Results

```python
validation_stats = {
    'checksum_validations': 1247,
    'checksum_failures': 3,
    'git_state_validations': 1247,
    'git_state_divergences': 0,
    'pattern_catalog_validations': 1247,
    'pattern_catalog_mismatches': 12,
    'overall_validation_success_rate': '99.1%',
}
```

---

## Reference

**See Also:**
- `PHASE_9_2_RECOVERY_PROCEDURES.md` - Detailed recovery procedures for each failure scenario
- `PHASE_9_2_LTM_PATTERNS.md` - Pattern catalog referenced in checkpoints
- `PHASE_9_2_SESSION_CONTEXT.md` - Session context checkpointing
