# PHASE 4.3 PRIORITY FIX LIST
**Top 40 High-Priority Link Validation Fixes**

---

## TIER 1: CRITICAL (P0) — MUST FIX THIS WEEK

### 1. [P0_001] Missing QUICKSTART.md — 8 files, 8 broken links

**Affected Files:**
- `docs/API_REFERENCE.md` → `./docs/guides/QUICKSTART.md`
- `docs/INGESTION_API_REFERENCE.md` → `./docs/guides/QUICKSTART.md`
- `docs/FAQ.md` → `./docs/guides/QUICKSTART.md`
- `docs/CONFIGURATION_GUIDE.md` → `./QUICKSTART.md`
- `docs/TROUBLESHOOTING.md` → `./QUICKSTART.md`
- `docs/RAG_API_REFERENCE.md` → `./QUICKSTART.md`
- `docs/INTEGRATION_GUIDE.md` → `./QUICKSTART.md`
- `docs/index.md` → `guides/quickstart.md`

**Resolution Steps:**
```
Option A: Create docs/QUICKSTART.md
1. Check if quickstart content exists elsewhere
2. Create docs/QUICKSTART.md with comprehensive getting-started guide
3. Keep docs/guides/quickstart.md as detailed version
4. Update index.md to use ./QUICKSTART.md
5. Update other references to use ./QUICKSTART.md

Option B: Use docs/guides/quickstart.md
1. Verify docs/guides/quickstart.md exists
2. Update all references to point to ./guides/quickstart.md
3. Add docs/QUICKSTART.md as redirect/symlink to avoid breaking old links

Recommended: Option A - Create unified QUICKSTART.md in docs/
```

**Effort:** 1-2 hours | **Impact:** HIGH | **Files Affected:** 8

---

## TIER 2: HIGH (P1) — RESOLVE THIS SPRINT

### 2. [P1_002] Create google-home-script-agent-DEPRECATION.md — 1 file

**Affected File:**
- `.github/agents/google-home-script-agent.md` → `../../GOOGLE_HOME_SCRIPT_AGENT_DEPRECATION.md`

**Resolution Steps:**
```
1. Create GOOGLE_HOME_SCRIPT_AGENT_DEPRECATION.md in repository root

Content template:
---
# Google Home Script Agent — Deprecation Notice

**Status:** DEPRECATED (as of 2026-01-15)
**Sunset Date:** 2026-06-15
**Reason:** Out-of-scope domain (smart-home automation)

## Details
- Zero ecosystem integration
- Purely aspirational design
- Not part of core _codex_ mission

## Archive Location
See: archive/deprecated-agents/google-home-script-agent/

## Migration Notes
If you're using this agent, consider these alternatives:
1. [Copilot Automation Framework](...) for general automation
2. [Home Automation Libraries](...) for smart home control
---
```

**Effort:** 30 minutes | **Impact:** MEDIUM | **Files Affected:** 1

---

### 3. [P1_003] Create energy-conversion-agent-DEPRECATION.md — 1 file

**Affected File:**
- `.github/agents/energy-conversion-agent.md` → `../../ENERGY_CONVERSION_AGENT_DEPRECATION.md`

**Resolution Steps:**
```
1. Create ENERGY_CONVERSION_AGENT_DEPRECATION.md in repository root

Content template:
---
# Energy Conversion Agent — Deprecation Notice

**Status:** DEPRECATED (as of 2026-01-15)
**Sunset Date:** 2026-06-15
**Reason:** Out-of-scope domain (energy systems)

## Details
- AI-enhanced agent for G2E (gas-to-electric) conversion
- Only 4 references, minimal integration (IQ=0.6558)
- Zero active use in codebase

## Archive Location
See: archive/deprecated-agents/energy-conversion-agent/

## Related
See: ENERGY_CONVERSION_AGENT_DEPRECATION.md for full details
---
```

**Effort:** 30 minutes | **Impact:** MEDIUM | **Files Affected:** 1

---

### 4. [P1_004] Create .codex/ARCHIVE_RECOVERY_PROCEDURES.md — 1 file

**Affected File:**
- `docs/RETENTION_POLICY_OPERATIONS_GUIDE.md` → `../.codex/ARCHIVE_RECOVERY_PROCEDURES.md`

**Resolution Steps:**
```
1. Create .codex/ARCHIVE_RECOVERY_PROCEDURES.md

Content should cover:
- Archive structure and organization
- Recovery process for different archive types
- Common failure scenarios and recovery steps
- Data integrity verification
- Disaster recovery examples
- Rollback procedures
- Troubleshooting guide

Example structure:
## Archive Types
- Session archives
- Artifact archives
- Backup archives

## Recovery Process
1. Locate archive
2. Verify integrity
3. Extract contents
4. Verify extraction
5. Restore to destination

## Troubleshooting
- Corrupt archives
- Missing metadata
- Permission issues
```

**Effort:** 2-3 hours | **Impact:** MEDIUM | **Files Affected:** 1

---

### 5. [P1_005] Fix docs/api/cli.md relative paths — 2 files, 2 broken links

**Affected File:**
- `docs/api/cli.md` → `../cli.md` (appears twice)

**Current Path:** docs/api/cli.md  
**Current Link:** ../cli.md (resolves to docs/cli.md)

**Resolution Steps:**
```
1. Locate the actual CLI documentation file
   - Check: docs/cli.md exists? 
   - Check: docs/CLI.md exists?
   - Check: docs/CLI_GUIDE.md exists?
   - Check: docs/guides/cli.md exists?

2. Update the link to correct location
   - If docs/cli.md exists: path is correct ✓
   - If ../../../docs/CLI_GUIDE.md: update to ../../CLI_GUIDE.md
   - Otherwise: create the missing docs/cli.md file

3. Verify link resolution
   - From docs/api/cli.md, ../cli.md should resolve to docs/cli.md
```

**Effort:** 30 minutes | **Impact:** MEDIUM | **Files Affected:** 1

---

### 6. [P1_006] Fix docs/LEARNING_PATHS.md CI.md reference — 1 file

**Affected File:**
- `docs/LEARNING_PATHS.md` → `./CI.md`

**Resolution Steps:**
```
1. Determine correct CI documentation location
   - Check: docs/CI.md exists?
   - Check: docs/ci/INDEX.md exists?
   - Check: docs/CI_GUIDE.md exists?

2. Update reference accordingly
   - If docs/ci/INDEX.md: change ./CI.md → ./ci/INDEX.md
   - If docs/CI_GUIDE.md: change ./CI.md → ./CI_GUIDE.md
   - Otherwise: create docs/CI.md
```

**Effort:** 30 minutes | **Impact:** MEDIUM | **Files Affected:** 1

---

### 7. [P1_007] Fix docs/validation/INDEX.md Tokenization reference — 1 file

**Affected File:**
- `docs/validation/INDEX.md` → `Tokenization_Validation.md`

**Resolution Steps:**
```
1. Add relative path prefix
   - Change: Tokenization_Validation.md
   - To: ./Tokenization_Validation.md

2. Verify file exists at docs/validation/Tokenization_Validation.md
3. If file is in different location, update accordingly
```

**Effort:** 15 minutes | **Impact:** LOW | **Files Affected:** 1

---

### 8. [P1_008] Fix docs/ci/README.md CI.md reference — 1 file

**Affected File:**
- `docs/ci/README.md` → `../CI.md`

**Resolution Steps:**
```
1. Determine correct CI documentation location from docs/ci/ directory
   - Check: docs/CI.md exists?
   - Check: docs/ci/INDEX.md exists? (local reference)

2. Update reference
   - If docs/CI.md: update to ../../CI.md
   - If docs/ci/INDEX.md: update to ./INDEX.md
   - Otherwise: create missing docs/CI.md
```

**Effort:** 30 minutes | **Impact:** MEDIUM | **Files Affected:** 1

---

### 9. [P1_009] Fix docs/admin/REPOSITORY_SECURITY_SETUP.md reference — 1 file

**Affected File:**
- `docs/admin/REPOSITORY_SECURITY_SETUP.md` → `../security/INCIDENT_RESPONSE.md`

**Resolution Steps:**
```
1. Verify directory structure
   - Does docs/security/ directory exist?
   - Does docs/security/INCIDENT_RESPONSE.md exist?

2. Update path if needed
   - If in docs/security/: path might be correct ✓
   - If elsewhere: update to correct relative path
   - Otherwise: create docs/security/INCIDENT_RESPONSE.md

3. Consider: should this be admin/INCIDENT_RESPONSE.md instead?
```

**Effort:** 30 minutes | **Impact:** MEDIUM | **Files Affected:** 1

---

### 10. [P1_010] Fix docs/guides/examples.md architecture reference — 1 file

**Affected File:**
- `docs/guides/examples.md` → `../docs/human-facing/architecture.md`

**Issue:** Incorrect path traversal (../../docs/ is invalid)

**Resolution Steps:**
```
1. Correct path: ../docs/human-facing/architecture.md
   From docs/guides/examples.md, need to go:
   - ../docs/  = /docs/docs/ (WRONG - double directory)
   - ../human-facing/ = /docs/human-facing/ (CORRECT)
   - OR: ../../docs/human-facing/ if human-facing is elsewhere

2. Fix to correct path
   - If docs/human-facing/architecture.md exists: 
     change to ../human-facing/architecture.md
   - Otherwise: verify actual path to architecture docs

3. Verify resolution
```

**Effort:** 30 minutes | **Impact:** MEDIUM | **Files Affected:** 1

---

### 11. [P1_011] Fix docs/tutorials/quickstart.md architecture reference — 1 file

**Affected File:**
- `docs/tutorials/quickstart.md` → `../architecture.md`

**Resolution Steps:**
```
1. Verify file location
   - Check: docs/architecture.md exists?
   - Check: docs/ARCHITECTURE.md exists?
   - Check: docs/architecture/INDEX.md exists?

2. Update link accordingly
   - If docs/architecture.md: path is correct ✓ (verify file existence)
   - If docs/ARCHITECTURE.md: change ../architecture.md to ../ARCHITECTURE.md
   - If docs/architecture/INDEX.md: change to ../architecture/INDEX.md
   - Otherwise: locate the actual architecture documentation

3. Create missing file if needed
```

**Effort:** 30 minutes | **Impact:** MEDIUM | **Files Affected:** 1

---

## TIER 3: MEDIUM (P2) — RESOLVE NEXT SPRINT

### 12-40: Process Improvements & Automation

These items represent process and tooling improvements to prevent future broken links:

#### Process Items (12-15)
- Implement pre-commit hook validation
- Add CI/CD link validation workflow
- Create documentation change review process
- Establish URL standardization guidelines

#### Documentation Items (16-25)
- Audit all external URLs for validity
- Update documentation standards
- Create contribution guide for doc changes
- Build documentation structure map
- Implement cross-reference index

#### Automation Items (26-35)
- Set up monthly link health reports
- Build documentation dependency graph
- Create automated redirect handling
- Implement link rot detection

#### Monitoring Items (36-40)
- Add link validation to PR checks
- Set up documentation health dashboard
- Create link validation metrics tracking
- Build broken link alerting system
- Implement quarterly link health audit schedule

---

## FIX COMPLETION CHECKLIST

### Week 1 (Critical Fixes)
- [ ] Resolve QUICKSTART.md references (P0_001)
- [ ] Create google-home-script deprecation notice (P1_002)
- [ ] Create energy-conversion deprecation notice (P1_003)

### Week 2 (High Priority)
- [ ] Create archive recovery documentation (P1_004)
- [ ] Fix all relative path references (P1_005 through P1_011)
- [ ] Run validation and confirm all links resolve

### Week 3 (Process Improvements)
- [ ] Enable pre-commit hook
- [ ] Add CI/CD validation
- [ ] Create documentation review process

### Week 4 (Monitoring)
- [ ] Set up automated health reports
- [ ] Begin monthly audits
- [ ] Monitor PR link validation

---

## EFFORT SUMMARY

| Tier | Count | Total Effort | Start Date |
|------|-------|-------------|------------|
| **P0 CRITICAL** | 1 | 1-2 hrs | This Week |
| **P1 HIGH** | 10 | 5-7 hrs | This Sprint |
| **P2 MEDIUM** | 29 | 10-15 hrs | Next Sprint |
| **TOTAL** | **40** | **16-24 hrs** | Immediate |

---

**Generated:** 2026-02-25  
**Phase:** 4.3 Link Validation & Reference Integrity  
**Status:** ✅ AUDIT COMPLETE
