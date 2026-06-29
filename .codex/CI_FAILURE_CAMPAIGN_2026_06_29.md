# 🎯 CI Failure Campaign Plan — 2026-06-29

**Campaign ID**: CI-CAMPAIGN-2026-06-29  
**Status**: 🔴 ACTIVE  
**Priority**: CRITICAL (2 blocking failures)  
**Authority**: @mbaetiong (Phase 3 autonomous GO approved 2026-06-27)

---

## 📋 Campaign Overview

This campaign addresses **two critical CI/CD failures** preventing main branch validation:

| Failure | Severity | Root Cause | Assigned Agent |
|---------|----------|-----------|----------------|
| **Job 84144909458**: Auth Module Tests (10m timeout) | 🔴 CRITICAL | Test suite calling non-existent PasswordHasher methods | `autonomous-test-healer-agent` |
| **Job 84144908797**: Secrets Baseline (46s timeout) | 🟠 HIGH | detect-secrets finding new secrets; baseline update needed | `secret-detection-agent` |

---

## 🔍 Failure Analysis

### Failure #1: Authentication Module Tests (Job 84144909458)

**Workflow**: Test Authentication Module (3.12.13) (push)  
**Status**: ❌ FAILED after 10m 9s  
**Test Suite**: 1,100+ auth module tests  

#### Root Causes Identified

Multiple test files call methods that **do not exist** on the `PasswordHasher` class:

1. **Missing Method: `verify_password()`**
   - Files affected:
     - `tests/auth/test_user_model_supplement.py` (lines 138, 144, 150, 161)
     - `tests/auth/test_user_store_wave2_comprehensive.py` (lines 320, 328, 336)
   - **Actual method name**: `verify()` (defined at `src/codex/auth/user_model.py:150`)
   - **Fix**: Replace all `hasher.verify_password(pwd, hash)` with `hasher.verify(pwd, hash)`

2. **Unexpected Keyword Argument: `metadata`**
   - File: `tests/auth/test_user_store_wave2_comprehensive.py:92`
   - Error: `TypeError: UserStore.create_user() got an unexpected keyword argument 'metadata'`
   - **Actual signature** (`src/codex/auth/user_store.py:98-105`):
     ```python
     def create_user(
         self,
         username: str,
         email: str,
         password: str,
         roles: Optional[list[str]] = None,
         display_name: Optional[str] = None,
     ) -> User:
     ```
   - **Fix**: Remove `metadata` argument from test calls; use `display_name` or other supported params

3. **Return Type Inconsistency**
   - File: `tests/auth/test_user_store_wave2_comprehensive.py:195`
   - Error: `AttributeError: 'str' object has no attribute 'password_hash'`
   - Context: `verify_password("bob", "WrongPassword123!")` returns string, not User
   - **Expected behavior**: Method should return `bool`, not `User`
   - **Fix**: Verify `verify_password()` method signature in UserStore and update tests

#### Test Failure Count

- Total tests: 1,100+
- Failed: **45+** (cascading from above issues)
- Passed: ~1,055

**Key Failures**:
```
- test_rapid_password_changes (line 434)
- test_deletion_is_permanent (line 408)
- test_user_deactivation (line 487)
- test_password_with_newlines (line 138) ← verify_password() issue
- test_password_with_tabs (line 144)
- test_similar_passwords_different_hashes (line 161)
- test_password_with_mixed_unicode (line 150)
- test_hash_consistency_across_instances (line 131)
- test_verify_password_case_sensitive (line 336)
- test_verify_password_failure (line 328)
- test_verify_password_success (line 320)
- test_create_user_with_metadata (line 92) ← metadata arg issue
- test_very_strong_password (line 426)
- test_verify_incorrect_password (line 195) ← return type issue
```

---

### Failure #2: Secrets Baseline Enforcer (Job 84144908797)

**Workflow**: Secrets Baseline Enforcer  
**Status**: ❌ FAILED after 46s  
**Failure Point**: Step 12: "Fail on genuine unfixed secrets"

#### Root Cause Analysis

1. **detect-secrets-hook** ran against staged files
2. New secrets detected → exit code ≠ 0
3. Auto-fix script (`sync_tracked_files.py --fix`) executed but **did not match any patterns**
4. Baseline update was blocked because secrets couldn't be categorized as "false positive" or "test/fixture"
5. Workflow exited with error

#### Key Output

```
##[error]New secrets found that are not in .secrets.baseline

Captured detect-secrets output:
The baseline file was updated.
Probably to keep line numbers of secrets up-to-date.
Please `git add .secrets.baseline`, thank you.
```

**Issue**: The baseline was **locally updated** by `detect-secrets` but:
- Not staged (`git add`)
- Not committed
- Workflow failure blocks auto-merge

#### Auto-Fix Categories (Lines 84-88)

Safe file extensions allowed in auto-fix:
- `tests/`, `src/.*/tests/`, `examples/`, `fixtures/`: `.py|.sh|.yml|.yaml|.md|.jsonl`
- `.codex/` subdirectories: Python, shell, YAML, markdown, JSONL only
- `docs/accountability/`, `docs/reference/`: same safe extensions
- `k8s/`, `manifests/`: YAML only

**Unknown Secret Location**: The exact file and line where the new secret was detected is **not visible in the log excerpt** (truncated at log step 22).

---

## 🛠️ Campaign Execution Strategy

This campaign uses **parallel delegation** to specialized agents as per @mbaetiong's preference (User Memory: "Aggressively use the task tool to delegate work to multiple custom specialized agents in parallel").

### Parallel Agent Lanes

#### Lane 1: Authentication Tests Healing (autonomous-test-healer-agent)

**Objective**: Fix all test failures in auth module  
**Scope**: 45+ failing tests across 6 test files  

**Tasks**:
1. Analyze test failures in detail (cascading failures)
2. Identify all method signature mismatches:
   - `verify_password()` → `verify()`
   - `metadata` argument removal
   - Return type corrections
3. Auto-patch test files:
   - `tests/auth/test_user_model_supplement.py`
   - `tests/auth/test_user_store_wave2_comprehensive.py`
   - Other affected files (if cascading failures exist)
4. Run auth test suite locally to verify fixes
5. Commit fixes with clear message: "fix(auth-tests): align test calls with PasswordHasher.verify() and UserStore API"

**Agent Capabilities**:
- ✅ Test failure analysis
- ✅ Method signature discovery
- ✅ Automated test patching
- ✅ Iterative local test validation
- ✅ P19 shadow import awareness

---

#### Lane 2: Secrets Baseline Resolution (secret-detection-agent)

**Objective**: Resolve new secrets detected by `detect-secrets-hook`  
**Scope**: 1+ unidentified secrets (location unknown from truncated logs)  

**Tasks**:
1. **Critical First**: Retrieve full `detect-secrets` output
   - Use GitHub Actions API to download full job logs
   - Parse `Location:` lines to identify flagged file + line number
   - Determine file type and directory

2. **Classify Secret**:
   - Is it in a test/fixture/docs file? → **False Positive** (Option 1)
   - Is it in a production code file? → **Real Secret** (Option 3)
   - Is it in a directory that should be auto-fixed? → **Update Allowlist** (Option 2)

3. **Remediation**:
   - **Option 1 (False Positive)**: Add `# pragma: allowlist secret` pragma to flagged line
   - **Option 2 (Safe Path Not Allowed)**: Expand workflow auto-fix regex to include file path
   - **Option 3 (Real Secret)**: 
     - Alert maintainer immediately
     - Rotate credential (GitHub Secrets)
     - Remove from codebase

4. **Update Baseline**:
   - `python scripts/ci/sync_tracked_files.py --fix`
   - Verify baseline changes
   - Commit with clear message

5. **Verify Workflow Passes**:
   - Re-run secrets-baseline-enforcer workflow
   - Confirm clean exit

**Agent Capabilities**:
- ✅ Secrets classification
- ✅ GitHub Actions log parsing
- ✅ detect-secrets baseline management
- ✅ Pragma documentation
- ✅ Credential rotation guidance

---

## 📊 Success Criteria

### Auth Tests Lane (Lane 1)

- [ ] All 45+ failing auth tests identified and mapped to root causes
- [ ] All `verify_password()` calls replaced with `verify()`
- [ ] All `metadata` keyword arguments removed or replaced
- [ ] Return type issues corrected
- [ ] Local auth test suite runs cleanly: `pytest tests/auth/ -v`
- [ ] Zero new test failures introduced
- [ ] Commit message explains all changes
- [ ] Pre-commit hooks pass (ruff, mypy, black, isort)

### Secrets Baseline Lane (Lane 2)

- [ ] Exact flagged file and line number identified
- [ ] Secret classified as false positive, real secret, or allowlist candidate
- [ ] Appropriate remediation applied (pragma, rotation, or allowlist update)
- [ ] `.secrets.baseline` updated and committed
- [ ] `secrets-baseline-enforcer` workflow passes on next push
- [ ] Commit message documents remediation choice

---

## 🚀 Campaign Execution

### Phase 1: Parallel Agent Activation (Immediate)

```bash
# Lane 1: Auth Tests Healing
@copilot Use autonomous-test-healer-agent to fix failing auth tests
- File: tests/auth/test_user_model_supplement.py (verify_password calls)
- File: tests/auth/test_user_store_wave2_comprehensive.py (verify_password + metadata args)
- Root cause: PasswordHasher.verify() method exists; tests call non-existent verify_password()
- Strategy: Auto-patch all test files; run pytest locally to validate

# Lane 2: Secrets Baseline Resolution  
@copilot Use secret-detection-agent to resolve baseline enforcer failure
- Job: 84144908797
- Workflow: secrets-baseline-enforcer.yml
- Root cause: New secrets detected; location unknown (logs truncated)
- Strategy: Retrieve full logs; classify secret; apply remediation; update baseline

```

### Phase 2: Merge & Validation (After Lane Completions)

Once both lanes complete:
1. Verify all changes are committed
2. Run full CI validation
3. Create PR summary documenting campaign results
4. Mark campaign complete in this file

---

## 🔐 Security Considerations

**For Lane 2 (Secrets)**:
- ⚠️ If secret is real: **DO NOT commit to main**
- ⚠️ Rotate immediately in GitHub Secrets
- ⚠️ Remove from codebase completely
- ⚠️ Update `.secrets.baseline` only after removal
- ⚠️ Never use `--baseline-fix` on production credentials

**For both lanes**:
- All changes must pass security scanning
- All changes must pass type checking (mypy)
- All changes must pass linting (ruff)
- No new secrets introduced during fixes

---

## 📞 Escalation Points

| Scenario | Action |
|----------|--------|
| Real secret detected in production code | Alert @mbaetiong; do not commit |
| Auth API changed; tests need redesign | Create issue; request guidance |
| detect-secrets false positive unresolvable | Escalate to @mbaetiong |
| Lane does not complete within 2 hours | Re-assess scope; break into smaller PRs |

---

## 📝 Campaign Status Log

| Time | Status | Notes |
|------|--------|-------|
| 2026-06-29T20:16 | 🟡 PLANNING | Campaign plan created; awaiting agent activation |
| 2026-06-29T20:XX | 🟠 EXECUTING | Agents activated (Lane 1 + Lane 2 parallel) |
| 2026-06-29T21:XX | 🟢 VALIDATING | Both lanes complete; running full CI |
| 2026-06-29T22:XX | ✅ COMPLETE | Campaign closed; all tests passing |

---

## 📎 References

- Job URL (Auth): https://github.com/Aries-Serpent/_codex_/actions/runs/28398939677/job/84144909458
- Job URL (Secrets): https://github.com/Aries-Serpent/_codex_/actions/runs/28398939677/job/84144908797
- Test Files: `/home/runner/work/_codex_/_codex_/tests/auth/*.py`
- Auth Source: `/home/runner/work/_codex_/_codex_/src/codex/auth/`
- Secrets Workflow: `.github/workflows/secrets-baseline-enforcer.yml`
- Baseline File: `.secrets.baseline` (48KB, 100+ known secrets)

---

## 🗂️ PHASE 3: Root Folder Cleanup Campaign (Next Session)

**Campaign Status**: 🔵 PLANNING  
**Execution**: Next session (deferred after current failures resolved)  
**Related Document**: `.codex/ROOT_FOLDER_CLEANUP_PLAN.md`

### Overview

Following CI failure resolution, comprehensive root folder cleanup campaign will:

1. **Analyze Breaking Links** (180+ root files)
   - Identify all references from workflows, source code, documentation
   - Create breaking link matrix showing impact of each reorganization
   - Validate safe vs. breaking changes

2. **Safe Cleanup Execution**
   - Delete 50+ temporary/test files (zero breaking changes)
   - Archive 40+ phase reports to `.codex/archive/phases/`
   - Create `.config.legacy/` documentation directory
   - Update all configuration file references

3. **Update All Systems**
   - Baselines (`.secrets.baseline`, `.mypy-baseline.txt`)
   - Auth configuration references
   - Workflows (if needed — minimize changes)
   - Documentation links
   - Mermaid diagrams and mappings

4. **Verification & Validation**
   - Link validation script execution
   - Complete CI workflow validation
   - Zero-breaking-change guarantee

### Key Findings from Analysis

| Item | Count | Action |
|------|-------|--------|
| Root-level files | 180+ | Categorize & organize |
| Files to delete | 50+ | Low-risk temp/test files |
| Files to archive | 40+ | Phase reports → `.codex/archive/phases/` |
| Files to keep in root | 60+ | Config, requirements, documentation |
| Workflow updates needed | 0 | Non-breaking design |
| Documentation updates needed | 5-10 | Link updates only |

### Breaking Link Categories Identified

1. **Configuration Files** (CRITICAL)
   - `pyproject.toml` — 100+ workflow/code references
   - `pytest.ini` — 50+ workflow references
   - `requirements-*.txt` — 80+ workflow references
   - **Decision**: Keep in root; non-breaking

2. **Workflows** (CRITICAL)
   - 100+ GitHub Actions workflows reference root files
   - Path references in `run:` steps are relative (SAFE)
   - Artifact upload paths may be absolute (CHECK)
   - **Decision**: Validate before moving any files

3. **Source Code** (HIGH)
   - Grep scan needed for hardcoded file references
   - Test discovery paths
   - Configuration file imports
   - **Decision**: Fix all references before cleanup

4. **Documentation** (MEDIUM)
   - Internal documentation links
   - Phase report cross-references
   - Configuration file references
   - **Decision**: Update after cleanup

### Execution Plan (Next Session)

**Phase 1: Validation** (60 min)
- Link validation scan script
- Workflow reference audit
- Test discovery verification
- Configuration file loading tests

**Phase 2: Cleanup** (90 min)
- Delete 50+ temp files
- Archive 40+ phase reports
- Create `.config.legacy/` directory
- Update baselines and references

**Phase 3: Verification** (45 min)
- Run full CI validation
- Link verification
- Document all changes

**Total Estimated Time**: 3.5 hours

---

**Campaign Plan Version**: 1.0  
**Last Updated**: 2026-06-29T20:16  
**Authority**: @mbaetiong (Phase 3 GO)
**Related Document**: `.codex/ROOT_FOLDER_CLEANUP_PLAN.md` (detailed planning)
