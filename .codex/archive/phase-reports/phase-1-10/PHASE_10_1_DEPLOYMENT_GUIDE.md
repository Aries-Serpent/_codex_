# Phase 10.1: Deployment Guide

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Deployment Date:** 2026-07-01

---

## Pre-Deployment Checklist

- [ ] All 33 integration tests passing (100%)
- [ ] Code review completed
- [ ] Security scan passed
- [ ] Documentation complete
- [ ] Configuration reviewed
- [ ] Monitoring configured
- [ ] Rollback plan prepared
- [ ] Team trained on recovery procedures

---

## Installation

### Step 1: Verify Dependencies

Required Python packages:
```bash
pip list | grep -E "msgpack|gzip"
# msgpack should be installed
# gzip is built-in
```

If msgpack is missing:
```bash
pip install msgpack>=1.0.5
```

### Step 2: Create Checkpoint Storage

```bash
mkdir -p .codex/checkpoints/v1
mkdir -p .codex/checkpoints/metadata
chmod 755 .codex/checkpoints
```

### Step 3: Deploy Configuration

Copy configuration file:
```bash
cp .codex/PHASE_10_1_CHECKPOINT_CONFIG.yaml ~/.codex/config/checkpoint_config.yaml
```

### Step 4: Update Agent Framework

Add checkpoint manager to agent initialization:

```python
# In your agent __init__.py or main.py
from codex.brain.checkpoint_manager import CheckpointManager
from codex.brain.session_resume import SessionResume

# Initialize checkpoint system
checkpoint_mgr = CheckpointManager()
session_resume = SessionResume(checkpoint_mgr)

# Restore from checkpoint if available
latest = checkpoint_mgr.get_latest_checkpoint()
if latest:
    print(f"Restoring from checkpoint: {latest}")
    result = session_resume.resume_latest_session()
    if result.success:
        agent.restore_state(result.state)
```

### Step 5: Add Checkpoint Triggers

In agent execution loop:

```python
# In agent execution loop
for task in tasks:
    execute_task(task)
    
    # Check if checkpoint should be created
    checkpoint_mgr.maybe_checkpoint(commit_count_delta=1)
```

---

## Configuration

### Primary Configuration File

Location: `.codex/PHASE_10_1_CHECKPOINT_CONFIG.yaml`

Key settings to review:

**1. Checkpoint Triggers**
```yaml
triggers:
  commit_based:
    enabled: true
    interval: 5  # Every 5 commits

  time_based:
    enabled: true
    interval_seconds: 1800  # Every 30 minutes
```

**2. Retention Policy**
```yaml
retention:
  max_checkpoints: 10  # Keep last 10
  cleanup_policy: "oldest_first"
  cleanup_on_creation: true
```

**3. Compression**
```yaml
compression:
  algorithm: "gzip"
  level: 9  # Maximum compression
  enabled: true
```

### Override Configuration

Per-agent overrides:

```python
# Custom configuration for specific agent
manager = CheckpointManager(
    checkpoint_dir=Path(".codex/checkpoints"),
    retention_count=20,  # Keep 20 for long-running agents
    commit_interval=2,   # Checkpoint every 2 commits
    time_interval_seconds=300,  # Every 5 minutes
)
```

---

## Integration Points

### Automatic Session Start Recovery

Add to Copilot session bridge:

```python
# In codex/cognitive/mcp_session_bridge.py
from codex.brain.checkpoint_manager import CheckpointManager
from codex.brain.session_resume import SessionResume

def register_mcp_session_hook(context):
    """Register checkpoint recovery in session hook"""
    
    # Attempt to resume from checkpoint
    try:
        checkpoint_mgr = CheckpointManager()
        session_resume = SessionResume(checkpoint_mgr)
        
        result = session_resume.resume_latest_session()
        if result and result.success:
            # Inject recovered state into system prompt
            context["recovered_state"] = result.state
            context["checkpoint_id"] = result.checkpoint_id
            logger.info(f"Session resumed from checkpoint: {result.checkpoint_id}")
    except Exception as e:
        logger.warning(f"Checkpoint recovery failed: {e}")
        # Fail-open: continue without recovery
    
    return context
```

### Integration with Decision Framework

Automatically checkpoint on major decisions:

```python
# In decision framework
def make_decision(decision_type, description, confidence):
    """Make a decision and checkpoint on major milestones"""
    
    decision = Decision(
        decision_type=decision_type,
        description=description,
        confidence=confidence
    )
    
    # Checkpoint after high-confidence decisions
    if decision_type in ["major_refactor", "security_fix", "api_change"]:
        checkpoint_mgr.create_checkpoint(
            label=f"after_{decision_type}"
        )
    
    return decision
```

### Integration with Error Recovery

Checkpoint before risky operations:

```python
# In error recovery
def attempt_recovery(error):
    """Attempt recovery with checkpoint safety"""
    
    # Create checkpoint before recovery attempt
    checkpoint_mgr.create_checkpoint(label="before_recovery")
    
    try:
        # Attempt recovery
        recovery_result = execute_recovery(error)
        
        # Checkpoint on successful recovery
        checkpoint_mgr.create_checkpoint(label="recovery_success")
        
        return recovery_result
    except Exception as e:
        # Checkpoint failure state
        checkpoint_mgr.create_checkpoint(label="recovery_failed")
        raise
```

---

## Monitoring & Alerts

### Metrics to Monitor

```python
# In monitoring/checkpoint_health.py
def monitor_checkpoint_health():
    """Monitor checkpoint system health"""
    
    mgr = CheckpointManager()
    
    # Number of checkpoints
    checkpoints = mgr.list_checkpoints()
    print(f"metric: checkpoints_count = {len(checkpoints)}")
    
    # Latest checkpoint age
    if checkpoints:
        latest = checkpoints[0]
        age_seconds = (now() - latest['timestamp']).total_seconds()
        print(f"metric: latest_checkpoint_age_seconds = {age_seconds}")
    
    # Average checkpoint size
    total_size = sum(cp['compressed_size_bytes'] for cp in checkpoints)
    avg_size = total_size / len(checkpoints) if checkpoints else 0
    print(f"metric: avg_checkpoint_size_bytes = {avg_size}")
    
    # Integrity check failures
    failures = 0
    for cp in checkpoints:
        if not mgr.verify_checkpoint_integrity(cp['checkpoint_id']):
            failures += 1
    print(f"metric: integrity_check_failures = {failures}")
```

### Alert Thresholds

| Alert | Threshold | Action |
|-------|-----------|--------|
| No checkpoints | N/A | Warn if none in 1 hour |
| Checkpoint creation slow | >500ms | Investigate I/O |
| Checkpoint corruption | Any | Investigate and rotate |
| Resume time slow | >2min | Optimize or reduce state |
| Storage full | >90% | Cleanup old checkpoints |

### Logging

Enable checkpoint logging in .codex/PHASE_10_1_CHECKPOINT_CONFIG.yaml:

```yaml
logging:
  level: "INFO"
  checkpoint_operations: true
  resume_operations: true
  integrity_checks: true
  performance_metrics: true
```

Log locations:
- `/var/log/codex/checkpoint_manager.log`
- `/var/log/codex/session_resume.log`

---

## Testing Deployment

### 1. Unit Tests

```bash
pytest tests/integration/test_phase_10_1_session_resume.py -v
# Expected: 33/33 passing
```

### 2. Integration Test with Real Agent

```python
# tests/deployment/test_real_agent_checkpoint.py
def test_agent_with_checkpointing():
    """Test real agent with checkpoint system"""
    
    # Create agent
    agent = create_semantic_search_agent()
    
    # Enable checkpointing
    checkpoint_mgr = CheckpointManager()
    
    # Run agent with checkpointing
    for task in tasks:
        agent.execute(task)
        checkpoint_mgr.maybe_checkpoint(commit_count_delta=1)
    
    # Verify checkpoints were created
    checkpoints = checkpoint_mgr.list_checkpoints()
    assert len(checkpoints) > 0
    
    # Simulate session end and restart
    agent_recovered = restore_agent_from_checkpoint()
    
    # Verify state restored correctly
    assert agent_recovered.current_task == agent.current_task
    assert agent_recovered.decisions == agent.decisions
```

### 3. Load Testing

```python
# tests/deployment/test_checkpoint_load.py
def test_high_volume_checkpointing():
    """Test checkpointing under load"""
    
    mgr = CheckpointManager()
    
    # Create many checkpoints rapidly
    start = time.time()
    for i in range(100):
        large_state = generate_large_state(size_mb=5)
        mgr.create_checkpoint(session_state=large_state)
    
    elapsed = time.time() - start
    
    # Performance assertion
    assert elapsed < 60  # 100 checkpoints in < 60 seconds
    assert mgr.checkpoint_dir.stat().st_size < 1_000_000_000  # < 1GB
```

### 4. Recovery Testing

```bash
# Manual recovery test
1. Run agent and create several checkpoints
2. Stop agent mid-execution
3. Restart agent and verify recovery
4. Check that no work was duplicated
5. Verify all decisions were preserved
```

---

## Production Rollout

### Phase 1: Beta (Week 1)

- Deploy to staging environment
- Run full test suite
- Manual testing with team
- Collect baseline metrics
- No automatic recovery (manual only)

### Phase 2: Canary (Week 2)

- Deploy to 10% of agents
- Monitor checkpoint creation rate
- Monitor recovery success rate
- Collect performance metrics
- Watch for corruption issues

### Phase 3: Gradual Rollout (Week 3-4)

- 25% → 50% → 75% → 100%
- Monitor each phase
- Adjust configuration based on metrics
- Enable automatic recovery gradually

### Phase 4: Full Production (Week 4+)

- 100% deployment
- Auto-recovery enabled
- Monitoring active
- Regular checkpoint cleanup

---

## Rollback Procedure

If critical issues found:

### Immediate Rollback (< 5 minutes)

```bash
# Disable automatic checkpointing
sed -i 's/checkpoint_mgr.maybe_checkpoint/# checkpoint_mgr.maybe_checkpoint/' agent.py

# Disable auto-recovery
sed -i 's/restore_from_checkpoint/# restore_from_checkpoint/' agent.py

# Restart agents
restart_all_agents()
```

### Full Rollback (if needed)

```bash
# Remove checkpoint system
rm -rf .codex/checkpoints/
git revert <commit_id>

# Restart with previous version
deploy_version(previous_stable)
```

---

## Performance Tuning

### Checkpoint Creation Too Slow

**Issue:** Checkpoint takes >500ms

**Diagnosis:**
```python
import time
start = time.time()
checkpoint_mgr.create_checkpoint(session_state=large_state)
elapsed = time.time() - start
print(f"Checkpoint creation: {elapsed:.2f}s")
```

**Solutions:**
1. Increase compression level (already at max)
2. Reduce state size (compress STM/LTM)
3. Switch to binary format (msgpack)
4. Move to faster storage (SSD)

### Resume Time Too Slow

**Issue:** Resume takes >2 minutes

**Diagnosis:**
```python
import time
start = time.time()
result = session_resume.resume_session(cp_id)
elapsed = time.time() - start
print(f"Resume time: {elapsed:.2f}s")
```

**Solutions:**
1. Use incremental checkpoints (Phase 10.2)
2. Reduce decision history size
3. Prune old patterns from memory
4. Use binary format instead of JSON

### Storage Too Large

**Issue:** Checkpoint directory >1GB

**Diagnosis:**
```python
import os
total = sum(os.path.getsize(f) for f in glob("**/*", recursive=True))
print(f"Checkpoint storage: {total / 1e9:.2f}GB")
```

**Solutions:**
1. Increase cleanup frequency
2. Reduce retention count
3. Enable compression (already enabled)
4. Archive old checkpoints

---

## Monitoring Dashboard

Example Grafana dashboard queries:

```prometheus
# Checkpoint creation rate
rate(checkpoint_created_total[5m])

# Average checkpoint size
avg(checkpoint_size_bytes)

# Resume success rate
resume_success_count / (resume_success_count + resume_failure_count)

# Largest checkpoints
topk(10, checkpoint_size_bytes)

# Checkpoint age
time() - checkpoint_created_timestamp
```

---

## Support & Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Checkpoint creation fails | Disk full | Cleanup old checkpoints |
| Recovery fails | Corrupted checkpoint | Try previous checkpoint |
| No checkpoints found | Not initialized | Check `.codex/checkpoints/` exists |
| Resume is slow | Large state | Use incremental checkpoints |
| Duplication after resume | Bug in progress tracking | Verify no_duplication test |

### Contact

- **Issues:** File GitHub issue in Aries-Serpent/_codex_
- **Questions:** Discussion forum or Slack #phase-10-1
- **Emergency:** Escalate to @mbaetiong

---

## Maintenance

### Daily Tasks

- Monitor checkpoint health metrics
- Check for integrity failures
- Review checkpoint creation rate

### Weekly Tasks

- Review performance metrics
- Analyze checkpoint sizes
- Check storage growth rate

### Monthly Tasks

- Backup checkpoint directory
- Review and prune old checkpoints
- Performance optimization review
