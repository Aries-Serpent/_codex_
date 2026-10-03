# Phase 2 Lane 2: Namespace Bridge Implementation Plan

**Status**: READY FOR EXECUTION  
**Priority**: CRITICAL PATH (unblocks Lanes 3-4)  
**Estimated Duration**: 15-30 minutes  
**Expected Outcome**: Reduce collection errors from 442 to ~50

---

## Quick Start

This lane creates a bridging namespace package to resolve the `codex.*` import errors identified in Lane 1.

### Lane 1 Summary (Reference)
```
Collection errors: 442 total
- 390 errors: ModuleNotFoundError: No module named 'codex'
- 28 errors: Missing optional dependencies
- 15 errors: Module-level issues
- 9 errors: Other (fixable)

Root cause: Namespace package refactoring
  OLD: from codex.agents import BrainClient
  NEW: from aries_serpent_core.agents import BrainClient
```

---

## Solution: Namespace Bridge Package

### Step 1: Create Bridging Package
**Location**: `src/codex/__init__.py`  
**Purpose**: Re-export from `aries_serpent_core` and `codex_*` packages

### Step 2: Map Import Paths
```python
# src/codex/__init__.py (EXAMPLE STRUCTURE)

"""Namespace bridge for legacy codex.* imports.

This module re-exports symbols from the refactored package structure:
  aries_serpent_core.*  (agents, utils, etc.)
  codex_ml.*           (ML core modules)
  codex_cli.*          (CLI components)
  ... others ...
"""

# Agent imports
try:
    from aries_serpent_core.agents.brain_client import BrainClient, BrainClientError
    from aries_serpent_core.agents import *
except ImportError:
    pass

# ML imports
try:
    from codex_ml.tracking import *
    from codex_ml.logging import *
except ImportError:
    pass

# Add more as needed based on Lane 1 findings
__all__ = [
    'BrainClient',
    'BrainClientError',
    # ... others ...
]
```

---

## Implementation Checklist

### Phase 2A: Generate Bridge Mappings
```
[ ] Identify all `codex.*` imports in tests/ (grep results available from Lane 1)
[ ] Map each to actual location in src/
[ ] Group by package (agents, utils, logging, etc.)
[ ] Create import matrix (codex.X → actual.Y)
```

### Phase 2B: Implement Bridge
```
[ ] Create src/codex/__init__.py
[ ] Add re-export statements for identified imports
[ ] Test basic import: python3 -c "from codex.agents import BrainClient"
[ ] Verify no circular imports
[ ] Ensure all __all__ exports are documented
```

### Phase 2C: Validate Bridge
```
[ ] Run pytest collection on agents tests (expect errors drop)
[ ] Run pytest collection on full suite (expect 442 → 50)
[ ] Verify tokenization tests still pass
[ ] Check for new import errors (should be 0)
```

### Phase 2D: Commit & Report
```
[ ] Commit src/codex/__init__.py
[ ] Update PHASE_2_LANE_2_NAMESPACE_BRIDGE_REPORT.md
[ ] Unblock Lane 3-4 (can proceed in parallel)
```

---

## Key Imports to Bridge (from Lane 1)

**Priority 1** (Most frequent):
```python
from codex.agents.brain_client import BrainClient, BrainClientError
from codex.clients import CodexOpenAIClient  # or similar
from codex.logging import get_default_logger  # (if needed)
```

**Priority 2** (Agent/bridge):
```python
from codex.ast.graph import DependencyGraph
from codex.monitoring import metrics
from codex.zendesk.monitoring import register_zendesk_metrics
from codex.diagram.flows import flow_to_mermaid
```

**Priority 3** (Auth/security):
```python
from codex.auth.token_manager import TokenManager
from codex.knowledge.pii import scrub as scrub_pii
```

---

## Critical Success Factors

1. **No Circular Imports**: Bridge only re-exports; doesn't add logic
2. **Graceful Degradation**: Use try/except for optional packages
3. **Clear Audit Trail**: Document each mapping
4. **Test Validation**: Run collection before/after

---

## Parallel Work (Can Start Immediately)

While Lane 2 is being executed:
- **Lane 3**: Prepare bulk import update script (sed/ast-based)
- **Lane 4**: Install optional dependencies (transformers, pynvml)

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|-----------|
| Collection errors reduction | 442 → 50 | `pytest --co -q` |
| No new errors introduced | 0 | Manual review |
| Bridge imports working | 100% | Sample imports tested |
| Tokenization tests pass | YES | `pytest tests/tokenization/ -x` |

---

## Expected Outcome

After Lane 2:
- ✅ 390 namespace errors resolved
- ✅ Remaining 52 errors: optional deps + module issues (for Lanes 3-4)
- ✅ Lanes 2-4 can execute in parallel
- ✅ Full collection expected in <60 seconds (vs. 180s currently)

---

## Resources

- **Reference**: `.codex/PHASE_2_LANE_1_CI_TESTING_REPORT.md` (full diagnostics)
- **Import List**: 572 `codex.*` imports across codebase
- **Actual Packages**: src/aries_serpent_core/, src/codex_ml/, src/codex_cli/, etc.

---

**Status**: Ready to implement. No blockers.  
**Next Handler**: Lane 2 agent / executor
