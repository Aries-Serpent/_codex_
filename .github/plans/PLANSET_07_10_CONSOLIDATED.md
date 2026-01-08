# Plansets 07-10: Comprehensive Remediation (Consolidated)

## Planset 07: Business Logic Elevation (D365 SLA)

**Planset ID:** PS-07  
**Priority:** P1 - High  
**Phase:** Pre-commit Cycle 1-2  
**Dependencies:** PS-01 (Configuration)

### Context
SLA business logic hardcoded in CSV: `configs/deployment/d365/slas.csv`

### Implementation
- [ ] Create `src/codex/dynamics/model/sla.py` with Pydantic models
- [ ] Define `SLAPolicy(BaseModel)` class
- [ ] Migrate CSV to validated code
- [ ] Add schema validation
- [ ] Tests (90%+ coverage)

### Success Criteria
- Zero CSV business logic
- Type-safe SLA definitions
- Validated policies
- Single source of truth

---

## Planset 08: Microservice Root Cleanup

**Planset ID:** PS-08  
**Priority:** P1 - High  
**Phase:** Pre-commit Cycle 1-2  
**Dependencies:** None

### Context
`audio_cleaner_v1/` violates monolith structure

### Implementation
- [ ] Move `audio_cleaner_v1/src/*` to `src/services/audio/`
- [ ] Migrate config to `conf/services/audio.yaml`
- [ ] Update import paths
- [ ] Delete root directory
- [ ] Update documentation

### Success Criteria
- Clean repository root
- Monolith structure enforced
- All tests passing
- Documentation updated

---

## Planset 09: Training Entry Point Unification

**Planset ID:** PS-09  
**Priority:** P1 - High  
**Phase:** Pre-commit Cycle 1-2  
**Dependencies:** PS-01 (Configuration)

### Context
Split Brain: `cli/train_codex.py` (legacy) vs `src/codex_ml/training/unified_training.py` (modern)

### Implementation
- [ ] Deprecate `cli/train_codex.py`
- [ ] Create `src/codex_ml/cli/train.py` with Hydra
- [ ] Use `@hydra.main` decorator
- [ ] Invoke `UnifiedTrainer` class
- [ ] Centralize logging/checkpointing
- [ ] Tests for all entry points

### Success Criteria
- Single training entry point
- Hydra configuration
- Unified logging
- Legacy code deprecated

---

## Planset 10: Owner Guard CI/CD Enforcement

**Planset ID:** PS-10  
**Priority:** P2 - Medium  
**Phase:** Pre-commit Cycle 1  
**Dependencies:** PS-02 (Secure Bridge)

### Context
`scripts/ci/owner_approval_guard.sh` exists but not enforced in autonomous workflow

### Implementation
- [ ] Modify `.github/workflows/autonomous-agent.yml`
- [ ] Add guard step before execution phase
- [ ] Fail fast if no `human-approved` label
- [ ] Add audit logging
- [ ] Document approval process

### Guard Logic
```yaml
- name: Owner Approval Guard
  run: |
    bash scripts/ci/owner_approval_guard.sh
    if [ $? -ne 0 ]; then
      echo "ERROR: PR not approved by owner"
      exit 1
    fi
```

### Success Criteria
- Guard enforced in CI/CD
- Zero unauthorized deployments
- Audit trail complete
- Documentation clear

---

**Created:** 2026-01-08  
**Agent:** GitHub Copilot (PR #2750)
