# Quantum Orchestrator Foundation Verification

> **Prompt**: 00_foundation.prompt.md  
> **Next**: 01_extend_operators.prompt.md  
> **Prerequisites**: Repository cloned, Python 3.12+, numpy installed

---

## Objective

Verify that the Quantum-Relativistic-Dirac Orchestrator foundation is complete and functional.

## Tasks

### 1. Verify Installation

```bash
cd /home/runner/work/_codex_/_codex_
pip install numpy pytest pytest-cov -q
```

### 2. Test Imports

```bash
PYTHONPATH=src:$PYTHONPATH python3 -c "
from codex.quantum_orchestrator import (
    create_orchestrator,
    PhysicsConstants,
    TaskVector,
    DiracSpinor,
    DiracMatrices,
    TaskState,
    OrchestratorState,
)
print('✓ All imports successful')
"
```

### 3. Run Core Tests

```bash
PYTHONPATH=src:$PYTHONPATH python3 -m pytest \
    tests/quantum_orchestrator/test_physics_validation.py::TestSpinorPhysics \
    -v --no-cov
```

Expected: All tests pass

### 4. Run Basic Example

```bash
PYTHONPATH=src:$PYTHONPATH python3 -c "
from codex.quantum_orchestrator import create_orchestrator

orch = create_orchestrator()
orch.add_task('test', 'Test Task', priority=0.8, rest_mass=1.0)
results = orch.run(max_iterations=10)

print(f'✓ Completed {results[\"completion_rate\"]:.0%}')
"
```

## Success Criteria

- [ ] All imports work without errors
- [ ] Spinor physics tests pass
- [ ] Basic orchestration runs successfully
- [ ] No import errors or missing dependencies

## If Tests Fail

1. Check Python version: `python3 --version` (need 3.12+)
2. Verify numpy installed: `pip list | grep numpy`
3. Check PYTHONPATH is set correctly
4. Review error messages and fix imports

## Next Steps

Once foundation is verified, proceed to:  
**Next Prompt**: `01_extend_operators.prompt.md`

---

**Status**: Foundation verification complete ✅
