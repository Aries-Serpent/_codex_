# Phase 10.1: Recovery Procedures Guide

**Version:** 1.0.0  
**Status:** ✅ Production Ready  

---

## Overview

This guide provides step-by-step recovery procedures for restoring agent sessions from checkpoints. It covers normal recovery, error handling, and troubleshooting.

---

## Normal Recovery Workflow

### Quick Resume (Most Common)

**Objective:** Resume session from latest checkpoint

```python
from codex.brain.checkpoint_manager import CheckpointManager
from codex.brain.session_resume import SessionResume

# Step 1: Initialize managers
checkpoint_mgr = CheckpointManager()
resume_mgr = SessionResume(checkpoint_mgr)

# Step 2: Check if checkpoints available
latest_cp = checkpoint_mgr.get_latest_checkpoint()
if not latest_cp:
    print("No checkpoints available - starting fresh")
    exit(1)

# Step 3: Resume from latest checkpoint
result = resume_mgr.resume_latest_session()
if result.success:
    print(f"Session resumed: {result.session_id}")
    print(f"Agent: {result.agent_id}")
    print(f"Recovered {len(result.state['decision_history'])} decisions")
else:
    print(f"Resume failed: {result.error_message}")
    exit(1)

# Step 4: Inject restored state back into agent
agent.restore_state(result.state)

# Step 5: Continue execution
agent.resume_from_checkpoint()
```

### Detailed Recovery Workflow

**Objective:** Manually control recovery process with validation at each step

```python
# Step 1: List available checkpoints
checkpoints = checkpoint_mgr.list_checkpoints()
print(f"Available checkpoints: {len(checkpoints)}")

for cp in checkpoints[:3]:  # Show 3 most recent
    print(f"  {cp['checkpoint_id']}")
    print(f"    Session: {cp['session_id']}")
    print(f"    Agent: {cp['agent_id']}")
    print(f"    Time: {cp['timestamp']}")

# Step 2: Select checkpoint to resume from
selected_cp = checkpoints[0]['checkpoint_id']  # Most recent

# Step 3: Validate checkpoint integrity
if not resume_mgr.validate_checkpoint(selected_cp):
    print(f"Checkpoint validation failed: {selected_cp}")
    print("Trying previous checkpoint...")
    selected_cp = checkpoints[1]['checkpoint_id']

# Step 4: Load checkpoint content
content = resume_mgr.load_checkpoint(selected_cp)
if not content:
    print("Failed to load checkpoint")
    exit(1)

# Step 5: Review recovered state before resuming
progress = resume_mgr.get_progress_snapshot(selected_cp)
print(f"Progress: {progress['completed_tasks']}")
print(f"Pending: {progress['pending_tasks']}")

decisions = resume_mgr.get_decision_history(selected_cp)
print(f"Recovered {len(decisions)} decisions")

# Step 6: Reconcile repository state
current_repo_state = {
    "branch": get_current_branch(),
    "commit_sha": get_current_commit(),
    "uncommitted_changes": count_uncommitted_changes(),
}

result = resume_mgr.resume_session(selected_cp, current_repo_state)

if result.success:
    print("✅ Session recovered successfully")
    if result.warnings:
        print("⚠️  Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
else:
    print(f"❌ Recovery failed: {result.error_message}")
    exit(1)
```

---

## Error Recovery Scenarios

### Scenario 1: Corrupted Checkpoint

**Problem:** SHA256 checksum mismatch indicates checkpoint corruption

**Detection:**
```python
if not resume_mgr.validate_checkpoint(cp_id):
    print(f"Checkpoint corrupted: {cp_id}")
```

**Recovery:**
1. Skip corrupted checkpoint
2. Try previous checkpoint
3. Fall back to manual recovery if needed

```python
def find_valid_checkpoint():
    for cp in checkpoint_mgr.list_checkpoints():
        if resume_mgr.validate_checkpoint(cp['checkpoint_id']):
            return cp['checkpoint_id']
    return None

valid_cp = find_valid_checkpoint()
if valid_cp:
    print(f"Found valid checkpoint: {valid_cp}")
    result = resume_mgr.resume_session(valid_cp)
else:
    print("No valid checkpoints found - manual recovery needed")
```

### Scenario 2: Repository Divergence

**Problem:** Repository state changed since checkpoint (branch changed, commits made)

**Detection:**
```python
result = resume_mgr.resume_session(cp_id, current_repo_state)
if result.warnings and "divergence" in result.warnings[0]:
    print("Repository divergence detected")
```

**Recovery Options:**

**Option A: Proceed with Warning** (default)
```python
# Just warn and continue - SessionResume allows this
if result.success:
    agent.restore_state(result.state)
    agent.resume()
```

**Option B: Manual Reconciliation**
```python
# Check what changed
divergence = check_repository_divergence(checkpoint_state, current_state)

if divergence.current_branch != divergence.checkpoint_branch:
    print(f"Branch changed: {divergence.checkpoint_branch} → {divergence.current_branch}")
    print("Manually merge or rebase checkpoint work")

if divergence.uncommitted_changes > 0:
    print(f"{divergence.uncommitted_changes} uncommitted changes detected")
    print("Stash or commit changes before resuming")
```

**Option C: Restore to Checkpoint State**
```python
# Reset repository to checkpoint state
checkout_branch(divergence.checkpoint_branch)
git_checkout(divergence.checkpoint_commit)

# Now resume
result = resume_mgr.resume_session(cp_id)
```

### Scenario 3: Missing Checkpoint Metadata

**Problem:** Checkpoint file exists but metadata corrupted

**Detection:**
```python
if resume_mgr.load_checkpoint(cp_id) is None:
    print("Failed to load checkpoint content")
```

**Recovery:**
```python
# Try to load raw checkpoint file directly
cp_file = Path(".codex/checkpoints/v1") / f"{cp_id}.json.gz"

try:
    import gzip
    import json
    
    with gzip.open(cp_file, 'rt') as f:
        checkpoint_data = json.load(f)
    
    print("✅ Successfully recovered checkpoint data")
    print(f"Session: {checkpoint_data.get('session_id')}")
    print(f"Agent: {checkpoint_data.get('agent_id')}")
    
except Exception as e:
    print(f"❌ Failed to recover checkpoint: {e}")
```

### Scenario 4: Schema Version Mismatch

**Problem:** Checkpoint uses different schema version

**Detection:**
```python
content = resume_mgr.load_checkpoint(cp_id)
if content['schema_version'] not in SessionResume.SUPPORTED_SCHEMA_VERSIONS:
    print(f"Unsupported schema version: {content['schema_version']}")
```

**Recovery:**
```python
# Manual migration (example for v0 → v1)
def migrate_v0_to_v1(old_state):
    """Migrate checkpoint from schema v0 to v1"""
    return {
        "schema_version": 1,
        "checkpoint_id": old_state.get("id"),
        "session_id": old_state.get("session_id"),
        # Map old fields to new schema
        "session_state": {
            "agent_state": old_state.get("agent", {}),
            "decision_history": old_state.get("decisions", []),
            # ... map all fields
        }
    }

migrated_state = migrate_v0_to_v1(old_checkpoint)
```

---

## Advanced Recovery Procedures

### Recovery with State Validation

Validate recovered state matches expected values:

```python
def validate_recovered_state(result, expected_session_id, expected_agent_id):
    """Validate recovered state matches expectations"""
    
    # Check session and agent match
    if result.session_id != expected_session_id:
        raise ValueError(f"Session mismatch: expected {expected_session_id}, got {result.session_id}")
    
    if result.agent_id != expected_agent_id:
        raise ValueError(f"Agent mismatch: expected {expected_agent_id}, got {result.agent_id}")
    
    # Check state completeness
    state = result.state
    required_keys = ["agent_state", "decision_history", "execution_progress"]
    for key in required_keys:
        if key not in state:
            raise ValueError(f"Missing required state key: {key}")
    
    # Validate no duplication
    completed_tasks = state['execution_progress'].get('completed_tasks', [])
    if len(completed_tasks) != len(set(completed_tasks)):
        raise ValueError("Duplicate tasks detected in completed_tasks")
    
    # Validate progress consistency
    progress = state['execution_progress']
    if progress['current_task'] in progress['completed_tasks']:
        raise ValueError(f"Current task already completed: {progress['current_task']}")
    
    return True

# Use in recovery
try:
    validate_recovered_state(result, "S001", "semantic_search")
    print("✅ State validation passed")
    agent.restore_state(result.state)
except ValueError as e:
    print(f"❌ State validation failed: {e}")
    exit(1)
```

### Recovery with Rollback

If recovered state causes issues, rollback to previous checkpoint:

```python
def recovery_with_rollback(session_id, max_retries=3):
    """Attempt recovery with rollback on failure"""
    
    checkpoints = checkpoint_mgr.list_checkpoints()
    
    for attempt, cp in enumerate(checkpoints[:max_retries]):
        print(f"Attempt {attempt + 1}: Trying {cp['checkpoint_id']}")
        
        try:
            # Try to resume
            result = resume_mgr.resume_session(cp['checkpoint_id'])
            if not result.success:
                print(f"  Resume failed: {result.error_message}")
                continue
            
            # Validate state
            validate_recovered_state(result, session_id, cp['agent_id'])
            
            # Try to resume execution
            agent = create_agent(cp['agent_id'])
            agent.restore_state(result.state)
            agent.resume()
            
            print(f"✅ Successfully resumed from {cp['checkpoint_id']}")
            return True
            
        except Exception as e:
            print(f"  Recovery failed: {e}")
            if attempt < max_retries - 1:
                print("  Rolling back to previous checkpoint...")
            continue
    
    print(f"❌ All {max_retries} recovery attempts failed")
    return False
```

---

## Checkpoint Inspection

### List All Checkpoints

```python
checkpoints = checkpoint_mgr.list_checkpoints()
print(f"Total checkpoints: {len(checkpoints)}\n")

for i, cp in enumerate(checkpoints, 1):
    print(f"{i}. {cp['checkpoint_id']}")
    print(f"   Session: {cp['session_id']}")
    print(f"   Agent: {cp['agent_id']}")
    print(f"   Created: {cp['timestamp']}")
    print(f"   Size: {cp['compressed_size_bytes']} bytes (compressed)")
    print(f"   Integrity: {cp['sha256'][:16]}...")
    print()
```

### Compare Checkpoints

```python
def compare_checkpoints(cp_id_1, cp_id_2):
    """Compare state between two checkpoints"""
    
    result1 = resume_mgr.resume_session(cp_id_1)
    result2 = resume_mgr.resume_session(cp_id_2)
    
    progress1 = result1.state['execution_progress']
    progress2 = result2.state['execution_progress']
    
    print(f"Checkpoint {cp_id_1}:")
    print(f"  Completed: {len(progress1['completed_tasks'])} tasks")
    print(f"  Pending: {len(progress1['pending_tasks'])} tasks")
    
    print(f"\nCheckpoint {cp_id_2}:")
    print(f"  Completed: {len(progress2['completed_tasks'])} tasks")
    print(f"  Pending: {len(progress2['pending_tasks'])} tasks")
    
    new_completed = set(progress2['completed_tasks']) - set(progress1['completed_tasks'])
    print(f"\nNew completed between checkpoints: {new_completed}")

compare_checkpoints(checkpoints[0]['checkpoint_id'], checkpoints[1]['checkpoint_id'])
```

---

## Troubleshooting

### Recovery is Slow (>2 minutes)

**Cause 1: Large checkpoint file**
```python
# Check checkpoint size
cp_metadata = checkpoint_mgr.get_checkpoint_metadata(cp_id)
if cp_metadata.uncompressed_size_bytes > 10_000_000:  # > 10MB
    print("Large checkpoint detected - this may be slow")
```

**Cause 2: I/O bottleneck**
```python
# Check disk I/O
import psutil
print(f"Disk I/O: {psutil.disk_io_counters()}")

# Move checkpoint to faster storage if needed
```

**Solution:** Use incremental checkpoints (Phase 10.2 feature) to reduce size

### Recovery Returns Wrong State

**Check 1: Verify checkpoint integrity**
```python
if not checkpoint_mgr.verify_checkpoint_integrity(cp_id):
    print("Checkpoint corrupted")
```

**Check 2: Verify you're resuming from correct checkpoint**
```python
cp = checkpoint_mgr.get_checkpoint_metadata(cp_id)
print(f"Checkpoint time: {cp.timestamp}")
print(f"Expected time: {expected_time}")
```

**Check 3: Verify state wasn't modified after checkpoint**
```python
current_branch = get_current_branch()
cp_branch = content['session_state']['repository_state']['branch']

if current_branch != cp_branch:
    print(f"Branch mismatch: {cp_branch} vs {current_branch}")
```

### Can't Find Latest Checkpoint

```python
# Manual search
checkpoint_dir = Path(".codex/checkpoints/v1")
all_files = sorted(checkpoint_dir.glob("*.json.gz"), key=lambda x: x.stat().st_mtime, reverse=True)

if all_files:
    latest_file = all_files[0]
    latest_cp_id = latest_file.stem.replace('.json', '')
    print(f"Latest checkpoint: {latest_cp_id}")
else:
    print("No checkpoint files found")
```

---

## Recovery Checklist

Use this checklist before critical recovery operations:

- [ ] Latest checkpoint verified with SHA256 ✅
- [ ] Repository state matches checkpoint (branch, commit)
- [ ] No uncommitted changes conflicting with checkpoint
- [ ] Sufficient disk space for restored state
- [ ] Agent still available (hasn't been deleted/changed)
- [ ] Schema version is supported
- [ ] Fallback checkpoint identified if primary fails
- [ ] All warnings reviewed and understood
- [ ] Test recovery in staging first if possible
- [ ] Backup created before recovery if possible

---

## Emergency Recovery

If standard recovery fails:

1. **Check checkpoint files exist**
   ```bash
   ls -lah .codex/checkpoints/v1/
   ```

2. **Manually extract checkpoint**
   ```bash
   gunzip -c .codex/checkpoints/v1/cp_*.json.gz | jq .
   ```

3. **Verify checkpoint integrity**
   ```bash
   sha256sum .codex/checkpoints/v1/cp_*.json.gz
   ```

4. **Contact support** if still stuck
