# OODA Loop Reinitialization Procedures

**Document:** `.codex/OODA_REINIT_PROCEDURES.md`  
**Phase:** 10.3 Day 6  
**Authority:** @mbaetiong (D-tier autonomy)  
**Track:** Critical Path P0  
**Effective:** 2026-07-06

---

## Executive Summary

This document specifies reinitialization procedures for the OODA loop system, enabling:
- **Cold Start:** Initialize OODA executor from session checkpoints
- **Warm Restart:** Load context from LTM patterns and decision history
- **State Recovery:** Recover from corrupted or missing agent state
- **Training Context:** Load training data for new OODA cycles
- **Graceful Degradation:** Fallback procedures when dependencies unavailable

**All procedures target < 100ms initialization time with 100% state consistency.**

---

## Architecture Integration

### Track 10.1: Session Checkpoints
- **API:** `SessionManager.get_checkpoint(checkpoint_id)`
- **Data:** Agent state snapshots, decision history, execution traces
- **Integration:** Reinitialization loads from recent successful checkpoints

### Track 10.2: Long-Term Memory (LTM)
- **API:** `PatternStore.search_by_tag(tag)`, `get_pattern(pattern_id)`
- **Data:** Historical patterns with success rates, conditions, tags
- **Integration:** Reinitialization loads top patterns by improvement area

### OODA Executor
- **State:** `OODAState` with phase, metrics, decision history
- **Initialization:** Load with executor, execute cycle normally
- **Recovery:** Checkpoint after each successful cycle (async)

---

## Reinitialization Procedures

### Procedure 1: Cold Start (First Execution)

**Trigger:** Agent first activation or complete state loss  
**Duration:** < 100ms  
**Success Criteria:** OODAState initialized with valid context

#### Steps

1. **Initialize OODA Executor**
   ```python
   executor = OODAExecutor(
       state_provider=state_provider,
       context_provider=context_provider,
       max_concurrent_loops=100,
   )
   ```

2. **Load Training Patterns** (from Track 10.2)
   ```python
   # Get top patterns by improvement area
   patterns = await pattern_store.get_patterns_by_tag(
       "training_data",
       limit=20,
   )
   
   # Store patterns in context provider cache
   context_provider.cache_patterns(patterns)
   ```

3. **Initialize Context Injector**
   ```python
   injector = ContextInjector(
       pattern_store=pattern_store,
       session_store=session_store,
   )
   ```

4. **Validate System Health**
   ```python
   health = {
       "state_provider": check_state_provider(state_provider),
       "pattern_store": check_pattern_store(pattern_store),
       "session_store": check_session_store(session_store),
   }
   
   if not all(health.values()):
       log_degradation(health)
       # Continue with graceful degradation
   ```

5. **Execute First OODA Cycle**
   ```python
   state = await executor.execute_cycle(
       task_id="init_task",
       task_type="initialization",
       priority="P2",
   )
   
   # Checkpoint successful initialization
   if state.action_result.status == "success":
       await session_manager.create_checkpoint(
           session_id="cold_start",
           state=state.to_dict(),
       )
   ```

#### Example (Cold Start)

```python
async def cold_start_initialization():
    """Initialize OODA loop from scratch."""
    logger.info("Starting cold start initialization...")
    
    # Create components
    state_provider = GitStateProvider()
    pattern_store = SQLitePatternStore(".codex/patterns.db")
    session_store = SQLiteSessionStore(".codex/sessions.db")
    
    # Load training patterns
    training_patterns = await pattern_store.get_patterns_by_tag("training_data")
    logger.info(f"Loaded {len(training_patterns)} training patterns")
    
    # Initialize OODA
    context_injector = ContextInjector(pattern_store, session_store)
    executor = OODAExecutor(
        state_provider=state_provider,
        context_provider=ContextProvider(context_injector),
    )
    
    # Validate health
    health_check = await validate_system_health(
        state_provider, pattern_store, session_store
    )
    
    if not health_check["healthy"]:
        logger.warning(f"System degraded: {health_check['issues']}")
        # Will run with graceful degradation
    
    # Execute first cycle
    state = await executor.execute_cycle(
        task_id="cold_start_001",
        task_type="initialization",
        priority="P2",
    )
    
    logger.info(f"Cold start complete: {state.action_result.status}")
    return executor, state
```

---

### Procedure 2: Warm Restart (From Checkpoint)

**Trigger:** Normal agent restart or session recovery  
**Duration:** < 100ms  
**Success Criteria:** Executor resumed from checkpoint with 100% state consistency

#### Steps

1. **Load Most Recent Checkpoint** (from Track 10.1)
   ```python
   checkpoint = await session_manager.get_latest_checkpoint(
       session_id=current_session_id,
   )
   
   if not checkpoint:
       logger.warning("No checkpoint found, falling back to cold start")
       return await cold_start_initialization()
   ```

2. **Restore Agent State**
   ```python
   restored_state = OODAState.from_dict(checkpoint["state"])
   
   # Validate state integrity
   if not validate_state_consistency(restored_state):
       logger.error("Checkpoint state corrupted, initiating recovery")
       return await recovery_procedure()
   ```

3. **Reinitialize Context Provider**
   ```python
   context_provider = ContextProvider(context_injector)
   
   # Prime pattern cache with last-used patterns
   if checkpoint.get("patterns"):
       context_provider.cache_patterns(checkpoint["patterns"])
   ```

4. **Resume OODA Executor**
   ```python
   executor = OODAExecutor(
       state_provider=state_provider,
       context_provider=context_provider,
       max_concurrent_loops=100,
   )
   
   # Restore internal metrics
   executor.metrics = checkpoint.get("executor_metrics", {})
   ```

5. **Verify Readiness**
   ```python
   # Execute warmup cycle
   warmup_state = await executor.execute_cycle(
       task_id="warmup_001",
       task_type="warmup",
       priority="P3",
   )
   
   if warmup_state.action_result.status != "success":
       logger.warning("Warmup failed, degrading to no-context mode")
       executor.context_provider = None
   ```

#### Example (Warm Restart)

```python
async def warm_restart_initialization(checkpoint_id: str):
    """Resume OODA loop from checkpoint."""
    logger.info(f"Starting warm restart from checkpoint {checkpoint_id}...")
    
    # Load checkpoint
    checkpoint = await session_manager.get_checkpoint(checkpoint_id)
    
    if not checkpoint:
        logger.error(f"Checkpoint {checkpoint_id} not found")
        return await cold_start_initialization()
    
    # Restore state
    restored_state = OODAState.from_dict(checkpoint["state"])
    logger.info(f"Restored state: phase={restored_state.phase}")
    
    # Validate integrity
    integrity = await validate_checkpoint_integrity(checkpoint)
    if not integrity["valid"]:
        logger.error(f"Checkpoint integrity check failed: {integrity['errors']}")
        return await recovery_procedure(checkpoint)
    
    # Reinitialize components
    pattern_store = await load_pattern_store()
    session_store = await load_session_store()
    
    context_injector = ContextInjector(pattern_store, session_store)
    executor = OODAExecutor(
        state_provider=state_provider,
        context_provider=ContextProvider(context_injector),
    )
    
    # Execute warmup
    warmup = await executor.execute_cycle("warmup", "warmup", "P3")
    
    if warmup.action_result.status == "success":
        logger.info("Warm restart complete and verified")
        return executor, warmup
    else:
        logger.warning("Warmup failed, degrading")
        executor.context_provider = None
        return executor, warmup
```

---

### Procedure 3: Context Loading (Training)

**Trigger:** Periodic context refresh or explicit training request  
**Duration:** < 500ms (async, doesn't block OODA cycles)  
**Success Criteria:** All historical patterns and sessions loaded and indexed

#### Steps

1. **Load Historical Patterns** (from Track 10.2)
   ```python
   patterns = await pattern_store.get_all_patterns()
   
   # Filter by age and relevance
   active_patterns = [
       p for p in patterns
       if datetime.fromisoformat(p["updated_at"]) > (datetime.now() - timedelta(days=90))
   ]
   
   logger.info(f"Loaded {len(active_patterns)} active patterns")
   ```

2. **Load Decision History** (from Track 10.1)
   ```python
   # Get last 100 decisions per task type
   for task_type in TASK_TYPES:
       decisions = await session_store.get_decision_history(
           task_type=task_type,
           limit=100,
       )
       
       # Index by outcome for quick lookup
       context_cache[task_type] = {
           "decisions": decisions,
           "success_rate": calculate_success_rate(decisions),
       }
   ```

3. **Build Pattern Index** (Vector Index)
   ```python
   # Create search index for pattern similarity
   pattern_vectors = [
       vector_encoder.encode_pattern(p)
       for p in active_patterns
   ]
   
   # Store in FAISS or similar index
   pattern_index = faiss.IndexFlatL2(vector_size)
   pattern_index.add(np.array(pattern_vectors))
   ```

4. **Cache Frequently Used Patterns**
   ```python
   # Get top 5 patterns for each improvement area
   for improvement_area in IMPROVEMENT_AREAS:
       top_patterns = await pattern_store.get_patterns_by_tag(
           improvement_area,
           limit=5,
       )
       
       context_cache["top_patterns"][improvement_area] = top_patterns
   ```

5. **Update Context Provider**
   ```python
   context_provider.refresh_cache(
       patterns=active_patterns,
       decisions=context_cache,
       pattern_index=pattern_index,
   )
   ```

#### Example (Training Context)

```python
async def load_training_context():
    """Load and index historical patterns for training."""
    logger.info("Loading training context...")
    
    start_time = time.time()
    
    # Load patterns from LTM
    all_patterns = await pattern_store.get_all_patterns()
    
    # Filter and rank
    active_patterns = [
        p for p in all_patterns
        if p["success_rate"] > 0.7  # High quality patterns
        and p["sample_size"] > 10   # Sufficient data
    ]
    
    logger.info(f"Selected {len(active_patterns)} high-quality patterns")
    
    # Build indexes
    pattern_vectors = np.array([
        vector_encoder.encode_pattern(p) for p in active_patterns
    ])
    
    # Create FAISS index for fast similarity search
    index = faiss.IndexFlatL2(vector_size)
    index.add(pattern_vectors)
    
    # Load decision history
    for task_type in TASK_TYPES:
        decisions = await session_store.get_decision_history(task_type, limit=100)
        
        # Calculate metrics
        success_count = sum(1 for d in decisions if d["outcome"] == "success")
        success_rate = success_count / len(decisions) if decisions else 0
        
        logger.info(f"{task_type}: {len(decisions)} decisions, {success_rate:.1%} success")
    
    elapsed = time.time() - start_time
    logger.info(f"Training context loaded in {elapsed:.1f}s")
```

---

### Procedure 4: State Recovery (Corrupted State)

**Trigger:** State validation failure or checkpoint corruption  
**Duration:** < 200ms  
**Success Criteria:** Valid state restored from backup or clean slate

#### Steps

1. **Detect Corruption**
   ```python
   corruption_signs = {
       "invalid_phase": state.phase not in OODAPhase,
       "missing_observation": state.observation is None and state.phase != OODAPhase.IDLE,
       "inconsistent_metrics": state.metrics.get("total_time_ms", 0) < 0,
       "corrupted_action_result": state.action_result and not isinstance(state.action_result, ActionResult),
   }
   
   if any(corruption_signs.values()):
       logger.error(f"State corruption detected: {corruption_signs}")
       # Initiate recovery
   ```

2. **Load Backup Checkpoint**
   ```python
   # Try previous checkpoints in reverse chronological order
   backups = await session_manager.list_checkpoints(
       session_id=current_session_id,
       limit=5,  # Last 5 checkpoints
   )
   
   recovered_state = None
   for backup in backups:
       if await validate_checkpoint_integrity(backup):
           recovered_state = OODAState.from_dict(backup["state"])
           logger.info(f"Recovered from backup checkpoint {backup['id']}")
           break
   ```

3. **Reset to Safe State**
   ```python
   if not recovered_state:
       # Reset to idle state
       recovered_state = OODAState(
           cycle_id=str(uuid.uuid4()),
           phase=OODAPhase.IDLE,
           start_time=datetime.now(),
       )
       logger.warning("No valid backup found, resetting to idle state")
   ```

4. **Reinitialize Executor with Recovered State**
   ```python
   executor = OODAExecutor(state_provider, context_provider)
   
   # Restore metrics
   executor.metrics = recovered_state.metrics
   
   # Continue execution
   logger.info(f"Recovery complete, resuming from {recovered_state.phase.value}")
   ```

5. **Log Recovery Event**
   ```python
   recovery_log = {
       "timestamp": datetime.now().isoformat(),
       "corruption_signs": corruption_signs,
       "recovery_source": "backup_checkpoint",
       "recovered_checkpoint_id": backup["id"] if recovered_state else None,
   }
   
   await session_manager.log_recovery_event(recovery_log)
   ```

#### Example (State Recovery)

```python
async def recover_corrupted_state(corrupted_state: OODAState):
    """Recover from corrupted OODA state."""
    logger.error(f"Initiating state recovery from corrupted state in phase {corrupted_state.phase}")
    
    # Check backup checkpoints
    backups = await session_manager.list_checkpoints(
        session_id=current_session_id,
        limit=10,
    )
    
    # Validate each backup
    for backup in backups:
        logger.debug(f"Checking backup {backup['id']}...")
        
        try:
            # Restore and validate
            state = OODAState.from_dict(backup["state"])
            
            # Quick validation
            assert state.cycle_id is not None
            assert state.phase in OODAPhase
            assert state.start_time is not None
            
            logger.info(f"✓ Backup {backup['id']} is valid")
            return state
        
        except Exception as e:
            logger.debug(f"✗ Backup {backup['id']} invalid: {e}")
            continue
    
    # No valid backups - reset to idle
    logger.warning("No valid backups found, resetting to IDLE")
    
    return OODAState(
        cycle_id=str(uuid.uuid4()),
        phase=OODAPhase.IDLE,
        start_time=datetime.now(),
    )
```

---

### Procedure 5: Graceful Degradation

**Trigger:** Dependency unavailable (LTM, Sessions, State Provider)  
**Duration:** Immediate (no extra latency)  
**Success Criteria:** OODA continues with reduced context

#### Degradation Levels

| Level | Condition | Context | Performance |
|-------|-----------|---------|-------------|
| **Full** | All dependencies available | Patterns + Sessions + External | 50-60ms/phase |
| **Pattern-Only** | LTM available, Sessions down | Patterns only | 45-55ms/phase |
| **No-Context** | Both LTM & Sessions down | Repository state only | 30-40ms/phase |
| **Emergency** | State provider failing | Last known good strategy | < 10ms/phase |

#### Recovery from Level 1 (Full) → Level 2 (Pattern-Only)

```python
async def degrade_to_pattern_only(context_injector, error: Exception):
    """Degrade context injection to pattern-only mode."""
    logger.warning(f"Session store unavailable: {error}")
    logger.warning("Degrading to pattern-only context")
    
    # Recreate context injector without session store
    context_injector_degraded = ContextInjector(
        pattern_store=context_injector.pattern_store,
        session_store=None,  # Disable sessions
    )
    
    # Update context provider
    context_provider.degradation_level = DegradationLevel.PATTERN_ONLY
    context_provider.injector = context_injector_degraded
    
    return context_injector_degraded
```

#### Recovery from Level 2 (Pattern-Only) → Level 3 (No-Context)

```python
async def degrade_to_no_context(executor: OODAExecutor, error: Exception):
    """Degrade to no-context execution."""
    logger.warning(f"Pattern store unavailable: {error}")
    logger.warning("Degrading to no-context OODA execution")
    
    # Disable context provider entirely
    executor.context_provider = None
    
    # Continue with repository state only
    logger.info("Continuing OODA execution with no context")
```

#### Recovery from Level 3 (No-Context) → Level 4 (Emergency)

```python
async def emergency_mode(executor: OODAExecutor, error: Exception):
    """Enter emergency mode with fallback strategy."""
    logger.critical(f"State provider failed: {error}")
    logger.critical("Entering emergency fallback mode")
    
    # Use last known good strategy
    last_strategy = executor.get_last_successful_strategy()
    
    # Execute without any observation/orientation
    result = await executor._act_emergency(last_strategy)
    
    # Escalate to Track 10.1 for state recovery
    await escalate_to_track_10_1(
        reason="State provider failure",
        last_strategy=last_strategy,
        error=str(error),
    )
```

---

## Initialization Checklist

Use this checklist before deploying OODA loop to production:

- [ ] Track 10.1 Session Manager API available and tested
- [ ] Track 10.2 Pattern Store API available and tested
- [ ] State Provider implements all required methods
- [ ] Context Provider implements all required async methods
- [ ] Vector encoder initialized with 128-dim vectors
- [ ] Pattern index built with > 1000 patterns
- [ ] Decision history loaded with > 100 decisions per task type
- [ ] All 5 reinitialization procedures tested
- [ ] Graceful degradation procedures tested (all 4 levels)
- [ ] State validation and recovery procedures tested
- [ ] Checkpoint serialization/deserialization working
- [ ] Metrics collection working
- [ ] Async concurrency tested (100+ parallel loops)
- [ ] Performance targets verified (< 200ms cycle time)
- [ ] Integration tests passing (> 99%)
- [ ] Monitoring and alerting configured

---

## Monitoring & Health Checks

### Periodic Health Checks (Every 5 minutes)

```python
async def check_ooda_health():
    """Periodic health check for OODA system."""
    
    health = {
        "timestamp": datetime.now().isoformat(),
        "executor_active": len(executor.active_cycles),
        "total_cycles": executor.metrics["total_cycles"],
        "success_rate": executor.metrics.get("success_rate", 0),
        "avg_cycle_time_ms": executor.metrics.get("avg_cycle_time_ms", 0),
    }
    
    # Check dependencies
    health["state_provider_ok"] = await check_state_provider()
    health["pattern_store_ok"] = await check_pattern_store()
    health["session_store_ok"] = await check_session_store()
    
    # Determine degradation level
    dependencies_ok = [
        health.get(f"{dep}_ok", False)
        for dep in ["state_provider", "pattern_store", "session_store"]
    ]
    
    if all(dependencies_ok):
        health["degradation_level"] = "FULL_CONTEXT"
    elif dependencies_ok[0] and dependencies_ok[1]:
        health["degradation_level"] = "PATTERN_ONLY"
    elif dependencies_ok[0]:
        health["degradation_level"] = "NO_CONTEXT"
    else:
        health["degradation_level"] = "EMERGENCY"
    
    # Alert if health degraded
    if health["degradation_level"] != "FULL_CONTEXT":
        logger.warning(f"OODA health degraded: {health['degradation_level']}")
    
    return health
```

---

## Summary

This document specifies 5 reinitialization procedures:
1. **Cold Start:** Initialize from scratch
2. **Warm Restart:** Resume from checkpoint
3. **Training Context:** Load historical data
4. **State Recovery:** Recover from corruption
5. **Graceful Degradation:** Handle dependency failures

All procedures target < 100ms initialization with 100% state consistency and support 4 degradation levels (Full → Pattern-Only → No-Context → Emergency).

---

**Sign-Off:** Reinitialization procedures complete and ready for Day 7 performance profiling.
