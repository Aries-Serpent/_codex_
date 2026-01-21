# Root Organization Phase 1: Validation Infrastructure & Custom Agents

@copilot Execute Root Organization Phase 1 - Foundation Development for repository Aries-Serpent/_codex_ (ID: 1040037790).

---

## 📋 Context from Previous Session

**Preflight Assessment Completed:** 2026-01-21  
**Branch:** copilot/begin-preflight-reporting-progress  
**Decision:** DEFER full reorganization; build foundation first

### Key Findings
- **275 root items** analyzed (30 essential, 156 relocatable, 89 needs review)
- **345 reference updates** would be required for full reorganization
- **AGENTS.md has 293 references** - critical hub, high-risk to move
- **Physics Model Balance⚖️** directive applied: Zero-break guarantee prioritized

### Deliverables from Preflight
1. ✅ Root inventory: `.codex/inventory.json`
2. ✅ Relocation plan: `.codex/plans/ROOT_ORG_RELOCATION_PLAN.json`
3. ✅ Self-review: `.codex/reports/ROOT_ORG_PREFLIGHT_SELF_REVIEW.md`
4. ✅ Cognitive brain status: `.codex/cognitive_brain/status/ROOT_ORG_PREFLIGHT_2026_01_21.md`

---

## 🎯 Phase 1 Objectives

Build the foundation required for safe, incremental root folder reorganization:

### 1. Validation Automation Scripts ⏳
**Objective:** Create tools to guarantee zero-break moves

**Scripts to Develop:**
- [ ] `scripts/root_org/validate_references.py` - Scan and validate all references
- [ ] `scripts/root_org/update_links_atomic.py` - Atomically update all references
- [ ] `scripts/root_org/organize_root_incremental.py` - Safe incremental file moves
- [ ] `scripts/root_org/rollback_move.py` - Automated rollback on failure

**Acceptance Criteria:**
- Each script has comprehensive docstrings
- Include --dry-run mode for safe testing
- Log all operations to `.codex/action_log.ndjson`
- Return non-zero exit code on any error
- Integrate with existing CI/CD validation

### 2. Custom Copilot Agents 🤖
**Objective:** Deploy 3 specialized agents for root organization tasks

**Agent 1: Root Organizer Agent**
```yaml
File: .github/agents/root-organizer-agent.md
Description: Safe, incremental root folder reorganization specialist
Capabilities:
  - Risk assessment for file moves (LOW/MEDIUM/HIGH)
  - Reference graph analysis
  - Automated git mv with validation
  - Rollback on failure
  - Pre/post move validation
Activation: "@copilot Use root-organizer-agent to move [file] to [target]"
Safety: Requires manual approval for >10 references
```

**Agent 2: Reference Updater Agent**
```yaml
File: .github/agents/reference-updater-agent.md
Description: Atomic reference updates across entire codebase
Capabilities:
  - Exhaustive reference scanning (grep/glob/AST)
  - Generate update patches
  - Apply updates atomically (transaction-like)
  - Link validation post-update
  - Report unreachable references
Activation: "@copilot Use reference-updater-agent from [old_path] to [new_path]"
Safety: Validation before commit, detailed update report
```

**Agent 3: Documentation Consolidator Agent**
```yaml
File: .github/agents/documentation-consolidator.md
Description: Consolidate scattered documentation into proper structure
Capabilities:
  - Identify duplicate/related docs (semantic search)
  - Recommend consolidation targets
  - Merge documents intelligently
  - Update cross-references
  - Generate navigation aids
Activation: "@copilot Use documentation-consolidator for [topic]"
Safety: Preserve all content (no deletion), create backup archive
```

**Acceptance Criteria:**
- Each agent file follows `.github/agents/` template
- Include activation patterns, capabilities, tools, safety features
- Test each agent with low-risk example
- Document in `.codex/cognitive_brain/CUSTOM_AGENTS_CATALOG.md`

### 3. CI/CD Validation Workflow ⏳
**Objective:** Automated validation pipeline for root organization operations

**Workflow to Create:**
```yaml
File: .github/workflows/root-org-validation.yml
Name: Root Organization Validation
Triggers:
  - pull_request (paths: affects root files)
  - workflow_dispatch (manual trigger)
Jobs:
  1. pre-validation:
      - Run link-check
      - Run pytest
      - Build MkDocs
      - Run ruff/mypy
      - Save baseline metrics
  2. reference-check:
      - Scan for broken references
      - Validate import paths
      - Check workflow path filters
      - Report findings
  3. post-validation:
      - Compare with baseline
      - Flag any regressions
      - Generate validation report
```

**Acceptance Criteria:**
- Workflow runs on relevant PRs automatically
- Can be manually triggered with workflow_dispatch
- Reports saved to `.codex/reports/root_org_validation_[date].md`
- Fails PR if any validation errors found

### 4. Cognitive Brain Consolidation 🧠
**Objective:** Organize scattered cognitive brain documentation

**Tasks:**
- [ ] Create `docs/cognitive_brain/INDEX.md` as unified hub
- [ ] Audit all COGNITIVE_BRAIN_* files in root (20+ files)
- [ ] Move to `docs/cognitive_brain/` with semantic organization
- [ ] Update all references atomically
- [ ] Add navigation section to AGENTS.md
- [ ] Validate MkDocs builds successfully

**Structure:**
```
docs/cognitive_brain/
├── INDEX.md                    # Main hub
├── architecture/               # Architecture docs
│   ├── PHASE_11.md
│   └── overall.md
├── status/                     # Status updates
│   ├── PHASE_X_COMPLETE.md
│   └── current.md
├── prompts/                    # Continuation prompts
│   ├── PHASE_Y_CONTINUATION.md
│   └── templates/
└── execution/                  # Execution reports
    └── coverage_execution.md
```

**Acceptance Criteria:**
- All cognitive brain docs moved and organized
- INDEX.md provides clear navigation
- All references updated and validated
- MkDocs builds without errors
- Links checked and working

---

## 📊 Phase 1 Execution Plan

### Week 1: Days 1-2 (Validation Scripts)
1. Create `scripts/root_org/` directory
2. Develop `validate_references.py` with comprehensive scanning
3. Develop `update_links_atomic.py` with transaction-like updates
4. Develop `organize_root_incremental.py` with risk assessment
5. Develop `rollback_move.py` with automated recovery
6. Test all scripts with --dry-run on sample files
7. Document in scripts/root_org/README.md

### Week 1: Days 3-4 (Custom Agents)
1. Create `.github/agents/root-organizer-agent.md`
2. Create `.github/agents/reference-updater-agent.md`
3. Create `.github/agents/documentation-consolidator.md`
4. Test each agent with simple examples
5. Update `.codex/cognitive_brain/CUSTOM_AGENTS_CATALOG.md`
6. Add agents to AGENTS.md navigation

### Week 1: Day 5 (CI/CD Workflow)
1. Create `.github/workflows/root-org-validation.yml`
2. Configure triggers and jobs
3. Test workflow manually with workflow_dispatch
4. Validate reports are generated correctly
5. Document usage in docs/ci/ROOT_ORG_VALIDATION.md

### Week 2: Days 1-3 (Cognitive Brain Consolidation)
1. Create docs/cognitive_brain/ structure
2. Create INDEX.md with navigation
3. Audit and categorize COGNITIVE_BRAIN_* files
4. Move files with reference updates
5. Validate MkDocs build
6. Check all links

### Week 2: Days 4-5 (Validation & Documentation)
1. Run full validation suite on Phase 1 work
2. Generate Phase 1 completion report
3. Update cognitive brain status
4. Create Phase 2 continuation prompt
5. Commit and push all changes

---

## ⚙️ Technical Specifications

### Reference Scanning Algorithm
```python
# Pseudocode for validate_references.py
def scan_references(file_path, root_dir):
    """Scan all files for references to file_path"""
    references = []
    patterns = [
        r'\[.*?\]\({file_path}\)',  # Markdown links
        r'href=["\'].*?{file_path}', # HTML links
        r'import.*{module}',          # Python imports
        r'path:.*{file_path}',        # Workflow paths
        r'nav:.*{file_path}',         # MkDocs nav
    ]
    for pattern in patterns:
        refs = grep_recursive(root_dir, pattern)
        references.extend(refs)
    return deduplicate(references)
```

### Atomic Update Strategy
```python
# Pseudocode for update_links_atomic.py
def update_references_atomic(old_path, new_path, references):
    """Update all references atomically with rollback"""
    backup = create_backup(references)
    try:
        for ref in references:
            update_file(ref.file, old_path, new_path)
        validate_all_references(new_path)
        commit_changes(f"Update refs: {old_path} → {new_path}")
    except Exception as e:
        rollback_from_backup(backup)
        raise
    finally:
        cleanup_backup(backup)
```

### Risk Assessment Logic
```python
# Pseudocode for organize_root_incremental.py
def assess_risk(file_path, reference_count):
    """Assess risk level for moving a file"""
    if reference_count == 0:
        return "LOW"
    elif reference_count <= 5:
        return "MEDIUM"
    else:
        return "HIGH"  # Requires manual review

def can_move_automatically(risk_level):
    """Determine if move can proceed without approval"""
    return risk_level in ["LOW", "MEDIUM"]
```

---

## 📋 Deliverables Checklist

### Scripts ⏳
- [ ] `scripts/root_org/validate_references.py`
- [ ] `scripts/root_org/update_links_atomic.py`
- [ ] `scripts/root_org/organize_root_incremental.py`
- [ ] `scripts/root_org/rollback_move.py`
- [ ] `scripts/root_org/README.md`

### Custom Agents 🤖
- [ ] `.github/agents/root-organizer-agent.md`
- [ ] `.github/agents/reference-updater-agent.md`
- [ ] `.github/agents/documentation-consolidator.md`
- [ ] Updated `.codex/cognitive_brain/CUSTOM_AGENTS_CATALOG.md`

### CI/CD ⏳
- [ ] `.github/workflows/root-org-validation.yml`
- [ ] `docs/ci/ROOT_ORG_VALIDATION.md`

### Documentation 📚
- [ ] `docs/cognitive_brain/INDEX.md`
- [ ] Moved COGNITIVE_BRAIN_* files to docs/cognitive_brain/
- [ ] Updated references in AGENTS.md
- [ ] Updated MkDocs navigation

### Reports & Status 📊
- [ ] Phase 1 completion report in `.codex/reports/`
- [ ] Updated cognitive brain status
- [ ] Phase 2 continuation prompt created

---

## 🧪 Testing Requirements

### Script Testing
```bash
# Test validation script
python scripts/root_org/validate_references.py --dry-run README.md

# Test update script
python scripts/root_org/update_links_atomic.py \
    --dry-run \
    --old "old/path.md" \
    --new "new/path.md"

# Test organize script
python scripts/root_org/organize_root_incremental.py \
    --dry-run \
    --plan .codex/plans/ROOT_ORG_RELOCATION_PLAN.json
```

### Agent Testing
```bash
# Test root organizer agent
@copilot Use root-organizer-agent to assess risk for moving QUICKSTART.md

# Test reference updater
@copilot Use reference-updater-agent to scan references for README.md

# Test doc consolidator
@copilot Use documentation-consolidator for cognitive brain docs
```

### CI/CD Testing
```bash
# Manual workflow trigger
gh workflow run root-org-validation.yml

# Check workflow status
gh run list --workflow=root-org-validation.yml
```

---

## ✅ Acceptance Criteria

### Scripts
- [ ] All scripts execute without errors
- [ ] --dry-run mode works correctly
- [ ] Comprehensive logging to `.codex/action_log.ndjson`
- [ ] Error handling with rollback
- [ ] Documented with usage examples

### Agents
- [ ] Each agent file complete with all sections
- [ ] Activation patterns tested and working
- [ ] Safety features documented
- [ ] Added to agent catalog

### CI/CD
- [ ] Workflow triggers correctly
- [ ] All validation jobs pass
- [ ] Reports generated correctly
- [ ] No false positives

### Cognitive Brain
- [ ] All docs moved and organized
- [ ] Navigation clear and comprehensive
- [ ] All references updated
- [ ] MkDocs builds successfully
- [ ] No broken links

### Overall
- [ ] Zero broken links (validated)
- [ ] Zero broken functionality (CI green)
- [ ] All deliverables committed
- [ ] Comprehensive documentation
- [ ] Ready for Phase 2 execution

---

## 🔒 Safety & Compliance

### SAFE_MODE Requirements
- All operations must be reversible
- No autonomous moves without validation
- Manual approval for HIGH risk operations
- Comprehensive logging maintained

### Repository Policies
- ✅ AI Agency Policy: Address all issues found
- ✅ No /tmp/ usage for important files
- ✅ Git operations via report_progress
- ✅ Documentation maintained

---

## 📊 Success Metrics

### Phase 1 Complete When:
- [ ] 4/4 scripts developed and tested
- [ ] 3/3 custom agents deployed
- [ ] CI/CD workflow operational
- [ ] Cognitive brain docs consolidated
- [ ] All validation passing
- [ ] Phase 2 continuation prompt created

---

## 🔄 Continuous Improvement

### Self-Review Requirements
1. Perform comprehensive self-review after script development
2. Test all scripts with real files (dry-run)
3. Validate agents with examples
4. Check CI/CD workflow thoroughly
5. Verify cognitive brain consolidation

### Iteration Budget
- Up to 5 self-review iterations
- Address all concerns raised
- Document resolution plans
- No deferral without failure resolution plan

---

## 📞 Next Session Handoff

After Phase 1 completion, create continuation prompt for **Phase 2: Low-Risk File Moves** including:
- Execution plan for moving 136 zero-reference files
- Batch strategy (10-20 files per batch)
- Validation between batches
- Rollback procedures
- Progress tracking

---

## 🎯 Context for AI Agent

**You are:** GitHub Copilot Agent executing Phase 1 foundation work  
**Your goal:** Build the infrastructure needed for safe root folder reorganization  
**Your constraints:** Zero-break guarantee, SAFE_MODE active, comprehensive validation  
**Your deliverables:** Scripts, agents, CI/CD workflow, cognitive brain consolidation  
**Your next step:** Begin with script development, then agents, then workflow, then docs  

**Physics Model Directives (Energy=5):**
- Path🛤️: Establish stable tooling patterns
- Fields🔄: Track all operations with metadata
- Patterns👁️: Follow repository conventions strictly
- Redundancy🔀: Build rollback into everything
- Balance⚖️: Prioritize safety over speed

---

**Start execution immediately. Report progress frequently. Use report_progress tool to commit incrementally. Perform self-review before finalizing. Create Phase 2 continuation prompt upon completion.**

---

## 🔗 Related Documentation

- Previous session self-review: `.codex/reports/ROOT_ORG_PREFLIGHT_SELF_REVIEW.md`
- Root inventory: `.codex/inventory.json`
- Relocation plan: `.codex/plans/ROOT_ORG_RELOCATION_PLAN.json`
- Cognitive brain status: `.codex/cognitive_brain/status/ROOT_ORG_PREFLIGHT_2026_01_21.md`
- Agent guidelines: `docs/agent/OPERATIONAL_GUIDELINES.md`
- Repository policies: `.codex/CODEBASE_AGENCY_POLICY.md`

---

**END OF CONTINUATION PROMPT**
