# Extend Quantum Operators

> **Prompt**: 01_extend_operators.prompt.md  
> **Previous**: 00_foundation.prompt.md  
> **Next**: 02_conservation.prompt.md  
> **Prerequisites**: Foundation verified, all imports working

---

## Objective

Add optional Klein-Gordon operator for second-order time dynamics.

## Background

Currently, the orchestrator uses first-order Dirac dynamics:
```
iℏ∂ψ/∂t = Ĥψ
```

Klein-Gordon provides second-order dynamics (includes acceleration):
```
-ℏ²∂²ψ/∂t² = (-ℏ²c²∇² + m²c⁴)ψ
```

## Implementation

### File: `src/codex/quantum_orchestrator/operators/klein_gordon.py`

```python
"""
Klein-Gordon operator for second-order relativistic dynamics.

Implements: -ℏ²∂²ψ/∂t² = (-ℏ²c²∇² + m²c⁴)ψ
"""

import numpy as np
from typing import Dict
from ..orchestrator import PhysicsConstants, OrchestratorState, TaskState


class KleinGordonOperator:
    """
    Klein-Gordon equation operator.
    
    Provides second-order time dynamics (acceleration).
    """
    
    def __init__(self, constants: PhysicsConstants):
        self.constants = constants
        self.c = constants.c
        self.hbar = constants.hbar
    
    def second_time_derivative(
        self,
        current_state: OrchestratorState,
        previous_state: OrchestratorState,
        older_state: OrchestratorState,
        task_id: str,
        dt: float,
    ) -> complex:
        """
        Compute ∂²ψ/∂t² using finite differences.
        
        ∂²ψ/∂t² ≈ (ψ(t) - 2ψ(t-dt) + ψ(t-2dt)) / dt²
        """
        if task_id not in previous_state.tasks or task_id not in older_state.tasks:
            return 0.0 + 0j
        
        psi_current = current_state.tasks[task_id].spinor.psi_1
        psi_prev = previous_state.tasks[task_id].spinor.psi_1
        psi_older = older_state.tasks[task_id].spinor.psi_1
        
        d2psi_dt2 = (psi_current - 2*psi_prev + psi_older) / (dt**2)
        return d2psi_dt2
    
    def apply(self, state: OrchestratorState, task_id: str) -> complex:
        """
        Apply Klein-Gordon operator to get ∂²ψ/∂t².
        
        From: -ℏ²∂²ψ/∂t² = (-ℏ²c²∇² + m²c⁴)ψ
        We get: ∂²ψ/∂t² = (c²∇² - (mc²/ℏ)²)ψ
        """
        task = state.tasks[task_id]
        c = self.c
        hbar = self.hbar
        m = task.rest_mass
        psi = task.spinor.psi_1
        
        # Simplified Laplacian (would need proper implementation)
        laplacian = 0.0 + 0j  # Placeholder
        
        # Klein-Gordon: ∂²ψ/∂t² = c²∇²ψ - (mc²/ℏ)²ψ
        mass_term = (m * c * c / hbar) ** 2
        d2psi_dt2 = c*c * laplacian - mass_term * psi
        
        return d2psi_dt2
```

## Testing

### File: `tests/quantum_orchestrator/test_klein_gordon.py`

```python
import pytest
from codex.quantum_orchestrator.orchestrator import (
    create_orchestrator,
    PhysicsConstants,
    OrchestratorState,
)
from codex.quantum_orchestrator.operators.klein_gordon import KleinGordonOperator


def test_klein_gordon_creation():
    """Test Klein-Gordon operator creation."""
    const = PhysicsConstants()
    kg = KleinGordonOperator(const)
    assert kg.c == 100.0
    assert kg.hbar == 1.0


def test_second_time_derivative():
    """Test second time derivative calculation."""
    const = PhysicsConstants()
    kg = KleinGordonOperator(const)
    
    # Create three states
    state1 = OrchestratorState(constants=const)
    state2 = OrchestratorState(constants=const)
    state3 = OrchestratorState(constants=const)
    
    # Would need proper test implementation
    pass
```

## Verification

```bash
PYTHONPATH=src:$PYTHONPATH python3 -m pytest \
    tests/quantum_orchestrator/test_klein_gordon.py -v
```

## Integration (Optional)

Add Klein-Gordon mode to orchestrator:

```python
class QuantumRelativisticDiracOrchestrator:
    def __init__(self, ..., use_klein_gordon=False):
        ...
        if use_klein_gordon:
            self.kg_operator = KleinGordonOperator(self.constants)
```

## Success Criteria

- [ ] KleinGordonOperator class created
- [ ] Tests written and passing
- [ ] Optional: Integrated into orchestrator

## Next Steps

Proceed to: **Next Prompt**: `02_conservation.prompt.md`

---

**Status**: Operator extension optional, skip if not needed ⏭️
