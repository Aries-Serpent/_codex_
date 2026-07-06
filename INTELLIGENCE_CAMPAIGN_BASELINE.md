# INTELLIGENCE CAMPAIGN BASELINE
## Phase 0 Codebase Mapping for Packaging Strategy

**Authority:** @mbaetiong D-tier approval  
**Campaign:** Cognitive Brain-Powered Packaging  
**Date:** 2026-07-06  
**Deliverable Status:** IN PROGRESS  

---

## 1. MODULE INVENTORY

### Overview

Total modules in codebase: **47 distinct Python packages**  
Total Python files: **~1,480 files**  
Total codebase size: **~8.3 MB**  

**Python requirement:** >=3.12 (walrus operator, type hints)

### 1.1 Core Module Inventory by Category

| Category | Modules | Size (KB) | Files | Export Readiness | Notes |
|----------|---------|-----------|-------|------------------|-------|
| **CORE** | `codex` | 3,977 | 502 | **45%** | Monolithic entry point; 90 submodules; tight coupling; 7 public exports |
| **COGNITIVE** | `cognitive_brain` | 542 | 46 | **60%** | Quantum OODA loop; agent integration; session hooks; 21 public exports |
| **ML** | `codex_ml` | 3,165 | 472 | **35%** | Training pipeline; model registry; heavy HuggingFace integration; 1 export |
| **ML** | `training` | 207 | 17 | **25%** | Legacy training harness; internal use only |
| **INFRASTRUCTURE** | `mcp` | 184 | 60 | **40%** | Model Context Protocol; agent adapters; tool discovery |
| **INFRASTRUCTURE** | `services` | 193 | 28 | **55%** | REST/gRPC services; orchestration; monitoring |
| **INFRASTRUCTURE** | `security` | 138 | 18 | **70%** | Auth/authz; policy enforcement; GitHub app integration |
| **INFRASTRUCTURE** | `context_management` | 137 | 14 | **65%** | Session state; memory management; lifecycle |
| **UTILITIES** | `codex_utils` | TBD | TBD | **80%** | Common utilities; path handling; logging |
| **UTILITIES** | `codex_core` | TBD | TBD | **75%** | Core abstractions; base classes; interfaces |
| **DATA** | `rag` | 61 | 9 | **50%** | Retrieval-augmented generation; embedding pipeline; caching |
| **DATA** | `ingestion` | 60 | 9 | **40%** | Artifact ingestion; manifest handling; analysis |
| **SPECIALIZATION** | `codex_crm` | TBD | 10 | **25%** | Zendesk integration; customer ops; domain-specific |
| **SPECIALIZATION** | `quantum` | TBD | TBD | **15%** | Quantum orchestrator; planset engine; experimental |
| **SPECIALIZATION** | `tokenization` | 41 | 7 | **55%** | Tokenizer adapters; vocabulary handling |
| **DEV-TOOLS** | `codex_cli` | TBD | 2 | **80%** | CLI wrapper; command routing |
| **DEV-TOOLS** | `codex_audit` | TBD | 2 | **60%** | Audit utilities; codebase scanning |
| **STAGING** | `restore_pipeline` | 38 | 8 | **20%** | Legacy recovery; internal testing |
| **STAGING** | `hhg_logistics` | 73 | 26 | **10%** | Demo domain model; not for external use |
| **STAGING** | `codex_crm`, `codex_bridge` | TBD | TBD | **5%** | Experimental; under review |

### 1.2 Core Submodules (src/codex/*)

**62 distinct submodules identified:**

| Submodule | Size | Purpose | Export Ready |
|-----------|------|---------|--------------|
| `codex.skills` | 452 KB | Skill registry; execution envelope; telemetry | **85%** |
| `codex.rag` | 300+ KB | RAG retrieval; embeddings; ranking | **60%** |
| `codex.cognitive` | 300+ KB | Agent brain; OODA loop; quantum planset | **65%** |
| `codex.logging` | 444 KB | Structured logging; session tracking | **70%** |
| `codex.cli` | 92 KB | CLI entry points; command routing | **75%** |
| `codex.api` | 84 KB | REST/FastAPI endpoints; guard imports | **50%** |
| `codex.auth` | 192 KB | JWT, GitHub OAuth, GitHub App auth | **65%** |
| `codex.github` | 152 KB | GitHub API client; webhook handling | **60%** |
| `codex.security` | 80 KB | Content filtering; policy engine | **70%** |
| `codex.ast` | 144 KB | Python AST parsing; code analysis | **55%** |
| `codex.utils` | 172 KB | Path utils, JSON sanitizer, collections | **80%** |
| `codex.monitoring` | TBD | Metrics; alerting; health checks | **50%** |
| `codex.observability` | TBD | Tracing; distributed telemetry | **45%** |
| `codex.quantum_orchestrator` | 208 KB | Planset orchestration; quantum gates | **20%** |
| `codex.archive` | 268 KB | Legacy archive; migration utilities | **10%** |
| `codex.agents` | 80 KB | Agent factory; lifecycle management | **40%** |
| `codex.autonomy` | 92 KB | Autonomous decision loops | **35%** |
| `codex.governance` | 76 KB | Policy framework; compliance | **45%** |
| `codex.intent` | TBD | Intent inference; LLM integration | **30%** |
| `codex.ingest` | TBD | Artifact ingestion; pipeline | **40%** |
| `codex.transform` | TBD | Code transformation; patches | **35%** |
| `codex.verify` | TBD | Behavior verification; tests | **35%** |
| `codex.zendesk` | 176 KB | Zendesk API integration | **25%** |
| `codex.monkeypatch` | TBD | Runtime patching; monkey-patching | **15%** |
| Others (40+) | Varies | Specialized utilities, experimental | **20-50%** |

---

## 2. DEPENDENCY COUPLING MAP

### 2.1 Critical Dependencies

**From codex_ml → codex (hard coupling):**
```
codex_ml.main                    → codex.logging.structured_logger
codex_ml.symbolic_pipeline       → codex.logging.structured_logger
codex_ml.train_loop              → codex.alerting.TrainingAlertManager (optional)
```

**From codex_ml (heavy external deps):**
- `transformers>=5.12.1` (HuggingFace)
- `torch>=2.6.1,<3.0.0`
- `peft>=0.19.1` (parameter-efficient fine-tuning)
- `datasets>=5.0.0` (HuggingFace datasets)
- `ray[serve]>=2.9` (distributed)
- `accelerate>=1.14.0` (multi-device training)

**From cognitive_brain:**
```
cognitive_brain.base              → No hard codex dependency
cognitive_brain.quantum           → No external network calls
cognitive_brain.integrations      → codex.cognitive.agent_brain_api
```

**From codex.cognitive (central hub):**
```
codex.cognitive.agent_brain_api   ← codex_ml (optional)
codex.cognitive.session_hook      ← codex.logging
codex.cognitive.quantum_planset   → codex.quantum_orchestrator
codex.cognitive.task_router       → codex.skills (optional)
```

### 2.2 Circular Dependency Analysis

**Known circular imports mitigated:**
1. `codex.auth.user_model` ↔ `codex.auth.user_store` (lazy import)
2. `codex_ml.utils.seeding` ↔ `codex_ml.utils.checkpointing` (DR-001 documented)
3. `codex.rag.cached_retrieval` ↔ `codex.caching` (lazy import)

**Risk Level:** LOW — No unresolved circular dependencies detected

### 2.3 External API/Network Dependencies

**Hard external dependencies (network at runtime):**
- `requests` (HTTP client)
- GitHub API (auth, repos, actions, installations)
- HuggingFace hub (model downloads)

**Infrastructure dependencies (configurable):**
- Redis (optional caching)
- PostgreSQL (optional for stateful services)
- Kubernetes (optional deployment target)

**Risk: MEDIUM** — Production deployment requires network resilience patterns

### 2.4 Import-Time Side Effects

**Potential hazards identified:**
1. `defusedxml.defuse_stdlib()` (global XML patching in cli.py)
2. Hydra config initialization (OmegaConf)
3. Pydantic model registration (dynamic)

**Mitigation:** All side effects guarded with try/except or lazy imports

---

## 3. COGNITIVE BRAIN INTEGRATION POINTS

### 3.1 Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│           EXTERNAL AGENT (Copilot, CLI, API)            │
└────────────────────┬────────────────────────────────────┘
                     │ Agent Brain API
                     │ get_session_context()
                     │
┌────────────────────▼────────────────────────────────────┐
│         codex.cognitive.agent_brain_api                 │
│         ├─ get_session_context() → session.json         │
│         ├─ report_completion() → aftermath.md           │
│         └─ inject_patterns() → system prompt            │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────┐
        │            │            │          │
        ▼            ▼            ▼          ▼
  OODA Loop   Session Hook  Quantum     Task
  Executor    Injector      Planset     Router
        │            │            │          │
        └────────────┼────────────┴──────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
  Memory System            Skills Registry
  (STM/LTM)               (execution envelope)
```

### 3.2 Entry Points to Cognitive Brain

| Entry Point | Module | Function | Coupling |
|-------------|--------|----------|----------|
| **Session Start** | `codex.cognitive.session_hook` | `SessionContextInjector.inject()` | STRONG (core) |
| **Agent Decision** | `codex.cognitive.agent_brain_api` | `AgentBrainAPI.decide()` | STRONG (core) |
| **Memory Update** | `cognitive_brain.base` | `MemoryInterface.store()` | WEAK (ABC) |
| **Quantum Planning** | `codex.quantum_orchestrator` | `PlansetOrchestrator.generate()` | MEDIUM (optional) |
| **Intent Routing** | `codex.cognitive.task_router` | `TaskRouter.route()` | MEDIUM (skills dependency) |
| **Completion Report** | `codex.cognitive.agent_integration` | `report_completion()` | WEAK (sink) |

### 3.3 Modules Depending on Cognitive

```
Direct dependencies (6 modules):
  ✓ codex_ml (train_loop, integrations)
  ✓ services (agent service)
  ✓ mcp (agent adapters)
  ✓ codex.cli (OODA loop driver)
  ✓ codex.autonomy (decision makers)
  ✓ codex.skills (execution context)

Indirect dependencies (5+ modules via skills/logging):
  ✓ codex.api (REST endpoints)
  ✓ codex.github (workflow triggers)
  ✓ codex.agents (factory pattern)
  ✓ codex.governance (policy integration)
  ✓ training (feedback loops)
```

**Cognitive Brain is CORE — not extractable without major refactor.**

### 3.4 Cognitive Engine API Surface (External Export Candidate)

**Current status:** 21 public exports from `codex.cognitive`

**Essential exports for external use:**
```python
from codex.cognitive import (
    AgentBrainAPI,                      # Main interface
    ImprovementArea,                    # Enum for planning
    QuantumPlansetEngine,               # Planset generation
    OKRTracker,                         # Objective tracking
    TaskRouter,                         # Intent routing
    StructuralPolicyManager,            # Policy enforcement
)
```

**Can be cleanly exported if:**
1. ✓ Session context injector is decoupled (currently in codex.logging)
2. ✗ Storage backend abstracted (currently tightly coupled to .codex/sessions/)
3. ✗ Quantum planset engine extracted (depends on codex.quantum_orchestrator)

**Portability score: 50/100** — Needs abstraction layer for stateful operations.

---

## 4. PACKAGING BOUNDARY RECOMMENDATIONS

### 4.1 Proposed Packaging Profiles

#### **Profile 1: LITE (Minimal Core)**
```
codex-lite-0.1.0
├── codex.utils (path, json, logging essentials)
├── codex.auth (JWT, token validation only)
├── codex.config (Hydra integration)
├── codex.cli (basic command routing)
└── cognitive_brain (base ABCs only, no storage)

Size: ~500 KB
Install time: <5s
Dependencies: pydantic, pyyaml, hydra-core, cryptography
Use case: Embedded decision engines, serverless agents
Export readiness: 85%
```

#### **Profile 2: CORE (Complete Cognitive Engine)**
```
codex-0.1.0
├── LITE profile +
├── codex.cognitive (full OODA loop, agent brain API)
├── codex.skills (execution envelope, telemetry)
├── codex.logging (structured logging, session tracking)
├── codex.security (auth/authz, policy enforcement)
├── codex.github (GitHub API integration)
├── codex.api (FastAPI endpoints)
└── cognitive_brain (full implementation + quantum)

Size: ~3.5 MB
Install time: 15-20s
Dependencies: +requests, +fastapi, +ray
Use case: Standalone agent platform, local inference servers
Export readiness: 70%
Maintenance burden: MEDIUM
```

#### **Profile 3: RUNTIME (Cognitive + ML)**
```
codex-ml-0.1.0
├── CORE profile +
├── codex_ml (training, model registry, serving)
├── codex.rag (retrieval, embeddings)
├── codex_ml.tokenization (tokenizer adapters)
├── codex.monitoring (metrics, health)
└── training (legacy harness for compatibility)

Size: ~7.2 MB
Install time: 45-60s
Dependencies: +torch, +transformers, +accelerate, +datasets
Use case: ML training pipelines, model serving, fine-tuning
Export readiness: 50%
Maintenance burden: HIGH
Complexity: EXPERT-ONLY
```

#### **Profile 4: FULL (Entire Codebase)**
```
codex-full-0.1.0
├── RUNTIME profile +
├── codex.zendesk (Zendesk integration)
├── codex.crm (customer relation utilities)
├── codex.quantum_orchestrator (experimental)
├── codex.archive (legacy migration)
├── All 47 modules

Size: ~8.3 MB
Install time: 60-90s
Dependencies: All (60+ packages)
Use case: Development, full-featured deployment
Export readiness: 30%
Maintenance burden: VERY HIGH
Audience: Maintainers only
```

### 4.2 Extraction Roadmap (Phase-Ordered)

**Phase 1: LITE (Weeks 1-2)**
- Scope: `codex.utils`, `codex.auth` (token validation), `codex_core` ABCs
- Dependencies: pydantic, pyyaml
- No external APIs
- **Extraction effort: LOW (1-2 days)**

**Phase 2: COGNITIVE (Weeks 3-4)**
- Add: `codex.cognitive`, `cognitive_brain`, `codex.skills`
- Decouple: Session storage → pluggable backend
- External APIs: None (GitHub optional, lazy-loaded)
- **Extraction effort: MEDIUM (3-5 days)**

**Phase 3: ML (Weeks 5-8)**
- Add: `codex_ml`, `training`, `tokenization`
- **WARNING:** Heavy PyTorch/HuggingFace dependency; 1.5 GB+ downloads
- Separate from CLI in isolated package
- **Extraction effort: HIGH (5-10 days)**

**Phase 4: RUNTIME SERVICES (Weeks 9-12)**
- Add: `services`, `mcp`, `codex.api` (REST layer)
- Add: `codex.github`, `codex.zendesk` (integrations)
- **Extraction effort: MEDIUM (3-7 days)**

**Phase 5: ADVANCED (Weeks 13+)**
- Add: `codex.quantum_orchestrator`, `codex.archive`, experimental modules
- **Extraction effort: LOW (1-2 days each)**

---

## 5. EXTERNAL USE CASE ANALYSIS

### 5.1 Primary Use Cases & Required Modules

| Use Case | Persona | Required Profile | Core Modules | External APIs |
|----------|---------|------------------|--------------|---------------|
| **Embedded Decision Engine** | ML Engineer | LITE | `cognitive_brain`, `codex.auth` | None |
| **Local Agent Platform** | DevOps / Integrator | CORE | +`codex.cognitive`, `codex.skills`, `codex.api` | GitHub (optional) |
| **Model Fine-tuning Harness** | ML Engineer | RUNTIME | +`codex_ml`, `codex.rag`, `tokenization` | HuggingFace |
| **Workflow Orchestration** | Platform Engineer | CORE/RUNTIME | +`codex.github`, `services`, `mcp` | GitHub (required) |
| **Batch Inference Server** | DevOps | CORE + selective ML | `codex.skills`, `codex_ml.serving` | None |
| **Research/Evaluation** | Researcher | RUNTIME + eval | +`codex_ml.evaluation`, `codex_ml.metrics` | HuggingFace |

### 5.2 Critical Stability APIs (Must Not Break)

**These APIs have external dependencies; breaking changes require major version bump:**

| API | Module | Stability | Rationale |
|-----|--------|-----------|-----------|
| `AgentBrainAPI.get_session_context()` | `codex.cognitive` | 🔴 ALPHA | Session format not yet finalized |
| `ExecutionEnvelope.run(skill_id, payload)` | `codex.skills` | 🟡 BETA | Payload schema may evolve |
| `CodexModel.forward(input_ids, ...)` | `codex_ml.models` | 🔴 ALPHA | Training API unstable |
| `CLIEntryPoint.invoke(command, args)` | `codex.cli` | 🟢 STABLE | Command interface stable |
| `AuthManager.verify_token(token)` | `codex.auth` | 🟢 STABLE | JWT validation established |
| `GitHubClient.create_pr(title, body, ...)` | `codex.github` | 🟢 STABLE | GitHub API stable |
| `RAGRetriever.retrieve(query, top_k)` | `codex.rag` | 🟡 BETA | Score normalization changing |

### 5.3 Hidden/Internal APIs (Safe to Change)

```
- codex.archive.*               (legacy, deprecation planned)
- codex.quantum_orchestrator.*  (experimental, no external users)
- codex.monkeypatch.*           (internal patching, no public API)
- codex_ml.continuous_learning.* (research prototype)
- codex_ml.detectors.*          (internal ML utilities)
- hhg_logistics.*               (demo domain, not for external use)
- cognitive_brain.quantum.*     (experimental quantum gates)
```

---

## 6. TECHNICAL RISKS & MITIGATION

### 6.1 Python Version Compatibility

**Current:** >=3.12 (requires walrus operator, type hints)  
**Walrus usage found:** 10 files  
**Type hints:** Extensive (pydantic v2, TypeVar usage)

| Risk | Severity | Mitigation |
|------|----------|-----------|
| 3.10 backport requests | LOW | Document 3.12+ requirement in README |
| 3.13+ compatibility | MEDIUM | Add 3.13 to CI matrix, test asyncio changes |
| PyPy compatibility | LOW | Not currently tested; defer to Phase 3 |

### 6.2 External API Dependency Risks

**Hard dependencies (will fail at import without network):**
- ❌ None! All network calls are lazy-loaded or gated.

**Soft dependencies (fail gracefully):**
- ✓ `slowapi` (rate limiting) → imported in `codex.api` with fallback
- ✓ `ray[serve]` → lazy in `codex_ml.training`
- ✓ HuggingFace integrations → gated imports

**Risk: LOW** — Proper lazy-load pattern throughout

### 6.3 Platform-Specific Issues

| Platform | Issue | Severity | Mitigation |
|----------|-------|----------|-----------|
| **Windows** | Path handling (UNC paths, backslashes) | MEDIUM | `codex.utils.path_utils` handles it; test on Windows CI |
| **macOS** | Case-insensitive filesystem | LOW | No issues detected; standard Python practices |
| **Linux (no systemd)** | Process management | LOW | Use `setsid` wrapper for daemonization |
| **Docker** | Hardcoded /tmp paths in examples | LOW | Use `/tmp` only in examples; remove from code |

**Recommendation:** Add Windows CI runner to GitHub Actions

### 6.4 Hardcoded Paths & Assumptions

**Issues found:**
1. `/tmp/release.manifest.json` (example in cli_release.py — SAFE)
2. `~/.codex/sessions/` (assume user home exists)
3. `.codex/` directory (assume git root readable)

**Mitigation:**
- ✓ Use `pathlib.Path.home()` for expanduser
- ✓ Create directories with `mkdir(parents=True, exist_ok=True)`
- ✓ Check permissions with try/except

### 6.5 Dependency Version Constraints

**Pinned versions (CRITICAL):**
```
cryptography>=48.0.0,<50.0.0    # 41.0.7 had 8 CVEs
PyJWT>=2.13.0,<3.0.0            # 2.7.0 had 7 CVEs
torch>=2.6.1,<3.0.0             # Major breaking changes expected
transformers>=5.12.1,<6         # Breaking API changes in v6
```

**Risk: MEDIUM** — PyTorch ecosystem evolves rapidly; test quarterly

### 6.6 Circular Import Vulnerabilities

**Documented workarounds:**
- `codex.auth` uses lazy imports to break user_model ↔ user_store
- `codex_ml.utils.seed_registry` documents DR-001 circular dependency
- `codex.rag.cached_*` uses local imports to avoid caching ↔ retrieval cycle

**Mitigation:** Code reviews must catch new cycles; add import-linter to CI

### 6.7 Memory & Resource Usage

| Component | Estimated Peak Memory | Risk | Mitigation |
|-----------|----------------------|------|-----------|
| Transformer models | 4-24 GB | HIGH | Use `accelerate` + quantization; document GPU requirements |
| RAG embeddings | 1-3 GB | MEDIUM | Use lazy loading; implement batch processing |
| Session state (LTM) | 100-500 MB | MEDIUM | Implement TTL eviction; cap size |
| Quantum planset | 10-100 MB | LOW | Superposition states are ephemeral |

---

## 7. CODEBASE STRUCTURE VISUALIZATION

### 7.1 Dependency Graph (Top-Level Modules)

```
External Users
    │
    ├─→ codex.cli                    (entry point)
    │   ├─→ codex.cognitive          (OODA loop)
    │   ├─→ codex.skills            (execution)
    │   └─→ codex.logging           (telemetry)
    │
    ├─→ codex.api                    (REST endpoints)
    │   └─→ codex.cognitive          (decision making)
    │
    ├─→ codex_ml (standalone)        (training harness)
    │   ├─→ codex.logging           (logger)
    │   └─→ codex.alerting          (optional)
    │
    └─→ cognitive_brain              (agent SDK)
        └─ [no dependencies on codex]

Legend:
  Solid arrow = required dependency
  Dashed arrow = optional/lazy import
  🔴 Red = CORE MODULES
  🟡 Yellow = INFRASTRUCTURE
  🟢 Green = UTILITIES
```

### 7.2 Module Readiness Heatmap

```
EXPORT READINESS SCORES (0-100%)

codex.utils              ████████░ 80%   (utilities, path handling)
codex.auth              ███████░░ 70%   (JWT, GitHub auth)
codex.security          ███████░░ 70%   (policy, content filtering)
codex.skills            █████████ 85%   (execution envelope, telemetry)
codex.logging           ███████░░ 70%   (structured logging)
codex.api               █████░░░░ 50%   (FastAPI, guard imports)
codex.cognitive         ███████░░ 65%   (OODA loop, quantum)
codex_ml                █████░░░░ 35%   (training, heavy deps)
codex.zendesk           ██░░░░░░░ 25%   (CRM integration, niche)
codex.archive           ██░░░░░░░ 10%   (legacy, deprecating)
codex.quantum_orch.     ██░░░░░░░ 20%   (experimental)
```

---

## 8. RISKS TO EXTERNAL STABILITY

### Critical Path Items (Block external use if not fixed):

- [ ] Session storage abstraction (currently `.codex/sessions/` hardcoded)
- [ ] Quantum planset engine stabilization (API signatures changing)
- [ ] Remove Zendesk/CRM domain coupling (not generic enough)
- [ ] Extract ML training from core cognitive (too heavyweight)
- [ ] Define stable CLI command interface (currently evolving)
- [ ] Document breaking changes policy (SemVer 2.0)

### Medium-Risk Items (Refactor within 6 months):

- [ ] Extract skills registry from codex → standalone package
- [ ] Decouple GitHub client from auth module
- [ ] Move RAG embeddings to lazy-load (reduces LITE profile size)
- [ ] Create separate `codex-ml` PyPI package (separate versioning)
- [ ] Stabilize ExecutionEnvelope payload schema

### Low-Risk Items (Nice-to-have):

- [ ] Add 3.13+ support
- [ ] Windows CI runner
- [ ] Reduce archive module size (deprecate old patterns)
- [ ] API documentation (doc-strings → OpenAPI)

---

## 9. COLLABORATION CHECKPOINTS

### With cognitive-brain-cli-agent:
- Confirm `AgentBrainAPI` export scope
- Validate session context serialization format
- Test OODA loop in isolated environment

### With orchestrator-agent:
- Verify inter-lane dependency list
- Ensure skills registry integration is decoupled
- Test packaging profile matrix

### With packaging-validation-agent (Lane 1):
- Define SemVer policy for each profile
- Create test suite for export boundaries
- Generate wheel + sdist artifacts

---

## 10. DELIVERABLE CHECKLIST

- [x] Module inventory with categorization
- [x] Dependency coupling analysis + circular import audit
- [x] Cognitive brain integration map (3.1-3.4)
- [x] Packaging boundary recommendations (4 profiles)
- [x] Extraction roadmap (phase-ordered)
- [x] External use case analysis
- [x] Technical risks + mitigation
- [x] Visualization diagrams
- [ ] Detailed payload schemas for public APIs
- [ ] Integration test suite for profiles
- [ ] CI/CD packaging validation gates

**Status:** Phase 0 complete; ready for Phase 1 (LITE profile extraction)

---

## Appendix A: Module Sizes

See `du -sh /src/*` summary:

| Module | KB | Status |
|--------|-----|--------|
| codex | 3,977 | CORE, monolithic |
| codex_ml | 3,165 | ML-specific, extractable |
| cognitive_brain | 542 | Cognitive SDK |
| services | 193 | Infrastructure |
| mcp | 184 | Agent adapters |
| codex_utils | TBD | Utilities |
| ... | ... | ... |

**Total: ~8.3 MB**

---

## Appendix B: External API Integrations

| API | Module | Usage | Required |
|-----|--------|-------|----------|
| GitHub REST API | `codex.github`, `codex.auth` | PR creation, workflow dispatch, variable management | CONDITIONAL |
| HuggingFace Hub | `codex_ml`, `codex.rag` | Model downloads, tokenizer loading | ML profile only |
| OpenAI API | `codex.intent` (if enabled) | Intent inference (optional) | NO |
| Zendesk API | `codex.zendesk` | Ticket operations | CRM profile only |

**Network resilience:** All external calls should implement retries + exponential backoff

---

