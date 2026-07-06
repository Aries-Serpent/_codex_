# Lane 1 Brief: Packaging & Distribution Refactor

**Lane 1 Owner:** `packaging-validation-agent`  
**Duration:** Days 3-9 (Phase 1) + Days 10-14 (iteration)  
**Authority:** @mbaetiong D-tier approved  
**Phase 0 Decision Leverage:** Strategic Decision #1 (3-tier package profiles)

---

## 🎯 Lane 1 Objective

Transform `pyproject.toml` from monolithic ML-focused package to modular, profile-based architecture enabling clean packaging of core, runtime, and full variants for external distribution.

---

## 📋 Deliverables

### By Phase 1 Day 9 (Target: 2026-07-15)

1. **Refactored pyproject.toml**
   - Package rename: `codex-ml` → `codex-core` (primary) with compatibility alias
   - 3 optional-dependencies profiles:
     - `core`: Minimal runtime (base dependencies only)
     - `runtime`: Core + cognitive brain + local server framework
     - `full`: Everything (ML training, RAG, integrations)
   - Clean console_scripts entrypoints (stable, externally-facing)
   - Example entrypoints:
     ```python
     [project.scripts]
     codex = "codex.cli:main"
     codex-cognitive = "codex.cognitive_brain.cli:main"
     codex-bootstrap = "codex_ml.cli.offline_bootstrap:main"
     ```

2. **Package Metadata Finalization**
   - Version: 0.1.0-external (or 0.1.0 with notes)
   - Authors: Aries Serpent (current is good)
   - License: MIT (verified)
   - Keywords: decision-engine, cognitive, offline, packaging-ready
   - Python requirement: >=3.12 (locked)
   - Classifiers: Updated for external consumption

3. **Core Wheel Build Validation**
   - `pip install codex-core-0.1.0.whl` succeeds in clean venv
   - All entrypoints work: `codex --version`, `codex-cognitive --help`
   - No import errors in isolated environment
   - Size target: <20 MB for core

4. **Profile Dependencies Locked**
   - `core`: Base dependencies only (65 packages)
   - `runtime`: + cognitive_brain modules (70 packages)
   - `full`: + ML/RAG (1,200+ transitive)
   - All pinned to exact versions (work with Lane 2 for lockfile)

---

## 🚀 Execution Roadmap

### Days 3-5: Profile Boundary Definition

**Task 1.1: Dependency Audit**
- Categorize all current dependencies by tier:
  - **Core:** Always required (OmegaConf, Pydantic, PyYAML)
  - **Runtime:** Optional for external users (cognitive_brain-specific)
  - **Optional:** ML/RAG features, integrations
- Output: Dependency mapping spreadsheet

**Task 1.2: Module-to-Profile Mapping**
- Cross-reference INTELLIGENCE_CAMPAIGN_BASELINE.md module list
- Assign each module to core/runtime/full
- Identify circular dependencies (resolve before refactoring)
- Output: Module → Profile matrix

**Task 1.3: pyproject.toml Spike**
- Backup current pyproject.toml
- Draft refactored version with 3 optional-dependencies groups
- Test: `pip install -e ".[core]"`, `pip install -e ".[runtime]"`, `pip install -e ".[full]"`
- Output: Refactored pyproject.toml (draft)

### Days 6-7: Entrypoint Stabilization

**Task 1.4: CLI Inventory**
- List all current entrypoints in pyproject.toml
- Assess external user relevance: Keep, remove, or rename?
- Examples:
  - ✅ KEEP: `codex` (main CLI), `codex-cognitive` (decision engine)
  - ⚠️ REVIEW: `codex-bootstrap` (offline-specific, maybe valuable)
  - ❌ REMOVE: Internal dev tools, GitHub-specific utilities
- Output: Approved entrypoints list

**Task 1.5: Entrypoint Testing**
- Build wheel with finalized entrypoints
- Test in clean venv: each entrypoint runs without errors
- Document usage: e.g., `codex-cognitive --help`
- Output: Entrypoint verification report

### Days 8-9: Package Finalization & Testing

**Task 1.6: Metadata & Classifiers**
- Update version to 0.1.0-external (or agreed version)
- Update keywords, description for external audience
- Update classifiers: Operating System, Python version, etc.
- Output: Finalized pyproject.toml

**Task 1.7: Clean-Room Build Test**
- Fresh Python 3.12 venv
- `pip install wheel setuptools`
- `python -m build --wheel`  (build codex-core-0.1.0.whl)
- `pip install codex-core-0.1.0.whl`
- Verify all entrypoints: `codex --version`, `codex-cognitive --version`
- Output: Build success report

**Task 1.8: Profile Size Validation**
- Report wheel size for each profile
- core: Target <20 MB ✅
- runtime: Target <35 MB ✅
- full: 150+ MB expected (informational)

---

## 🔗 Cross-Lane Dependencies

### Lane 1 ← Lane 2 (Packaging ← Offline Bootstrap)

**Dependency:** Lane 2 lockfile informs Lane 1 dependency selection
- Lane 1 finalizes dependencies by Day 7
- Lane 2 uses Lane 1 dependency list to build lockfile (Day 3-9)
- **Sync Point:** Daily standup, confirm no conflicts

### Lane 1 → Lane 3 (Packaging → Cognitive Runtime)

**Dependency:** Lane 3 cognitive extraction aligns with Lane 1 profile boundaries
- Lane 1 locks cognitive_brain modules in runtime profile (Day 6)
- Lane 3 extracts only modules in runtime profile (Days 3-9)
- **Sync Point:** Lane 3 reviews Lane 1 module assignments, confirms alignment

### Lane 1 → Lane 5 (Packaging → Documentation)

**Dependency:** Lane 5 documentation references Lane 1 package profiles
- Lane 5 waits for Lane 1 final pyproject.toml (by Day 9)
- Lane 5 documents installation instructions for each profile (Phase 3)
- **Sync Point:** Lane 5 has Lane 1 entrypoints + wheel sizes by Day 9

---

## ✅ Acceptance Criteria

| Criterion | Validation | Owner |
|-----------|-----------|-------|
| 3 profiles defined & installable | Test all 3: `pip install .[core]`, `.[runtime]`, `.[full]` | packaging-validation-agent |
| Wheel builds successfully | `python -m build --wheel` succeeds in clean env | packaging-validation-agent |
| Entrypoints stable & documented | All approved entrypoints listed, tested, documented | packaging-validation-agent |
| Profile sizes meet targets | core <20 MB, runtime <35 MB, full ~150+ MB | packaging-validation-agent |
| No import errors | `codex --version` works in clean venv | packaging-validation-agent |
| Phase 1 gate passed | >90% deliverables complete, no blockers | orchestrator-agent |

---

## 📌 Key Decisions from Phase 0

**Strategic Decision #1: 3-Tier Package Profiles**
- ✅ APPROVED in INTELLIGENCE_CAMPAIGN_BASELINE.md
- core: Minimal cognitive engine + CLI
- runtime: core + local server framework + offline bootstrap
- full: runtime + ML training + RAG + integrations

**Entrypoint Philosophy:**
- Stable: No breaking changes post-release
- External-user-focused: Useful outside codex repo context
- Documented: Clear usage instructions
- Minimal: Only essential commands exported

---

## 🛠️ Tools & Commands

```bash
# Build wheel
python -m build --wheel

# Install for testing
pip install -e ".[core]"
pip install -e ".[runtime]"
pip install -e ".[full]"

# Verify entrypoints
codex --version
codex-cognitive --help
codex-bootstrap --help

# Check wheel contents
unzip -l dist/codex-core-0.1.0.whl | head -20
```

---

## 📞 Escalation

**Blockers or Conflicts?** Report to orchestrator-agent with:
- Blocker description
- Current progress (which task blocked?)
- Proposed workaround (if any)

**Example escalation:**
> Blocker: Circular dependency between codex.cognitive_brain and codex.auth prevents clean extraction. Proposed: Delay auth integration to "runtime" profile only.

