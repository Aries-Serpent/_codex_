# Project Plans & Roadmaps

**Last Updated**: 2026-06-22  
**Total Plans**: 93 files  
**Active Plans**: ~60  
**Archived Plans**: ~33 in `archive/` directory

---

## 📚 Quick Navigation

### Quick Links
- **[Active Plans](#active-plans)** - Currently active projects
- **[Archived Plans](archive/)** - Completed and historical plans
- **[Plan Index](#plan-index)** - Full list of plans

---

## 🎯 Active Plans

### Current Phase Initiatives

| Plan | Status | Owner | Target |
|------|--------|-------|--------|
| Coverage Improvement Roadmap | 🟡 In Progress | QA | Q3 2026 |
| MSP Audit Gap Remediation | 🟡 In Progress | Compliance | Q2 2026 |
| Copilot Workflow Agent | 🟡 In Progress | AI/Agents | Q3 2026 |
| Operational Runbook | 🟡 In Progress | Ops | Q2 2026 |

### Recent Plans

- `COVERAGE_IMPROVEMENT_ROADMAP.md` - Test coverage roadmap
- `MSP_Audit_Gap_Remediation_Plan_of_Action.md` - Audit remediation
- `COGNITIVE_BRAIN_UNIFIED_IMPLEMENTATION_TASKS.md` - Brain implementation
- `COPILOT_SESSION_HANDOFF_DESIGN.md` - Session design

---

## 📦 Plan Categories

### Phase Planning
- PHASE_* plans - Phase-specific implementation plans
- Cycle completion summaries
- Phase continuation prompts

### Infrastructure
- `operational_runbook.md` - Operations manual
- CI failure resolution plans
- System architecture plans

### Testing & Quality
- `COVERAGE_IMPROVEMENT_ROADMAP.md` - Coverage roadmap
- `AST_TEST_STRATEGY.md` - Testing strategy
- Test infrastructure plans

### Compliance & Audit
- `MSP_Audit_Gap_Remediation_Plan_of_Action.md` - Audit plan
- `AUDIT_IMPROVEMENT_IMPLEMENTATION_SUMMARY.md` - Audit summary
- Compliance plans

### AI & Agents
- `COPILOT_SESSION_HANDOFF_DESIGN.md` - Agent session design
- `COGNITIVE_BRAIN_UNIFIED_IMPLEMENTATION_TASKS.md` - Brain tasks
- Agent implementation plans

### Product & Features
- `capability_code_score_improvement-*.md` - Feature improvements
- `PR*_whats_next.md` - PR follow-up plans
- Feature roadmaps

---

## 🗂️ Directory Structure

```
docs/plans/
├── README.md                                    # This file
├── archive/                                     # Completed plans (33 files)
│   ├── PHASE*_COMPLETE*.md                     # Completed phase reports
│   └── ...
├── [Active Plans]                              # Current initiatives
├── COVERAGE_IMPROVEMENT_ROADMAP.md
├── MSP_Audit_Gap_Remediation_Plan_of_Action.md
├── COGNITIVE_BRAIN_UNIFIED_IMPLEMENTATION_TASKS.md
├── COPILOT_SESSION_HANDOFF_DESIGN.md
├── copilot-workflow-agent/                     # Copilot workflow agent
│   ├── README.md
│   ├── 00-PLANSET.md
│   ├── 01-BATCHSET.md
│   ├── 02-PATCHSET.md
│   ├── 08-CHECKPOINTS.md
│   └── 09-CONTINUATION-PROMPTS.md
└── [other plans]
```

---

## 📋 Full Plan Index

### Coverage & Quality
- `COVERAGE_IMPROVEMENT_ROADMAP.md` - Test coverage roadmap
- `AST_TEST_STRATEGY.md` - AST module testing strategy
- `ci_failures_resolution_plan.md` - CI failure resolution

### Audit & Compliance
- `MSP_Audit_Gap_Remediation_Plan_of_Action.md` - Audit remediation
- `AUDIT_IMPROVEMENT_IMPLEMENTATION_SUMMARY.md` - Audit summary

### Infrastructure & Operations
- `operational_runbook.md` - Operations manual
- `capability_code_score_improvement-2025_12_11.md` - Capability improvement

### AI & Agents
- `COPILOT_SESSION_HANDOFF_DESIGN.md` - Session handoff design
- `COGNITIVE_BRAIN_UNIFIED_IMPLEMENTATION_TASKS.md` - Brain implementation
- `AGENT_CONTINUATION_PROMPT.md` - Agent prompts
- `copilot-workflow-agent/` - Copilot workflow agent (directory)

### PR Follow-ups
- `PR4416_whats_next.md` - PR 4416 follow-up
- `PR4356_whats_next.md` - PR 4356 follow-up
- `PR_2205_fix_gap-and-comments.md` - PR 2205 plan

### Miscellaneous
- `patchset.md` - Patch set documentation

### Archived Plans (in `archive/`)
- `PHASE2_*.md` - Phase 2 completion reports (7+ files)
- Other completed phase plans

---

## 🚀 How to Use This Directory

### Finding a Plan
1. Check the **Quick Links** above
2. Browse **Plan Categories** for topic
3. Search in **Full Plan Index**
4. Look in `archive/` for completed plans

### Creating a New Plan
1. Check if a similar plan exists
2. Use descriptive filename (kebab-case)
3. Add to appropriate category
4. Update this README
5. Link from relevant pages

### Archiving a Plan
1. When plan is complete, move to `archive/`
2. Add date stamp to filename
3. Keep in git history
4. Update this README

### Referencing Plans
- From docs: `[Plan Name](./plans/FILENAME.md)`
- From root: `[Plan Name](./docs/plans/FILENAME.md)`
- Archived: `[Plan Name](./plans/archive/FILENAME.md)`

---

## 📊 Plan Statistics

| Category | Count | Status |
|----------|-------|--------|
| Active Plans | ~60 | 🟢 Current |
| Archived Plans | ~33 | ✅ Complete |
| Phases | 5+ | 🟡 In Progress |
| Infrastructure | 3 | 🟡 Active |
| Compliance | 2 | 🟡 Active |
| AI/Agents | 5+ | 🟡 Active |
| **Total** | **93+** | **📋 Organized** |

---

## 🔗 Related Documentation

- **[docs/archive/](../archive/)** - Archived documentation
- **[docs/](../)** - Main documentation hub
- **[Repository Roadmap](../roadmap/)** - Overall roadmap

---

## 💡 Best Practices

- Keep plans focused and specific
- Document decisions and rationale
- Update as progress is made
- Archive when complete
- Cross-reference related plans
- Include target dates and owners

---

## 🔄 Plan Lifecycle

```
Create → Active → In Progress → Complete → Archive
         ↑                           ↑
         └──── Review & Update ─────┘
```

1. **Create**: New plan identified
2. **Active**: Plan is current priority
3. **In Progress**: Work ongoing
4. **Complete**: Plan objectives met
5. **Archive**: Move to archive/ directory

---

## 📝 Contributing

When adding or updating plans:
1. Use clear, descriptive titles
2. Include objectives and success criteria
3. Add owner/responsible party
4. Include target date
5. Link related documents
6. Update this README
7. Commit with reference to PR/issue

---

**Last Updated**: 2026-06-22  
**Organization**: Phase 5 - Structure & Organization Improvement  
**Status**: ✅ Complete
