# 🎯 Phase 8 WS3 Execution Coordination Plan

**Authority:** @mbaetiong (D-tier autonomous, GO CONTINUE)  
**Status:** Ready for agent activation  
**Entry Point:** This document + 4 track execution briefs

---

## 📋 Executive Summary

Phase 8 Workstream 3 coordinates execution of 4 parallel/sequential agent tracks to complete repository stabilization:
- **Track 8.3** (PRIORITY): Case-collision de-duplication + .gitattributes (9.5 hours)
- **Track 8.1** (AFTER 8.3): Doc remediation + ownership system (12 hours, starts 2026-07-07T20:00Z)
- **Track 8.2** (AFTER 8.1): Cleanup strategy execution (9 hours, starts 2026-07-08T09:00Z)
- **Track 8.4** (PARALLEL): Dependency standardization (14 hours, starts 2026-07-07T18:00Z)

**Total Duration:** ~28 hours (sequential 8.3→8.1→8.2, parallel 8.4)  
**Target Completion:** 2026-07-08T18:00Z

---

## 🎯 Execution Timeline

```
TIMELINE — Phase 8 WS3 Execution (All times UTC)

2026-07-07
├─ 18:00Z ── LAUNCH TRACK 8.4 (PARALLEL)
│           Dependency standardization (independent execution)
│           Expected end: 2026-07-08T14:00Z
│
├─ 18:00Z ── LAUNCH TRACK 8.3 (PRIORITY SEQUENCE START)
│           Case-collision de-duplication
│           Expected end: 2026-07-07T20:30Z
│
├─ 20:30Z ── TRACK 8.3 COMPLETE (assume +30 min buffer)
│           Await completion confirmation
│
├─ 20:00Z ── QUEUE TRACK 8.1 (ready to start post-8.3)
│           Doc remediation
│           Expected start: 2026-07-07T20:30Z
│           Expected end: 2026-07-08T08:00Z
│
└─ 08:00Z ── QUEUE TRACK 8.2 (ready to start post-8.1)
            Cleanup strategy
            Expected start: 2026-07-08T09:00Z
            Expected end: 2026-07-08T18:00Z

2026-07-08
├─ 08:00Z ── TRACK 8.1 COMPLETE
│           Await completion confirmation
│
├─ 09:00Z ── LAUNCH TRACK 8.2
│           Cleanup strategy (all 4 phases)
│
├─ 14:00Z ── TRACK 8.4 COMPLETE (parallel run)
│           Await completion confirmation
│
└─ 18:00Z ── ALL TRACKS COMPLETE
            Start WS4 (validation phase)
```

---

## 🔄 Track Execution Sequencing

### Parallel Lane (Track 8.4 — Independent)
```
TRACK 8.4: Dependency Standardization
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2026-07-07 18:00Z ──────────────────► 2026-07-08 14:00Z
(14 hours, independent of all other tracks)

No blocking dependencies on 8.1/8.2/8.3
No deliverables for other tracks
Can proceed immediately when authorized
```

### Sequential Lane (Tracks 8.3 → 8.1 → 8.2)
```
TRACK 8.3: Case-Collision De-Duplication
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2026-07-07 18:00Z ──► 2026-07-07 20:30Z
(9.5 hours, PRIORITY)

↓ Deliverable: Stable filenames + .gitattributes
↓ Blocks: Track 8.1 (doc links must point to stable paths)

TRACK 8.1: Documentation Remediation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2026-07-07 20:30Z ──────────────────► 2026-07-08 08:00Z
(12 hours, requires Track 8.3 complete)

↓ Deliverable: Doc structure finalized, ownership system active
↓ Blocks: Track 8.2 (cleanup must not break doc structure)

TRACK 8.2: Cleanup Strategy Execution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2026-07-08 09:00Z ──────► 2026-07-08 18:00Z
(9 hours, requires Track 8.1 complete)

↓ Deliverable: Repository structure standardized
↓ Final step before WS4 validation
```

---

## 🚀 Agent Activation Sequence

### Phase A: Immediate Activation (NOW)

**Command:** Activate Track 8.4 immediately (independent execution)
```bash
# Track 8.4 Agent Activation
@task name="track-8-4-dependency" \
      agent_type="dependency-conflict-agent" \
      prompt="Execute .codex/PHASE_8_WS3_TRACK_8_4_EXECUTION_BRIEF.md"
```

**Agent Assignment:**
- Primary: `dependency-conflict-agent`
- Support: `packaging-validation-agent`, `cache-management-agent`
- Expected duration: 14 hours
- Expected completion: 2026-07-08T14:00Z

### Phase B: Priority Sequence Activation (2026-07-07T18:00Z)

**Command:** Activate Track 8.3 (priority first)
```bash
# Track 8.3 Agent Activation
@task name="track-8-3-case-collision" \
      agent_type="unified-doc-agent" \
      prompt="Execute .codex/PHASE_8_WS3_TRACK_8_3_EXECUTION_BRIEF.md"
```

**Agent Assignment:**
- Primary: `unified-doc-agent` + `branch-divergence-resolution-agent`
- Expected duration: 9.5 hours
- Expected completion: 2026-07-07T20:30Z
- **BLOCKING for Track 8.1** — await completion confirmation before launch

### Phase C: Cascading Launches (Post-Track-8.3)

**Upon Track 8.3 completion (2026-07-07T20:30Z):**
```bash
# Track 8.1 Agent Activation
@task name="track-8-1-doc-remediation" \
      agent_type="unified-doc-agent" \
      prompt="Execute .codex/PHASE_8_WS3_TRACK_8_1_EXECUTION_BRIEF.md"
```

**Agent Assignment:**
- Primary: `unified-doc-agent` + `post-merge-doc-alignment-agent`
- Expected duration: 12 hours
- Expected completion: 2026-07-08T08:00Z
- **BLOCKING for Track 8.2** — await completion confirmation before launch

### Phase D: Final Track Activation (Post-Track-8.1)

**Upon Track 8.1 completion (2026-07-08T08:00Z):**
```bash
# Track 8.2 Agent Activation
@task name="track-8-2-cleanup" \
      agent_type="unified-governance-gate" \
      prompt="Execute .codex/PHASE_8_WS3_TRACK_8_2_EXECUTION_BRIEF.md"
```

**Agent Assignment:**
- Primary: `unified-governance-gate` + `repository-hygiene-agent`
- Expected duration: 9 hours
- Expected completion: 2026-07-08T18:00Z

---

## 📊 Milestone Gates & Completion Criteria

### Milestone 1: Track 8.3 Complete
**Gate:** All case-collisions resolved, .gitattributes committed  
**Trigger:** Upon agent completion report  
**Criteria:**
- [ ] Git diff shows 8-12 file renames
- [ ] `.gitattributes` committed with case-sensitivity rules
- [ ] No duplicate basenames with different cases
- [ ] Commit SHA documented

### Milestone 2: Track 8.1 Complete
**Gate:** Documentation remediation finished, ownership system active  
**Trigger:** Upon agent completion report  
**Criteria:**
- [ ] Broken link count reduced 90%+
- [ ] `.codex/DOC_OWNERSHIP_REGISTRY.json` committed
- [ ] Update cadence system deployed
- [ ] Sprint roadmap activated

### Milestone 3: Track 8.4 Complete
**Gate:** Dependencies standardized, offline wheelhouse ready  
**Trigger:** Upon agent completion report  
**Criteria:**
- [ ] All 3 conflicts resolved
- [ ] All 18 pinning rules applied
- [ ] Offline wheelhouse built (100+ wheels)
- [ ] Reproducibility validation: ✅ PASS

### Milestone 4: Track 8.2 Complete
**Gate:** Repository cleanup finished, structure standardized  
**Trigger:** Upon agent completion report  
**Criteria:**
- [ ] All 4 cleanup phases executed
- [ ] Disk space freed: 10-20% of original
- [ ] Directory structure matches DIRECTORY_STANDARDS.md
- [ ] Cleanup manifest committed

---

## ✅ WS3 Completion Criteria

**ALL of the following must be true:**

1. ✅ Track 8.3: Case-collision fixes + `.gitattributes`
2. ✅ Track 8.1: Doc remediation + ownership system  
3. ✅ Track 8.2: Cleanup strategy + directory standards
4. ✅ Track 8.4: Dependencies standardized + offline distribution ready

**Success Status:** 🟢 **READY FOR WS4 (Validation Phase)**

---

## 🔄 Dependency Flow Diagram

```
                    Track 8.4 (PARALLEL)
                   Dependency Standardization
                    (2026-07-07 18:00 → 14:00Z)
                           ║
        ╔══════════════════╩════════════════════╗
        ║                                       ║
    Track 8.3                              [Independent]
    Case-Collisions                    No blocking deps
    (18:00 → 20:30Z)
        ║
        ✓ Filenames stable
        ║
        ├──► Track 8.1
             Doc Remediation
             (20:30Z → 08:00+1Z)
             ║
             ✓ Doc structure final
             ║
             └──► Track 8.2
                  Cleanup Strategy
                  (09:00 → 18:00+1Z)
                  ║
                  ✓ Repository standardized
                  ║
                  └──► WS4 VALIDATION PHASE READY
```

---

## 📊 Resource Allocation

**Expected Parallel Capacity:**
- Track 8.4: 1 agent (dependency conflict agent)
- Tracks 8.3+8.1+8.2: 1 primary lane + support agents

**Token Budget:**
- Track 8.4: High (14 hours, complex Python environment)
- Track 8.3: Medium (9.5 hours, file operations)
- Track 8.1: High (12 hours, extensive doc updates)
- Track 8.2: Medium (9 hours, cleanup operations)

**Total Agent Hours:** 45 agent-hours (mostly parallel)

---

## 🎯 Success Metrics

**By 2026-07-08T18:00Z:**
- 4/4 tracks complete
- 50-80 files modified (renames + updates)
- Disk space freed: 500 MB - 2 GB
- Zero blocking issues escalated
- All completion reports filed

---

## ⚠️ Risk Management

**Risk 1: Track 8.3 delays block 8.1**
- **Mitigation:** Use simplified case-collision set if needed; keep core filenames stable
- **Escalation:** If >2 hours delayed, reduce scope to critical collisions only

**Risk 2: Track 8.1 link updates break across renames**
- **Mitigation:** Wait for 8.3 completion; use sed for bulk link fixes
- **Escalation:** If >50% links fail, roll back and retry with manual verification

**Risk 3: Track 8.2 cleanup deletes active files**
- **Mitigation:** Pre-deletion manifests; use `git mv` for all moves
- **Escalation:** If deletion impacts workflows, use `git reflog` to recover

**Risk 4: Track 8.4 offline wheelhouse too large**
- **Mitigation:** Separate into core/runtime/full profiles; use `requirements-base.txt` minimal set
- **Escalation:** If wheelhouse >1 GB, split across multiple distributions

---

## 📞 Support & Communication

**During Execution:**
- Track 8.3 issues → Contact `unified-doc-agent`
- Track 8.1 issues → Contact `post-merge-doc-alignment-agent`
- Track 8.2 issues → Contact `repository-hygiene-agent`
- Track 8.4 issues → Contact `dependency-conflict-agent`

**Escalation Path:**
1. Agent documents issue in brief completion report
2. If blocking, post comment mentioning @mbaetiong
3. @mbaetiong decides: rollback, reduced scope, or continue with workaround

**Status Updates:**
- Track completion reports due immediately upon finish
- WS3 summary consolidation due by 2026-07-08T19:00Z

---

## 🚀 LAUNCH SEQUENCE

### Ready for Immediate Authorization

**Status:** ✅ All execution briefs created and committed

**Briefings Ready:**
- `.codex/PHASE_8_WS3_TRACK_8_3_EXECUTION_BRIEF.md` ✅
- `.codex/PHASE_8_WS3_TRACK_8_1_EXECUTION_BRIEF.md` ✅
- `.codex/PHASE_8_WS3_TRACK_8_2_EXECUTION_BRIEF.md` ✅
- `.codex/PHASE_8_WS3_TRACK_8_4_EXECUTION_BRIEF.md` ✅

**Awaiting:** @mbaetiong authorization to launch all 4 agents

**Command:** "GO CONTINUE with WS3 execution" → Launches Phases A-D above

---

**Authority:** @mbaetiong (D-tier autonomous)  
**Prepared By:** Phase 8 Session Consolidation  
**Entry Point:** This document + 4 track execution briefs  
**Status:** 🟢 **READY FOR LAUNCH**
