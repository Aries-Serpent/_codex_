# Phase 8.2.2 Repository Structure Organization Planning

**Phase Code**: 8.2.2  
**Authority**: D-mode autonomy (no approval gates required)  
**Timeline**: 20–30 minutes  
**Status**: 🟡 PLANNING (ready for execution)  
**Generated**: 2026-01-26

---

## Executive Summary

Based on the comprehensive audit findings from **Phase 8.2.3 Cleanup Execution**, this planning document outlines a structured approach to organize the remaining repository structure challenges. With **17,081 tracked files** across the codebase, **~25% concentrated in .codex/**, and **~715 virtual environment files** requiring cleanup, we have identified critical organizational inefficiencies and opportunities for strategic consolidation.

This phase focuses on **proactive planning** and **risk mitigation** before executing the major cleanup batches (which have already been completed in 8.2.3). The planning document serves as a reference for ongoing repository health maintenance and establishes decision frameworks for future optimization efforts.

---

## Part 1: Analysis of Audit Findings

### 1.1 Current State Metrics

| Metric | Pre-Cleanup | Post-Cleanup (8.2.3) | Trend |
|--------|------------|----------------------|-------|
| **Total tracked files** | 17,101 | 16,377 | -724 files (-4.2%) |
| **Filesystem files** | 17,201 | 15,500+ | -1,700+ files (-9.8%) |
| **Files in .codex/** | ~4,275 | ~4,000+ | Consolidated |
| **Virtual environment files** | 705 | 0 | 100% removed ✅ |
| **Phase reports** | 885 | 0 (archived) | Organized ✅ |
| **Root directory clutter** | 114+ | ~40 | 65% reduced ✅ |

### 1.2 Critical Findings

#### Finding A: Virtual Environment Bloat (✅ RESOLVED in 8.2.3)
- **Identified**: ~715 venv files across `venv_test/`, `.venv_ci/`, and other patterns
- **Impact**: Significant filesystem pollution; slows git operations; increases sync times
- **Status**: Batch 0 removed 705 venvs; .gitignore hardened with patterns
- **Outcome**: Zero venvs remaining; regeneration verified safe

#### Finding B: Archive Structure Gap (✅ RESOLVED in 8.2.3)
- **Identified**: 885 phase history files scattered in .codex/ root
- **Impact**: Navigation difficulty; cluttered directory; slow lookups
- **Status**: Batch 3 organized into nested structure (phase-1-10, phase-11-20, etc.)
- **Outcome**: Phase reports archived with INVENTORY.ndjson and RETRIEVAL_GUIDE.md

#### Finding C: Root Directory Clutter (✅ RESOLVED in 8.2.3)
- **Identified**: 114+ loose files in repository root (PHASE_*, GATE_*, *_REPORT.md, etc.)
- **Impact**: Difficult to distinguish active files from historical data; navigation friction
- **Status**: Batch 2 moved 55+ files to `.codex/archive/root-consolidation/`
- **Outcome**: Root directory reduced to ~40 essential files

#### Finding D: Build Artifacts Persistence (✅ RESOLVED in 8.2.3)
- **Identified**: 20+ coverage reports, .build/ directory, coverage_tests/
- **Impact**: Increases repository size; can be regenerated; not essential to maintain
- **Status**: Batch 1 archived to `.codex/archive/artifacts/`
- **Outcome**: Build artifacts organized with clear retrieval path

#### Finding E: Configuration Fragmentation (⏸️ DEFERRED to Batch 4)
- **Identified**: `config_legacy/`, `yaml_legacy/`, `config_experiments/` scattered across root
- **Impact**: Import confusion; unclear which configs are active; maintenance burden
- **Status**: Deferred pending Track 8.3 (case-collision fixes)
- **Outcome**: Will consolidate after dependency resolution

#### Finding F: .codex/ Directory Expansion (~25% of all files)
- **Identified**: .codex/ contains phase reports, archived files, temporary outputs, and documentation
- **Impact**: Directory is becoming a catch-all; needs internal organization standards
- **Status**: Post-cleanup structure in place; ongoing maintenance needed
- **Outcome**: `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md` established

### 1.3 Key Insights

| Insight | Implication | Priority |
|---------|-------------|----------|
| **Filesystem files exceed git-tracked files** | Many files in .gitignore (venvs, caches); cleanup impacts actual disk usage significantly | High |
| **25% of tracked files in .codex/** | Archive and phase reports create organizational challenges; need indexing/retrieval aids | High |
| **Phase reports moved to archive** | Historical data preserved but needs navigation guides to remain accessible | Medium |
| **Root directory now ~40 files** | Much cleaner; easier to identify active vs. historical; supports project discoverability | High |
| **Venvs completely removed** | Improves git clone times; simplifies CI/CD; venvs are easily regenerated | High |

---

## Part 2: Priority Matrix (Impact × Effort)

### 2.1 3×3 Priority Matrix

```
IMPACT
  ↑
  │  [Q2: Quick Wins]         [Q1: Strategic Initiatives]
  │  - Validate archive          - Implement .codex/ standards
  │    navigation                 - Set up retention policies
  │  - Create retrieval guides    - Establish naming conventions
  │
  ├──────────────────────────────────────────────────────→ EFFORT
  │
  │  [Q3: Low Value]           [Q4: Deferred/Complex]
  │  - Review temp outputs       - Config consolidation (Batch 4)
  │  - Validate cleanup           - External storage integration
  │    completeness              - ML-based candidate prediction
  │
  └─────────────────────────────────────────────────────
```

### 2.2 Task Prioritization

#### 🔴 CRITICAL PRIORITY (High Impact + Low Effort)

1. **Task: Validate Archive Structure Integrity**
   - **Effort**: Low (30 min) | **Impact**: High (enables ongoing maintenance)
   - **Owner**: repository-organization-agent
   - **Scope**: Verify all 1,666+ files reached target locations; check INVENTORY.ndjson completeness
   - **Success**: All archived files accessible via retrieval guides

2. **Task: Document .codex/ Organization Standards**
   - **Effort**: Low (45 min) | **Impact**: High (prevents future clutter)
   - **Owner**: QA Walkthrough + repository-organization-agent
   - **Scope**: Codify directory structure, naming conventions, retention policies
   - **Success**: `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md` complete and enforced

#### 🟠 HIGH PRIORITY (Medium Impact + Medium Effort)

3. **Task: Implement Retention Policy Framework**
   - **Effort**: Medium (60 min) | **Impact**: Medium (prevents re-accumulation of clutter)
   - **Owner**: repository-organization-agent
   - **Scope**: Define time-based retention (permanent vs. temporary files); automate cleanup triggers
   - **Success**: Retention policy document + automation checklist

4. **Task: Set Up Archive Monitoring Dashboard**
   - **Effort**: Medium (45 min) | **Impact**: Medium (ongoing health tracking)
   - **Owner**: repository-organization-agent
   - **Scope**: Create `.codex/repository_health/DASHBOARD.md` with metrics, trends, recommendations
   - **Success**: Dashboard updated weekly; shows repository size, top files, growth trends

#### 🟡 MEDIUM PRIORITY (Medium Impact + High Effort)

5. **Task: Establish Naming Convention Enforcement**
   - **Effort**: High (90 min) | **Impact**: Medium (improves consistency)
   - **Owner**: policy-coach-agent + repository-organization-agent
   - **Scope**: Define file naming patterns (PHASE_*, GATE_*, etc.); create linting rules; document exceptions
   - **Success**: Naming guide published; no violations in new commits

#### 🟢 LOW PRIORITY (Low Impact + Low Effort)

6. **Task: Create Quick-Reference Index**
   - **Effort**: Low (30 min) | **Impact**: Low (convenience feature)
   - **Owner**: documentation-quality-agent
   - **Scope**: Summarize archive structure in README; link to retrieval guides
   - **Success**: `.codex/archive/README.md` created with quick links

---

## Part 3: Action Sequences (5–7 Concrete Items)

### Sequence Overview

All actions are ordered by **dependency** and **risk level** (lowest risk first):

```
Action 1: Validate Archive Integrity
    ↓
Action 2: Document .codex/ Standards
    ↓
Action 3: Implement Retention Policies
    ↓
Action 4: Set Up Health Dashboard
    ↓
Action 5: Enforce Naming Conventions
    ↓
Action 6: Create Quick-Reference Index
    ↓
Action 7: (Optional) Plan Batch 4 Execution
```

### Action Items

#### **Action 1: Validate Archive Integrity** (30 min)
**Purpose**: Ensure all archived files are accessible and complete  
**Authority**: repository-organization-agent  
**Dependencies**: None (Actions 8.2.3 Batch 0–3 completed)  
**Steps**:
1. Verify INVENTORY.ndjson in `.codex/archive/phase-reports/` contains all 885 phase report entries
2. Spot-check 10 random files in `.codex/archive/artifacts/`, `.codex/archive/root-consolidation/`
3. Validate all retrieval guides (3 RETRIEVAL_GUIDE.md files) have correct paths
4. Confirm git commits for Batches 0–3 contain expected file moves

**Success Criteria**:
- ✅ All 1,666+ files present in archive locations
- ✅ No orphaned file references
- ✅ INVENTORY.ndjson validates against actual files

**Output**:
- Validation report in `.codex/PHASE_8_2_2_VALIDATION_INTEGRITY.md`

---

#### **Action 2: Document .codex/ Organization Standards** (45 min)
**Purpose**: Establish clear organizational rules for the .codex/ directory  
**Authority**: repository-organization-agent  
**Dependencies**: Action 1 (archive validated)  
**Steps**:
1. Review current `.codex/` structure post-cleanup:
   - `archive/` (phase-reports, artifacts, root-consolidation)
   - Active working directories (qa_walkthrough, repository_health, etc.)
   - Temporary outputs (action_log.ndjson, etc.)
2. Define standardized structure:
   ```
   .codex/
   ├── archive/              (permanent storage; never modify)
   ├── qa_walkthrough/       (active QA documents)
   ├── repository_health/    (metrics & dashboards)
   ├── agent_context/        (agent configurations)
   └── [temporary outputs]   (cleaned quarterly)
   ```
3. Document retention rules:
   - **Permanent**: phase-reports, artifacts, qa_walkthrough
   - **90-day**: temporary outputs, action logs
   - **180-day**: deprecated-reports, experimental configs
4. Create `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md` with:
   - Directory structure diagram
   - Naming conventions (PHASE_*, GATE_*, *_COMPLETION_*)
   - Retention schedule
   - Examples of correct vs. incorrect organization

**Success Criteria**:
- ✅ Standards document published and linked from main README
- ✅ No ambiguity about where files should go
- ✅ Retention rules clear and enforceable

**Output**:
- `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md` (updated/finalized)

---

#### **Action 3: Implement Retention Policy Framework** (60 min)
**Purpose**: Automate cleanup to prevent re-accumulation of clutter  
**Authority**: repository-organization-agent  
**Dependencies**: Action 2 (standards defined)  
**Steps**:
1. Define retention tiers:
   - **PERMANENT**: Phase reports, coverage baselines, archived artifacts
   - **LONG-TERM** (180 days): Deprecated documentation, experimental configs
   - **MEDIUM-TERM** (90 days): Temporary test outputs, build artifacts
   - **SHORT-TERM** (30 days): Action logs, CI/CD debug output
2. Create retention policy document:
   - File patterns matching each tier
   - Archival procedures (gzip compression for ≥1MB files)
   - Retrieval instructions
   - Audit trail logging
3. Establish automated triggers:
   - Quarterly cron job to identify archival candidates
   - Monthly health report generation
   - Manual override mechanism for exceptions
4. Document in `.codex/PHASE_8_2_RETENTION_POLICY.md`

**Success Criteria**:
- ✅ Retention policy document complete and signed off
- ✅ Automation checklist created for future implementation
- ✅ Clear process for exception handling

**Output**:
- `.codex/PHASE_8_2_RETENTION_POLICY.md`
- `.codex/PHASE_8_2_RETENTION_AUTOMATION_CHECKLIST.md`

---

#### **Action 4: Set Up Repository Health Dashboard** (45 min)
**Purpose**: Establish ongoing metrics to track repository organization health  
**Authority**: repository-organization-agent  
**Dependencies**: Action 1 (archive validated), Action 3 (policies in place)  
**Steps**:
1. Create `.codex/repository_health/DASHBOARD.md` with:
   - **Current Metrics**:
     - Total repository size (in MB)
     - Git-tracked files breakdown (by category)
     - Archive size and growth rate
     - Top 10 largest files/directories
   - **Historical Trends**:
     - File count over time (last 5 phases)
     - Archive growth trajectory
     - Cleanup impact (before/after)
   - **Health Indicators**:
     - % of files in .codex/ (target: ≤25%)
     - % of root clutter (target: ≤40 files)
     - Archive organization score (1–10)
   - **Recommendations**:
     - Next optimization opportunities
     - Candidates for Batch 4 (config consolidation)
     - External storage candidates (>1MB files)

2. Establish update schedule:
   - Weekly: File count snapshots
   - Monthly: Trend analysis
   - Quarterly: Full health audit

**Success Criteria**:
- ✅ Dashboard created with current metrics
- ✅ Historical baseline established
- ✅ Automated snapshot scripts ready

**Output**:
- `.codex/repository_health/DASHBOARD.md`
- `.codex/repository_health/metrics_baseline.json`

---

#### **Action 5: Enforce Naming Convention Standards** (90 min)
**Purpose**: Standardize file naming to improve discoverability and consistency  
**Authority**: policy-coach-agent + repository-organization-agent  
**Dependencies**: Action 2 (standards defined)  
**Steps**:
1. Identify naming patterns currently in use:
   - Phase reports: `PHASE_*.md`, `PHASE_*_COMPLETION_*.md`
   - Gate documents: `GATE_*.md`
   - Summaries: `*_SUMMARY*.md`, `*_COMPLETION*.md`
   - Reports: `*_REPORT*.md`
   - Archives: `*_ARCHIVE*.md`

2. Document conventions in `.codex/NAMING_CONVENTIONS.md`:
   - Approved prefixes (PHASE, GATE, TRACK, PHASE, etc.)
   - Required components (date, status, category)
   - Anti-patterns to avoid
   - Examples (correct vs. incorrect)

3. Create linting rules (pre-commit hook or CI check):
   - Validate new files match naming conventions
   - Warn on deviations; fail on severe violations
   - Document exceptions process

4. Audit existing files in `.codex/`:
   - Identify ~10 files that violate conventions
   - Schedule remediation or exceptions
   - Document in violation log

**Success Criteria**:
- ✅ Naming conventions documented and agreed upon
- ✅ Linting rules in place (or scheduled for Phase 9)
- ✅ No new violations in recent commits

**Output**:
- `.codex/NAMING_CONVENTIONS.md`
- `.codex/NAMING_CONVENTION_VIOLATIONS.md` (audit report)

---

#### **Action 6: Create Quick-Reference Archive Index** (30 min)
**Purpose**: Help users quickly find archived files without searching manually  
**Authority**: documentation-quality-agent  
**Dependencies**: Action 1 (integrity validated)  
**Steps**:
1. Create `.codex/archive/README.md` with:
   - Quick description of each archive category
   - Links to RETRIEVAL_GUIDE.md files
   - Common use cases ("I need coverage reports from Phase 5")
   - Search/filtering tips
   - Examples of restore commands

2. Update main `.codex/README.md` to link to archive README

3. Create `.codex/archive/QUICK_LOOKUP.md`:
   - Searchable table of archive categories
   - File count per category
   - Last updated date
   - Compression status (if applicable)

**Success Criteria**:
- ✅ Archive README published and discoverable
- ✅ Quick lookup guide created
- ✅ No questions from users about archive location

**Output**:
- `.codex/archive/README.md`
- `.codex/archive/QUICK_LOOKUP.md`

---

#### **Action 7: Plan Batch 4 Execution (Configuration Consolidation)** (60 min, deferred)
**Purpose**: Prepare for the next cleanup batch (dependent on Track 8.3 completion)  
**Authority**: repository-organization-agent  
**Dependencies**: Track 8.3 (case-collision fixes), Action 1–3 (foundation tasks)  
**Timeline**: Execute **after** Track 8.3 completes  
**Steps**:
1. Review deferred Batch 4 specification in `.codex/PHASE_8_2_CLEANUP_PHASES.md`
2. Identify config files to consolidate:
   - `config_legacy/` → `.codex/archive/config-legacy/`
   - `yaml_legacy/` → `.codex/archive/config-legacy/yaml/`
   - `config_experiments/` → `.codex/archive/config-experiments/`
   - Other legacy configs
3. Validate import references:
   - Scan `src/` and `tests/` for imports of legacy config modules
   - Document any active imports (may need refactoring)
   - Plan update PRs if needed
4. Create Batch 4 execution plan:
   - File-by-file move strategy
   - Reference update checklist
   - Testing/validation strategy
5. Document in `.codex/PHASE_8_2_BATCH_4_EXECUTION_PLAN.md`

**Success Criteria**:
- ✅ Batch 4 plan reviewed and approved
- ✅ Prerequisites tracked (Track 8.3 completion)
- ✅ Ready to execute within 1–2 weeks

**Output**:
- `.codex/PHASE_8_2_BATCH_4_EXECUTION_PLAN.md`
- `.codex/PHASE_8_2_BATCH_4_PREREQUISITES_CHECKLIST.md`

---

## Part 4: Decision Gates

### Gate 1: Archive Retrieval Validation
**When**: After Action 1 (Validate Archive Integrity)  
**Question**: Are all archived files accessible and correctly indexed?  
**Decision Points**:
- ✅ **GO**: All 1,666+ files present; INVENTORY.ndjson complete → Proceed to Actions 2–3
- ⏸️ **HOLD**: <95% files accessible → Audit and fix missing files before proceeding
- ❌ **STOP**: Critical retrieval failure (e.g., corrupted INVENTORY.ndjson) → Rollback and investigate

**Owner**: repository-organization-agent  
**Timeline**: Must complete within 48 hours

---

### Gate 2: Standards Adoption & Documentation
**When**: After Action 2 (Document .codex/ Standards)  
**Question**: Is the organizational structure clear enough that contributors can follow it?  
**Decision Points**:
- ✅ **GO**: Standards document complete; no ambiguity in directory structure → Proceed to Actions 4–6
- 🟡 **CONDITIONAL**: Standards need minor clarification → Quick revision (< 15 min); then proceed
- ❌ **STOP**: Fundamental disagreement on structure → Escalate to QA Walkthrough for consensus

**Owner**: repository-organization-agent + QA Walkthrough  
**Timeline**: Must complete within 1 week

---

### Gate 3: Batch 4 Prerequisites Cleared
**When**: Before executing Action 7 (Batch 4 Execution Plan)  
**Question**: Are all dependencies (Track 8.3, import validation) resolved?  
**Decision Points**:
- ✅ **GO**: Track 8.3 complete; no active imports of legacy config modules → Execute Batch 4 per plan
- 🟡 **DEFER**: Track 8.3 in progress; estimated completion within 1 week → Schedule Batch 4 for following week
- ❌ **ESCALATE**: Active imports of legacy configs; refactoring needed → Coordinate with Track 8.3 lead; estimate additional 2–3 weeks

**Owner**: repository-organization-agent + Track 8.3 Lead  
**Timeline**: Review daily; update status in `.codex/PHASE_8_2_BATCH_4_PREREQUISITES_CHECKLIST.md`

---

## Part 5: Validation Plan

### Validation Strategy Overview

Each action will be validated using a **three-tier approach**:

1. **Pre-Execution Validation**: Confirm prerequisites are met
2. **Execution Validation**: Verify action produces expected outputs
3. **Post-Execution Validation**: Ensure no unintended side effects

### Tier 1: Pre-Execution Validation

| Action | Check | Method | Pass Criteria |
|--------|-------|--------|---------------|
| **Action 1** | Archive completeness | Count files in archive dirs | 1,666+ files present |
| **Action 2** | .codex/ structure clear | Manual review | No ambiguity in structure |
| **Action 3** | Policies definable | Review retention tiers | 4+ tiers with clear rules |
| **Action 4** | Metrics collectable | Test dashboard script | Dashboard renders without errors |
| **Action 5** | Conventions enforceable | Review linting approach | Pre-commit hook compatible |
| **Action 6** | Archive docs complete | Check for missing guides | 3+ retrieval guides linked |
| **Action 7** | Batch 4 prerequisites trackable | List all dependencies | Track 8.3 status known |

### Tier 2: Execution Validation

| Action | Output Artifact | Success Check |
|--------|-----------------|----------------|
| **Action 1** | `.codex/PHASE_8_2_2_VALIDATION_INTEGRITY.md` | All archives verified; no errors |
| **Action 2** | `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md` | Structure diagram clear; rules unambiguous |
| **Action 3** | `.codex/PHASE_8_2_RETENTION_POLICY.md` | All file patterns matched to tiers |
| **Action 4** | `.codex/repository_health/DASHBOARD.md` | Dashboard displays current metrics |
| **Action 5** | `.codex/NAMING_CONVENTIONS.md` | Examples show correct vs. incorrect |
| **Action 6** | `.codex/archive/README.md` | Links to all retrieval guides valid |
| **Action 7** | `.codex/PHASE_8_2_BATCH_4_EXECUTION_PLAN.md` | Plan addresses all config files |

### Tier 3: Post-Execution Validation

| Action | Side-Effect Check | Rollback Plan |
|--------|-------------------|---------------|
| **Action 1** | No git diffs generated; read-only | No rollback needed |
| **Action 2** | No impact on git-tracked files | Revert `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md` if rejected |
| **Action 3** | No files moved/deleted | Revert policy; restore to previous standards |
| **Action 4** | Dashboard script doesn't modify files | Remove dashboard artifacts |
| **Action 5** | Linting rules don't break CI | Disable rule; update enforcement timeline |
| **Action 6** | Documentation changes only | Revert `.codex/archive/README.md` if needed |
| **Action 7** | No execution (planning only); no side effects | Delete execution plan; schedule revisit later |

### Validation Checklist (Go/No-Go)

```markdown
## Action 1: Archive Integrity ✅
- [ ] INVENTORY.ndjson has 885 entries
- [ ] All 3 retrieval guides exist and are readable
- [ ] Spot-check 10 random files (all present)
- [ ] No orphaned references in documentation

## Action 2: Directory Standards ✅
- [ ] Directory structure diagram matches current layout
- [ ] Naming conventions examples provided
- [ ] Retention rules unambiguous
- [ ] Document linked from main README

## Action 3: Retention Policies ✅
- [ ] 4+ retention tiers defined
- [ ] File patterns match each tier
- [ ] Archival & retrieval procedures clear
- [ ] Automation checklist complete

## Action 4: Health Dashboard ✅
- [ ] Current metrics populated
- [ ] Historical baseline data collected
- [ ] Top 10 files identified
- [ ] Recommendations generated

## Action 5: Naming Conventions ✅
- [ ] All current patterns documented
- [ ] Approved prefixes listed
- [ ] Examples show correct vs. incorrect
- [ ] Violation audit completed

## Action 6: Quick-Reference Index ✅
- [ ] Archive README created
- [ ] All retrieval guides linked
- [ ] Quick lookup table created
- [ ] Integration tested

## Action 7: Batch 4 Plan ✅
- [ ] All config files identified
- [ ] Import validation strategy clear
- [ ] Move procedures documented
- [ ] Prerequisites tracked
```

---

## Timeline & Resource Allocation

### Execution Schedule

| Action | Duration | Owner | Start | End |
|--------|----------|-------|-------|-----|
| 1. Archive Integrity | 30 min | repository-organization-agent | Now | +30 min |
| 2. Directory Standards | 45 min | repository-organization-agent | +30 min | +75 min |
| 3. Retention Policies | 60 min | repository-organization-agent | +75 min | +135 min |
| 4. Health Dashboard | 45 min | repository-organization-agent | +135 min | +180 min |
| 5. Naming Conventions | 90 min | policy-coach-agent | +180 min | +270 min |
| 6. Quick-Reference Index | 30 min | documentation-quality-agent | +270 min | +300 min |
| **SUBTOTAL** | **300 min** | Multiple agents | — | **5 hours** |
| 7. Batch 4 Plan | 60 min | repository-organization-agent | Deferred | +1 week |

### Resource Requirements

- **Primary**: repository-organization-agent (240 min total)
- **Secondary**: policy-coach-agent (90 min), documentation-quality-agent (30 min)
- **Infrastructure**: File system access, git history, metrics collection
- **No external approvals** required (D-mode autonomy)

---

## Success Metrics & KPIs

### Phase Completion Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Actions completed** | 6/6 | 0/6 | 🟡 In Progress |
| **Documentation artifacts** | 7 documents | 0 | 🟡 Pending |
| **Decision gates passed** | 3/3 | 0/3 | 🟡 Pending |
| **Validation checklist** | 100% completion | 0% | 🟡 Pending |
| **Timeline adherence** | ≤300 min | — | ⏳ To Execute |

### Long-Term Success Indicators (Phase 8.3+)

- **Repository health maintained**: .codex/ stays ≤25% of tracked files
- **Retention policies enforced**: No re-accumulation of clutter within 6 months
- **Archive usage**: Users can retrieve archived files within 2 min of search
- **Naming consistency**: 100% of new files follow conventions within 2 phases
- **Batch 4 execution**: Config consolidation completes without import refactoring

---

## Appendix: Key References

### Phase 8 Ecosystem

| Document | Purpose | Status |
|----------|---------|--------|
| `.codex/PHASE_8_2_CLEANUP_STRATEGY.md` | Strategic approach to cleanup | ✅ Reference |
| `.codex/PHASE_8_2_CLEANUP_PHASES.md` | Batch 0–4 procedures | ✅ Reference (Batch 4 deferred) |
| `.codex/PHASE_8_2_3_COMPLETION_REPORT.md` | Execution results (Batches 0–3) | ✅ Input to this plan |
| `.codex/archive/phase-reports/RETRIEVAL_GUIDE.md` | Navigate archived phase reports | ✅ Active |
| `.codex/archive/root-consolidation/INDEX.md` | Consolidated root files index | ✅ Active |
| `.codex/archive/artifacts/RETRIEVAL_GUIDE.md` | Retrieve build artifacts | ✅ Active |

### Agent Ecosystem

| Agent | Role | Status |
|-------|------|--------|
| repository-organization-agent | Track 8.2 Lead | ✅ Active |
| policy-coach-agent | Naming enforcement | ✅ Available |
| documentation-quality-agent | Archive documentation | ✅ Available |
| QA Walkthrough Agent | Overall coordination | ✅ Available |

---

## Conclusion

**Phase 8.2.2 Planning establishes a solid foundation for ongoing repository organization by:**

1. ✅ Validating the success of Phase 8.2.3 cleanup (Batches 0–3)
2. ✅ Creating standards to prevent re-accumulation of clutter
3. ✅ Establishing health metrics to track long-term organization
4. ✅ Planning the deferred Batch 4 execution
5. ✅ Documenting decision gates for autonomous execution

**Ready for execution** with D-mode autonomy. No approval gates required. All actions are low-risk and produce documentation-only outputs.

---

**Document Status**: 🟡 PLANNING (ready for immediate execution)  
**Generated**: 2026-01-26  
**Authority**: D-mode autonomy (full execution rights)  
**Next Phase**: Execute Actions 1–6 (this session or next); Batch 4 after Track 8.3 completes  
**Maintained by**: repository-organization-agent (Track 8.2 Lead)
