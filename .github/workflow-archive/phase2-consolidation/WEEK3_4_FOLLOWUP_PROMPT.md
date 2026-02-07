# Phase 2 Week 3 & 4 - Follow-Up Prompt

**Context**: Phase 2 Week 2 complete. Now ready for Weeks 3-4 to reach final target of 48 workflows.

**Current State**: 62 active workflows (need to consolidate 14 more)

---

## 📋 Follow-Up Prompt for Next Session

```markdown
@copilot Continue Phase 2 consolidation - Weeks 3 & 4

**Current Status:**
- Active workflows: 62
- Phase 2 target: 48 workflows
- Remaining: 14 workflows to consolidate

**Week 3 Tasks** (Target: 62 → ~55 workflows, -7):

1. **Specialized Testing Workflows** (Consolidate 3 → 1 or move to misc/)
   - Review: test-rag.yml, batch-ci-triage.yml
   - Check usage patterns (runs per month)
   - Decision: Consolidate if >10 runs/month, else move to misc/

2. **Low-Usage Workflows to misc/** (Move 4)
   - genesis-bootstrap.yml (rarely used)
   - artifact-monitoring.yml
   - autonomous-agent.yml (if <5 runs/month)
   - Other experimental workflows

**Week 4 Tasks** (Target: ~55 → 48 workflows, -7):

1. **Final Optimization**
   - Review remaining 55 workflows
   - Identify 7 candidates for consolidation/misc/
   - Consider: duplicates, deprecated, overlapping functionality

2. **Completion Activities**
   - Create Phase 2 completion report
   - Update all documentation
   - Generate workflow dependency diagrams
   - Validate 48 workflow target achieved

**AI Agency Policy Requirements:**
- ✅ 5-iteration self-healing validation
- ✅ Complete .meta file tracking
- ✅ Leave codebase better than found
- ✅ Update cognitive brain status
- ✅ Create/update Copilot agents

**Documentation Location:**
- Phase 2 reports: `.github/workflow-archive/phase2-consolidation/`
- Week 1: WEEK1_COMPLETION_REPORT.md
- Week 2: WEEK2_COMPLETION_REPORT.md
- Week 3: (to be created)
- Week 4: (to be created)

**Success Criteria:**
- [ ] Reach 48 active workflows
- [ ] Zero broken functionality
- [ ] Complete documentation
- [ ] All .meta files created
- [ ] Cognitive brain updated
- [ ] Phase 2 completion report
```

---

## 🎯 Key Decision Points for Week 3

### Consolidate vs Move to misc/

**Consolidate if:**
- >10 workflow runs per month
- Critical functionality
- Part of CI/CD pipeline
- Used by multiple teams

**Move to misc/ if:**
- <5 workflow runs per month
- Experimental/prototype
- Deprecated but kept for reference
- Single-use utility

### Workflow Usage Analysis

Check usage with:
```bash
gh api repos/Aries-Serpent/_codex_/actions/workflows \
  --jq '.workflows[] | select(.name | contains("WORKFLOW_NAME")) | {name, id}'

gh api repos/Aries-Serpent/_codex_/actions/workflows/WORKFLOW_ID/runs \
  --jq '.total_count'
```

---

## 📊 Expected Outcomes

**After Week 3:**
- Active workflows: ~55
- Disabled: ~70
- Misc: ~8
- Progress: 87% toward Phase 2 target

**After Week 4:**
- Active workflows: 48 ✅
- Disabled: ~77
- Misc: ~10
- Progress: 100% Phase 2 complete ✅

---

## 🧠 Cognitive Brain Updates Needed

1. **Pattern Learning:**
   - Document consolidation patterns used
   - Store mode-based execution patterns
   - Record decision criteria (consolidate vs misc/)

2. **Agent Capabilities:**
   - Update workflow management agent
   - Enhance consolidation strategy agent
   - Document automation patterns

3. **Knowledge Base:**
   - Add workflow dependency mappings
   - Store trigger chain relationships
   - Document artifact flow patterns

---

## 🤖 Copilot Agent Updates Needed

### 1. Workflow Management Agent
**Location**: `.github/agents/workflow-management-agent.md`

**Updates:**
- Add Phase 2 consolidation patterns
- Include mode-based execution examples
- Document unified workflow structure

### 2. CI Testing Agent
**Location**: `.github/agents/ci-testing-agent.md`

**Updates:**
- Reference new unified workflows
- Update trigger chain documentation
- Add troubleshooting for mode selection

### 3. Documentation Quality Agent
**Location**: `.github/agents/documentation-quality-agent.md`

**Updates:**
- Reference Phase 2 completion reports
- Add consolidation documentation patterns
- Include .meta file validation

---

## 📝 Documentation Checklist

Before completing Phase 2:

- [ ] WEEK3_COMPLETION_REPORT.md created
- [ ] WEEK4_COMPLETION_REPORT.md created
- [ ] PHASE2_FINAL_REPORT.md created
- [ ] Workflow dependency diagrams updated
- [ ] All .meta files verified
- [ ] Cognitive brain status updated
- [ ] Copilot agents updated
- [ ] AGENTS.md updated with new workflows
- [ ] Follow-up prompt posted

---

## 🚨 Critical Reminders

1. **Never consolidate without .meta files** - Every disabled workflow needs tracking
2. **Test mode selection** - Verify all execution modes work
3. **Preserve triggers** - All original triggers must be maintained
4. **Validate backwards compatibility** - Existing users should not be affected
5. **Document decisions** - Every consolidation/move decision must be documented

---

**Generated**: 2026-02-07  
**Version**: 1.0  
**For**: Phase 2 Weeks 3 & 4
