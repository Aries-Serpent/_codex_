# IP-005: Dependency Security Updates Implementation Planset

**Created:** 2026-01-16  
**Status:** 📋 Ready for Execution  
**Priority:** CRITICAL (Security vulnerabilities)  
**Agent Type:** AI Agent with Human Admin tasks clearly identified  
**Policy Compliance:** AI Agency Policy v1.0.0

---

## Executive Summary

This planset provides end-to-end implementation guidance for applying IP-005 dependency security updates identified in the audit. The plan addresses 26 known vulnerabilities across 11 packages, with clear separation of Human Admin tasks (manual configuration) and AI Agent autonomous tasks.

### Security Impact

- **6 High-Priority** vulnerabilities (cryptography, jinja2, setuptools - RCE risks)
- **14 Medium-Priority** vulnerabilities (various packages - DoS, bypass risks)
- **6 Low-Priority** vulnerabilities (XSS, sandbox escape)

---

## Human Admin Tasks vs AI Agent Tasks

### Human Admin Planset (Manual Steps Required)

These tasks require human intervention and CANNOT be automated by AI Agent:

#### Task HA-1: GitHub Environment Configuration
**Blocker:** Requires repository admin access and manual configuration
**Best-Effort Alternative:** AI Agent can generate configuration templates

**Manual Steps:**
1. Review security advisory reports
2. Approve dependency version updates in security policy
3. Configure GitHub Dependabot alerts settings
4. Review and approve any breaking changes

**AI Agent Support:**
- Generate security advisory summary
- Create configuration templates
- Document breaking changes
- Provide testing recommendations

---

#### Task HA-2: Production Deployment Approval
**Blocker:** Requires human approval for production deployment
**Best-Effort Alternative:** AI Agent can prepare staging deployment

**Manual Steps:**
1. Review test results and coverage reports
2. Approve staging deployment
3. Monitor staging for issues
4. Approve production rollout

**AI Agent Support:**
- Execute all pre-deployment tests
- Generate deployment readiness report
- Create rollback procedures
- Document monitoring checklist

---

### AI Agent Planset (Autonomous Tasks)

These tasks can be executed autonomously by AI Agent:

#### Phase 1: Update Critical Security Dependencies

**Pre-commit 1-2: Update High-Priority Packages**

**Goal:** Update cryptography, jinja2, and setuptools to fix critical RCE vulnerabilities

**Tasks:**
- [ ] Update `requirements.txt`: `cryptography==41.0.7` → `cryptography>=43.0.1`
- [ ] Update `requirements.txt`: `jinja2==3.1.2` → `jinja2>=3.1.6`
- [ ] Update `pyproject.toml`: `setuptools>=67` → `setuptools>=78.1.1`
- [ ] Run dependency resolver to check for conflicts
- [ ] Document version changes in CHANGELOG.md

**Success Criteria:**
- [ ] All three packages updated successfully
- [ ] No dependency conflicts detected
- [ ] Requirements files validated with pip-compile

**Files to Modify:**
- `requirements.txt` (3 lines)
- `pyproject.toml` (1 line)
- `CHANGELOG.md` (add entry)

**Estimated Complexity:** Low (direct version updates)

**Alternative if Blocked:**
- Document any dependency conflicts
- Propose alternative versions
- Create compatibility testing plan

---

**Pre-commit 3-4: Validate Critical Updates**

**Goal:** Run comprehensive tests to ensure no regressions from security updates

**Tasks:**
- [ ] Install updated dependencies in test environment
- [ ] Run full test suite (1700+ tests)
- [ ] Execute security scanning (CodeQL, pip-audit)
- [ ] Verify no new vulnerabilities introduced
- [ ] Test backward compatibility with existing code

**Success Criteria:**
- [ ] All 1700+ tests passing
- [ ] Zero new security vulnerabilities
- [ ] No breaking changes detected
- [ ] Performance benchmarks maintained

**Testing Commands:**
```bash
# Install updated dependencies
pip install -r requirements.txt

# Run test suite
pytest tests/ --cov=src --cov-report=html

# Security scan
pip-audit --format=json > audit_post_update.json

# Compare vulnerability counts
python scripts/compare_audits.py audit_pre_update.json audit_post_update.json
```

**Alternative if Blocked:**
- Document any test failures with root cause
- Create issue tickets for breaking changes
- Propose incremental update strategy

---

#### Phase 2: Update Medium-Priority Dependencies

**Pre-commit 5-6: Update Networking and File I/O Packages**

**Goal:** Update certifi, filelock, idna, requests, urllib3, pip

**Tasks:**
- [ ] Update `requirements.txt` or `requirements-dev.txt`:
  - `certifi>=2024.7.4` (was 2023.11.17)
  - `filelock>=3.20.3` (was 3.20.0)
  - `idna>=3.7` (was 3.6)
  - `requests>=2.32.4` (currently >=2.31.0)
  - `urllib3>=2.6.3` (was 2.0.7)
  - `pip>=25.3` (was 24.0)
- [ ] Run dependency resolver
- [ ] Update CHANGELOG.md

**Success Criteria:**
- [ ] All 6 packages updated
- [ ] Dependency tree validated
- [ ] No conflicts with other packages

**Files to Modify:**
- `requirements.txt` or `requirements-dev.txt` (6 lines)
- `CHANGELOG.md` (add entry)

**Alternative if Blocked:**
- Update packages individually
- Document any conflicts
- Use compatible version ranges

---

**Pre-commit 7-8: Validate Medium-Priority Updates**

**Goal:** Test networking, file I/O, and HTTP functionality

**Tasks:**
- [ ] Run integration tests for network operations
- [ ] Test file locking mechanisms
- [ ] Verify HTTP/HTTPS requests working
- [ ] Test certificate validation
- [ ] Execute pip operations in test environment

**Success Criteria:**
- [ ] All integration tests passing
- [ ] Network operations functional
- [ ] No SSL/TLS errors
- [ ] File operations working correctly

**Testing Focus:**
```bash
# Test network operations
pytest tests/integration/ -k "network or http or request"

# Test file operations
pytest tests/integration/ -k "file or lock"

# Test pip operations
pip install --dry-run -r requirements.txt
```

**Alternative if Blocked:**
- Test individual components in isolation
- Document any compatibility issues
- Propose workarounds or patches

---

#### Phase 3: Update Low-Priority and Remaining Dependencies

**Pre-commit 9-10: Update Remaining Packages**

**Goal:** Update twisted and configobj to address remaining vulnerabilities

**Tasks:**
- [ ] Update `requirements-optional.txt` or main requirements:
  - `twisted>=24.7.0` (was 24.3.0)
  - `configobj>=5.0.9` (was 5.0.8)
- [ ] Run dependency resolver
- [ ] Update CHANGELOG.md

**Success Criteria:**
- [ ] Both packages updated
- [ ] No dependency conflicts
- [ ] Optional dependencies validated

**Files to Modify:**
- `requirements-optional.txt` or `requirements.txt` (2 lines)
- `CHANGELOG.md` (add entry)

**Alternative if Blocked:**
- Mark packages as optional if not critical
- Document workarounds for known issues
- Propose alternative packages

---

**Pre-commit 11-12: Final Validation and Documentation**

**Goal:** Complete end-to-end validation and update all documentation

**Tasks:**
- [ ] Run complete test suite (all 1700+ tests)
- [ ] Execute full security scan suite
- [ ] Generate vulnerability comparison report
- [ ] Update SECURITY.md with new baseline
- [ ] Update dependency documentation
- [ ] Create upgrade guide for users

**Success Criteria:**
- [ ] All tests passing (100% pass rate)
- [ ] Vulnerability count: 26 → 0
- [ ] Documentation complete and accurate
- [ ] Upgrade guide tested

**Documentation Updates:**
- `SECURITY.md` - Update vulnerability baseline
- `docs/DEPENDENCY_MANAGEMENT.md` - Add upgrade guide
- `.codex/plans/IP-005_DEPENDENCY_AUDIT.md` - Mark as COMPLETE
- `CHANGELOG.md` - Comprehensive entry with all updates

**Final Verification:**
```bash
# Complete test suite
nox -s tests

# Security verification
pip-audit --format=json > final_audit.json
python scripts/verify_zero_vulnerabilities.py final_audit.json

# Generate comparison report
python scripts/generate_vulnerability_report.py \
  --before .codex/qa_walkthrough/ip005_pip_audit_report.json \
  --after final_audit.json \
  --output IP-005_COMPLETION_REPORT.md
```

**Alternative if Blocked:**
- Document any remaining vulnerabilities with justification
- Create follow-up tickets for unresolved issues
- Implement compensating controls

---

### Review, Verify, Commit

**Final Checklist:**
- [ ] All 26 vulnerabilities addressed
- [ ] 100% test pass rate maintained
- [ ] Zero new vulnerabilities introduced
- [ ] Documentation complete
- [ ] CHANGELOG.md updated
- [ ] Security baseline updated
- [ ] Upgrade guide created
- [ ] Human Admin tasks documented for review

---

## AI Agency Policy Compliance

### Comprehensive Issue Resolution
✅ All 26 vulnerabilities addressed systematically
✅ Root cause (outdated dependencies) resolved
✅ Prevention strategy (automated scanning) included

### Planning Before Execution
✅ End-to-end plan with phases and pre-commits
✅ Clear success criteria for each phase
✅ Dependencies and order documented

### No Deferral Without Plan
✅ All blockers identified (Human Admin tasks)
✅ Best-effort alternatives documented for each blocker
✅ Minimum 5 iterations planned (12 pre-commits)

### Timeline Terminology
✅ Uses pre-commit/commit cycles (not time-based)
✅ Organized into Phases (not weeks/months)
✅ Clear steps (not hours/days)

---

## Blocker Documentation and Alternatives

### Known Blockers

1. **Human Admin Approval Required**
   - **Task:** HA-1, HA-2
   - **Blocker:** Requires repository admin access
   - **AI Agent Alternative:** Generate templates, prepare reports, create recommendations

2. **Potential Dependency Conflicts**
   - **Task:** Phase 1-3 updates
   - **Blocker:** Breaking changes in major versions
   - **AI Agent Alternative:** Incremental updates, compatibility testing, version pinning

3. **Test Failures from Updates**
   - **Task:** Validation phases
   - **Blocker:** Unexpected regressions
   - **AI Agent Alternative:** Isolation testing, rollback procedures, compatibility patches

---

## Success Metrics

### Quantitative
- Vulnerabilities: 26 → 0 (100% reduction)
- Test pass rate: 100% maintained
- Security scan: PASS
- Coverage: ≥72% maintained

### Qualitative
- All critical RCE vulnerabilities eliminated
- No breaking changes introduced
- Documentation complete and accurate
- Smooth upgrade path for users

---

## Cognitive Brain Context

This planset is designed for the cognitive brain to execute autonomously with the following understanding:

1. **Security Priority:** Critical vulnerabilities require immediate action
2. **Testing First:** No updates without comprehensive validation
3. **Incremental Approach:** Phase-by-phase updates reduce risk
4. **Human Checkpoints:** Clear identification of manual approval gates
5. **Rollback Ready:** All phases include alternative strategies

The cognitive brain should approach this work with:
- **Risk awareness:** Security vs stability balance
- **Test discipline:** Validate everything before proceeding
- **Documentation focus:** Keep stakeholders informed
- **Flexibility:** Use alternatives when blocked

---

## Estimated Effort

- **AI Agent Autonomous Work:** 12 pre-commits (3 phases)
- **Human Admin Manual Tasks:** 2 tasks (configuration + approval)
- **Total Phases:** 3 phases
- **Complexity:** Medium (dependency updates with testing)

---

## Next Steps

For AI Agent to begin autonomous execution:

```markdown
@copilot Begin IP-005 Dependency Security Updates following `.codex/plans/IP-005_DEPENDENCY_UPDATES_PLANSET.md`.

Start with Phase 1: Update Critical Security Dependencies (cryptography, jinja2, setuptools).

**Policy Compliance:**
- Follow `.codex/CODEBASE_AGENCY_POLICY.md`
- Use pre-commit/commit terminology
- 5+ self-review iterations
- Address ALL issues discovered
- Document blockers with alternatives

**Success Criteria:**
- ✅ All 26 vulnerabilities eliminated
- ✅ 100% test pass rate maintained
- ✅ Zero new vulnerabilities
- ✅ Documentation complete
```

---

**Status:** Ready for autonomous AI Agent execution with documented Human Admin checkpoints
