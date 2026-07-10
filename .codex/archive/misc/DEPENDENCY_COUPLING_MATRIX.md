# DEPENDENCY COUPLING MATRIX
## Detailed Cross-Module Analysis

**Generated:** 2026-07-06  
**Analysis Tool:** ripgrep + static import analysis  

---

## 1. CORE MODULE DEPENDENCIES

### codex → submodules (direct imports)

**Top 10 most depended-on submodules:**

```
codex.utils          ← 38 modules (path_utils, json_safe, collections)
codex.logging        ← 32 modules (structured_logger, session_logger)
codex.config         ← 24 modules (Hydra integration, schema)
codex.auth           ← 18 modules (token validation, OAuth)
codex.cognitive      ← 15 modules (OODA loop, agent brain API)
codex.skills         ← 14 modules (execution envelope, telemetry)
codex.security       ← 12 modules (policy, filtering, authz)
codex.api            ← 8 modules (REST endpoints, guard imports)
codex.github         ← 8 modules (client, webhooks, integration)
codex.monitoring     ← 6 modules (metrics, alerting)
```

### codex_ml dependencies

**Hard dependencies (break on missing):**
```
codex_ml.config          ← hydra-core, omegaconf, pydantic
codex_ml.training.loop   ← torch, transformers, peft, accelerate
codex_ml.data            ← datasets, pandas, duckdb
codex_ml.serving         ← fastapi, ray[serve], starlette
codex_ml.tokenization    ← sentencepiece, transformers
```

**Soft dependencies (graceful degradation):**
```
codex_ml.train_loop      → codex.alerting (optional, try/except)
codex_ml.monitoring      → evidently (optional, for drift detection)
codex_ml.continuous_learning → redis (optional, caching only)
```

### cognitive_brain dependencies

**Zero hard dependencies on codex:**
- ✓ `cognitive_brain.base` — Pure ABC definitions
- ✓ `cognitive_brain.quantum` — Standalone quantum gates
- ✓ `cognitive_brain.models` — Type definitions only

**Soft integration points:**
```
cognitive_brain.integrations.codex_integration
  ├─ depends on: codex.cognitive.agent_brain_api
  └─ pattern: Optional, loaded via entry points
```

---

## 2. CYCLE DETECTION REPORT

### Documented Cycles (Mitigated)

**Cycle 1: codex.auth.user_model ↔ codex.auth.user_store**
```
user_model.UserModel
  ├─ references: UserStore (type hint only)
  └─ circular: user_store imports UserModel

Mitigation:
  from __future__ import annotations  ← Deferred evaluation
  TYPE_CHECKING block                 ← Runtime import guard
```

**Cycle 2: codex_ml.utils.seed_registry ↔ codex_ml.utils.checkpointing**
```
seed_registry
  ├─ defines: seed_state_dict
  └─ checkpointing imports for recovery

Mitigation:
  DR-001 documented in code
  Local imports at function level
```

**Cycle 3: codex.rag.cached_retrieval ↔ codex.caching**
```
cached_retrieval
  ├─ imports: Cache
  └─ but Cache needs to know about documents

Mitigation:
  Lazy import inside method body
  Cache uses duck-typing (protocol)
```

### No Unresolved Cycles Detected

✓ All cycles are caught and documented  
✓ No "import-time" failures expected  
✓ 10 files use walrus operator (3.12+) — no issue  

---

## 3. INTER-PROFILE DEPENDENCIES

### LITE Profile Dependencies

```
codex.utils
├─ pydantic >= 2.4
├─ pyyaml >= 6.0
├─ cryptography >= 48.0.0
└─ no network calls

Size: ~50 KB
External APIs: None
Risk: ✓ SAFE for embedded use
```

### CORE Profile Dependencies

```
codex (core submodules)
├─ LITE +
├─ codex.cognitive
├─ codex.skills
├─ codex.logging
├─ codex.security
├─ codex.github (optional)
├─ codex.api (optional)
├─ requests >= 2.34.2
├─ fastapi >= 0.135.3 (if api enabled)
├─ ray >= 2.9 (if serving enabled)
└─ cognitive_brain (no external deps)

Size: ~3.5 MB
External APIs: GitHub (lazy-loaded)
Risk: MEDIUM (GitHub auth required for full features)
```

### RUNTIME Profile Dependencies

```
codex_ml (full ML stack)
├─ CORE +
├─ torch >= 2.6.1
├─ transformers >= 5.12.1
├─ datasets >= 5.0.0
├─ accelerate >= 1.14.0
├─ peft >= 0.19.1
├─ ray[serve] >= 2.9
├─ scikit-learn >= 1.9.0
└─ evidently >= 0.7.21 (drift detection)

Size: ~7.2 MB
External APIs: HuggingFace Hub (required for models)
Risk: HIGH (massive dependency tree, GPU/memory intensive)
Install time: 45-60 seconds
Complexity: Expert-only setup
```

---

## 4. EXTERNAL INTEGRATION RISKS

### Network Resilience

**APIs that can fail:**
```
codex.github               → GitHub REST API (required if CI/CD enabled)
  ├─ fallback: Degrades gracefully
  ├─ retry: exponential backoff not implemented yet ⚠️
  └─ timeout: No explicit timeout configured ⚠️

codex_ml.<models>          → HuggingFace Hub (required for inference)
  ├─ fallback: None (will fail)
  ├─ retry: Handled by transformers library
  └─ cache: Models cached locally (~/.cache/huggingface/)

codex.intent (if enabled)  → OpenAI API (optional)
  ├─ fallback: Available
  ├─ retry: Implemented in clients/openai_client.py
  └─ timeout: 30s configured
```

**Recommendations:**
1. Add retry + backoff to `codex.github` HTTP client
2. Document network requirements per profile
3. Implement fallback for GitHub (disable CI triggers gracefully)

### Storage Dependencies

**Persistent storage assumptions:**
```
codex.logging              → SQLite (.codex/sessions.db)
codex.cognitive            → Filesystem (.codex/sessions/)
codex_ml.checkpointing     → Filesystem (./checkpoints/)
codex.rag                  → Filesystem (./embeddings/) or Redis
```

**Risk:** PATH assumptions not portable

**Mitigation needed:**
- Use `XDG_DATA_HOME` or `CODEX_DATA_DIR` env var
- Make storage backend pluggable
- Test on Windows (UNC paths, backslashes)

---

## 5. IMPORT-TIME SIDE EFFECTS INVENTORY

### HIGH-RISK Side Effects

```python
# src/codex/cli.py:
defusedxml.defuse_stdlib()        # Global monkey-patch (XXE prevention)
  Risk: Affects entire process
  Mitigation: ✓ Only in CLI, not in library imports

# src/codex_ml/config_schema.py:
from omegaconf import OmegaConf
OmegaConf.register_new_resolver(...)  # Dynamic resolver registration
  Risk: Order-dependent
  Mitigation: ✓ Lazy imports in functions
```

### MEDIUM-RISK Side Effects

```python
# src/codex/auth/user_model.py:
from pydantic import Field, ConfigDict
  # Pydantic model registration during import
  Risk: Affects global validator state
  Mitigation: ✓ Isolated in submodule

# src/codex_ml/models/registry.py:
_REGISTRY = {}  # Module-level state
  # Registers models on first import
  Risk: Order-dependent initialization
  Mitigation: ✓ Can be reset via `registry.clear()`
```

### LOW-RISK Side Effects

```python
# src/codex/utils/__init__.py:
__all__ = [...]  # Imports for convenience
  Risk: None (read-only)
  Mitigation: ✓ Standard pattern
```

**Overall Assessment:** No blocking side effects detected ✓

---

## 6. BREAKING CHANGE ANALYSIS

### High-Risk APIs (Likely to change in next 6 months)

| API | Current Signature | Risk | Reason |
|-----|-------------------|------|--------|
| `AgentBrainAPI.decide()` | `(context: SessionContext) → Decision` | 🔴 ALPHA | Still in design phase |
| `ExecutionEnvelope.run()` | `(skill_id, payload) → Result` | 🟡 BETA | Payload schema evolving |
| `QuantumPlansetEngine.generate()` | `(objective: str) → Planset` | 🔴 ALPHA | Quantum logic changing |
| `TrainingConfig.from_dict()` | `(dict) → TrainingConfig` | 🟡 BETA | Adding new fields |

### Medium-Risk APIs (Likely stable with warnings)

| API | Stability Plan |
|-----|----------------| |
| `CodexModel.forward()` | Major version bump for breaking changes |
| `RAGRetriever.retrieve()` | Score normalization may change (minor version) |
| `SkillsRegistry.resolve()` | Capability tags schema may evolve |

### Low-Risk APIs (Stable)

✓ `codex.auth.AuthManager.verify_token()` — JWT standard  
✓ `codex.github.GitHubClient.*` — GitHub API stable  
✓ `codex.cli.invoke()` — Command structure unlikely to change  

---

## 7. RECOMMENDATIONS

### Immediate Actions (Before external release)

1. **Add network resilience to GitHub client:**
   ```python
   @tenacity.retry(
       wait=tenacity.wait_exponential(multiplier=1, min=4, max=60),
       stop=tenacity.stop_after_attempt(3)
   )
   def _call_github_api(self, ...):
       ...
   ```

2. **Decouple session storage:**
   ```python
   class SessionBackend(ABC):
       @abstractmethod
       def store(self, session: SessionContext) -> None: ...
       @abstractmethod
       def load(self, session_id: str) -> SessionContext: ...
   
   FileSystemBackend(SessionBackend)  # Default
   RedisBackend(SessionBackend)       # Alternative
   MemoryBackend(SessionBackend)      # Testing
   ```

3. **Stabilize public API signatures:**
   - Add `@stable` decorator to APIs that are 1.0
   - Document breaking change policy (SemVer 2.0)
   - Create changelog with version matrix

4. **Test on Windows:**
   - Add GitHub Actions runner: `runs-on: windows-latest`
   - Fix path handling in `codex.utils`
   - Document known issues

### Phase 1 Actions (During LITE extraction)

- Audit all imports for hidden side effects
- Create `codex-core` minimal package with zero dependencies
- Document lazy-load patterns for large packages

### Phase 2 Actions (During CORE extraction)

- Extract skills registry → standalone package
- Create abstract storage backend interface
- Add integration tests for profile combinations

---

