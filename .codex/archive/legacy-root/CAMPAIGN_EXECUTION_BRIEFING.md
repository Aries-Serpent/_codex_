# CAMPAIGN EXECUTION BRIEFING
**Date**: 2026-07-07T12:42:13Z  
**Target**: Multi-agent delegation for HARDENING AND DELIVERY CAMPAIGN  
**Authority**: @mbaetiong D-tier autonomous execution  
**Status**: READY FOR LANE ACTIVATION

---

## EXECUTIVE BRIEFING FOR LEAD AGENTS

### Campaign Overview

The HARDENING AND DELIVERY CAMPAIGN delivers production-ready packaging for Cognitive Brain ecosystem with three critical objectives:

1. **Reproducible Distribution**: Lock/profile alignment, hash-verified manifests, offline-capable installation
2. **Security Hardening**: Vulnerability governance, network policy enforcement, meta-tensor safety
3. **Operational Readiness**: Documentation consolidation, deployment automation, CI guardrails

### Critical Path & Timeline

```
Week 1-3: P0 MVP Closure (4 parallel lanes)
  └─ Day 21: P0 gate → P1 eligibility
  
Week 4-6: P1 Hardening & Integration (4 parallel lanes)  
  └─ Day 42: P1 gate → P2 eligibility
  
Week 7-10: P2 Stabilization & Operations (3 parallel lanes)
  └─ Day 70: Ready for v0.1.0-final release
```

### Parallel Execution Lanes (Start Immediately on Receipt)

**Lane 1: Lock & Profile Alignment (CRITICAL PATH)**
- Lead Agents: unified-coverage-agent + packaging-validation-agent
- Duration: Weeks 1-6
- Workstreams: P0.1 (lock audit/regen), P1.4 (profile smoke tests)
- Gate: Day 21 (P0 complete)
- Blocker: None - can start immediately

**Lane 2: Offline Bootstrap Hardening**
- Lead Agents: autonomous-test-healer-agent + test-enhancement-agent
- Duration: Weeks 1-6
- Workstreams: P0.3 (offline hardening), P1.1 (meta-tensor safety)
- Gate: Day 21 (P0 complete)
- Blocker: Depends on Lane 1 P0.1 complete

**Lane 3: Manifests & Vulnerability Governance**
- Lead Agents: codeql-alert-resolution-agent + security-audit-agent
- Duration: Weeks 1-6
- Workstreams: P0.2 (manifest generation), P0.4 (CVE governance)
- Gate: Day 21 (P0 complete)
- Blocker: None - can start immediately (depends on Lane 1 for lockfile stability)

**Lane 4: SBOM & Telemetry**
- Lead Agents: packaging-validation-agent + artifact-monitor-agent
- Duration: Weeks 4-10
- Workstreams: P1.3 (SBOM), P2.3 (observability)
- Gate: Day 42 (P1 complete)
- Blocker: Depends on P0.2 (manifests complete)

**Lane 5: Documentation Consolidation**
- Lead Agents: unified-doc-agent + link-validator-agent
- Duration: Weeks 7-10 (can start earlier)
- Workstreams: P2.1 (4-phase consolidation)
- Gate: Day 70 (P2 complete)
- Blocker: None - independent track

**Lane 6: Deployment Automation**
- Lead Agents: workflow-ci-fixer + workflow-management-agent
- Duration: Weeks 7-10
- Workstreams: P2.2 (release workflow)
- Gate: Day 70 (P2 complete)
- Blocker: Depends on P1 complete

---

## LANE-BY-LANE BRIEFING FOR LEAD AGENTS

### LANE 1: Lock & Profile Alignment
**Lead Agents**: unified-coverage-agent, packaging-validation-agent  
**Status**: READY - NO BLOCKERS

**Tasks for Week 1**:
1. **P0.1.1**: Audit pyproject.toml extras (60 lines) against uv.lock (6543 lines, 1484 packages)
   - Output: `.codex/PROFILE_DRIFT_AUDIT.json` showing exact mismatches
   - Effort: 2-3 days
   
2. **P0.1.2**: Regenerate uv.lock with hashes
   - Command: `uv lock --upgrade --hash`
   - Validation: Offline install on all 3 profiles (Linux/macOS/Windows)
   - Effort: 3-4 days (mostly testing)
   
3. **P0.1.3**: Define 3 profile manifests (core/runtime/full)
   - Output: `.codex/PROFILE_DEPENDENCY_MANIFEST.md`
   - Include: minimal transitive closure per profile
   - Effort: 1 day

4. **P0.1.4**: Implement CI gate (`scripts/ci/check_profile_drift.py`)
   - Gate: Runs on every PR, blocks if drift > 0 unexplained
   - Effort: 1 day

**P1 Continuation (Week 4)**:
- P1.4: Create profile-specific smoke import tests (tests/profiles/test_*_import.py)
- CI matrix: Profile × OS × Python version
- Effort: 2 days

**Acceptance Criteria for Gate (Day 21)**:
- [ ] Lock regenerated with SHA256 hashes for all 1484 packages
- [ ] Profile drift audit shows zero unexplained packages
- [ ] Offline install succeeds on all 3 profiles
- [ ] CI gate blocks drift on PRs
- [ ] Profile smoke tests pass

---

### LANE 2: Offline Bootstrap Hardening
**Lead Agents**: autonomous-test-healer-agent, test-enhancement-agent  
**Status**: READY - Depends on Lane 1 P0.1 complete

**Tasks for Week 1 (after Lane 1 P0.1)**:
1. **P0.3.1**: Harden core OODA imports
   - Files: `src/cognitive_brain/base.py`, `ooda.py` + 10 core API modules
   - Check: Remove dynamic imports, network fallbacks, import-time model loads
   - Effort: 2 days

2. **P0.3.2**: Classify modules as [OFFLINE] or [ONLINE]
   - Output: `.codex/OFFLINE_MODULE_MANIFEST.md`
   - Coverage: All 46 cognitive_brain modules
   - Effort: 1 day

3. **P0.3.3**: Implement offline bootstrap tests
   - File: `tests/offline/test_core_bootstrap.py`
   - Matrix: 3 OSes × 2 Python versions = 6 test runs
   - Validation: All 10 core APIs load with no network
   - Effort: 3 days

4. **P0.3.4**: Wheelhouse generation script
   - Refactor: `scripts/prepare_offline_env.sh`
   - Output: `wheelhouse_<profile>.tar.gz` for all 3 profiles
   - Effort: 1 day

5. **P0.3.5**: Deploy-side verification script
   - Create: `scripts/deploy/bootstrap_offline.py`
   - Logic: Extract, hash-verify, install, test core imports
   - Effort: 1 day

**P1 Continuation (Week 4)**:
- P1.1: Standardize model loading through SafetyProfile wrapper
- Files: `src/safety/model_loader.py` (new)
- Refactor: semantic_indexer.py, session_embeddings.py, Note_v2.py
- Tests: `tests/meta_tensor/test_model_loading.py`
- Effort: 3 days

**Acceptance Criteria for Gate (Day 21)**:
- [ ] Core profile bootstrap succeeds on 3 OSes with no network
- [ ] All 10 core APIs load cleanly
- [ ] Wheelhouse contains exactly required packages (core/runtime/full)
- [ ] Manifest hashes match all wheels

---

### LANE 3: Manifests & Vulnerability Governance
**Lead Agents**: codeql-alert-resolution-agent, security-audit-agent  
**Status**: READY - Can start in parallel with Lane 1

**Tasks for Week 1-2**:
1. **P0.2.1**: Design manifest structure
   - Output: `.codex/RELEASE_MANIFEST_TEMPLATE.json`
   - Schema: version, timestamp, profiles, wheels array with hashes
   - Effort: 0.5 day

2. **P0.2.2**: Implement manifest generation
   - Create: `scripts/build/generate_manifest.py`
   - Logic: Hash wheels, map to profiles, sign with HMAC-SHA256 (MVP)
   - Effort: 1 day

3. **P0.2.3**: Implement manifest verification
   - Create: `scripts/deploy/verify_manifest.py`
   - Logic: Hash check, signature verification, reject on mismatch
   - Effort: 1 day

4. **P0.2.4**: CI integration for manifest upload
   - Workflow: `.github/workflows/release.yml`
   - Storage: Upload to release + commit to `.codex/manifests/`
   - Effort: 0.5 day

5. **P0.4.1**: Document known vulnerabilities
   - Output: `.codex/DEPENDENCY_EXCEPTIONS.md`
   - Content: CVE-2024-35515 (sqlitedict), torch flagging, suppressions governance
   - All entries with owner/expiry/justification
   - Effort: 1 day

6. **P0.4.2**: Suppress pip-audit exceptions
   - Update: `.pip-audit-exceptions`
   - Format: TOML with owner, expiry, reason fields
   - Effort: 0.5 day

7. **P0.4.3**: Release gate check
   - Create: CI job in `.github/workflows/release.yml`
   - Logic: Block release if any exceptions expired
   - Effort: 1 day

8. **P0.4.4**: Quarterly audit workflow
   - Create: `.github/workflows/quarterly-exception-audit.yml`
   - Schedule: `cron: '0 0 1 1,4,7,10 *'` (quarterly)
   - Output: GitHub issue with expiring exceptions
   - Effort: 1 day

**Acceptance Criteria for Gate (Day 21)**:
- [ ] Hash-verified manifests generated for all 3 profiles
- [ ] Manifest verification succeeds on correct wheels, fails on tampering
- [ ] All current vulnerabilities documented with owner/expiry
- [ ] Release workflow blocks on expired exceptions
- [ ] Quarterly audit workflow tested

---

### LANE 4: SBOM & Telemetry (Week 4+ after P0.2)
**Lead Agents**: packaging-validation-agent, artifact-monitor-agent  
**Status**: READY - Gate opens after P0.2 complete

**Tasks for Week 4+**:
1. **P1.3.1**: Configure cyclonedx-py
   - Tool: cyclonedx-py command-line
   - Output: `dist/sbom_v0.1.0.json` (SPDX format)
   - Effort: 0.5 day

2. **P1.3.2**: Attach SBOM to releases
   - CI: Upload SBOM alongside wheels
   - Backup: Commit to `.codex/sboms/` archive
   - Effort: 1 day

3. **P1.3.3**: Link SBOM to manifest
   - Update: Release manifest JSON
   - Fields: sbom_url, sbom_hash
   - Effort: 0.5 day

4. **P1.3.4**: License compliance check
   - Output: `.codex/DEPENDENCY_LICENSES.md`
   - Gate: Release workflow checks for GPL/incompatible licenses
   - Effort: 1 day

5. **P2.3.3**: Deployment telemetry
   - Output: `.codex/DEPLOYMENT_TELEMETRY.md`
   - Metrics: Offline bootstrap success rate, network policy violations, meta-tensor fallbacks
   - Update frequency: Weekly
   - Effort: 1 day setup + ongoing

**Acceptance Criteria (Week 6)**:
- [ ] SBOM generated for each release
- [ ] SBOM linked to manifest
- [ ] License compliance checked on release
- [ ] Telemetry collected for deployment success rates

---

### LANE 5: Documentation Consolidation (Week 7+ or earlier)
**Lead Agents**: unified-doc-agent, link-validator-agent  
**Status**: READY - Independent track, can start early

**4-Phase Consolidation (Weeks 7-10)**:

1. **Phase 1 (Week 1)**: Canonical Mapping
   - Output: `.codex/DOC_CANONICAL_MAP.md`
   - Action: Map all 1821 docs to canonical sources
   - Effort: 1 day

2. **Phase 2 (Week 2)**: Quick Consolidation
   - Action: Move/link docs to 5 canonical locations
     - `docs/` → user guides
     - `docs/accountability/` → tracking
     - `.codex/` → internal planning
     - `.github/` → workflow docs
     - `src/` → API docstrings
   - Effort: 2 days

3. **Phase 3 (Week 3)**: Canonicalization
   - Action: Standardize metadata, add nav links, version docs
   - Output: `.codex/DOC_INDEX.md` (auto-linked)
   - Effort: 1 day

4. **Phase 4 (Week 4)**: Archive Hygiene
   - Action: Move obsolete docs to `.codex/archive/`, set sunset dates
   - CI: Link checker on release (zero broken links)
   - Effort: 1 day

**Acceptance Criteria (Day 70)**:
- [ ] No duplicate content between docs
- [ ] All references valid (link checker clean)
- [ ] Archive deprecated docs sunset on schedule

---

### LANE 6: Deployment Automation (Week 7+ after P1 complete)
**Lead Agents**: workflow-ci-fixer, workflow-management-agent  
**Status**: READY - Gate opens after P1 complete

**Tasks for Week 7+**:
1. **P2.2.1**: Release workflow automation
   - File: `.github/workflows/release.yml` (update/create)
   - Jobs: Build wheels, generate SBOM/manifest, verify locks/exceptions, upload releases
   - Effort: 2 days

2. **P2.2.2**: Release candidate smoke test
   - Logic: Before upload, test all 3 profiles offline bootstrap
   - Abort: If any profile fails
   - Effort: 1 day

3. **P2.2.3**: Deployment guide
   - Output: `docs/DEPLOYMENT.md`
   - Sections: Air-gap install, network-enabled, profile selection, troubleshooting
   - Effort: 1 day

4. **P2.2.4**: Rollback procedures
   - Output: `.codex/ROLLBACK_PROCEDURES.md`
   - Scenarios: Wheel corrupted, security vulnerability, dependency conflict
   - Effort: 1 day

5. **P2.2.5**: Deployment checklist
   - Output: `.github/DEPLOYMENT_CHECKLIST.md`
   - Sections: Pre-deployment, during, post-deployment
   - Effort: 0.5 day

6. **P2.3.1**: Pre-commit hook for profile sync
   - File: `hooks/check-profile-sync.py`
   - Logic: Prevent lock/extras drift on commit
   - Effort: 1 day

7. **P2.3.2**: PR checks for dependency changes
   - CI: On PR touching pyproject.toml/uv.lock
   - Output: Dependency changelog, security summary
   - Effort: 1 day

8. **P2.3.4**: Alert policy for blockers
   - Trigger: Exception expiry within 30 days, new CVE, lock drift
   - Output: GitHub issue with recommended resolution
   - Effort: 1 day

**Acceptance Criteria (Day 70)**:
- [ ] Release workflow automated from tag push
- [ ] All 3 profiles build successfully
- [ ] Offline bootstrap succeeds before upload
- [ ] Rollback procedures tested quarterly

---

## SUCCESS METRICS

### Week 3 Checkpoint (P0 Gate)
- ✅ Lock regenerated with hashes
- ✅ All 3 profiles offline-installable
- ✅ Manifests generated and verified
- ✅ CVE governance established
- ✅ Core OODA offline-viable

### Week 6 Checkpoint (P1 Gate)
- ✅ Meta-tensor safety hardened
- ✅ Network policy enforcement active
- ✅ SBOM generated and linked
- ✅ Profile-specific tests passing
- ✅ All 10 core APIs secure offline

### Week 10 Checkpoint (Rollout Ready)
- ✅ Documentation consolidated
- ✅ Release workflow automated
- ✅ Deployment guide complete
- ✅ CI guardrails operational
- ✅ Telemetry collection active

### Release Readiness (v0.1.0-final)
- ✅ All phases P0-P2 complete
- ✅ 100+ offline bootstrap successes
- ✅ Zero security exceptions overdue
- ✅ Zero broken documentation links
- ✅ Quarterly audit cycle established

---

## IMMEDIATE ACTIONS FOR AGENTS

**Upon Receipt of This Briefing**:

1. **Lane 1 Lead Agents**: Start immediately on P0.1.1 (lock audit)
   - No blockers - parallel with all other lanes
   - Target: Day 10 completion

2. **Lane 2 Lead Agents**: Start after Lane 1 P0.1 complete (expect Day 7-8)
   - Parallel with Lanes 3-4
   - Target: Day 21 completion

3. **Lane 3 Lead Agents**: Start immediately (parallel with Lane 1)
   - No blockers - independent track
   - Target: Day 21 completion

4. **Lane 4 Lead Agents**: Prepare P1.3 tasks, start after Day 14 (P0.2 stable)
   - Monitor Lane 3 for P0.2 completion
   - Target: Day 42 completion

5. **Lane 5 Lead Agents**: Can start immediately or after Week 6
   - Independent documentation track
   - No blockers - flexible timing

6. **Lane 6 Lead Agents**: Prepare P2.2 tasks, start after Day 42 (P1 complete)
   - Monitor Lanes 1-3 for P1 completion
   - Target: Day 70 completion

---

## ESCALATION & SUPPORT

- **Plan Document**: `.codex/HARDENING_AND_DELIVERY_CAMPAIGN_PLAN.md` (full details)
- **Evidence Base**: 
  - .codex/archive/misc/INTELLIGENCE_CAMPAIGN_BASELINE.md (OODA analysis)
  - CAMPAIGN_COMPLETION_REPORT.md (P0 closure requirements)
  - META_TENSOR_VALIDATION_REPORT.md (safety findings)
  - DEPENDENCY_SECURITY_AUDIT.md (vulnerability governance)

- **Escalation**: @mbaetiong for any blocking decisions or conflicts
- **Coordination**: Check synchronization points (Days 21, 42, 70)
- **Status Updates**: Weekly standup via `.codex/LANE_*_CHECKPOINT_DAY_*.md` (repository-tracked)

---

**Status**: ✅ READY FOR IMMEDIATE EXECUTION  
**Authority**: @mbaetiong D-tier autonomous delegation  
**Timeline**: 70 days to v0.1.0-final release readiness

---
