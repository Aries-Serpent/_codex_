# Post-Merge Session Continuation Brief

**Created**: 2026-06-25T22:20:00Z  
**Audience**: Copilot agent starting post-merge session  
**Scope**: Expected environment state + validated safe zones + escalation paths  
**Duration**: For first 30 minutes of post-merge session

---

## Expected Environment (Post-Merge)

### What Will Work ✅
- Python 3.12+ environment ready
- Core dependencies installed (setuptools, hydra-core, omegaconf, pydantic, etc.)
- Git repository checked out with full history
- GitHub Actions secrets injected (CODEX_MASTER_KEY, CODEX_BACKUP_KEY)
- CCA version lock variables active
- LFS opt-in policy (GIT_LFS_SKIP_SMUDGE=1) active

### What Will NOT Work ❌ (Pre-Existing)
- `zstandard` package (missing from test environment)
- `sqlalchemy` package (transitive, not explicit)
- Some test modules will fail collection due to above
- Optional RAG, database, compression tests will skip

### What You MUST Do First
1. **Run validation** (5 min): `.codex/POST_MERGE_COPILOT_SETUP_VALIDATION.md`
2. **Baseline test collection** (5 min): `pytest --collect-only 2>&1 | tee .codex/POST_MERGE_TEST_COLLECTION_STATUS.txt`
3. **Compare against pre-merge** (5 min): Diff vs `.codex/PRE_MERGE_TEST_COLLECTION_STATUS.json`
4. **Decide: proceed or revert** (5 min): Follow decision tree in `.codex/POST_MERGE_REVERSION_PROTOCOL.md`

---

## Validation Checklist (First 20 minutes)

### ☐ Phase 1: Setup Validation (5 min)
**Run**:
```bash
yamllint .github/workflows/copilot-setup-steps.yml
echo "Exit code: $?"
```

**Expected**: Exit code 0 (or warnings only)

**If FAIL**: Run reversion protocol immediately

---

### ☐ Phase 2: Test Collection Baseline (5 min)
**Run**:
```bash
pytest --collect-only 2>&1 | tee .codex/POST_MERGE_TEST_COLLECTION_STATUS.txt
echo "Collection completed. Check for errors above."
```

**Expected**: 
- Collection completes (may show import errors for optional deps)
- Errors match pre-merge baseline OR fewer
- No new errors in core modules

**If new core errors**: Investigate → may need reversion

---

### ☐ Phase 3: Environment Variable Check (5 min)
**Run**:
```bash
echo "COPILOT_AGENT_CCA_VERSION_LOCK: $COPILOT_AGENT_CCA_VERSION_LOCK"
echo "COPILOT_AGENT_DEDUPLICATION_ENABLED: $COPILOT_AGENT_DEDUPLICATION_ENABLED"
echo "COPILOT_AGENT_TURN_ISOLATION_ENABLED: $COPILOT_AGENT_TURN_ISOLATION_ENABLED"
```

**Expected**: All three set to `stable`, `true`, `true`

**If missing**: Reversion protocol (env variable injection broken)

---

### ☐ Phase 4: Optional Dependencies Assessment (5 min)
**Run**:
```bash
python3 -c "import zstandard" 2>&1 || echo "zstandard missing (expected)"
python3 -c "import sqlalchemy" 2>&1 || echo "sqlalchemy missing (expected)"
```

**Expected**: Both fail (pre-existing)

**If both succeed**: Unexpected, but not a blocker

**If you need them**: 
```bash
pip install zstandard sqlalchemy
pytest --collect-only 2>&1 | tee .codex/POST_MERGE_TEST_COLLECTION_AFTER_INSTALL.txt
```

---

## Decision Point: Proceed vs. Revert

### ✅ PROCEED if:
- YAML validation passed (yamllint exit 0)
- No new errors in test collection (vs. baseline)
- Environment variables present and correct
- CCA version lock active

**Action**: Continue with post-merge work

---

### ⚠️ INVESTIGATE if:
- Test collection shows same errors as pre-merge baseline
- Optional deps missing (zstandard, sqlalchemy)
- Warnings in yamllint (non-blocking)

**Action**: Document in accountability report, proceed

---

### ❌ REVERT if:
- YAML parse error in copilot-setup-steps.yml
- 10+ NEW errors in test collection (core modules)
- Python version <3.12
- Environment variables missing/wrong

**Action**: See `.codex/POST_MERGE_REVERSION_PROTOCOL.md` for reversion procedure

---

## Safe Zones (Validated Pre-Merge)

These components are confirmed working and safe to continue with:

| Component | Status | Evidence | Next Steps |
|-----------|--------|----------|-----------|
| copilot-setup-steps.yml | ✅ Valid | YAML lint pass | Proceed to work |
| Python 3.12+ | ✅ Required | pyproject.toml | Use existing env |
| Core dependencies | ✅ Installed | requirements/ pass | Build on existing |
| CCA version lock | ✅ Active | Env vars present | Multi-turn safe |
| Session preload | ✅ Works | Block scalar validated | No refactoring |

---

## Known Blockers (Do NOT Work On)

These are NOT in scope for post-merge session:

1. **Missing zstandard** → Document as pre-existing, don't fix in this session
2. **Missing sqlalchemy** → Document as pre-existing, don't fix in this session
3. **Optional dep test skips** → Expected behavior, not a regression
4. **LFS policy questions** → Defer to @mbaetiong if concerns arise

---

## Escalation Paths

### If YAML validation fails:
```
→ Follow reversion protocol
→ Revert .github/workflows/copilot-setup-steps.yml
→ Create escalation issue with @mbaetiong tag
→ STOP all work
```

### If 10+ NEW test errors:
```
→ Follow reversion protocol  
→ Document root cause
→ Create escalation issue
→ STOP all work
```

### If environment variables missing:
```
→ Check GitHub Actions secret injection <!-- pragma: allowlist secret -->
→ If not @mbaetiong responsibility → Escalate
→ Do NOT revert workflow (this is external config)
``` <!-- pragma: allowlist secret -->

### If pre-existing issues only:
```
→ Document in accountability report
→ Update .codex/POST_MERGE_ENVIRONMENT_BASELINE.md with findings
→ PROCEED to post-merge work
```

---

## Documentation to Update (After Validation)

### Update 1: Accountability Report
**File**: `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`

Add section:
```markdown
## Session X: Post-Merge Validation (2026-06-XX)

**Validation Result**: ✅ PASS / ❌ REVERT

### Pre-Merge → Post-Merge Comparison
- Test collection errors: [X] → [Y]
- New regressions: [none / list if any]
- Pre-existing issues documented: [yes/no]

### Findings
[Brief summary of validation findings]
```

### Update 2: Baseline Status
**File**: `.codex/POST_MERGE_ENVIRONMENT_BASELINE.md`

Update section "Pre-Merge Snapshot" with:
- Actual date/time of post-merge validation
- Exact test collection output
- Any variations from expected baseline

---

## Timeline Expectations

| Phase | Duration | Owner | Status |
|-------|----------|-------|--------|
| Setup validation | 5 min | Agent | Before work starts |
| Test collection baseline | 5 min | Agent | Before work starts |
| Environment check | 5 min | Agent | Before work starts |
| Optional dep assessment | 5 min | Agent | Before work starts |
| Decision (proceed/revert) | 5 min | Agent | Gate to work |
| **Total before work**: | **25 min** | **Agent** | **Required** |

After validation passes: Standard post-merge work can begin.

---

## NO-LOOP Guarantee

This protocol ensures:
- ✅ **One decision**, not retries
- ✅ **Clear escalation**, not guessing
- ✅ **Documented baseline**, not assumptions
- ✅ **Terminal reversion**, not loops

If reversion is triggered, it is FINAL until @mbaetiong reviews and approves next steps.

Do not retry post-merge work if validation fails. Escalate instead.
