# CodeQL Alert Remediation Master Plan
## PR #4427 — Session S968+ — 126 Alerts → 0

**Status**: 🔴 ACTIVE  
**Created**: 2026-05-12T21:05Z  
**Target**: Zero CodeQL alerts  
**Current Count**: 126 open alerts  
**Progress**: 1 fixed (S967: Empty except in verify_living_files.py)

---

## 🎯 PRIMARY OBJECTIVE

**Reduce CodeQL security and quality alerts from 126 to 0 through systematic remediation.**

### Success Criteria
- ✅ All 126 CodeQL alerts resolved
- ✅ No new alerts introduced
- ✅ All fixes validated with tests
- ✅ Pattern 25 compliance maintained (CHANGELOG + AAAR in every commit)
- ✅ All validation checks passing

---

## 📊 REMEDIATION STRATEGY

### Phase 1: Discovery & Classification (S968)
**Goal**: Identify all alerts, categorize by severity and type

**Tasks**:
1. ✅ Fetch CodeQL alert list via artifact or GitHub API
2. ⏳ Classify alerts by:
   - Severity (Critical, High, Medium, Low)
   - Category (Security, Quality, Best Practice)
   - File/Module affected
   - Fix complexity (Simple, Moderate, Complex)
3. ⏳ Create remediation priority matrix
4. ⏳ Document alert patterns and common fixes

**Deliverables**:
- `CODEQL_ALERT_INVENTORY.md` — Complete alert catalog
- `CODEQL_REMEDIATION_PRIORITY.md` — Prioritized fix order
- `CODEQL_FIX_PATTERNS.md` — Common patterns and solutions

**Validation**:
```bash
# Verify alert count
python scripts/ci/check_codeql_alerts.py --count

# Generate inventory
python scripts/ci/check_codeql_alerts.py --export-inventory
```

---

### Phase 2: High-Priority Remediation (S969-S975)
**Goal**: Fix Critical and High severity alerts (estimated 40-60 alerts)

**Batch Strategy**: Fix in groups of 10-15 alerts per session

#### Batch 1: Critical Security Issues (S969)
**Target**: SQL Injection, Command Injection, Path Traversal
**Estimated**: 10-15 alerts

**Tasks**:
1. Fix SQL injection vulnerabilities
2. Fix command injection issues
3. Fix path traversal vulnerabilities
4. Add input validation and sanitization
5. Update tests to cover security fixes

**Validation**:
```bash
python -m pytest tests/ -k security
python scripts/ci/auto_fix_common_issues.py --check-only
```

#### Batch 2: Authentication & Authorization (S970)
**Target**: Weak crypto, insecure random, auth bypass
**Estimated**: 10-15 alerts

**Tasks**:
1. Replace weak cryptographic functions
2. Fix insecure random number generation
3. Strengthen authentication checks
4. Add authorization validation

#### Batch 3: Data Exposure & Leaks (S971)
**Target**: Information disclosure, sensitive data exposure
**Estimated**: 10-15 alerts

**Tasks**:
1. Remove hardcoded secrets
2. Fix information disclosure issues
3. Add data sanitization
4. Implement proper error handling

#### Batch 4: Resource Management (S972)
**Target**: Resource exhaustion, memory leaks, file handle leaks
**Estimated**: 10-15 alerts

**Tasks**:
1. Fix resource exhaustion vulnerabilities
2. Add proper cleanup in exception handlers
3. Implement timeout guards
4. Add resource limits

---

### Phase 3: Medium-Priority Remediation (S976-S982)
**Goal**: Fix Medium severity alerts (estimated 40-50 alerts)

**Batch Strategy**: Fix in groups of 15-20 alerts per session

#### Batch 5: Code Quality Issues (S976-S977)
**Target**: Unused variables, dead code, complexity
**Estimated**: 20-25 alerts

**Tasks**:
1. Remove unused imports and variables
2. Eliminate dead code
3. Refactor complex functions
4. Improve code readability

#### Batch 6: Error Handling (S978-S979)
**Target**: Empty except, broad exceptions, missing error handling
**Estimated**: 15-20 alerts

**Tasks**:
1. Add explanatory comments to empty except blocks
2. Replace broad exception catches with specific ones
3. Add proper error logging
4. Implement graceful degradation

---

### Phase 4: Low-Priority Remediation (S983-S985)
**Goal**: Fix Low severity and best practice alerts (estimated 20-30 alerts)

#### Batch 7: Best Practices (S983-S984)
**Target**: Naming conventions, documentation, type hints
**Estimated**: 15-20 alerts

**Tasks**:
1. Fix naming convention violations
2. Add missing docstrings
3. Add type hints where missing
4. Improve code documentation

#### Batch 8: Final Cleanup (S985)
**Target**: Remaining alerts and edge cases
**Estimated**: 5-10 alerts

**Tasks**:
1. Fix remaining miscellaneous alerts
2. Address edge cases
3. Final validation sweep
4. Update documentation

---

### Phase 5: Validation & Verification (S986)
**Goal**: Ensure all alerts resolved and no regressions

**Tasks**:
1. ✅ Run full CodeQL scan
2. ✅ Verify 0 open alerts
3. ✅ Run full test suite
4. ✅ Run security scanning suite
5. ✅ Validate no new alerts introduced
6. ✅ Update PR description with final metrics

**Validation**:
```bash
# Full validation suite
python -m pytest tests/ --cov=src --cov-report=term-missing
python -m ruff check src/ tests/
python scripts/ci/mypy_baseline.py --require-baseline
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/sync_tracked_files.py --fix
python scripts/ci/verify_living_files.py --strict

# Security scans
bandit -r src/ -f json -o .codex/bandit_final.json
semgrep --config=auto src/ --json -o .codex/semgrep_final.json
```

---

## 🔄 SESSION WORKFLOW TEMPLATE

### Pre-Session Checklist
```bash
# 1. Verify current state
git status
git log --oneline -3

# 2. Check Pattern 25 compliance
git show --stat HEAD

# 3. Run validation baseline
python scripts/ci/verify_living_files.py --strict
python -m ruff check src/ tests/ --output-format=concise
python scripts/ci/sync_tracked_files.py --check
```

### Session Execution Pattern
```bash
# 1. Fetch alerts for current batch
python scripts/ci/check_codeql_alerts.py --batch <N>

# 2. Fix alerts one-by-one or in small groups
# - Make targeted fixes
# - Add tests for each fix
# - Validate locally

# 3. Commit with Pattern 25 compliance
# - Update CHANGELOG.md
# - Update AGENT_ACCOUNTABILITY_REPORT.md
# - Commit both files together

# 4. Run validation
python -m ruff check src/ tests/ --fix
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/verify_living_files.py --strict

# 5. Push and verify CI
git push
# Monitor CI for new alerts
```

### Post-Session Checklist
```bash
# 1. Update this master plan
# - Mark completed tasks
# - Update alert count
# - Document any blockers

# 2. Update follow-up prompt
# - Update PR-4425-followup.md
# - Add next session priorities

# 3. Reply to PR comments
# - Update status
# - Report progress
```

---

## 📋 ALERT TRACKING

### Alert Count by Phase
| Phase | Target | Fixed | Remaining | Status |
|-------|--------|-------|-----------|--------|
| Phase 1 | Discovery | - | 126 | ⏳ In Progress |
| Phase 2 | Critical/High | 0 | 50-60 | ⏳ Pending |
| Phase 3 | Medium | 0 | 40-50 | ⏳ Pending |
| Phase 4 | Low | 0 | 20-30 | ⏳ Pending |
| Phase 5 | Validation | - | - | ⏳ Pending |
| **TOTAL** | **All** | **1** | **125** | **🔴 Active** |

### Alert Count by Severity
| Severity | Count | Fixed | Remaining |
|----------|-------|-------|-----------|
| Critical | TBD | 0 | TBD |
| High | TBD | 0 | TBD |
| Medium | TBD | 0 | TBD |
| Low | TBD | 1 | TBD |
| **TOTAL** | **126** | **1** | **125** |

### Alert Count by Category
| Category | Count | Fixed | Remaining |
|----------|-------|-------|-----------|
| Security | TBD | 0 | TBD |
| Quality | TBD | 1 | TBD |
| Best Practice | TBD | 0 | TBD |
| **TOTAL** | **126** | **1** | **125** |

---

## 🛠️ COMMON FIX PATTERNS

### Pattern 1: Empty Except Blocks
**Alert**: "Empty except clause does nothing but pass"

**Fix**:
```python
# Before
try:
    risky_operation()
except:
    pass

# After
try:
    risky_operation()
except Exception:
    # Intentionally suppressed: operation is optional and failure is acceptable
    pass
```

### Pattern 2: SQL Injection
**Alert**: "SQL query built from user input"

**Fix**:
```python
# Before
query = f"SELECT * FROM users WHERE id = {user_id}"

# After
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

### Pattern 3: Command Injection
**Alert**: "Command built from user input"

**Fix**:
```python
# Before
os.system(f"ls {user_path}")

# After
subprocess.run(["ls", user_path], check=True, shell=False)
```

### Pattern 4: Path Traversal
**Alert**: "Path built from user input"

**Fix**:
```python
# Before
file_path = os.path.join(base_dir, user_file)

# After
file_path = os.path.join(base_dir, os.path.basename(user_file))
if not os.path.abspath(file_path).startswith(os.path.abspath(base_dir)):
    raise ValueError("Invalid path")
```

### Pattern 5: Hardcoded Secrets
**Alert**: "Hardcoded credentials"

**Fix**:
```python
# Before
API_KEY = "sk-1234567890abcdef"

# After
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

---

## 📝 DOCUMENTATION REQUIREMENTS

### Per-Session Documentation
1. **CHANGELOG.md**: Document functional changes only
2. **AGENT_ACCOUNTABILITY_REPORT.md**: Session summary with metrics
3. **This Master Plan**: Update progress and alert counts
4. **PR-4425-followup.md**: Update next session priorities

### Final Documentation
1. **Security Audit Report**: Complete remediation summary
2. **CodeQL Baseline**: New baseline with 0 alerts
3. **Test Coverage Report**: Coverage impact of fixes
4. **Migration Guide**: Breaking changes (if any)

---

## 🚨 CRITICAL CONSTRAINTS

### Pattern 25 Compliance
**EVERY commit MUST include**:
- ✅ CHANGELOG.md update
- ✅ AGENT_ACCOUNTABILITY_REPORT.md update
- ✅ Both files in same commit

### Validation Gates
**Before EVERY push**:
```bash
python scripts/ci/verify_living_files.py --strict
python -m ruff check src/ tests/ --fix
python scripts/ci/sync_tracked_files.py --fix
python scripts/ci/auto_fix_common_issues.py --check-only
```

### WEC Block Requirement
**EVERY report_progress MUST include**:
- Full WEC block from `session_wrapup_autofix.py --print-wec-block`

---

## 📊 PROGRESS METRICS

### Session Velocity Target
- **Optimal**: 15-20 alerts per session
- **Minimum**: 10 alerts per session
- **Maximum**: 25 alerts per session (avoid rushing)

### Estimated Timeline
- **Phase 1**: 1 session (S968)
- **Phase 2**: 4-6 sessions (S969-S975)
- **Phase 3**: 3-4 sessions (S976-S982)
- **Phase 4**: 2-3 sessions (S983-S985)
- **Phase 5**: 1 session (S986)
- **Total**: 11-15 sessions

### Quality Gates
- ✅ No new alerts introduced
- ✅ All tests passing
- ✅ Code coverage maintained or improved
- ✅ No regressions in functionality
- ✅ Security posture improved

---

## 🔗 RELATED RESOURCES

### Scripts
- `scripts/ci/check_codeql_alerts.py` — Alert fetching and analysis
- `scripts/ci/auto_fix_common_issues.py` — Automated fixes
- `scripts/ci/verify_living_files.py` — Living file validation
- `scripts/ci/sync_tracked_files.py` — Tracked file sync

### Documentation
- `.codex/CODEBASE_AGENCY_POLICY.md` — Fix ALL issues policy
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` — Session tracking
- `.github/copilot-prompts/active/PR-4425-followup.md` — Follow-up tasks

### Workflows
- `.github/workflows/codeql-analysis.yml` — CodeQL scanning
- `.github/workflows/security-scanning-suite.yml` — Security suite
- `.github/workflows/auto-fix-pr-check.yml` — Auto-fix validation

---

## 📞 ESCALATION

### Blockers
If any of these occur, escalate to @mbaetiong:
- Alert requires breaking API changes
- Alert fix introduces test failures
- Alert is false positive requiring suppression
- Alert requires external dependency changes

### Decision Points
Require human approval for:
- Suppressing alerts (false positives)
- Breaking changes to public APIs
- Major refactoring (>500 lines)
- Security policy changes

---

**Last Updated**: 2026-05-12T21:05Z (S968)  
**Next Review**: After Phase 1 completion  
**Owner**: @copilot (S968+)
