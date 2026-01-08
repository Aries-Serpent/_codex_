# Planset 01: Configuration Consolidation (Hydra Integration)

**Planset ID:** PS-01  
**Priority:** P0 - Critical  
**Phase:** Pre-commit Cycle 1-3  
**Status:** 📋 Planned  
**Dependencies:** None  
**Cognitive Brain Objective:** Eliminate configuration sprawl, establish single source of truth

---

## Context

**Problem:** Configuration fragmented across multiple locations:
- `conf/` (Hydra YAML)
- `configs/` (Legacy YAML)
- `config_legacy/errors.py` (Hardcoded Python dictionaries)

**Impact:** Configuration drift, inconsistent behavior, difficult maintenance

**Solution:** Consolidate all configuration into Hydra-managed YAML structure

---

## Implementation Plan

### Pre-commit Cycle 1: Refactor Error Configuration

**Goal:** Move hardcoded error config to YAML

**Tasks:**
- [ ] Analyze `config_legacy/errors.py` for error definitions
- [ ] Create `conf/errors/defaults.yaml` with structured error schemas
- [ ] Implement `src/codex/utils/config_loader.py` using Hydra Compose API
- [ ] Add validation for error config schema
- [ ] Create unit tests for config loader (80%+ coverage)

**Files to Create:**
- `conf/errors/defaults.yaml` (~100 lines)
- `src/codex/utils/config_loader.py` (~150 lines)
- `tests/test_config_loader.py` (~200 lines)

**Files to Deprecate:**
- `config_legacy/errors.py` → Move to `misc/archive/`

**Success Criteria:**
- [ ] All error configs loaded from YAML
- [ ] Zero hardcoded dictionaries
- [ ] Hydra validation passing
- [ ] Tests passing (100% of new code)

### Pre-commit Cycle 2: Configuration Migration

**Goal:** Migrate remaining configs to Hydra structure

**Tasks:**
- [ ] Audit all `configs/` YAML files
- [ ] Identify configs suitable for Hydra migration
- [ ] Create migration mapping document
- [ ] Move configs to `conf/` with proper structure
- [ ] Update import paths in codebase
- [ ] Validate all configs load correctly

**Files to Modify:**
- Multiple configs in `configs/` → `conf/`
- Update imports in ~20 Python files

**Success Criteria:**
- [ ] Configs follow Hydra conventions
- [ ] Config loading centralized
- [ ] Documentation updated

### Pre-commit Cycle 3: Validation & Testing

**Goal:** Ensure configuration reliability

**Tasks:**
- [ ] Run full test suite with new config system
- [ ] Validate config schemas
- [ ] Test config overrides work correctly
- [ ] Document config usage patterns
- [ ] Create troubleshooting guide

**Documentation:**
- `docs/configuration/HYDRA_MIGRATION_GUIDE.md`
- `docs/configuration/CONFIG_USAGE.md`

**Success Criteria:**
- [ ] All tests passing
- [ ] Zero config-related failures
- [ ] Documentation complete

---

## Success Metrics

- **Configuration Files Consolidated:** 15+ configs migrated
- **Code Reduction:** -500 lines (eliminating duplicates)
- **Config Loading Time:** <100ms
- **Maintainability:** Single source of truth established

---

## Risk Mitigation

**Risk 1:** Breaking existing config consumers
- **Mitigation:** Backward compatibility layer for 2 implementation cycles
- **Fallback:** Keep legacy configs with deprecation warnings

**Risk 2:** Hydra learning curve for contributors
- **Mitigation:** Comprehensive documentation and examples
- **Fallback:** Migration guide with clear patterns

---

## Cognitive Brain Integration

**Patterns Learned:**
1. Hydra Compose API usage for dynamic config loading
2. YAML schema validation patterns
3. Configuration migration strategies

**Reusable Utilities:**
1. `config_loader.py` - Generic Hydra config loader
2. Config validation helpers
3. Migration scripts for future config changes

**Knowledge Base Update:**
- Add Hydra best practices to coding standards
- Document config file organization patterns
- Create config troubleshooting runbook

---

## Dependencies

**Required:**
- Hydra (already installed)
- PyYAML (already installed)

**Validates:**
- Pydantic for schema validation (already installed)

---

## Follow-Up Plansets

- **PS-02:** Schema Authority (uses centralized config)
- **PS-07:** Business Logic Elevation (depends on config patterns)

---

**Created:** 2026-01-08  
**Agent:** GitHub Copilot (PR #2750)  
**Status:** Ready for implementation
