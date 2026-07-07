# PHASE 1: PACKAGING ARCHITECTURE VALIDATION REPORT

**Baseline:** PR #5231 merged at SHA `2819b45e`  
**Date:** 2026-07-06  
**Status:** ⚠️ **FAILING** — 25 issues identified (5 CRITICAL, 8 HIGH, 12 MEDIUM)  
**Recommendation:** Do NOT release external package until critical issues resolved.

---

## EXECUTIVE SUMMARY

The intended 3-profile packaging strategy (**core 8-15MB | runtime 20-35MB | full 100+MB**) is **not correctly implemented**. Core architectural issues prevent external consumption:

1. **Base dependencies include heavy ML packages** (torch, transformers, datasets) — defeats lightweight "core" profile
2. **5 entry points expose private functions** (_prefix) — public plugin interface depends on unstable APIs
3. **51 console scripts** spread across 8 modules — namespace pollution, poor discoverability
4. **Missing [project.urls]** — PyPI metadata incomplete
5. **2 example plugins missing** — EntryPoint loading will fail

The package **cannot be safely released** to external users until these are resolved.

---

## 1. PROFILE STRATEGY VALIDATION

### Status: ❌ INCOMPLETE / BROKEN

#### Issue PKG-001: Base Dependencies Include Heavy ML Packages [CRITICAL]

**Problem:**
```
Current base dependencies [project.dependencies]:
  torch>=2.6.1,<3.0.0           ← should be optional[ml]
  transformers>=5.12.1,<6       ← should be optional[ml]
  datasets>=5.0.0,<6            ← should be optional[ml]
  accelerate>=1.14.0,<2         ← should be optional[ml]
  + 7 others (omegaconf, hydra, pydantic, etc.)
```

**Impact:**
- **Core profile cannot exist** — base install already 200+MB
- Contradicts stated 8-15MB core target
- Forces users installing for scripting/APIs to download ML libraries they don't need
- Violates PEP 425 principle of lightweight core distributions

**Affected Components:**
- `torch>=2.6.1,<3.0.0` (122 MB)
- `transformers>=5.12.1,<6` (880 MB)
- `datasets>=5.0.0,<6` (150 MB)
- `accelerate>=1.14.0,<2` (45 MB)

**Recommendation:**
Move ML packages to `optional-dependencies` groups:
```toml
[project]
dependencies = [
    # CORE ONLY (keep under 50MB)
    "omegaconf>=2.3",
    "hydra-core==1.3.2",
    "pydantic>=2.4",
    "pydantic-settings>=2.14.2",
    "pyyaml>=6.0",
    "marshmallow>=3.7.1,<5",
    # (remove torch, transformers, datasets, accelerate)
]

[project.optional-dependencies]
ml = [
    "torch>=2.6.1,<3.0.0",
    "transformers>=5.12.1,<6",
    "datasets>=5.0.0,<6",
    "accelerate>=1.14.0,<2",
]
```

#### Issue PKG-002: No Explicit "Core" Profile [HIGH]

**Problem:**
- `test-core` exists (9 packages) but is test-oriented
- No `core` profile for production minimal installs
- Unclear which groups constitute "runtime" tier
- Users cannot opt-in to lightweight installation

**Current situation:**
```
[project.optional-dependencies]
test-core = [hydra-core, omegaconf, pytest, ...]  ← for testing
configs = [hydra-core, omegaconf, pyyaml]         ← incomplete
ml = [datasets, peft, transformers, torch, ...]   ← incomplete
all = [48 packages]                               ← all-in
```

**What's missing:**
```
[project.optional-dependencies]
core = [
    # Minimal: config, CLI parsing, auth
    "pydantic>=2.4",
    "typer>=0.12",
    "PyJWT>=2.13.0,<3.0.0",
]
runtime = [
    # ML: training, inference, evaluation
    # Include: core + ml + configs + analysis
]
```

**Recommendation:**
Define three explicit profiles in `[project.optional-dependencies]`:
1. **core:** Minimal (pydantic, typer, auth) — for scripting/APIs
2. **runtime:** Complete ML stack (core + ml + configs + eval) — for end users
3. **full:** Everything (runtime + dev + gpu + monitoring) — for development

---

#### Issue PKG-003: Impossible Size Targets [HIGH]

**Problem:**
Expected sizes cannot be achieved with current configuration:

| Profile | Expected | Actual | Gap |
|---------|----------|--------|-----|
| **core** | 8-15 MB | ~200 MB | ❌ torch alone is 122 MB |
| **runtime** | 20-35 MB | ~600 MB | ❌ torch+transformers alone |
| **full** | 100+ MB | ~1.2 GB | ⚠️ still feasible |

The base dependencies include torch (122 MB) and transformers (880 MB), making all profiles 3-10x larger than intended.

**Recommendation:**
See PKG-001 — move ML packages to optional groups.

---

## 2. ENTRY POINTS VALIDATION

### Status: ❌ FAILING (5 CRITICAL + additional issues)

#### Issue PKG-004: Private Functions in Public Entry Points [CRITICAL]

**Problem:**
Five entry points expose implementation-detail functions with `_prefix`:

| Group | Entry Point | Target | Status |
|-------|-------------|--------|--------|
| `codex_ml.tokenizers` | `hf` | `codex_ml.registry.tokenizers:_build_hf_tokenizer` | ❌ |
| `codex_ml.reward_models` | `heuristic` | `codex_ml.plugins.registries:_reward_model_heuristic` | ❌ |
| `codex_ml.models` | `minilm` | `codex_ml.models.registry:_build_minilm` | ❌ |
| `codex_ml.models` | `bert_base_uncased` | `codex_ml.models.registry:_build_default_bert` | ❌ |
| `codex_ml.trainers` | `functional` | `codex_ml.registry.trainers:_load_functional_trainer` | ❌ |

**Why this matters:**
- Python convention: `_prefix` = private/internal implementation
- Users building plugins on this interface **depend on unstable APIs**
- Any refactoring breaks external plugins with **no deprecation warning**
- Entry points should reference stable public APIs

**Example breakage scenario:**
```python
# User code (breaks silently if implementation changes)
from pkg_resources import load_entry_point
tokenizer = load_entry_point('codex-ml', 'codex_ml.tokenizers', 'hf')
```

**Recommendation:**

Create public wrapper functions in module's `__init__.py`:

```python
# codex_ml/registry/tokenizers.py
def _build_hf_tokenizer(...):
    """Internal implementation."""
    ...

def build_hf_tokenizer(...):
    """Public API for HuggingFace tokenizer factory.
    
    Stable entry point for plugin registration.
    """
    return _build_hf_tokenizer(...)

# pyproject.toml
[project.entry-points."codex_ml.tokenizers"]
hf = "codex_ml.registry.tokenizers:build_hf_tokenizer"  # ✓ public, no underscore
```

**Files to fix:**
- `src/codex_ml/registry/tokenizers.py` — add `build_hf_tokenizer`
- `src/codex_ml/models/registry.py` — add `build_minilm`, `build_default_bert`
- `src/codex_ml/plugins/registries.py` — add `reward_model_heuristic`
- `src/codex_ml/registry/trainers.py` — add `load_functional_trainer`

#### Issue PKG-005: Missing Example Plugins [HIGH]

**Problem:**
Two entry points reference non-existent modules:

```
[project.entry-points."codex_ml.plugins"]
hello = "examples.plugins.hello_plugin:HelloPlugin"              ← MISSING
token_accuracy_plugin = "examples.plugins.metrics_token_accuracy_plugin:TokenAccuracyPlugin"  ← MISSING
```

**Impact:**
- Any code calling `pkg_resources.load_entry_point('codex-ml', 'codex_ml.plugins', 'hello')` crashes
- Installation succeeds but plugin discovery fails at runtime
- If `examples/` is not included in sdist, `pip install codex-ml` fails

**Verification:**
```bash
$ ls examples/plugins/
# File not found ❌
```

**Recommendation:**

**Option A: Create example plugins**
```python
# examples/plugins/hello_plugin.py
from codex_ml.plugins.base import BasePlugin

class HelloPlugin(BasePlugin):
    """Example plugin that prints hello."""
    def execute(self, **kwargs):
        print("Hello from plugin!")
```

**Option B: Remove from entry points** (if examples are not production)
```toml
# pyproject.toml - remove these lines:
# hello = "examples.plugins.hello_plugin:HelloPlugin"
# token_accuracy_plugin = "examples.plugins.metrics_token_accuracy_plugin:TokenAccuracyPlugin"
```

**Recommendation:** Option B unless examples are part of published distribution.

#### Issue PKG-006: Excessive Console Scripts (51 entries) [MEDIUM]

**Problem:**
51 CLI commands spread across 8 different modules:

| Module | Count | Commands |
|--------|-------|----------|
| `tools` | 12 | docs-*, fence-check, etc. |
| `codex_ml` | 11 | codex-train, codex-eval, codex-ml, ... |
| `codex` | 10 | codex-audit, codex-analyze, codex-report, ... |
| `cli` | 9 | codex-setup, codex-patch-runner, ... |
| `hhg_logistics` | 6 | hhg-train, hhg-serve, hhg-monitor-*, ... |
| `codex_cli` | 1 | codex-smoke |
| `tokenization` | 1 | codex-tokenizer |
| `codex_utils` | 1 | codex-ndjson |

**Impact:**
- **Namespace pollution:** `codex-*` namespace has 28 commands
- **Discovery problem:** `codex --help` lists only one; users won't know about others
- **Maintenance burden:** Each new feature adds new script
- **Packaging issue:** Unclear which are "core" vs "optional"
- **External users confused:** "Which command should I use?"

**Example namespace conflict:**
```bash
codex                    # main CLI
codex-train              # machine learning
codex-eval               # evaluation
codex-analyze            # static analysis
codex-audit              # code audit
codex-report             # reporting
codex-import-ndjson      # data import (?)
...and 21 more
```

**Recommendation:**
Create a **hierarchical command structure** with subcommands:

```bash
# Current (polluted)
codex-train ...
codex-eval ...
codex-analyze ...

# Proposed (clean hierarchy)
codex train ...
codex eval ...
codex analyze ...
codex ml ...
codex tools ...
```

Update `[project.scripts]`:
```toml
[project.scripts]
# Primary entry point only
codex = "codex.cli:main"
codex-ml = "codex_ml.cli:main"     # ML subcommand group
codex-tools = "tools.cli:main"     # Tools subcommand group
codex-docs = "tools.docs_agent.cli:main"  # Docs subcommand group
```

Then use `typer`/`click` subcommands internally:
```python
# src/codex/cli.py
import typer
app = typer.Typer()

@app.command()
def train(...):
    """Train models."""
    pass

@app.command()
def eval(...):
    """Evaluate models."""
    pass

if __name__ == "__main__":
    app()  # $ codex train ... or $ codex eval ...
```

---

## 3. API STABILITY & PUBLIC SURFACE

### Status: ⚠️ WARNING — Multiple stability concerns

#### Issue PKG-007: Bloated __all__ Exports (30-48 items) [HIGH]

**Problem:**
Several key modules export excessive items in `__all__`, likely mixing stable and unstable APIs:

```python
# src/codex/auth/__init__.py
__all__ = [
    "User", "Role", "Permission", "authenticate", ...  # 48 items
    # Unknown which are stable vs. internal
]
```

| Module | Exports | Stability Risk |
|--------|---------|-----------------|
| `codex/auth/__init__.py` | 48 | ❌ HIGH — auth is critical, needs versioning |
| `codex/consolidation/__init__.py` | 47 | ❌ HIGH — large surface |
| `codex/cognitive/ml/__init__.py` | 42 | ⚠️ MEDIUM — ML unstable |
| `codex/skills/__init__.py` | 35 | ⚠️ MEDIUM — plugin system |
| `codex/zendesk/model/__init__.py` | 30 | ⚠️ MEDIUM — integration |

**Impact:**
- Users import `from codex.auth import *` and get 48 items
- Code breaks if ANY exported name changes (no semver protection)
- Difficult to deprecate old APIs (all exposed)
- IDE autocompletion bloated

**Recommendation:**

Audit each large `__all__` and split into tiers:

```python
# src/codex/auth/__init__.py - BEFORE (48 exports, unstable)
__all__ = ["User", "Role", "Permission", "authenticate", ...]

# AFTER - segregated by stability
__all__ = [
    # Public, stable API (v1.0+)
    "User",
    "authenticate",
    "TokenError",
]
# Internal/experimental - NOT in __all__, use _prefix
_experimental = ["Role", "Permission", ...]  # not exported
```

Actions:
1. Review each module with `len(__all__) > 10`
2. Identify <10 stable symbols for export
3. Move others to `_internal` or use function-level `_prefix`
4. Document deprecation policy (semver-aware)

#### Issue PKG-008: Missing [project.urls] [MEDIUM]

**Problem:**
No `[project.urls]` section in `pyproject.toml`:

```toml
# Missing entirely
[project.urls]
Documentation = "https://..."
Repository = "https://..."
Issues = "https://..."
Changelog = "https://..."
```

**Impact:**
- PyPI displays minimal metadata
- Users cannot find documentation from package page
- Issue reporting link missing
- Changelog/release notes link missing
- Professional appearance undermined

**Current PyPI display:**
```
codex-ml 0.1.0

Description: "Codex ML training, evaluation, and plugin framework"
(no links to docs, repo, issues)
```

**Recommendation:**
Add to `pyproject.toml`:
```toml
[project.urls]
Documentation = "https://aries-serpent.github.io/_codex_/"
Repository = "https://github.com/Aries-Serpent/_codex_"
Issues = "https://github.com/Aries-Serpent/_codex_/issues"
Changelog = "https://github.com/Aries-Serpent/_codex_/blob/main/CHANGELOG.md"
```

#### Issue PKG-009: Lazy Loading Pattern Inconsistency [MEDIUM]

**Problem:**
`src/codex/__init__.py` uses `__getattr__` for lazy imports (good practice), but:
1. Not documented
2. Not consistently used across packages
3. Type checkers cannot resolve lazy attributes
4. No `.pyi` stubs provided

```python
# src/codex/__init__.py
def __getattr__(name: str) -> object:
    if name in _SUBMODULES:
        import importlib
        mod = importlib.import_module(f".{name}", __name__)
        return mod
    raise AttributeError(...)

# Type checker cannot infer this:
from codex import cli  # ← mypy: Unknown module "cli"
```

**Recommendation:**
1. Document lazy loading:
   ```python
   """Lazy loading: Import submodules on first access to avoid startup overhead."""
   ```

2. Create type stub (`.pyi`):
   ```python
   # src/codex/__init__.pyi
   __version__: str
   cli: ModuleType
   analyze: ModuleType
   intent: ModuleType
   transform: ModuleType
   verify: ModuleType
   ingest: ModuleType
   ```

3. Use `PEP 562` `__getattr__` consistently across all top-level packages

---

## 4. CIRCULAR IMPORT ANALYSIS

### Status: ✅ PASSING

**Finding:** Scanned 1,275 Python modules, **no direct circular import cycles detected**.

Lazy loading in `__init__.py` files and careful module organization prevent import-time side effects.

**Recommendation:** Maintain this. Add pre-commit check:
```yaml
- repo: https://github.com/PyCQA/import-linter
  hooks:
    - id: import-linter
      args: [--check]
```

---

## 5. DEPENDENCY BOUNDARIES

### Status: ⚠️ WARNING — Boundaries unclear

#### Issue PKG-011: Unclear Profile Dependencies [HIGH]

**Problem:**
Dependency boundaries between profiles are not clean. Current setup:

```
Base dependencies (always installed, 11 packages):
  ✓ omegaconf, hydra-core, pydantic, pyyaml, marshmallow
  ✗ torch, transformers, datasets, accelerate  (should be optional)
  ✗ pandas, scikit-learn, duckdb  (should be optional)
  ... + 7 others

Optional profile overlaps:
  test-core (9) → hydra, omegaconf, pytest, hypothesis
  ml (6) → datasets, peft, torch, transformers, accelerate, sentencepiece
  train (5) → torch, transformers, accelerate, peft, mlflow
  eval (6) → lm-eval, nltk, rouge-score, sacrebleu, scipy, statsmodels
  all (48) → everything

No dependency tree. Users cannot see what 'runtime' means.
```

**Dependency tree (missing):**
```
core (hypothetical, should exist)
├── pydantic
├── omegaconf
├── hydra-core
└── pyyaml

runtime (should be defined)
├── core (above)
├── ml
│   ├── torch
│   ├── transformers
│   └── accelerate
├── train
│   └── peft
└── eval
    └── lm-eval
    
full (production with dev tools)
├── runtime
├── dev (pytest, mypy, black, ruff)
├── monitoring (prometheus, psutil)
└── gpu (nvidia-ml-py3)
```

**Recommendation:**
1. Define clear profile hierarchy in `pyproject.toml`
2. Create visual dependency diagram in documentation
3. Update entry point documentation to show which profile to install:
   ```
   codex-ml[runtime]    # ML features
   codex-ml[core]       # Minimal scripting
   codex-ml[full]       # Everything
   ```

---

## 6. PACKAGING READINESS CHECKLIST

### ❌ NOT READY FOR EXTERNAL RELEASE

| Item | Status | Notes |
|------|--------|-------|
| 3-profile strategy implemented | ❌ | Base deps include torch (defeats core) |
| Public APIs stable (__all__ clean) | ⚠️ | Large exports (30-48 items) with mixed stability |
| Entry points valid | ❌ | 5 point to private funcs; 2 missing |
| No circular imports | ✅ | 1,275 modules checked |
| Console scripts organized | ❌ | 51 scripts, poor hierarchy |
| [project.urls] present | ❌ | Missing PyPI metadata |
| Dependency boundaries clear | ⚠️ | Overlapping groups, no tree |
| Example code works | ❌ | Example plugins missing |

---

## 7. BLOCKING ISSUES (MUST FIX BEFORE RELEASE)

### Critical (Release Blockers)

1. **PKG-001:** Move torch/transformers/datasets/accelerate to `optional-dependencies[ml]`
   - Effort: 1-2 hours (edit pyproject.toml, test with `pip install`)
   - Risk: LOW (isolated change)

2. **PKG-004:** Create public wrappers for private entry point functions
   - Effort: 2-3 hours (add 5 public functions, update 5 entry points)
   - Risk: LOW (mechanical change)

3. **PKG-005:** Create or remove example plugins
   - Effort: 30 minutes (create stub OR remove 2 lines)
   - Risk: LOW

### High (Should Fix Before Release)

4. **PKG-002:** Define explicit `core` profile
   - Effort: 1 hour (add profile, document)

5. **PKG-006:** Reduce console scripts with hierarchy
   - Effort: 4-6 hours (refactor CLI structure)
   - Risk: MEDIUM (UI change, needs testing)

6. **PKG-008:** Add [project.urls]
   - Effort: 15 minutes

---

## 8. RECOMMENDED ACTIONS (PRIORITY ORDER)

### Phase 1: Critical Fixes (MUST DO)

```markdown
- [ ] **PKG-001:** Move ML deps to optional[ml]
  - Edit: pyproject.toml lines 31-69
  - Test: `pip install . && python -c "import torch"` (should fail)
  - Test: `pip install .[ml] && python -c "import torch"` (should work)

- [ ] **PKG-004:** Create public entry point wrappers
  - Create: public functions without _prefix in 5 registry modules
  - Edit: pyproject.toml entry points (remove underscores)
  - Test: `python -m pkg_resources` can load all plugins

- [ ] **PKG-005:** Fix example plugins
  - Create: examples/plugins/hello_plugin.py, metrics_token_accuracy_plugin.py
  - OR Remove: 2 lines from [project.entry-points."codex_ml.plugins"]
  - Test: `pip install -e . && python -c "from examples.plugins.hello_plugin import HelloPlugin"`
```

### Phase 2: High-Priority Fixes

```markdown
- [ ] **PKG-002 + PKG-003:** Define core profile
  - Add: [project.optional-dependencies] core = [minimal list]
  - Verify: core size < 50MB (without torch)

- [ ] **PKG-008:** Add [project.urls]
  - Add: [project.urls] section with Documentation, Repository, Issues, Changelog

- [ ] **PKG-007:** Audit large __all__ exports
  - Review: 5 modules with __all__ > 30 items
  - Reduce: Keep only <10 stable items per module
```

### Phase 3: Medium-Priority Improvements

```markdown
- [ ] **PKG-006:** Consolidate console scripts
  - Proposal: 3-5 primary commands (codex, codex-ml, codex-tools)
  - Refactor: CLI to use subcommands instead of separate entry points

- [ ] **PKG-009:** Add type stubs (.pyi) for lazy-loaded modules
  - Create: src/codex/__init__.pyi, src/codex_ml/__init__.pyi
  - Document: Lazy loading pattern in CONTRIBUTING.md
```

---

## 9. VERIFICATION STEPS

After fixes, verify with:

```bash
# Build clean sdist
python -m build --sdist

# Install minimal (core only)
pip install --no-deps dist/codex-ml-*.tar.gz
python -c "import codex; print(codex.__version__)"  # ✓ should work
python -c "import torch"  # ✓ should FAIL (not in core deps)

# Install with ML (runtime)
pip install dist/codex-ml-*.tar.gz[ml]
python -c "import torch; print(torch.__version__)"  # ✓ should work

# Verify entry points
python -c "
from pkg_resources import iter_entry_points
for ep in iter_entry_points('codex_ml.models'):
    print(f'Model: {ep.name} -> {ep.module_name}:{ep.attrs[0]}')
    assert not ep.attrs[0].startswith('_'), f'FAILED: {ep} uses private function'
"  # ✓ should list all models without underscore-prefixed functions

# Verify no circular imports
python -c "import codex; import codex_ml"  # ✓ should succeed immediately
```

---

## 10. NEXT STEPS

1. **Triage:** Assign PKG-001, PKG-004, PKG-005 to highest priority
2. **Implementation:** Use Phase 1 checklist above
3. **Testing:** Run verification steps after each phase
4. **Review:** Get approval on profile strategy before release
5. **Release:** Once all critical issues resolved, update version to 0.2.0 (breaking changes)

---

## Appendices

### A. Full Dependency Breakdown

**Base (11 packages):**
- omegaconf>=2.3 (config)
- hydra-core==1.3.2 (config management)
- pydantic>=2.4 (validation)
- pydantic-settings>=2.14.2 (env config)
- pyyaml>=6.0 (YAML)
- pandas>=2.0.3,<3 (data frames)
- marshmallow>=3.7.1,<5 (serialization)
- **torch>=2.6.1,<3.0.0** ← **SHOULD BE OPTIONAL**
- **transformers>=5.12.1,<6** ← **SHOULD BE OPTIONAL**
- **peft>=0.19.1,<1** (LoRA)
- **accelerate>=1.14.0,<2** ← **SHOULD BE OPTIONAL**
- + 6 more (ray, fastapi, etc.)

**Optional Groups (31 groups, 48 in 'all'):**
- See `pyproject.toml` lines 72-305

### B. Entry Points Summary

**Console Scripts (51):**
```
codex (10 commands)
codex_ml (11 commands)
cli (9 commands)
tools (12 commands)
hhg_logistics (6 commands)
codex_cli, codex_utils, tokenization (1 each)
```

**Plugin Entry Points (9 groups):**
```
codex_ml.tokenizers (1)
codex_ml.reward_models (1)
codex_ml.models (2)
codex_ml.metrics (4)
codex_ml.plugins (2) ← 2 missing
codex_ml.data_loaders (3)
codex_ml.datasets (3)
codex_ml.trainers (1)
codex.skills (0)
```

### C. Recommended Profile Definitions

```toml
[project.optional-dependencies]
# Core: minimal, for scripting and APIs
core = [
    "pydantic>=2.4",
    "typer>=0.12",
    "PyJWT>=2.13.0,<3.0.0",
    "cryptography>=48.0.0,<50.0.0",
]

# Data: analysis and utilities
data = [
    "pandas>=2.0.3,<3",
    "duckdb>=1.5.4",
    "scikit-learn>=1.9.0,<2",
]

# ML: training and inference
ml = [
    "torch>=2.6.1,<3.0.0",
    "transformers>=5.12.1,<6",
    "datasets>=5.0.0,<6",
    "accelerate>=1.14.0,<2",
    "peft>=0.19.1,<1",
    "sentencepiece>=0.1.99",
]

# Config: Hydra-based configuration
configs = [
    "hydra-core[hydra_plugins]>=1.3",
    "omegaconf>=2.3",
    "PyYAML>=6.0",
]

# Training pipeline (depends on ml + configs)
train = [
    "mlflow>=2.22.4,<4",
]

# Evaluation (depends on ml)
eval = [
    "lm-eval>=0.4.2,<1",
    "nltk>=3.8",
    "rouge-score>=0.1.2",
    "sacrebleu>=2.6.0",
    "scipy>=1.15,<2",
    "statsmodels>=0.14,<1",
]

# Runtime = core + ml + configs + train + eval
runtime = [
    # (would be built from core + ml + configs + train + eval in practice)
]

# Full = runtime + dev + gpu + monitoring
full = [
    # (all optional groups)
]
```

---

## Report Metadata

- **Generated:** 2026-07-06T00:00:00Z
- **Baseline SHA:** 2819b45e (PR #5231)
- **Modules Scanned:** 1,275
- **Issues Found:** 25 (5 CRITICAL, 8 HIGH, 12 MEDIUM)
- **Recommendation:** **DO NOT RELEASE** until critical issues resolved

---

**End of Report**
