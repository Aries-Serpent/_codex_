# Conservation Law Verification & Enforcement

> **Prompt**: 02_conservation.prompt.md  
> **Previous**: 01_extend_operators.prompt.md  
> **Next**: 03_testing.prompt.md  
> **Prerequisites**: Foundation working, tests passing

---

## Objective

Enhance conservation checking to detect and repair probability leaks.

## Current Implementation

The orchestrator already has `verify_conservation()` method that checks:
```python
∂ρ/∂t + ∇·j = 0  # Continuity equation
```

## Enhancement Tasks

### 1. Add Leak Detection

Update `orchestrator.py` to add leak detection:

```python
def find_leaks(self) -> List[Dict[str, Any]]:
    """
    Find tasks that are leaking probability.
    
    Returns list of tasks violating conservation.
    """
    if len(self.history) < 1:
        return []
    
    leaks = []
    prev_state = self.history[-1]
    dt = self.dt
    
    for task_id, task in self.state.tasks.items():
        if task_id not in prev_state.tasks:
            continue
        
        prev_task = prev_state.tasks[task_id]
        
        # Probability change
        p_current = task.probability
        p_previous = prev_task.probability
        dp_dt = (p_current - p_previous) / dt
        
        # Current for this task
        j = self.current_op.task_current(
            self.state, prev_state, task_id, dt
        )
        
        # Local violation
        local_violation = abs(dp_dt + j)
        
        if local_violation > 0.05:  # Threshold
            leaks.append({
                "task_id": task_id,
                "violation": local_violation,
                "probability": p_current,
                "current": j,
            })
    
    return leaks
```

### 2. Add Automatic Repair

```python
def repair_conservation(self) -> None:
    """
    Repair conservation violations.
    
    Applies renormalization and dampening to fix leaks.
    """
    leaks = self.find_leaks()
    
    if not leaks:
        return
    
    # Renormalize all spinors
    self.state.normalize()
    
    # Apply dampening to leaking tasks
    for leak in leaks:
        task = self.state.tasks[leak["task_id"]]
        # Dampen amplitude slightly
        task.spinor.components *= 0.95
        task.spinor.normalize()
```

### 3. Integrate into Self-Healing

Update `self_heal()` to include conservation repair:

```python
def self_heal(self) -> None:
    """Self-healing with conservation enforcement."""
    # Existing stability checks
    unstable_tasks = self.check_stability()
    for task_id in unstable_tasks:
        self.stabilize_task(task_id)
    
    # NEW: Conservation repair
    conservation_status = self.verify_conservation()
    if not conservation_status["is_conserved"]:
        self.repair_conservation()
    
    # Existing bottleneck handling
    if len(self.history) >= 1:
        bottlenecks = self.flow_analyzer.identify_bottlenecks(
            self.state, self.history[-1], self.dt
        )
        for bottleneck in bottlenecks[:3]:
            task = self.state.tasks[bottleneck["task_id"]]
            task.position.priority *= 1.2
            task.spinor.components[0] *= 1.1
            task.spinor.components[1] *= 1.1
    
    # Final renormalization
    self.state.normalize()
```

## Testing

### File: `tests/quantum_orchestrator/test_conservation.py`

```python
import pytest
from codex.quantum_orchestrator import create_orchestrator


def test_conservation_verification():
    """Test conservation checking."""
    orch = create_orchestrator()
    orch.add_task("t1", "Task 1", rest_mass=1.0)
    
    # Evolve
    for _ in range(5):
        orch.evolve()
    
    # Check conservation
    status = orch.verify_conservation()
    assert "is_conserved" in status
    assert "violation" in status


def test_leak_detection():
    """Test leak detection."""
    orch = create_orchestrator()
    orch.add_task("t1", "Task 1", rest_mass=1.0)
    
    # Evolve to build history
    for _ in range(3):
        orch.evolve()
    
    # Check for leaks
    leaks = orch.find_leaks()
    assert isinstance(leaks, list)


def test_conservation_repair():
    """Test automatic repair."""
    orch = create_orchestrator()
    orch.add_task("t1", "Task 1", rest_mass=1.0)
    
    # Evolve
    for _ in range(5):
        orch.evolve()
    
    # Force repair
    orch.repair_conservation()
    
    # Verify normalized
    assert abs(orch.state.total_probability() - len(orch.state.tasks)) < 0.1
```

## Verification Commands

```bash
# Run conservation tests
PYTHONPATH=src:$PYTHONPATH python3 -m pytest \
    tests/quantum_orchestrator/test_conservation.py -v

# Run full test suite
PYTHONPATH=src:$PYTHONPATH python3 -m pytest \
    tests/quantum_orchestrator/ -v --no-cov
```

## Success Criteria

- [ ] `find_leaks()` method added
- [ ] `repair_conservation()` method added
- [ ] Integrated into `self_heal()`
- [ ] Tests written and passing
- [ ] No conservation violations in examples

## Monitoring

Add logging to track conservation:

```python
def evolve(self):
    ...
    # After evolution, check conservation
    if self.state.timestamp % 1.0 < self.dt:  # Every second
        status = self.verify_conservation()
        if not status["is_conserved"]:
            print(f"⚠️  Conservation violation: {status['violation']:.4f}")
```

## Next Steps

Proceed to: **Next Prompt**: `03_testing.prompt.md`

---

**Status**: Conservation enhancement ✅
