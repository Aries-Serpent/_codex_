# PHASE 0 CAMPAIGN INDEX
## Cognitive Brain-Powered Packaging - Codebase Reconnaissance Complete

**Campaign Authority:** @mbaetiong D-tier  
**Campaign Period:** Phase 0 (Complete as of 2026-07-06)  
**Next Phase:** Phase 1 LITE Extraction (Week of 2026-07-15)  

---

## 📋 Deliverables Overview

### Document 1: INTELLIGENCE_CAMPAIGN_BASELINE.md (25 KB)

**Contents:**
- 1.1: Module Inventory (47 modules categorized)
- 1.2: Core Submodules (62 distinct modules in src/codex/*)
- 2.0: Dependency Coupling Map
- 3.0: Cognitive Brain Integration Points (detailed)
- 4.0: Packaging Boundary Recommendations (4 profiles)
- 5.0: External Use Case Analysis
- 6.0: Technical Risks & Mitigation
- 7.0: Codebase Structure Visualization
- 8.0: Risks to External Stability
- 9.0: Collaboration Checkpoints
- 10.0: Deliverable Checklist

**Key Numbers:**
- 47 modules inventoried
- 4 packaging profiles defined
- 6 critical risks identified
- 62 codex submodules mapped
- Export readiness: 85% (LITE) → 30% (FULL)

**Use This For:**
- Understanding module organization
- Identifying which modules can be extracted first
- Risk assessment for external release
- Use case alignment (which profile for which user)

---

### Document 2: DEPENDENCY_COUPLING_MATRIX.md (9.3 KB)

**Contents:**
- 1.0: Core Module Dependencies (top 10 dependency chains)
- 2.0: Cycle Detection Report (3 cycles identified, all mitigated)
- 3.0: Inter-Profile Dependencies (per packaging profile)
- 4.0: External Integration Risks (network, storage)
- 5.0: Import-Time Side Effects Inventory
- 6.0: Breaking Change Analysis (risk matrix)
- 7.0: Immediate Recommendations

**Key Findings:**
- 0 unresolved circular dependencies ✓
- 0 blocking import-time side effects ✓
- 3 HIGH-RISK APIs that may break in next 6 months
- 4 network resilience gaps to fix

**Use This For:**
- Understanding tight coupling points
- Identifying decoupling priorities
- Planning breaking change communication
- Network resilience requirements

---

### Document 3: PHASE_0_EXTRACTION_ROADMAP.md (16 KB)

**Contents:**
- Phase 1: LITE Profile (Weeks 1-2)
  * Extract: codex.utils, codex.config, cognitive_brain.base
  * Size: 50 KB, no external APIs
  * Effort: LOW (1-2 days)
  
- Phase 2: COGNITIVE Core (Weeks 3-5)
  * Extract: codex.cognitive, cognitive_brain, codex.skills, codex.logging
  * Size: 3.5 MB
  * Effort: MEDIUM (5-10 days)
  * Critical tasks: Decouple session storage, make quantum optional
  
- Phase 3: ML Pipeline (Weeks 6-10)
  * Extract: codex_ml (separate PyPI package)
  * Size: 3.5 MB
  * Effort: HIGH (10-15 days)
  * Critical: Decouple from codex.logging
  
- Phase 4: Runtime Services (Weeks 11-13)
  * Extract: REST API, GitHub integration, MCP adapters
  * Effort: MEDIUM (5-10 days)
  
- Phase 5: Advanced Modules (Weeks 14-16)
  * Archive/deprecate quantum, CRM, hhg_logistics
  * Effort: LOW (2-3 days)

**Key Metrics:**
- Total effort: 40-60 engineering days
- Timeline: 16 weeks (Aug-Nov 2026)
- Team: 2-3 senior engineers + 1 QA
- Final deliverable: 4 separate PyPI packages

**Use This For:**
- Planning extraction sprints
- Identifying critical path items
- Task allocation and effort estimation
- Risk mitigation sequencing

---

### Document 4: PHASE_0_SUMMARY.txt (9.8 KB)

**Contents:**
- Executive Summary (codebase health)
- Cognitive Brain Portability Assessment
- External Use Case Alignment (LITE/CORE/RUNTIME)
- Packaging Strategy Recommendation (4-package approach)
- Critical Blockers (3 identified, timelines provided)
- Immediate Next Steps
- Collaboration Agreements
- Risk Register (4 risks, mitigations)
- Approval Checkpoint
- KPIs & Success Metrics

**Key Takeaways:**
- Cognitive brain portability: 50→75/100 post-refactor
- 3 blocking issues, all solvable in Phase 2 (2 weeks)
- Windows CI testing is HIGH PRIORITY
- 4-package strategy is optimal (not 1 monolith)

**Use This For:**
- Executive-level overview
- Stakeholder communication
- Approval checklists
- Risk tracking

---

## 🎯 Critical Path Items (Do First)

1. **Week 1:** Add Windows CI runner to GitHub Actions
   - Status: REQUIRED before Phase 1
   - Effort: 0.5 days
   - Owner: Infrastructure

2. **Week 3-4 (Phase 2):** Decouple session storage
   - Status: BLOCKS cognitive portability
   - Effort: 2 days
   - Owner: @skills-master
   - Task: Create SessionBackend ABC + 3 implementations

3. **Week 3-4 (Phase 2):** Make quantum planset optional
   - Status: REDUCES cognitive complexity
   - Effort: 1-2 days
   - Owner: @quantum-compliance-tuning-agent
   - Task: Create PlansetGenerator ABC + fallback

4. **Week 2 (Phase 1):** Stabilize public API signatures
   - Status: REQUIRED for external release
   - Effort: 1 day
   - Owner: @skills-master
   - Task: Add @stable decorator, document SemVer policy

5. **Week 6 (Phase 3):** Decouple codex_ml from codex.logging
   - Status: ENABLES codex_ml independence
   - Effort: 2 days
   - Owner: @skills-master
   - Task: Mirror logger or make optional

---

## 🤝 Collaboration Map

### With cognitive-brain-cli-agent
- **Task:** Validate AgentBrainAPI export scope
- **Deadline:** 2026-07-15
- **Deliverable:** Session context serialization spec
- **Integration point:** Phase 2 Week 5

### With packaging-validation-agent
- **Task:** Define SemVer policy per profile
- **Deadline:** 2026-07-22
- **Deliverable:** Profile test matrix + wheel generation
- **Integration point:** Phase 1 Week 2

### With orchestrator-agent
- **Task:** Identify inter-lane dependencies
- **Deadline:** 2026-07-15
- **Deliverable:** Dependency list + validation gates
- **Integration point:** Phase 1 completion

### With autonomous-test-healer-agent
- **Task:** Write profile integration tests
- **Deadline:** Ongoing
- **Deliverable:** Test coverage for each extraction phase
- **Integration point:** All phases

---

## 📊 Success Criteria by Phase

### Phase 1 (Week 1-2)
- ✓ codex-lite-0.1.0 installs in <5s
- ✓ Windows CI runner green
- ✓ Zero blocking import errors
- ✓ AAIS ≥0.80 for all modules
- ✓ Quickstart docs published

### Phase 2 (Week 3-5)
- ✓ Session storage abstracted (3 backends)
- ✓ Quantum planset optional
- ✓ codex-0.1.0 installs in 20s
- ✓ AgentBrainAPI works standalone
- ✓ 0 circular imports verified

### Phase 3 (Week 6-10)
- ✓ codex-ml independent from codex
- ✓ HuggingFace models loadable
- ✓ Training pipeline functional
- ✓ GPU memory usage documented

### Phase 4 (Week 11-13)
- ✓ REST API working
- ✓ GitHub integration tested
- ✓ MCP adapters functional

### Phase 5 (Week 14-16)
- ✓ 4 PyPI packages available
- ✓ All modules AAIS ≥0.70
- ✓ Comprehensive docs
- ✓ Example projects

---

## 🚨 Risk Summary

| Risk | Severity | Probability | Mitigation | Owner |
|------|----------|-------------|-----------|-------|
| PyTorch ecosystem churn | HIGH | HIGH | Quarterly compat tests | @test-pattern-guardian |
| Session storage portability | MEDIUM | MEDIUM | Abstract backend + Windows CI | @skills-master |
| Quantum engine instability | MEDIUM | HIGH | Make optional, add fallback | @quantum-compliance-tuning-agent |
| API breaking changes | HIGH | MEDIUM | SemVer policy + @stable decorator | @skills-master |
| Windows path handling | MEDIUM | MEDIUM | Platform-specific tests | @cross-platform-filename-validator |
| GitHub API resilience | MEDIUM | MEDIUM | Add retry/backoff | @ci-emergency-response-agent |

---

## 📍 File Locations

All Phase 0 documents are committed to the repository root:

```
/INTELLIGENCE_CAMPAIGN_BASELINE.md      (25 KB)  → Module inventory & profiles
/DEPENDENCY_COUPLING_MATRIX.md          (9.3 KB) → Coupling analysis & risks
/PHASE_0_EXTRACTION_ROADMAP.md          (16 KB)  → Task-level timeline
/PHASE_0_SUMMARY.txt                    (9.8 KB) → Executive summary
/PHASE_0_INDEX.md                       (this)   → Navigation guide
```

---

## 🔍 How to Use These Documents

### For Project Managers
1. Start with **PHASE_0_SUMMARY.txt** for high-level overview
2. Review **Critical Path Items** section above
3. Track using **Collaboration Map** for inter-team dependencies
4. Monitor **Risk Summary** weekly

### For Architects
1. Read **INTELLIGENCE_CAMPAIGN_BASELINE.md** sections 1-4 (modules + dependencies)
2. Study **DEPENDENCY_COUPLING_MATRIX.md** section 3 (inter-profile deps)
3. Reference **PHASE_0_EXTRACTION_ROADMAP.md** for decoupling strategy
4. Use **section 7** of baseline for visualization

### For Engineers (Phase 1)
1. Read **PHASE_0_EXTRACTION_ROADMAP.md** Phase 1 section
2. Review **INTELLIGENCE_CAMPAIGN_BASELINE.md** section 4.1 (LITE profile)
3. Check **DEPENDENCY_COUPLING_MATRIX.md** section 2 (cycles are mitigated)
4. Create tasks from roadmap checklist

### For Engineers (Phase 2)
1. Study **PHASE_0_EXTRACTION_ROADMAP.md** Phase 2 section (critical tasks!)
2. Focus on **Task 2.1** (session storage abstraction)
3. Focus on **Task 2.2** (quantum planset optional)
4. Reference **DEPENDENCY_COUPLING_MATRIX.md** sections 1-4

### For QA Engineers
1. Extract test checklist from each phase in roadmap
2. Use **Success Criteria by Phase** section above
3. Review **verification gates** in roadmap
4. Cross-reference with **INTELLIGENCE_CAMPAIGN_BASELINE.md** section 9

---

## ✅ Phase 0 Completion Checklist

- [x] 47 modules inventoried & categorized
- [x] 4 packaging profiles designed
- [x] All modules export-readiness scored
- [x] 3 circular dependencies documented + mitigated
- [x] Cognitive brain portability assessed (50→75/100)
- [x] 6 technical risks identified + mitigations
- [x] 16-week extraction timeline created
- [x] Critical decoupling tasks identified (session storage, quantum)
- [x] Collaboration agreements drafted
- [x] Success metrics defined per phase
- [x] 4 detailed documents created (60 KB total)

**Status:** ✅ COMPLETE — Ready for Phase 1 kickoff

---

## 🚀 Next Actions

**Immediate (This Week):**
1. Schedule Phase 2 kickoff with @mbaetiong
2. Set up Windows CI runner
3. Circulate PHASE_0_SUMMARY.txt to stakeholders for approval

**This Week (2026-07-08 to 2026-07-12):**
1. Validate cognitive brain export scope (cognitive-brain-cli-agent)
2. Get packaging strategy approval (packaging-validation-agent)
3. Confirm resource allocation (orchestrator-agent)
4. Lock down SemVer policy (all teams)

**Phase 1 Kickoff (Week of 2026-07-15):**
1. Extract LITE profile (codex-lite-0.1.0)
2. Add Windows CI testing
3. Publish quickstart docs
4. Get Phase 1 completion sign-off

---

**Campaign Lead:** @mbaetiong  
**Technical Lead:** @skills-master  
**Last Updated:** 2026-07-06  
**Next Review:** 2026-07-13 (Phase 1 progress)

