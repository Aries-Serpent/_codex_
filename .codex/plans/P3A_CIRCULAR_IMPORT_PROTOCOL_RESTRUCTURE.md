# Planset: P3a — Circular Import Restructuring via Protocol Types

**Status**: 🟢 ENHANCEMENT — After Phase 6 merge  
**Priority**: P3 — Enhancement  
**Created**: 2026-02-20  
**Scope**: `src/codex/archive/` (backend.py ↔ config.py cycle)

---

## Problem

`src/codex/archive/backend.py` and `src/codex/archive/config.py` have a circular import:

```
config.py  imports  ArchiveConfig  from  backend.py
backend.py imports  ArchiveAppConfig from config.py  (lazy workaround currently)
```

The current workaround (lazy import inside `from_env()` + `Any` annotation on `from_settings`) is functional but loses type safety and triggers CodeQL cyclic import alerts.

---

## Solution: Protocol + Shared Types Module

### Option A (Preferred): Extract shared types to `src/codex/archive/types.py`

```
archive/
├── __init__.py
├── backend.py       ← imports from types.py only
├── config.py        ← imports from types.py only
├── types.py         ← NEW: shared dataclasses/protocols
├── schema.py
└── util.py
```

**`types.py` content**:
```python
"""Shared type definitions for archive modules (breaks backend↔config cycle)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ArchiveBackendSpec:
    """Minimal backend specification shared between config and backend modules."""
    url: str
    backend: str


class ArchiveSettingsProtocol(Protocol):
    """Protocol for any settings object that provides backend configuration."""
    @property
    def backend(self) -> ArchiveBackendSpec: ...
```

**`backend.py` change**:
```python
# Remove: lazy import of ArchiveAppConfig from config.py
# Add:
from .types import ArchiveSettingsProtocol

@classmethod
def from_settings(cls, settings: ArchiveSettingsProtocol) -> ArchiveConfig:
    return cls(url=settings.backend.url, backend=settings.backend.backend)
```

**`config.py` change**:
```python
# Remove: from .backend import ArchiveConfig (or make lazy)
from .types import ArchiveBackendSpec
```

### Option B: Use `__init__.py` as the coordination layer

Move `ArchiveConfig` to `types.py` so neither `config.py` nor `backend.py` imports from each other.

---

## Implementation Steps

1. **Create `src/codex/archive/types.py`** with `ArchiveBackendSpec` and `ArchiveSettingsProtocol`
2. **Update `backend.py`**: remove lazy import, use `ArchiveSettingsProtocol` annotation
3. **Update `config.py`**: import `ArchiveBackendSpec` from `types.py` instead of `backend.py`
4. **Update `__init__.py`**: export from `types.py`
5. **Run tests**: `pytest tests/archive/ -q`
6. **Run CodeQL**: confirm cyclic import alert is resolved

## Success Criterion

- Zero cyclic import CodeQL alerts in `archive/`
- `from_settings()` has proper type annotation (`ArchiveSettingsProtocol` not `Any`)
- All `tests/archive/` tests pass
- No regressions in `tests/` suite

---

## Estimated Effort

1 hour — isolated change, no cross-module impact.
