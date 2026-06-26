# WEC Hardening & Workflow Governance - Complete Documentation Index

**Version:** 1.0.0  
**Date:** 2026-06-26  
**Status:** ✅ COMPLETE (Phases 1-5)  
**Author:** Copilot Agent Hardening Initiative  

---

## 🎯 Quick Navigation

**📊 I need to understand...**
| Question | Document | Section |
|----------|----------|---------|
| "What is WEC and why does it matter?" | `WEC_SESSION_INVARIANT.md` | Executive Summary |
| "Why did my workflow fail?" | `WORKFLOW_FAILURE_MATRIX.md` | Pattern identification table |
| "How do I fix a REQ-4 or REQ-5 failure?" | `WORKFLOW_FAILURE_MATRIX.md` | WF-001, WF-002 |
| "Why can't approval workflows run?" | `AUTO_APPROVE_PREREQUISITE_GUIDE.md` | Failure Scenarios 1-2 |
| "What is a 'healthy' PR?" | `MAIN_BRANCH_WORKFLOW_HEALTH.md` | Healthy PR Profile |
| "What are all the WEC workflows?" | `WEC_CANONICAL_ITEMS.md` | Item definitions table |
| "How do I preserve WEC during my session?" | `WEC_SESSION_INVARIANT.md` | Session Phases 1-4 |

---

## 📚 Document Library

### Core WEC Documentation (Required Reading)

#### 1. **WEC Session Invariant** (12.3 KB)
**File:** `.codex/WEC_SESSION_INVARIANT.md`  
**Purpose:** Binding contract defining how Copilot Agents MUST handle WEC throughout their session lifecycle

**Contains:**
- 4 Session Phases (INIT → WORK → PRE-COMMIT → FINALIZE)
- WEC Requirements by merge target (main vs 0D_base_)
- State preservation algorithm (read → maintain → verify)
- WEC validation gates at each phase
- Recovery procedures for WEC corruption
- Merge-blocking rules per branch

**Who Should Read:**
- ✅ All Copilot Agents (MANDATORY before first commit)
- ✅ Session designers
- ✅ CI/CD maintainers

**Key Sections:**
- Lines 1-50: Executive summary & motivation
- Lines 51-150: 4 Session phases with detailed actions
- Lines 151-200: WEC requirements by branch
- Lines 201-250: Validation gates & recovery

**Action Items for Copilot Agents:**
```
1. Read PHASE 1 (INITIALIZATION) at session start
2. Follow PHASE 2 (WORK) action list on every report_progress call
3. Run PHASE 3 (PRE-COMMIT) validation before final commit
4. Complete PHASE 4 (FINALIZATION) before session end
```

---

#### 2. **WEC Canonical Items** (12.1 KB)
**File:** `.codex/WEC_CANONICAL_ITEMS.md`  
**Purpose:** Authoritative definition of all 9 WEC workflow items

**Contains:**
- Complete item roster (9 items, 5 REQUIRED + 4 OPTIONAL)
- Merge target rules (main vs 0D_base_ requirements)
- Auto-approval prerequisites for each item
- Owner agent assignments
- Validation rules and format specification
- Auto-fix procedures

**Who Should Read:**
- ✅ Copilot Agents (reference before selecting workflows)
- ✅ WEC validation tools
- ✅ CI maintainers

**Key Sections:**
- Lines 1-50: Item roster table
- Lines 51-100: Merge target requirements
- Lines 101-150: Auto-approval matrix
- Lines 151-200: Validation & format rules

**Action Items for Copilot Agents:**
```
1. Before merging to main: check all 5 REQUIRED items are [x]
2. Before merging to 0D_base_: check all 5 REQUIRED items are [x]
3. Optional items: check only if your session made changes requiring them
4. Validate format: all [x] or [ ], no [X] or [ x]
```

---

### Failure Diagnosis & Prevention (Reference)

#### 3. **Workflow Failure Root-Cause Matrix** (18.9 KB)
**File:** `.codex/WORKFLOW_FAILURE_MATRIX.md`  
**Purpose:** Comprehensive diagnosis library for 8 common workflow failure patterns

**Contains:**
- WF-001: REQ-4 missing (AGENT_ACCOUNTABILITY_REPORT.md)
- WF-002: REQ-5 missing (CHANGELOG.md)
- WF-003: WEC state loss (stripped from PR body)
- WF-004: WEC format corruption (invalid checkbox syntax)
- WF-005: Approval token insufficient (no actions:write scope)
- WF-006: Required items unchecked (governance blocking merge)
- WF-007: Cost gate exceeded
- WF-008: Rate limiting (GitHub API quota)

**Each Pattern Includes:**
- Root cause explanation
- Automatic detection method
- Failure mode (blocking vs non-blocking)
- Automatic & manual remediation steps
- Prevention strategy for future sessions
- Related issues & documentation links

**Who Should Read:**
- ✅ When a workflow fails and you need to diagnose
- ✅ Copilot Agents (for prevention strategies)
- ✅ CI troubleshooting agents
- ✅ Maintainers investigating patterns

**Quick Reference:**
- Lines 1-100: Critical patterns (WF-001, WF-002, WF-003, WF-004)
- Lines 101-200: Medium patterns (WF-005, WF-006)
- Lines 201-300: Low patterns (WF-007, WF-008)
- Lines 301-350: Summary table & escalation procedures

**Action Items When Failure Occurs:**
```
1. Check failure message/logs
2. Match pattern to WF-00X using pattern ID or symptom
3. Follow "Remediation Steps" (automatic or manual)
4. Apply "Prevention Strategy" for next session
5. If pattern recurs: escalate per "Escalation Procedures"
```

---

#### 4. **Auto-Approve Prerequisite Guide** (12.9 KB)
**File:** `.codex/AUTO_APPROVE_PREREQUISITE_GUIDE.md`  
**Purpose:** Explain token requirements and auto-approval failure recovery

**Contains:**
- Token hierarchy (CODEX_MASTER_KEY > CODEX_BACKUP_KEY > github.token)
- Token scope matrix (which scopes enable which operations)
- Explanation of why github.token fails (no actions:write)
- Auto-approval workflow selection logic
- WEC item → auto-approve mapping
- 4 failure scenarios with recovery procedures
- Best practices for Copilot Agents
- Troubleshooting checklist

**Who Should Read:**
- ✅ When approval workflows won't run
- ✅ Copilot Agents (for token strategy understanding)
- ✅ Repository maintainers (for secret configuration)
- ✅ CI infrastructure maintainers

**Key Sections:**
- Lines 1-100: Token hierarchy & scope requirements
- Lines 101-150: Approval mechanics & WEC mapping
- Lines 151-250: Failure scenarios 1-4 with recovery
- Lines 251-300: Best practices & troubleshooting

**Action Items When Approval Fails:**
```
1. Check error message for symptom (403, 429, timeout, etc.)
2. Match to Scenario 1-4 in "Failure Scenarios" section
3. Follow "Recovery" steps for that scenario
4. Verify token scope: GH_TOKEN=$CODEX_MASTER_KEY gh auth status --show-token
5. If still failing: escalate with full logs
```

---

### Health Tracking & Monitoring (Baseline)

#### 5. **Main Branch Workflow Health Baseline** (7.7 KB)
**File:** `.codex/MAIN_BRANCH_WORKFLOW_HEALTH.md`  
**Purpose:** Establish and track metrics for "healthy PR" state

**Contains:**
- Health metrics definitions (success rate, auto-approve rate, compliance rate, WEC preservation)
- Health score formula
- Template for recording successful merges
- Trend analysis sections (populated after merges)
- Alert thresholds (critical 🔴, warning 🟡, info 🟢)
- Escalation procedures
- Reference "healthy PR profile" checklist
- Tool dependencies

**Who Should Read:**
- ✅ When investigating pattern recurrence
- ✅ Repository maintainers (for health trending)
- ✅ Automation designers (for alert configuration)
- ✅ Copilot Agents (as reference baseline)

**Key Sections:**
- Lines 1-50: Metrics definitions & formula
- Lines 51-100: Baseline entry template
- Lines 101-150: Trend analysis (to be populated)
- Lines 151-200: Alert thresholds & escalation
- Lines 201-250: Healthy PR profile checklist

**Action Items:**
```
1. After each successful merge to main:
   - Record new entry using template provided
   - Update summary statistics
   - Check if any metrics dropped below thresholds

2. If health score drops below 85%:
   - Investigate last 3 failed merges for common pattern
   - Reference WORKFLOW_FAILURE_MATRIX.md for root causes
   - Implement prevention strategy
   - Escalate if pattern recurs
```

---

## 🔄 Session Workflow

### Copilot Agent Session Checklist

```
🟢 SESSION START
└─ [ ] Read WEC_SESSION_INVARIANT.md PHASE 1 (INITIALIZATION)
└─ [ ] Extract current WEC from PR body
└─ [ ] Validate WEC format (all [x] or [ ], no typos)
└─ [ ] Reference WEC_CANONICAL_ITEMS.md to confirm all items present
└─ [ ] Log WEC state to session context comment

🟠 SESSION WORK
└─ [ ] Before EVERY report_progress call:
      └─ [ ] Read current WEC state from PR body
      └─ [ ] Reference WEC_SESSION_INVARIANT.md PHASE 2 (WORK)
      └─ [ ] Include WEC block in prDescription parameter
      └─ [ ] Verify WEC is still in PR body after push
└─ [ ] If workflow fails:
      └─ [ ] Reference WORKFLOW_FAILURE_MATRIX.md for root cause
      └─ [ ] Apply remediation step
      └─ [ ] Document fix in session comment

🔴 PRE-COMMIT
└─ [ ] Run compliance check:
      python scripts/ci/session_wrapup_autofix.py --check --pr N
└─ [ ] Expected output: REQ-4 ✅, REQ-5 ✅, WEC valid ✅
└─ [ ] If any check fails:
      └─ [ ] For REQ-4/REQ-5: run --auto-update
      └─ [ ] For WEC: run wec_enforcer.py --validate-body --pr N
      └─ [ ] Re-run --check to confirm all pass
└─ [ ] Reference WORKFLOW_FAILURE_MATRIX.md WF-001, WF-002, WF-003, WF-004

🟣 SESSION END
└─ [ ] Verify WEC is in final PR body (not stripped)
└─ [ ] Confirm all REQUIRED items are [x] for merge target
└─ [ ] Reference WEC_SESSION_INVARIANT.md PHASE 4 (FINALIZE)
└─ [ ] Post session summary comment with:
      └─ [ ] WEC state at session START vs END
      └─ [ ] Governance compliance: REQ-4 ✅, REQ-5 ✅
      └─ [ ] Which workflows were selected/deselected and why
      └─ [ ] Any manual interventions or escalations
```

---

## 🚀 Phase Implementation Roadmap

### ✅ Completed (Phases 1-5)

- [x] **Phase 1:** Root Cause Diagnosis (analysis only)
- [x] **Phase 2:** WEC Template Hardening (documentation + copilot-instructions)
- [x] **Phase 3 (Doc):** Governance File Enforcement (documentation)
- [x] **Phase 4 (Doc):** Auto-Approve Hardening (documentation)
- [x] **Phase 5:** Verification & Documentation (5 documents created)

### ⏳ In Progress / Ready for Next Session

**Phase 3 Implementation (Code Changes):**
```
Task 3.1: Enhance session_wrapup_autofix.py
- Add _validate_req4_req5_compliance() function
- Pre-commit validation logic
- Auto-append accountability info if missing

Task 3.2: Session Accountability Template
- Auto-populate using template structure
- Integration with session_wrapup_autofix.py

Task 3.3: Add WEC Checks to pre-merge-validation.yml
- Validate all required items listed
- Check no deprecated items
- Validate checkbox format
- Post blocking comment on violations
```

**Phase 4 Implementation (Code Changes):**
```
Task 4.1: Update auto-approve-workflows.yml
- Call wec_enforcer.py --check-workflow for each pending
- Honor checkbox state (checked = approve, unchecked = skip)
- Log approval decisions

Task 4.2: AUTO_APPROVE_PREREQUISITE_GUIDE.md (DONE)
- Token configuration
- Failure recovery documented

Task 4.3: Add Approval Recovery Logic
- Periodic approval sweep
- Approval state logging
- Diagnosis & recovery
```

**Phase 6: Continuous Monitoring (Code Changes):**
```
Task 6.1: Create workflow_health_monitor.py
- Daily health report generation
- Failure pattern detection
- Auto-create issues if health drops

Task 6.2: Create WEC_AUDIT_TRAIL.md
- Append-only event log
- WEC state changes, approvals, compliance

Task 6.3: Enhance Session Template
- WEC state section
- Compliance checklist
- Auto-approval decisions log
```

**Phase 7: Acceptance Criteria (Validation):**
```
Success Metrics (30-day evaluation):
- Zero REQ-4/REQ-5 failures on main merges
- 100% WEC state preservation
- 95%+ auto-approval success rate
- All sessions document WEC & governance
- Workflow health score ≥90%
```

---

## 📞 Support & Escalation

### When to Reference Each Document

| Situation | Document | Section |
|-----------|----------|---------|
| Starting a new Copilot session | WEC_SESSION_INVARIANT.md | PHASE 1 (INITIALIZATION) |
| Selecting WEC workflows | WEC_CANONICAL_ITEMS.md | Item roster & merge target rules |
| Fixing REQ-4 failure | WORKFLOW_FAILURE_MATRIX.md | WF-001 |
| Fixing REQ-5 failure | WORKFLOW_FAILURE_MATRIX.md | WF-002 |
| Fixing WEC stripped from PR | WORKFLOW_FAILURE_MATRIX.md | WF-003 |
| Fixing WEC format errors | WORKFLOW_FAILURE_MATRIX.md | WF-004 |
| Approval workflows won't run | AUTO_APPROVE_PREREQUISITE_GUIDE.md | Failure Scenarios |
| Token 403 errors | AUTO_APPROVE_PREREQUISITE_GUIDE.md | Token scope matrix |
| Health score dropped | MAIN_BRANCH_WORKFLOW_HEALTH.md | Alert thresholds & escalation |
| Workflow keeps failing | WORKFLOW_FAILURE_MATRIX.md | Summary table |

### Escalation Path

```
Level 1: Check Documentation
└─ Reference the relevant doc above
└─ Follow remediation steps
└─ If resolved: document prevention strategy

Level 2: Apply Auto-Fix
└─ Run session_wrapup_autofix.py --auto-update
└─ Run wec_enforcer.py --validate-body --pr N --fix
└─ Re-validate: --check passes

Level 3: Manual Intervention
└─ If auto-fix fails: post diagnostic comment
└─ Document findings in session summary
└─ Create GitHub issue [CI_HEALTH] for investigation

Level 4: Agent Escalation
└─ unified-governance-gate (for governance issues)
└─ workflow-ci-fixer (for workflow YAML issues)
└─ ci-auto-healer-agent (for automated repair)
└─ @mbaetiong (for policy decisions)
```

---

## 📊 Metrics & Success Criteria

### 30-Day Evaluation (Post-Implementation)

| Metric | Target | Success Criteria |
|--------|--------|------------------|
| **REQ-4/REQ-5 Failures** | 0 on main | Zero governance failures over 30 days |
| **WEC Preservation** | 100% | All PR merges preserve WEC state |
| **Auto-Approve Rate** | 95%+ | (Workflows auto-approved / needing approval) |
| **Health Score** | ≥90% | Calculated per formula in baseline doc |
| **Session Documentation** | 100% | All sessions document WEC state changes |
| **Workflow Success Rate** | 95%+ | (Successful runs / total runs) |

### Red Flags (Escalate If Observed)

- ❌ 2+ consecutive REQ-4 or REQ-5 failures
- ❌ Any WEC stripped from PR body (governance violation)
- ❌ Health score drops below 85%
- ❌ Auto-approval success rate falls below 90%
- ❌ Same failure pattern on 3+ consecutive merges
- ❌ Token scope issues preventing approvals

---

## 🔗 Cross-References

**Related Repository Documents:**
- `.codex/CODEBASE_AGENCY_POLICY.md` - Governance policy
- `.codex/WEC_PR_BODY_CONFLICTS.md` - PR body conflict patterns
- `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md` - Token configuration
- `docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md` - Secrets management
- `.github/copilot-instructions.md` - Copilot Agent responsibilities

**Tools & Scripts:**
- `scripts/ci/session_wrapup_autofix.py` - Compliance checking & auto-update
- `scripts/ci/wec_enforcer.py` - WEC validation & enforcement
- `scripts/ci/workflow_health_monitor.py` (TBD) - Health tracking
- `.github/workflows/pre-merge-validation.yml` - Pre-merge gates
- `.github/workflows/phase-12-2-compliance-check.yml` - Governance gates

---

## 📝 Document Version History

| Document | Version | Date | Status |
|----------|---------|------|--------|
| WEC_SESSION_INVARIANT.md | 1.0.0 | 2026-06-26 | ✅ COMPLETE |
| WEC_CANONICAL_ITEMS.md | 1.0.0 | 2026-06-26 | ✅ COMPLETE |
| WORKFLOW_FAILURE_MATRIX.md | 1.0.0 | 2026-06-26 | ✅ COMPLETE |
| AUTO_APPROVE_PREREQUISITE_GUIDE.md | 1.0.0 | 2026-06-26 | ✅ COMPLETE |
| MAIN_BRANCH_WORKFLOW_HEALTH.md | 1.0.0 | 2026-06-26 | ✅ COMPLETE |
| This Index | 1.0.0 | 2026-06-26 | ✅ COMPLETE |

---

## 🎓 Training & Adoption

### For Copilot Agents

**Required Reading (Before First Commit):**
1. WEC_SESSION_INVARIANT.md (PHASE 1)
2. WEC_CANONICAL_ITEMS.md (merge target rules)
3. copilot-instructions.md (⚙️ WEC Template Maintenance section)

**Reference During Session:**
- Keep WORKFLOW_FAILURE_MATRIX.md open for quick lookup
- Reference AUTO_APPROVE_PREREQUISITE_GUIDE.md if approvals fail
- Use MAIN_BRANCH_WORKFLOW_HEALTH.md as reference baseline

**Training Checklist:**
- [ ] Understand all 4 session phases (WEC_SESSION_INVARIANT)
- [ ] Know the 9 WEC items and their requirements (WEC_CANONICAL_ITEMS)
- [ ] Know how to run compliance check (copilot-instructions + session_wrapup_autofix.py)
- [ ] Know how to recover from 3 most common failures (WORKFLOW_FAILURE_MATRIX WF-001, WF-002, WF-003)
- [ ] Pass test merge to staging branch preserving WEC

### For Repository Maintainers

**Setup Tasks:**
1. Ensure CODEX_MASTER_KEY and CODEX_BACKUP_KEY are configured with actions:write scope
2. Verify pre-merge-validation.yml and phase-12-2-compliance-check.yml are enabled
3. Review alert thresholds in MAIN_BRANCH_WORKFLOW_HEALTH.md; adjust if needed
4. Set up daily health monitoring (Phase 6 implementation)

**Monitoring Tasks:**
1. Weekly review of health metrics (MAIN_BRANCH_WORKFLOW_HEALTH.md)
2. Monthly review of failure patterns (WORKFLOW_FAILURE_MATRIX.md)
3. Alert on health score drop below 85%
4. Escalate recurring patterns to specialized agents

---

**Document Status:** ✅ COMPLETE  
**Ready for:** Phase 6-7 implementation in next session  
**Copilot Agent:** Start with WEC_SESSION_INVARIANT.md PHASE 1 at every session start
