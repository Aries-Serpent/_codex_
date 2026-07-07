# 📑 PHASE 8.3 PLANNING DOCUMENTS INDEX — WORKSTREAM 2 COMPLETE

**Generated:** 2026-07-07T14:26Z  
**Authority:** @mbaetiong (D-tier autonomous)  
**Status:** ✅ **WORKSTREAM 2 PLANNING COMPLETE & READY FOR WS3 EXECUTION**

---

## 📚 DOCUMENT ROADMAP

### WS1 INPUT (Audit Phase — Completed 2026-07-03)

**File:** `.codex/archive/phase-reports/phase-1-10/PHASE_8_3_PLATFORM_AUDIT_REPORT.md`  
**Scope:** Complete audit of 17,081 tracked files  
**Key Findings:**
- ✅ Zero Windows-illegal characters (clean)
- 🔴 **13 case-collision groups (BLOCKING)**
- 🟠 **Inactive `.gitattributes` (HIGH)**
- 🟠 **44 hardcoded repo-root paths (HIGH)**
- 🟠 **15 tracked symlinks (HIGH)**
- 🟡 93 /tmp/ hardcodes (MEDIUM)
- 🟡 216 bash-only scripts (MEDIUM)
- 🔵 2 config-file mislocations (LOW)

**Use For:** Detailed finding analysis; reference throughout WS2/WS3 planning.

---

### WS2 OUTPUT (Planning Phase — Completed 2026-07-07)

#### Document 1: COMPATIBILITY MATRIX ✅

**File:** `.codex/PHASE_8_3_COMPATIBILITY_MATRIX.md` (379 lines)  
**Purpose:** Detailed case-collision de-collision plan

**What It Contains:**
- All 13 case-collision groups with canonical file selections
- De-collision sequencing (2-phase: reference mapping → consolidation)
- Reference update scope (Type A–D files: Markdown, YAML, Python, GitHub)
- Merge strategies per group
- Blast-radius analysis (internal links, external backlinks, hierarchy level)
- Coordination framework (Track 8.1, 8.2 dependencies)
- Validation checkpoints (link integrity, case-collision re-scan)
- Gitattributes supporting action
- Success criteria for WS2 → WS3

**When To Use:**
- Reference during WS3 Wave 1 execution (case-collision consolidation)
- Share with Track 8.1 (canonical filenames for doc renames)
- Share with Track 8.2 (de-collision sequence before bulk moves)

**Key Decisions:**
- Canonical naming: Lowercase preferred (e.g., `docs/ci.md`)
- Execution sequence: GROUP 1 (3-way) → GROUP 5/9 (QUICKSTARTs) → remaining 10
- Risk: HIGH (most complex item); start first
- Impact: All 13 groups are Markdown docs (zero source code impact)

---

#### Document 2: REMEDIATION PRIORITY ✅

**File:** `.codex/PHASE_8_3_REMEDIATION_PRIORITY.md` (628 lines)  
**Purpose:** Comprehensive phased remediation approach for all 31 findings

**What It Contains:**
- Priority tiers (Blocking → High → Medium → Low)
- **Wave 1 (1–2 weeks):** Blocking fixes
  - **B1:** Case-collision consolidation
  - **H1:** Root `.gitattributes` activation (PARALLEL)
- **Wave 2 (2–4 weeks):** High-impact fixes
  - **H2:** Symlink conversion (Wave 2A)
  - **H3:** Hardcoded repo-root replacement (Wave 2B)
  - **H4:** Linux tool-path guards (Wave 2C)
- **Wave 3 (2–3 weeks):** Medium/low improvements
  - **M1:** `/tmp/` literal replacement (Wave 3A)
  - **M2:** Bash script documentation (Wave 3B)
  - **M3:** Linux-tool guards (Wave 3C)
  - **L1/L2:** Config cleanup (Wave 3D)
- Effort estimates per item (SMALL/MEDIUM/LARGE)
- Risk assessment per item and wave
- Blast-radius analysis (repo-wide and item-level)
- Dependency graph (execution constraints)
- Success metrics per wave
- Rollback procedures
- Timeline: 5–9 weeks, 1–2 FTE
- Coordination framework (Track 8.1, 8.2, CI/CD, developers)
- Open questions for WS3

**When To Use:**
- Reference throughout WS3 execution (Wave 1, 2, 3)
- Share with resource planning (FTE allocation, timeline)
- Share with CI/CD team (Wave 2 hardcode changes)
- Share with developers (Wave 3 platform requirements)

**Key Decisions:**
- **Wave 1 is critical path:** Case collisions + `.gitattributes` = clean Windows checkout
- **Parallelizable within waves:** Wave 1B runs parallel with 1A; Wave 2 runs in phases; Wave 3 items concurrent
- **Testing required:** Windows (native + WSL), macOS, Linux per wave
- **External dependencies:** Architecture review (symlink policy), GitHub search (external backlinks)

---

#### Document 3: WORKSTREAM 2 COMPLETION ✅

**File:** `.codex/PHASE_8_3_WORKSTREAM_2_COMPLETION_REPORT.md` (412 lines)  
**Purpose:** Overall WS2 handoff summary and next steps

**What It Contains:**
- Executive summary (WS2 complete, all success criteria met)
- Deliverables recap (3 documents + dates/sizes)
- Success criteria validation (all 14 criteria met)
- Key findings recap (31 findings categorized)
- Interdependencies & coordination (Track 8.1, 8.2, CI/CD, developers)
- Timeline & resource allocation (5–9 weeks, 1–2 FTE)
- Immediate next steps for WS3 (Phase A/B/C breakdown)
- Decision points resolved (naming, sequencing, timing, policies)
- Risks & mitigations (5 identified; all manageable)
- Success metrics (post-WS3: Windows checkout, off-CI execution, full portability)
- Sign-off & approval (D-tier autonomous authorization)

**When To Use:**
- Overview for stakeholders (high-level summary)
- Reference for WS3 kickoff meeting
- Share with Track leads (coordination points)
- Refer back if timeline/scope questions arise

**Key Insights:**
- **All success criteria met:** WS2 ready for execution
- **Risks identified & mitigated:** No blockers to proceeding
- **Coordination clear:** Track 8.1, 8.2, CI/CD, developers all aligned
- **Timeline realistic:** 5–9 weeks with 1–2 FTE (parallelizable, mostly sequential phases)

---

## 🎯 HOW TO USE THESE DOCUMENTS

### For WS3 Execution Team (Immediate)

1. **Read:** `PHASE_8_3_WORKSTREAM_2_COMPLETION_REPORT.md` (5–10 min overview)
2. **Reference:** `PHASE_8_3_COMPATIBILITY_MATRIX.md` (Wave 1A execution)
3. **Reference:** `PHASE_8_3_REMEDIATION_PRIORITY.md` (Wave 1B/2/3 execution)
4. **Link:** Original audit in `.codex/archive/` (detailed findings reference)

### For Track 8.1 (Doc Renames — Post-Wave 1)

1. **Wait for:** Completion of WS3 Wave 1A (case-collision de-collision)
2. **Receive:** Canonical filenames + reference map
3. **Reference:** Sections in COMPATIBILITY_MATRIX.md about doc renames
4. **Coordinate:** Timing to avoid cascading failures

### For Track 8.2 (Bulk Moves — Post-Wave 2)

1. **Wait for:** Completion of WS3 Waves 1 + 2
2. **Receive:** Final reference map + validated paths + de-collision confirmation
3. **Reference:** Coordination notes in REMEDIATION_PRIORITY.md
4. **Execute:** Bulk moves after reference graph is stable

### For CI/CD Team (During Wave 2)

1. **Monitor:** WS3 Wave 2B execution (hardcode replacements)
2. **Verify:** CI scripts still work after hardcode fixes
3. **Test:** On non-GHA runners (Linux, macOS)
4. **Reference:** REMEDIATION_PRIORITY.md §4 (H3 hardcode replacement)

### For Developers (During/After Wave 3)

1. **Read:** REMEDIATION_PRIORITY.md §5 (Wave 3 outcomes)
2. **Follow:** WSL/Git-Bash requirement documentation (Wave 3B)
3. **Understand:** Platform-specific tool dependencies (Wave 3C)
4. **Update:** Local development environment as needed

---

## 📊 DOCUMENT STATISTICS

| Document | Lines | KB | Purpose |
|----------|-------|----|----|
| PHASE_8_3_COMPATIBILITY_MATRIX.md | 379 | 15 | Case-collision sequence |
| PHASE_8_3_REMEDIATION_PRIORITY.md | 628 | 22 | Phased remediation |
| PHASE_8_3_WORKSTREAM_2_COMPLETION_REPORT.md | 412 | 18 | WS2 handoff |
| **TOTAL WS2 DELIVERABLES** | **1,419** | **55** | **Complete planning** |

---

## ✅ SUCCESS CRITERIA (WS2 → WS3 HANDOFF)

All criteria met. WS2 is **COMPLETE** and **READY FOR EXECUTION.**

- [x] Compatibility matrix with all 13 case-collision groups
- [x] De-collision sequence (explicit ordering, dependencies)
- [x] Reference update scope (Type A–D files identified)
- [x] Coordination framework (Track 8.1, 8.2, CI/CD, developers)
- [x] Validation checkpoints (link integrity, git status)
- [x] Risk assessment (high/medium/low classification)
- [x] Blast-radius analysis (repo-wide and item-level)
- [x] Gitattributes remediation plan (quick-win)
- [x] Phased approach (3 waves, concurrent execution)
- [x] Effort estimates (5–9 weeks, 1–2 FTE)
- [x] Success metrics (per wave, post-execution)
- [x] Rollback procedures (per wave)
- [x] Open questions flagged
- [x] Documentation complete

---

## 🚀 NEXT STEPS: WAVE 1 EXECUTION (WS3 PHASE A)

### Week 1: Reference Mapping & Case-Collision De-collision

```
Day 1-3:  Build case-collision reference graph
          • Grep all references (Markdown, YAML, Python)
          • Document content uniqueness
          • Generate merge plan → .codex/PHASE_8_3_CASE_COLLISION_REFERENCE_MAP.md

Day 4-6:  Execute de-collision (GROUP 1 first)
          • Consolidate GROUP 1 (3-way merge)
          • Update all Type A–D references
          • Validation: link integrity, case-collision re-scan

Day 7-10: Continue de-collision (GROUP 5/9, then remaining 10)
          • Same process as GROUP 1
          • Parallel reference updates possible

Parallel:
Day 1-7:  Root .gitattributes activation
          • Copy .config/.gitattributes → ./.gitattributes
          • Verify: git check-attr
          • Commit atomically with case-collision fixes
```

### Success Metrics (End of Wave 1)

- [ ] All 13 case-collision groups consolidated
- [ ] Zero case-collision entries in git
- [ ] All 216 bash scripts have LF line endings
- [ ] Zero broken links in documentation
- [ ] Repository clones successfully on Windows

---

## 📋 QUICK REFERENCE: WHAT GETS FIXED WHEN

| When | What | Why | Files |
|------|------|-----|-------|
| **Wave 1 (Weeks 1–2)** | Case collisions + .gitattributes | Blocks clean Windows checkout | 13 groups + 1 config |
| **Wave 2 (Weeks 3–6)** | Symlinks + hardcodes + tool paths | Breaks off-CI execution | 15 symlinks + 44 hardcodes + ~3–5 CI helpers |
| **Wave 3 (Weeks 7–9)** | Temp files + bash docs + tool guards | Full cross-platform portability | 93 files + 216 scripts + ~33 scripts + 2 configs |

---

## 🔗 RELATED DOCUMENTS (Reference)

**WS1 Audit (Completed):**
- `.codex/archive/phase-reports/phase-1-10/PHASE_8_3_PLATFORM_AUDIT_REPORT.md`

**WS2 Planning (Completed):**
- `.codex/PHASE_8_3_COMPATIBILITY_MATRIX.md` ← Detailed case-collision plan
- `.codex/PHASE_8_3_REMEDIATION_PRIORITY.md` ← Phased execution roadmap
- `.codex/PHASE_8_3_WORKSTREAM_2_COMPLETION_REPORT.md` ← Handoff summary

**WS3 Execution (To Be Generated):**
- `.codex/PHASE_8_3_CASE_COLLISION_REFERENCE_MAP.md` (Wave 1A)
- `.codex/PHASE_8_3_WAVE_1_EXECUTION_REPORT.md` (Wave 1A/1B results)
- `.codex/PHASE_8_3_WAVE_2_EXECUTION_REPORT.md` (Wave 2A/2B/2C results)
- `.codex/PHASE_8_3_WAVE_3_EXECUTION_REPORT.md` (Wave 3A/3B/3C results)
- `.codex/PHASE_8_3_FINAL_VALIDATION_REPORT.md` (Windows/macOS/Linux verification)

---

## ❓ FREQUENTLY ASKED QUESTIONS (WS2 Planning)

**Q: Why does case-collision matter if filenames are clean?**  
A: On Windows NTFS and macOS APFS (default case-insensitive), having multiple files like `docs/ARCHITECTURE.md` and `docs/architecture.md` causes silent file loss during checkout — one file overwrites the other. This breaks links and makes the repo unusable on Windows.

**Q: Can we execute Waves in parallel?**  
A: **No.** Wave 1 must complete first (it cleans up the repo state). Within Wave 1, items 1A (case collisions) and 1B (.gitattributes) can run in parallel. Wave 2 depends on Wave 1 completion. Wave 3 depends on Wave 2 completion. However, within Waves 2 and 3, some items (H2/H3/H4 and M1/M2/M3) can run in phases or parallel.

**Q: What if case-collision consolidation reveals duplicate content?**  
A: That's expected (likely for CI.md/ci.md, QUICKSTART.md/quickstart.md, etc.). WS3 Wave 1A includes a content-merge phase to handle this.

**Q: How long will this take?**  
A: 5–9 weeks with 1–2 FTE. Wave 1 (1–2 weeks) is critical path; Waves 2–3 can run in series or with some parallelization.

**Q: What about the shell scripts (216 bash files)?**  
A: They're documented as medium-priority (Wave 3B). We're not porting them to Windows-native in this round, just documenting the WSL/Git-Bash requirement. Selective porting (Tier A: 47 high-traffic scripts) is a future stretch goal.

**Q: Can I start WS3 execution now?**  
A: **YES.** All planning is complete. WS3 is ready to begin immediately. Start with Wave 1 (case collisions + .gitattributes).

---

## 📞 ESCALATION & QUESTIONS

**For planning clarifications:** Refer to relevant section in REMEDIATION_PRIORITY.md or COMPATIBILITY_MATRIX.md.

**For execution blockers:** Flag as GitHub issue with label `phase-8.3-ws3` and link to relevant section.

**For coordination:** Contact Track 8.1 lead (doc renames), Track 8.2 lead (bulk moves), CI/CD team (hardcode changes).

---

**Index Status:** ✅ COMPLETE  
**WS2 Status:** ✅ COMPLETE & READY FOR WS3  
**Authority:** @mbaetiong (D-tier autonomous)  
**Next Phase:** WS3 Execution (Waves 1, 2, 3)  
**Timestamp:** 2026-07-07T14:26Z
