# Execution Loop Integration Guide

## Overview

This guide describes how to integrate the core autonomy foundations into runtime systems to enforce the full 8-step deterministic execution loop.

## 8-Step Execution Loop

```
1. OBSERVE   → Gather input data and environmental context
2. CONTEXT   → Enrich with historical and dependency info
3. DECIDE    → Evaluate options against constraints
4. ACT       → Execute selected action
5. VALIDATE  → Verify state meets all constraints (NEW - CRITICAL)
6. PERSIST   → Save to checkpoint storage (NEW - CRITICAL)
7. HANDOFF   → Prepare agent transition (NEW - CRITICAL)
8. COMPLETE  → Mark task complete or continue to next step
```

## Hard Rules for Execution Loop

### 1. No Skipping Validation

```python
if execution_step == "act":
    # MUST proceed to validate step
    next_step = "validate"
    
    # MUST call validation_engine.validate_state()
    validation_result = validate_state(current_state)
    
    # Block if invalid
    if not validation_result["valid"]:
        current_state["status"] = "blocked"
        # MUST NOT continue to persist
        return escalate_or_retry()
```

### 2. No Skipping Persistence

```python
if execution_step == "validate":
    if validation_result["valid"]:
        # MUST persist to checkpoint
        checkpoint_id = checkpoint_manager.create_checkpoint(current_state)
        
        # MUST update state with checkpoint reference
        current_state["_checkpoint_id"] = checkpoint_id
        
        # Only THEN proceed to handoff
        next_step = "persist"
```

### 3. Handoff Before Continuation

```python
if execution_step == "persist":
    # If handing off to another agent
    if next_agent != current_agent:
        handoff = prepare_handoff(
            state=current_state,
            next_agent=next_agent,
            current_agent=current_agent
        )
        
        # Store handoff
        current_state["_handoff_object"] = handoff.to_dict()
        
        # Only then transition
        next_step = "handoff"
```

## Integration Points

### Phase 10: Session Manager

```python
# session_manager.py should:

def create_session(agent_id, phase_id, track_id, task_id):
    # Initialize canonical state
    state = {
        "state_id": uuid.uuid4(),
        "agent_id": agent_id,
        "phase_id": phase_id,
        "track_id": track_id,
        "task_id": task_id,
        "execution_step": "observe",
        "status": "in_progress",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        ...
    }
    
    # Create checkpoint manager
    self.checkpoint_manager = CheckpointManager()
    
    return state

def resume_session(checkpoint_id):
    # MUST use checkpoint_manager
    state = self.checkpoint_manager.load_checkpoint(checkpoint_id)
    state = self.checkpoint_manager.resume_execution(checkpoint_id)
    
    return state
```

### Phase 10: OODA Loop

```python
# ooda_loop_executor.py should:

def execute_ooda_iteration(state):
    # Step 1: Observe
    state = observe_step(state)
    state["execution_step"] = "observe"
    
    # Step 2: Context
    state = context_step(state)
    state["execution_step"] = "context"
    
    # Step 3: Decide
    state = decide_step(state)
    state["execution_step"] = "decide"
    
    # Step 4: Act
    state = act_step(state)
    state["execution_step"] = "act"
    
    # Step 5: VALIDATE (NEW)
    validation = validate_state(state)
    state["validation_results"] = validation
    state["execution_step"] = "validate"
    
    if not validation["valid"]:
        state["status"] = "blocked"
        return escalate(state)
    
    state["status"] = "validated"
    
    # Step 6: PERSIST (NEW)
    checkpoint_id = checkpoint_manager.create_checkpoint(state)
    state["_checkpoint_id"] = checkpoint_id
    state["execution_step"] = "persist"
    
    # Step 7: HANDOFF (NEW)
    if needs_handoff(state):
        handoff = prepare_handoff(state, next_agent)
        state["_handoff_object"] = handoff
    
    state["execution_step"] = "handoff"
    
    # Step 8: Continue
    state["execution_step"] = "complete"
    
    return state
```

### Phase 12: Governance

```python
# governance_rbac.py should:

def validate_state_transition(current_state, proposed_state):
    # Use validation engine
    from scripts.core import validate_state_transition
    
    validation = validate_state_transition(current_state, proposed_state)
    
    if not validation["valid"]:
        # RBAC can block
        return deny_transition(validation)
    
    # Check escalation flag
    if validation.get("requires_escalation"):
        return require_approval(proposed_state)
    
    return allow_transition(proposed_state)
```

## Migration Checklist

- [ ] Import core modules: `from scripts.core import *`
- [ ] Replace ad-hoc state dicts with canonical schema
- [ ] Add validation after ACT step
- [ ] Add checkpoint after VALIDATE step
- [ ] Add handoff protocol before agent transitions
- [ ] Update session manager to use CheckpointManager
- [ ] Update OODA loop to include full 8 steps
- [ ] Connect governance to validation_engine
- [ ] Test full loop with test_execution_loop.py
- [ ] Verify no step skipping in logs
- [ ] Verify no data loss in state transitions

## Success Metrics

1. **No Execution Halts**: Full 8/8 steps complete
2. **No State Loss**: Every state checkpointed and recoverable
3. **Decision Preservation**: 100% of decision rationale transferred
4. **STM Preservation**: 100% of context preserved in handoffs
5. **Validation Coverage**: All state transitions validated
6. **Zero Data Loss**: Lineage fully tracked for all states
