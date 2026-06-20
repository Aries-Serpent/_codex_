# TRACK 1: GitHub Release Automation Agent Brief

**Campaign:** Comprehensive Automation Campaign (Discussion #4872)  
**Track:** 1 - GitHub Release Creation & Announcement (Item 4)  
**Agent Assignment:** autonomous-test-healer-agent (or general-purpose)  
**Agent ID:** automation-campaign-track1-release  
**Duration:** 5-6 hours  
**Timeline:** Phase 1 Quick Wins (parallel with Tracks 2-3)

---

## EXECUTIVE BRIEF

Automate GitHub release creation, announcement, and artifact generation. The goal is to create reusable workflow templates and scripts that extract release notes, generate SBOMs, create attestations, and publish releases with minimal human intervention.

**Input:** Phase 7D certification reports, CHANGELOG.md  
**Output:** Workflow template + SBOM generation script + release creation automation  
**Success Criteria:** Workflow template functional, SBOM script tested, dry-run release successful

---

## DETAILED TASKS

### Task 1.1: Release Notes Extraction & Parsing (1 hour)

**Objective:** Create a script that extracts release notes from Phase 7D certification and CHANGELOG.md

**Actions:**
1. Read `.codex/PHASE_7D_EXECUTION_SUMMARY.txt` and `.codex/PHASE_7D_DOCKER_BUILD_REPORT.md`
2. Read `CHANGELOG.md` to extract the latest version entry
3. Create `scripts/deployment/extract_release_notes.py`:
   - Parse Phase 7D metrics and achievements
   - Extract version info from CHANGELOG.md
   - Generate professional release notes markdown
   - Format for GitHub release body (handles 65k char limit)
4. Create `scripts/deployment/validate_release_notes.py`:
   - Verify release notes contain key sections (Features, Fixes, Security, Breaking Changes)
   - Check for required metadata (version, date, author)
   - Generate validation report

**Deliverables:**
- `scripts/deployment/extract_release_notes.py` (functional, tested)
- `scripts/deployment/validate_release_notes.py` (functional, tested)
- `.codex/TRACK_1_TASK_1_RELEASE_NOTES_EXTRACTION.md` (execution report)

**Success Criteria:**
- [ ] Script extracts release notes from both sources
- [ ] Output format valid for GitHub release API
- [ ] Validation script working
- [ ] Test run successful on latest CHANGELOG entry

---

### Task 1.2: SBOM Generation & Management (1.5 hours)

**Objective:** Ensure SBOM generation script is functional and integrated with release workflow

**Actions:**
1. Review existing `scripts/generate_sbom.py` (if it exists) or create new one
2. Verify SBOM generation:
   - Generates SBOMs for all Docker image variants (5 images from Phase 7D)
   - Output formats: JSON (CycloneDX/SPDX) + YAML + text
3. Create `scripts/deployment/validate_sbom_completeness.py`:
   - Verify all components listed
   - Check for duplicate entries
   - Validate version numbers
   - Generate completeness report
4. Ensure SBOMs are committed to `.codex/sbom/` directory
5. Document SBOM generation procedure in SBOM_GENERATION_GUIDE.md

**Deliverables:**
- `scripts/generate_sbom.py` (verified working)
- `scripts/deployment/validate_sbom_completeness.py` (functional)
- `.codex/SBOM_GENERATION_GUIDE.md` (documentation)
- `.codex/TRACK_1_TASK_2_SBOM_REPORT.md` (execution report)

**Success Criteria:**
- [ ] SBOM generation for all 5 Docker variants successful
- [ ] Output in multiple formats (JSON, YAML, text)
- [ ] Validation script confirms completeness
- [ ] SBOMs committed and versioned

---

### Task 1.3: Attestations & Provenance Records (1.5 hours)

**Objective:** Generate attestations and provenance records for release artifacts

**Actions:**
1. Create `scripts/deployment/generate_attestations.py`:
   - Generate artifact attestation files (SLSA format)
   - Include build environment metadata
   - Sign with repository credentials
   - Output to `.codex/attestations/`
2. Create `scripts/deployment/generate_provenance.py`:
   - Generate software provenance record
   - Include source code commit SHA
   - Include build timestamp
   - Include builder identity (GitHub Actions)
3. Integrate with GitHub's OIDC token system for signing
4. Document attestation verification procedure

**Deliverables:**
- `scripts/deployment/generate_attestations.py` (functional)
- `scripts/deployment/generate_provenance.py` (functional)
- `.codex/ATTESTATION_GENERATION_GUIDE.md` (documentation)
- `.codex/TRACK_1_TASK_3_ATTESTATIONS_REPORT.md` (execution report)

**Success Criteria:**
- [ ] Attestation generation script functional
- [ ] Provenance records generated with all required metadata
- [ ] Signatures valid
- [ ] Documentation complete

---

### Task 1.4: GitHub Release Workflow Template Creation (1.5 hours)

**Objective:** Create reusable GitHub Actions workflow for automated release creation

**Actions:**
1. Create `.github/workflows/automated-release-creation.yml`:
   ```yaml
   # Inputs:
   # - version: Release version (e.g., v0.1.0)
   # - dry_run: If true, create draft release; if false, publish immediately
   # 
   # Outputs:
   # - release_id: Created release ID
   # - release_url: URL to created release
   # 
   # Steps:
   # 1. Extract release notes
   # 2. Generate SBOM
   # 3. Generate attestations
   # 4. Generate GitHub Discussions announcement template
   # 5. Create GitHub release (with artifacts)
   # 6. Upload artifacts to release
   # 7. Generate release audit log
   ```

2. Implement all workflow steps:
   - Call extract_release_notes.py
   - Call generate_sbom.py
   - Call generate_attestations.py
   - Call gh release create
   - Handle dry-run vs. live modes
   - Error handling and rollback

3. Add approval gate for editorial review:
   - Environment: `release-approval`
   - Require manual approval before final publish
   - Approval comment captures editorial changes

**Deliverables:**
- `.github/workflows/automated-release-creation.yml` (complete workflow)
- `.codex/AUTOMATED_RELEASE_CREATION_GUIDE.md` (operational guide)
- `.codex/TRACK_1_TASK_4_WORKFLOW_REPORT.md` (execution report)

**Success Criteria:**
- [ ] Workflow syntax valid (GitHub validates)
- [ ] Dry-run mode successful
- [ ] All workflow steps executed
- [ ] Approval gate operational
- [ ] Operational guide complete

---

### Task 1.5: Release Announcement Template Generation (1 hour)

**Objective:** Create announcement templates for GitHub Discussions and other channels

**Actions:**
1. Create `scripts/deployment/generate_announcement_templates.py`:
   - Generate GitHub Discussions post template
   - Include release highlights
   - Link to full release notes
   - Include download instructions
   - Include upgrade guide
   - Include known issues section

2. Create template variations:
   - GitHub Discussions (markdown)
   - Email announcement (plain text + HTML)
   - Slack announcement (formatted for Slack)
   - Twitter announcement (short form)

3. Generate announcement templates for next release

**Deliverables:**
- `scripts/deployment/generate_announcement_templates.py` (functional)
- `.codex/release-announcements/` (directory with templates)
- `.codex/TRACK_1_TASK_5_ANNOUNCEMENT_TEMPLATES.md` (execution report)

**Success Criteria:**
- [ ] Template generation script functional
- [ ] All template variations generated
- [ ] Templates include all required sections
- [ ] Ready for human review before publication

---

### Task 1.6: Release Audit Artifact Creation (1 hour)

**Objective:** Create comprehensive audit trail for each release

**Actions:**
1. Create `scripts/deployment/generate_release_audit.py`:
   - Capture all release metadata
   - Record approvals and approvers
   - List all artifacts included
   - Document all contributors
   - Timestamp all actions
   - Include verification checksums

2. Generate audit artifact for v0.1.0-final release:
   - `.codex/release-audits/v0.1.0-final-audit.json`
   - Include all above information
   - Sign with repository key

3. Create audit verification script:
   - `scripts/deployment/verify_release_audit.py`
   - Validate audit artifact integrity
   - Verify all referenced artifacts still present

**Deliverables:**
- `scripts/deployment/generate_release_audit.py` (functional)
- `scripts/deployment/verify_release_audit.py` (functional)
- `.codex/release-audits/` (directory with audit files)
- `.codex/TRACK_1_TASK_6_AUDIT_REPORT.md` (execution report)

**Success Criteria:**
- [ ] Audit generation script functional
- [ ] Audit file created and signed
- [ ] Verification script confirms integrity
- [ ] Audit format documented

---

## INTEGRATION REQUIREMENTS

### Cognitive Brain Integration
- Query Cognitive Brain for release history patterns: "get_release_patterns"
- Store release metadata in Cognitive Brain: "store_release_metadata"
- Use Cognitive Brain for automated approval recommendations

### Webhook Integration
- Trigger webhook on release creation: `/webhooks/release_created`
- Notify dependent systems (analytics, distribution, etc.)
- Store webhook delivery status in audit trail

### Repository Variables Integration
- Store release version in `RELEASE_VERSION` variable
- Store release status in `RELEASE_STATUS` variable
- Store release metadata in `RELEASE_METADATA` variable (JSON)

---

## DEPENDENCIES & BLOCKERS

### Required Before Start
- [ ] Phase 7D execution complete (metrics available)
- [ ] CHANGELOG.md up to date with latest release notes
- [ ] Docker SBOM files generated and available

### External Dependencies
- [ ] GitHub API token with `repo` and `contents` scopes (CODEX_MASTER_KEY)
- [ ] Signing key for attestations (stored in GitHub secrets)

### Known Blockers
- **Editorial Review Gate:** Workflow template includes approval gate requiring human review before final publish
- **Credentials:** Release requires GitHub API token (one-time setup)

---

## SUCCESS DEFINITION

**Track 1 Complete When:**

1. ✅ All 6 tasks complete with deliverables
2. ✅ `.github/workflows/automated-release-creation.yml` created and validated
3. ✅ All support scripts (`extract_release_notes.py`, `generate_sbom.py`, etc.) created and tested
4. ✅ Dry-run release creation successful
5. ✅ All artifacts in `.codex/` and committed
6. ✅ Documentation complete and accurate
7. ✅ Approval gate operational (editorial review gate configured)
8. ✅ No breaking issues; all success criteria met

**Effort Target:** 5-6 hours  
**ROI:** 1.5-2 hours saved per release (break-even: 3-4 releases)

---

## REPORTING

**Progress Report Location:** `.codex/TRACK_1_RELEASE_AUTOMATION_REPORT.md`  
**Update Frequency:** After each task completion  
**Final Report:** Consolidate into `.codex/AUTOMATION_CAMPAIGN_PROGRESS_DASHBOARD.md`

---

## AUTHORITY & APPROVAL

**Campaign Authority:** @mbaetiong (D-level autonomy)  
**Execution Authority:** This agent brief  
**Status:** READY FOR DELEGATION

