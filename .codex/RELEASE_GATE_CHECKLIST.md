# RELEASE GATE CHECKLIST

**Version**: 0.1.0  
**Created**: 2026-07-07  
**Last Updated**: 2026-07-07  
**Authority**: @mbaetiong  
**Status**: Template Ready for Pre-Release

---

## PURPOSE

This checklist must be completed and approved **before any release** of Cognitive Brain. It validates:
1. All CVE exceptions current (not expired)
2. No new unhandled CVEs in release
3. All suppressions justified
4. Manifest integrity verified
5. SBOM generated (P1.3 dependency)
6. Offline bootstrap validation complete
7. Profile smoke tests passing

---

## PRE-RELEASE VALIDATION (MANDATORY)

### 1. CVE Exception Governance ✅

#### 1.1 Expiry Date Verification
- [ ] Run: `python scripts/ci/check_cve_drift.py --check-expiry`
- [ ] Output: "No expired exceptions"
- [ ] All exceptions have dates > release date
- [ ] Exceptions with <30 days remaining are documented with remediation plan
- [ ] **Owner**: @mbaetiong
- [ ] **Deadline**: 24 hours before release

#### 1.2 New CVE Detection
- [ ] Run: `pip-audit --format json --file uv.lock > cve-report.json`
- [ ] Parse report: All CVEs have entries in `.codex/VULNERABILITY_EXCEPTION_REGISTRY.md`
- [ ] Undocumented CVEs: **FAIL RELEASE** - add exception or fix dependency
- [ ] **Owner**: @mbaetiong
- [ ] **Deadline**: 24 hours before release

#### 1.3 Exception Registry Current
- [ ] File exists: `.codex/VULNERABILITY_EXCEPTION_REGISTRY.md`
- [ ] All documented CVEs: owner, approved_at, expires_at fields present
- [ ] Remediation plans documented for HIGH risk exceptions
- [ ] Cross-referenced with `.pip-audit-exceptions` TOML
- [ ] **Owner**: @mbaetiong
- [ ] **Deadline**: 24 hours before release

### 2. Suppression Rules Validation ✅

#### 2.1 Bandit Suppressions
- [ ] All skipped rules in `.bandit` justified in comments
- [ ] No orphaned `# nosec` comments in source code
- [ ] Run: `bandit -r src/ --configfile .bandit --severity-level medium` → zero medium/high issues
- [ ] **Owner**: codeql-alert-resolution-agent
- [ ] **Deadline**: 48 hours before release

#### 2.2 Semgrep Suppressions
- [ ] All patterns in `.semgrepignore` documented
- [ ] Run: `semgrep --config p/security-audit --exclude-dir .semgrepignore src/` → zero high-priority violations
- [ ] **Owner**: codeql-alert-resolution-agent
- [ ] **Deadline**: 48 hours before release

#### 2.3 CodeQL Suppressions
- [ ] All filters in `.codeql/codeql-config.yml` justified in file comments
- [ ] False positive justifications documented
- [ ] Run: CodeQL database analysis → verify suppressed alerts match documented FPs
- [ ] **Owner**: codeql-alert-resolution-agent
- [ ] **Deadline**: 48 hours before release

#### 2.4 Suppression Audit Report
- [ ] File exists: `.codex/SUPPRESSION_RULES_AUDIT_REPORT.md`
- [ ] Audit completed in last 90 days
- [ ] All suppressions marked ✅ VALID
- [ ] No orphaned or undocumented suppressions
- [ ] **Owner**: codeql-alert-resolution-agent
- [ ] **Deadline**: 48 hours before release

### 3. Manifest Generation & Verification ✅

#### 3.1 Manifest Template
- [ ] File exists: `.codex/RELEASE_MANIFEST_TEMPLATE.json`
- [ ] JSON schema with all required fields:
  - `version`, `timestamp`, `created_by`, `signature_method`
  - `profiles`: [core, runtime, full]
  - `wheels`: array with name/sha256/size/profiles
  - `metadata`: integrity_hash, release_notes_url
- [ ] **Owner**: codeql-alert-resolution-agent
- [ ] **Deadline**: 24 hours before release

#### 3.2 Manifest Generation Script
- [ ] File exists: `scripts/build/generate_manifest.py`
- [ ] Generates manifests for all 3 profiles:
  - `v0.1.0_RELEASE_MANIFEST_CORE.json`
  - `v0.1.0_RELEASE_MANIFEST_RUNTIME.json`
  - `v0.1.0_RELEASE_MANIFEST_FULL.json`
- [ ] All wheels hashed with SHA256
- [ ] Signed with HMAC-SHA256 (CODEX_MASTER_KEY environment variable)
- [ ] Archived to `.codex/manifests/`
- [ ] **Owner**: codeql-alert-resolution-agent
- [ ] **Deadline**: 24 hours before release

#### 3.3 Manifest Verification
- [ ] File exists: `scripts/deploy/verify_manifest.py`
- [ ] Test 1: Verify signature on valid manifest → **PASS**
- [ ] Test 2: Verify signature on tampered manifest → **FAIL with clear error**
- [ ] Test 3: Hash wheels and compare against manifest → **all match**
- [ ] Test 4: Missing wheel in manifest → **caught and reported**
- [ ] Audit log created: `.codex/security/manifest_audit.log`
- [ ] **Owner**: codeql-alert-resolution-agent
- [ ] **Deadline**: 24 hours before release

#### 3.4 Manifest Release Artifacts
- [ ] Manifests uploaded to GitHub release page
- [ ] SHAs documented in release notes
- [ ] Manifests linked from `.codex/manifests/` directory (git-tracked)
- [ ] Release notes include:
  - Core profile manifest link
  - Runtime profile manifest link
  - Full profile manifest link
  - SHA256 hashes for verification
  - Verification command: `python scripts/deploy/verify_manifest.py --manifest <url>`
- [ ] **Owner**: CI release workflow
- [ ] **Deadline**: At release time

### 4. Offline Bootstrap Validation (P1 Dependency, can start early)

#### 4.1 Core OODA Module Hardening
- [ ] File: `src/cognitive_brain/base.py` - no import-time network calls
- [ ] File: `src/cognitive_brain/ooda.py` - 10 core APIs load without network
- [ ] All dynamic imports removed or wrapped in try/except
- [ ] No model loading at import time
- [ ] **Owner**: autonomous-test-healer-agent (Lane 2)
- [ ] **Deadline**: Day 14 (P0 gate)

#### 4.2 Offline Module Manifest
- [ ] File exists: `.codex/OFFLINE_MODULE_MANIFEST.md`
- [ ] All 46 cognitive_brain modules classified as [OFFLINE] or [ONLINE]
- [ ] Core profile modules: [OFFLINE]
- [ ] Runtime profile modules: [OFFLINE] or [ONLINE]
- [ ] Full profile modules: any combination
- [ ] **Owner**: autonomous-test-healer-agent (Lane 2)
- [ ] **Deadline**: Day 14 (P0 gate)

#### 4.3 Offline Bootstrap Tests
- [ ] Test file: `tests/offline/test_core_bootstrap.py`
- [ ] Test matrix: 3 profiles × 2 Python versions = 6 test runs
- [ ] All 10 core APIs load successfully
- [ ] No network requests made
- [ ] Test result: ✅ ALL PASS
- [ ] **Owner**: autonomous-test-healer-agent (Lane 2)
- [ ] **Deadline**: Day 21 (P0 gate)

#### 4.4 Wheelhouse Generation & Verification
- [ ] Generated wheelhouses exist:
  - `wheelhouse_core.tar.gz`
  - `wheelhouse_runtime.tar.gz`
  - `wheelhouse_full.tar.gz`
- [ ] Each wheelhouse hash-verified with manifest
- [ ] Offline install test on all 3 OS targets (Linux/macOS/Windows)
- [ ] Test result: ✅ All profiles install offline successfully
- [ ] **Owner**: autonomous-test-healer-agent (Lane 2)
- [ ] **Deadline**: Day 21 (P0 gate)

### 5. Profile Smoke Tests ✅

#### 5.1 Core Profile
- [ ] All required dependencies present
- [ ] Import test: `from cognitive_brain import OODA` → succeeds
- [ ] Core APIs accessible: list_patterns, validate_pattern, apply_pattern
- [ ] Test result: ✅ PASS
- [ ] **Owner**: unified-coverage-agent (Lane 1)
- [ ] **Deadline**: Day 21 (P0 gate)

#### 5.2 Runtime Profile
- [ ] All core + runtime dependencies present
- [ ] Import test: `from cognitive_brain.rag import RAGManager` → succeeds
- [ ] ML inference callable (no actual inference, just API check)
- [ ] Test result: ✅ PASS
- [ ] **Owner**: unified-coverage-agent (Lane 1)
- [ ] **Deadline**: Day 21 (P0 gate)

#### 5.3 Full Profile
- [ ] All dependencies present
- [ ] Import test: Full ecosystem imports
- [ ] Dev tools available (testing, linting, etc.)
- [ ] Test result: ✅ PASS
- [ ] **Owner**: unified-coverage-agent (Lane 1)
- [ ] **Deadline**: Day 21 (P0 gate)

### 6. SBOM Generation (P1 Dependency, starts Day 22)

#### 6.1 SBOM Configuration
- [ ] Tool: cyclonedx-py installed
- [ ] Configuration: `.codex/sbom-config.json` present
- [ ] Output format: SPDX JSON v1.3
- [ ] **Owner**: packaging-validation-agent (Lane 4)
- [ ] **Deadline**: Day 42 (P1 gate)

#### 6.2 SBOM Generation
- [ ] Run: `cyclonedx-py -r --format json > dist/sbom_v0.1.0.json`
- [ ] SBOM generated for each profile (core, runtime, full)
- [ ] SBOM includes all transitive dependencies
- [ ] SBOM includes license information
- [ ] **Owner**: packaging-validation-agent (Lane 4)
- [ ] **Deadline**: Day 42 (P1 gate)

#### 6.3 SBOM Validation
- [ ] SBOM is valid JSON
- [ ] SBOM includes spec_version, serialNumber fields
- [ ] All wheels in manifest have corresponding SBOM entries
- [ ] CVE exceptions documented in SBOM metadata
- [ ] **Owner**: packaging-validation-agent (Lane 4)
- [ ] **Deadline**: Day 42 (P1 gate)

#### 6.4 SBOM Release Artifacts
- [ ] SBOM uploaded to GitHub release page
- [ ] SBOM hash included in manifest JSON
- [ ] Release notes link to SBOM
- [ ] **Owner**: CI release workflow
- [ ] **Deadline**: At release time (Day 42+)

---

## APPROVAL WORKFLOW

### Sign-Off Authority

| Role | Sign-Off Required | Authority | Timeline |
|------|------------------|-----------|----------|
| **Release Lead** | ✅ **MUST PASS** | @mbaetiong | 24 hours before |
| **Security Lead** | ✅ **MUST PASS** | @security-team | 24 hours before |
| **Package Manager** | ✅ **MUST PASS** | @packaging-lead | 12 hours before |
| **QA Lead** | ✅ **MUST PASS** | @qa-lead | 12 hours before |

### Failure Escalation

| Failure Type | Action | Escalation |
|--------------|--------|-----------|
| Expired CVE exception | FAIL RELEASE | Re-approve or fix dependency |
| New undocumented CVE | FAIL RELEASE | Add exception or fix dependency |
| Manifest signature invalid | FAIL RELEASE | Regenerate manifest |
| Offline bootstrap test fails | FAIL RELEASE | Fix offline mode in code |
| Suppression audit fails | FAIL RELEASE | Update suppression rules |
| Profile smoke test fails | FAIL RELEASE | Fix profile configuration |

---

## QUARTERLY AUDIT SCHEDULE

### Scheduled Review Dates
- **Q1 2027** (Jan 1): Full audit of all exceptions
- **Q2 2027** (Apr 1): Full audit of all exceptions
- **Q3 2027** (Jul 1): Full audit of all exceptions
- **Q4 2027** (Oct 1): Full audit of all exceptions

### Audit Process
1. Run: `python scripts/ci/check_cve_drift.py --quarterly-audit`
2. Review findings
3. Update VULNERABILITY_EXCEPTION_REGISTRY.md
4. Create GitHub issue if remediation needed
5. Close issue after remediation + re-approval

---

## RELEASE NOTES TEMPLATE

```markdown
## v0.1.0 Release

### Security & Integrity
- ✅ Manifests generated and hash-verified
- ✅ All CVE exceptions documented and non-expired
- ✅ Offline bootstrap validated on all 3 profiles
- ✅ SBOM generated with license compliance check

### Manifest Verification
To verify wheel integrity before installation:

\`\`\`bash
python scripts/deploy/verify_manifest.py \
  --manifest https://github.com/Aries-Serpent/_codex_/releases/download/v0.1.0/v0.1.0_RELEASE_MANIFEST_CORE.json \
  --wheelhouse ./wheelhouse/ \
  --master-key $CODEX_MASTER_KEY
\`\`\`

### Known Vulnerabilities
- CVE-2024-35515 (sqlitedict): [Exception details]
- TORCH-2024-BACKLOG: [Exception details]

See `.codex/VULNERABILITY_EXCEPTION_REGISTRY.md` for full details.

### Offline Installation
All 3 profiles support offline installation. See `docs/DEPLOYMENT.md` for instructions.
```

---

## RELATED DOCUMENTS

- `.codex/VULNERABILITY_EXCEPTION_REGISTRY.md` - CVE exception registry
- `.codex/SUPPRESSION_RULES_AUDIT_REPORT.md` - Suppression audit
- `.codex/RELEASE_MANIFEST_TEMPLATE.json` - Manifest template
- `scripts/build/generate_manifest.py` - Manifest generation
- `scripts/deploy/verify_manifest.py` - Manifest verification
- `scripts/ci/check_cve_drift.py` - CI gate for CVE drift

---

## CONTACT & ESCALATION

- **Gate Owner**: @mbaetiong
- **Security Review**: @security-team
- **Questions**: File issue #security:release-gate
- **Emergency**: Ping @mbaetiong on Slack

---

**Status**: ✅ READY FOR RELEASE PREPARATION
