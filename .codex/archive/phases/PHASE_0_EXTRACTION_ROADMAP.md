# PHASE 0 EXTRACTION ROADMAP
## Detailed Timeline & Dependency Resolution

**Campaign:** Cognitive Brain-Powered Packaging  
**Timeline:** Weeks 1-16 (Aug 2026 - Nov 2026)  
**Authority:** @mbaetiong D-tier  

---

## Phase 1: LITE Profile (Weeks 1-2) — Foundation Layer

### Objective
Extract minimal, self-contained core utilities that can be used anywhere without external dependencies.

### Deliverables

**Package:** `codex-lite-0.1.0`

**Modules to extract:**
```
src/codex/utils/          (path_utils, json_safe, collections)
src/codex/config/         (Hydra integration, YAML)
cognitive_brain/base.py   (ABC interfaces only)
```

**Size:** ~50 KB  
**Dependencies:** `pydantic`, `pyyaml`, `hydra-core`, `cryptography` (only)  
**Install time:** <5 seconds  
**Python:** >=3.12  

### Detailed Tasks

| Task | Owner | Duration | Blockers |
|------|-------|----------|----------|
| Extract `codex.utils` submodule | @skills-master | 1 day | None |
| Audit imports for side effects | @skills-master | 0.5 day | None |
| Write minimal `__init__.py` | @skills-master | 0.5 day | None |
| Create `pyproject.toml` | @packaging-validation-agent | 1 day | None |
| Test install on 3 platforms (Linux/Mac/Windows) | @task | 1 day | Windows CI runner |
| Write quickstart docs | @doc-freshness-checker | 1 day | None |

### Export Readiness Checklist

- [x] Zero imports from `codex` (except config)
- [x] No network calls
- [x] No filesystem assumptions (uses `pathlib`)
- [x] No circular imports
- [x] 100% type hints
- [x] AAIS score ≥ 0.80 for all modules

### Success Criteria

- ✓ LITE package installs in <5s
- ✓ 100% import coverage (all APIs exported)
- ✓ Windows path handling verified
- ✓ Zero external API calls
- ✓ CI passing on Python 3.12+

### Failure Scenarios & Mitigations

| Scenario | Mitigation |
|----------|-----------|
| `pathlib` behaves differently on Windows | Add platform-specific tests; use `Path.resolve()` |
| Hydra dynamic config registration | Move to lazy imports; test with @pytest.fixture |
| YAML loader security | Already using `safe_load`; audit for XXE |

---

## Phase 2: COGNITIVE Core (Weeks 3-5) — Agent Engine

### Objective
Extract the full cognitive brain + OODA loop infrastructure as standalone module.

### Deliverables

**Package:** `codex-0.1.0`

**Modules to extract:**
```
src/codex/cognitive/              (OODA loop, agent brain API)
src/cognitive_brain/              (full implementation + quantum)
src/codex/skills/                 (execution envelope, telemetry)
src/codex/logging/                (structured logging, session tracking)
src/codex/security/               (auth/authz, policy)
src/codex/auth/                   (JWT validation)
```

**New dependencies:**
```
requests >= 2.34.2
fastapi >= 0.135.3 (optional)
ray >= 2.9 (optional)
```

**Size:** ~3.5 MB  
**Install time:** 15-20 seconds  

### Critical Decoupling Tasks

#### Task 2.1: Abstract Session Storage

**Current state:**
```python
# src/codex/cognitive/session.py
sessions_dir = Path.home() / ".codex" / "sessions"
session_data = json.load(open(sessions_dir / f"{session_id}.json"))
```

**Target state:**
```python
# src/codex/storage/backend.py
class SessionBackend(ABC):
    @abstractmethod
    def store(self, session: SessionContext) -> None: ...
    @abstractmethod
    def load(self, session_id: str) -> SessionContext: ...
    @abstractmethod
    def list_sessions(self) -> list[str]: ...

# implementations/
class FileSystemBackend(SessionBackend):  # Default
    def __init__(self, base_dir: Path = Path.home() / ".codex"):
        self.base_dir = base_dir
    
    def store(self, session: AbstractContext) -> None:
        (self.base_dir / "sessions" / f"{session.id}.json").write_text(...)

class RedisBackend(SessionBackend):  # Alternative
    def __init__(self, redis_url: str = "redis://localhost"):
        self.client = redis.from_url(redis_url)
    
    def store(self, session: SessionContext) -> None:
        self.client.set(f"session:{session.id}", session.model_dump_json())

class MemoryBackend(SessionBackend):  # Testing
    def __init__(self):
        self._sessions: dict[str, SessionContext] = {}
```

**Effort:** 2-3 days  
**Blocker:** None (pure refactoring)

#### Task 2.2: Decouple Quantum Planset Engine

**Current state:**
```
codex.quantum_orchestrator
  ├─ PlansetOrchestrator
  ├─ QuantumPlansetEngine
  ├─ ImprovementArea enum
  └─ imports from: codex.skills, codex.cognitive
```

**Issue:** Quantum engine only used internally; should be optional

**Solution:**
```python
# src/codex/cognitive/planner.py
class PlansetGenerator(ABC):
    @abstractmethod
    def generate(self, objective: str) -> list[Plan]: ...

# implementations/
class QuantumPlansetEngine(PlansetGenerator):
    """Optional quantum-enhanced planning"""
    def generate(self, objective: str) -> list[Plan]:
        ...
        return superposition_states

class SimplePlansetEngine(PlansetGenerator):
    """Fallback non-quantum planning"""
    def generate(self, objective: str) -> list[Plan]:
        return deterministic_plan(objective)
```

**Effort:** 1-2 days  
**Impact:** Makes quantum optional; reduces complexity

#### Task 2.3: Create Stable API Layer

**New file:** `src/codex/public_api.py`

```python
"""
Stable public API for CORE profile.

All exports here are STABLE (SemVer 2.0).
Breaking changes require MAJOR version bump.
"""

from codex.cognitive import (
    AgentBrainAPI,            # ✓ v0.1.0 (BETA)
    ImprovementArea,          # ✓ v0.1.0 (BETA)
    OKRTracker,               # ✓ v0.1.0 (BETA)
)

from codex.skills import (
    ExecutionEnvelope,        # ✓ v0.1.0 (BETA)
    SkillRegistry,            # ✓ v0.1.0 (BETA)
    SkillManifest,            # ✓ v0.1.0 (BETA)
)

from codex.auth import (
    AuthManager,              # ✓ v0.1.0 (STABLE)
    TokenValidator,           # ✓ v0.1.0 (STABLE)
)

from codex.storage import (
    SessionBackend,           # ABC (STABLE)
    FileSystemBackend,        # Default (STABLE)
    RedisBackend,             # Optional (BETA)
)

__all__ = [
    "AgentBrainAPI",
    "ExecutionEnvelope",
    "AuthManager",
    "SessionBackend",
    # ... 15 more
]

__api_version__ = "0.1.0"
```

**Effort:** 1 day  
**Benefit:** Clear contract for users; easier versioning

### Detailed Tasks

| Task | Owner | Duration | Blocker |
|------|-------|----------|---------|
| Abstract session storage (2.1) | @skills-master | 2 days | None |
| Create storage backend interface | @skills-master | 1 day | 2.1 |
| Refactor quantum engine (2.2) | @quantum-compliance-tuning-agent | 2 days | None |
| Extract cognitive → new package | @skills-master | 2 days | 2.1, 2.2 |
| Create stable API layer (2.3) | @skills-master | 1 day | Extract done |
| Write integration tests | @autonomous-test-healer-agent | 2 days | All tasks |
| Update docs (session backend, quantum optional) | @doc-freshness-checker | 2 days | All tasks |

### Export Readiness Checklist

- [ ] All submodules import from LITE without issue
- [ ] Session storage backend abstracted + tested
- [ ] Quantum engine optional + tested without quantum
- [ ] AAIS score ≥ 0.75 for all new modules
- [ ] CI passing on all Python versions
- [ ] Windows path handling verified
- [ ] No hidden imports from codex_ml
- [ ] API docs generated (OpenAPI)

### Success Criteria

- ✓ CORE package installs in <20s
- ✓ AgentBrainAPI can be instantiated standalone
- ✓ Session storage can use 3 backends (FS, Redis, Memory)
- ✓ Quantum engine optional (graceful degradation)
- ✓ All APIs in `public_api.py` documented

### Risk: Cognitive Brain Portability

**Current impedance:** 50/100

**Blocking issues:**
1. `.codex/sessions/` hardcoded in 12 places ⚠️
2. Quantum engine tightly coupled to orchestrator ⚠️
3. Skills registry integration not clean ⚠️

**By end of Phase 2:**
- Session storage abstracted → impedance +30
- Quantum optional → impedance +15
- Final impedance: 75/100 ✓

---

## Phase 3: ML Pipeline Extraction (Weeks 6-10) — Heavy Lifting

### Objective
Extract codex_ml as standalone package (separate from cognitive core).

### Deliverables

**New package:** `codex-ml-0.1.0` (separate PyPI package)

**Modules:**
```
src/codex_ml/
├── training/        (train loop, config, callbacks)
├── models/          (model registry, architectures)
├── evaluation/      (metrics, eval harness)
├── data/            (dataset loaders, preprocessing)
├── tokenization/    (tokenizer adapters)
├── serving/         (model serving, Ray integration)
└── monitoring/      (metrics, drift detection)
```

**New dependencies:**
```
torch >= 2.6.1
transformers >= 5.12.1
datasets >= 5.0.0
peft >= 0.19.1
accelerate >= 1.14.0
ray[serve] >= 2.9
scikit-learn >= 1.9.0
evidently >= 0.7.21
```

**Size:** ~3.5 MB (ML code only)  
**Install time:** 45-60 seconds  
**Complexity:** Expert-only; GPU/large memory required  

### Critical Decoupling: codex_ml → codex.logging

**Current problem:**
```python
# src/codex_ml/train_loop.py
from codex.logging.structured_logger import logger  # Hard dependency!

# This means codex_ml imports from codex, breaking independence
```

**Solution 1: Mirror logger in codex_ml**
```python
# src/codex_ml/logging/logger.py (new)
import logging
import json
from pathlib import Path
from typing import Any, Optional

class CodexLogger:
    """Minimal logger compatible with codex.logging.StructuredLogger"""
    
    def __init__(self, name: str, log_dir: Optional[Path] = None):
        self.logger = logging.getLogger(name)
        self.log_dir = log_dir or Path.home() / ".codex" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def info(self, msg: str, **metadata) -> None:
        event = {"level": "info", "msg": msg, **metadata}
        self.logger.info(json.dumps(event))
    
    # ... other methods
```

**Solution 2: Make codex.logging optional**
```python
# src/codex_ml/train_loop.py
try:
    from codex.logging.structured_logger import logger
    _has_codex_logging = True
except ImportError:
    from codex_ml.logging.logger import CodexLogger
    logger = CodexLogger("codex_ml.training")
    _has_codex_logging = False
```

**Effort:** 2-3 days  
**Impact:** codex_ml becomes truly independent ✓

### Detailed Tasks

| Task | Owner | Duration | Blocker |
|------|-------|----------|---------|
| Decouple codex_ml.logging | @skills-master | 2 days | None |
| Extract training pipeline | @skills-master | 3 days | logging decoupled |
| Extract model registry | @skills-master | 2 days | None |
| Extract evaluation harness | @autonomous-test-healer-agent | 2 days | None |
| Create `codex-ml` PyPI package | @packaging-validation-agent | 2 days | All tasks |
| Test with real ML workflow (HF models) | @task | 3 days | Package ready |
| Document GPU requirements | @doc-freshness-checker | 1 day | All tasks |

### Export Readiness Checklist

- [ ] codex_ml imports zero from codex (except optional logging)
- [ ] All torch/transformers imports are in functions (lazy)
- [ ] AAIS score ≥ 0.70 for all ML modules
- [ ] Can train with codex-lite (no CORE required)
- [ ] Can be installed separately from codex-core
- [ ] Memory usage documented (min 4GB recommended)
- [ ] GPU optional (CPU-only mode supported)

### Success Criteria

- ✓ `pip install codex-ml` works standalone
- ✓ Can run `codex-ml train` without codex-core
- ✓ Model registry can load HuggingFace models
- ✓ Evaluation metrics computed correctly
- ✓ Training with 4 GPUs or CPU fallback

### Risk: PyTorch Ecosystem Churn

**Mitigation:**
- Pin torch>=2.6.1 to stable release
- Add quarterly compatibility tests
- Document breaking changes per version

---

## Phase 4: Runtime Services (Weeks 11-13) — Production Ready

### Objective
Extract REST API layer, agent adapters, and integrations.

### Deliverables

**New package:** `codex-services-0.1.0`

**Modules:**
```
src/codex/api/              (FastAPI endpoints)
src/codex/github/           (GitHub client, webhooks)
src/mcp/                    (Model Context Protocol adapters)
src/services/               (orchestration, gRPC)
src/codex/zendesk/          (Zendesk integration)
```

**New optional dependencies:**
```
fastapi >= 0.135.3
starlette >= 1.0.1
pydantic-settings >= 2.14.2
ray[serve] >= 2.9
```

**Effort:** 3 weeks  

### Detailed Tasks

| Task | Owner | Duration |
|------|-------|----------|
| Extract REST API layer | @skills-master | 2 days |
| Extract GitHub integration | @skills-master | 2 days |
| Extract MCP adapters | @skills-master | 2 days |
| Create service health checks | @performance-monitor-agent | 1 day |
| Document API (OpenAPI/Swagger) | @unified-doc-agent | 2 days |
| Integration tests (E2E) | @integration-test-runner | 3 days |

### Success Criteria

- ✓ `codex.api` can be imported without torch
- ✓ REST endpoints documented in OpenAPI
- ✓ GitHub webhooks validated + secured
- ✓ MCP adapters work with Copilot + Claude

---

## Phase 5: Advanced Modules (Weeks 14-16) — Nice-to-Have

### Objective
Extract experimental/specialized modules.

**Modules:**
```
codex.quantum_orchestrator     (move to own package?)
codex.archive                  (deprecate or archive)
codex_crm                      (move to examples/)
hhg_logistics                  (move to examples/)
```

**Recommendation:** Archive quantum (experimental), deprecate CRM/hhg, keep archive for legacy users

---

## Verification Gates (All Phases)

### Gate 1: Import-Time Verification
```bash
# Should not error for each profile
python3 -c "import codex_lite"          # Phase 1
python3 -c "import codex"               # Phase 2
python3 -c "import codex_ml"            # Phase 3
python3 -c "import codex.api"           # Phase 4
```

### Gate 2: AAIS Scoring
```bash
# All modules must score >=0.70
codex-skill score --skill codex.utils
codex-skill score --skill codex.cognitive
codex-skill score --skill codex_ml
```

### Gate 3: Dependency Audit
```bash
# No unexpected imports
python3 scripts/audit_imports.py --strict
```

### Gate 4: Platform Testing
```bash
# Test on Linux, macOS, Windows
nox -s test_windows
nox -s test_macos
nox -s test_linux
```

### Gate 5: Integration Tests
```bash
# Profile dependencies must be correct
pytest tests/integration/test_profiles.py -v
```

---

## Timeline Summary

| Phase | Duration | Deliverable | Effort | Risk |
|-------|----------|------------|--------|------|
| **Phase 1** | Weeks 1-2 | `codex-lite-0.1.0` | LOW (1-2 days) | ✓ LOW |
| **Phase 2** | Weeks 3-5 | `codex-0.1.0` | MEDIUM (5-10 days) | 🟡 MEDIUM (decoupling) |
| **Phase 3** | Weeks 6-10 | `codex-ml-0.1.0` | HIGH (10-15 days) | 🔴 HIGH (PyTorch churn) |
| **Phase 4** | Weeks 11-13 | `codex-services-0.1.0` | MEDIUM (5-10 days) | 🟡 MEDIUM (HTTP resilience) |
| **Phase 5** | Weeks 14-16 | Archive/deprecate | LOW (2-3 days) | ✓ LOW |

**Total effort:** 40-60 engineering days  
**Team size:** 2-3 senior engineers + 1 QA  
**Timeline:** 16 weeks (Aug-Nov 2026)  

---

## Success Metrics

By end of Phase 5:

- ✓ 4 separate PyPI packages (lite, core, ml, services)
- ✓ LITE installs in <5s; CORE in 20s; ML in 60s
- ✓ All APIs documented with OpenAPI/examples
- ✓ Windows CI green (LITE + CORE verified)
- ✓ AAIS scores all ≥0.70
- ✓ Zero unresolved circular dependencies
- ✓ Integration tests pass (100% coverage for public APIs)
- ✓ External users can extend via entry points (e.g., custom skill types)

---

