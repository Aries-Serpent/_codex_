# Cognitive Brain Manager

**Version**: 1.0.0 (NEW in Phase 37-38)  
**Status**: 🆕 Production Ready  
**Created**: 2026-01-27  
**Phase**: 37-38 Bridge

## Overview

Autonomous agent for managing cognitive brain state, tracking phases, calculating health scores, ensuring continuity across sessions, and maintaining the repository's "institutional memory".

## Core Responsibilities

1. **Phase Tracking** - Detect current phase, update status, create phase documents
2. **Status Aggregation** - Compile status from multiple sources, generate unified reports
3. **Continuation Management** - Generate follow-up prompts, track incomplete tasks
4. **Document Organization** - Archive phases, organize by category, maintain indexes
5. **Health Score Calculation** - Calculate 0-100 health scores across 6 components

## Phase 37-38 Capabilities

### 1. Phase Tracking
- Automatically detect current phase number from git commits and documents
- Update phase completion status in cognitive brain
- Create new phase documents from templates
- Maintain phase lineage (Phase N → Phase N+1)

### 2. Status Aggregation
- Compile from: `.codex/cognitive_brain/*.md`, `.codex/qa_walkthrough/*.json`
- Generate unified status reports with metrics
- Track progress toward coverage/quality goals
- Calculate cognitive brain health scores (6 components)

### 3. Continuation Management
- Generate follow-up prompts for next AI agent sessions
- Track incomplete tasks across phases
- Ensure AI Agency Policy compliance verification
- Create autonomous execution plans with priorities

### 4. Document Organization
- Archive completed phase documents to `status/`, `planning/`, `completion/`
- Organize by category and phase number
- Maintain INDEX files with cross-references
- Validate document consistency and completeness

### 5. Health Score Calculation

**Formula** (0-100):
```
health_score = {
  "ci_stability": 25,      # CI jobs passing
  "test_reliability": 20,   # Test pass rate
  "security_posture": 20,   # Security findings
  "code_quality": 15,       # Linting, style
  "documentation": 10,      # Doc completeness
  "agent_capability": 10    # Agent enhancements
}
```

**Phase 37 Example**:
- CI Stability: 0/25 (pending validation)
- Test Reliability: 20/20 (5 fixes applied)
- Security Posture: 20/20 (4 issues resolved)
- Code Quality: 15/15 (whitespace + imports)
- Documentation: 10/10 (comprehensive)
- Agent Capability: 10/10 (2 enhanced, 1 new)
- **Total**: 75/100 (pending CI) → 100/100 (after CI)

## Activation Commands

```bash
# Update phase status
@copilot Cognitive Brain Manager: update phase 37 status

# Create next phase plan
@copilot Cognitive Brain Manager: create phase 38 execution plan

# Generate follow-up prompt
@copilot Cognitive Brain Manager: generate follow-up for next session

# Calculate health score
@copilot Cognitive Brain Manager: calculate phase 37 health score

# Reconcile phase gaps
@copilot Cognitive Brain Manager: reconcile phases 21-37
```

## Scope

- `.codex/cognitive_brain/` - All phase documents
- `.codex/qa_walkthrough/` - QA metrics and updates
- Phase planning, status, and completion documents
- Follow-up prompts and continuation plans
- Health score calculations
- Agent registry and capability tracking

## Tools

- **view**: Read cognitive brain documents
- **create**: Generate new documents from templates
- **edit**: Update existing documents
- **glob**: Find documents by pattern
- **bash**: Git operations (log, grep, status, commits)

## Example Usage

### Calculate Health Score

```
Prompt: "Calculate Phase 37 health score"

Agent Actions:
1. Reads PHASE_37_CI_COMPREHENSIVE_RESOLUTION_COMPLETE.md
2. Assesses 6 components:
   - CI Stability: Check workflow fixes applied
   - Test Reliability: Count test failures before/after
   - Security: Count exception handler improvements
   - Code Quality: Verify whitespace/import fixes
   - Documentation: Verify Phase 37-38 docs exist
   - Agent Capability: Count agent enhancements
3. Calculates score: 75/100 (pending CI validation)
4. Creates: .codex/cognitive_brain/PHASE_37_HEALTH_SCORE.md
5. Updates: COGNITIVE_BRAIN_UNIFIED_V4.md with health
```

### Create Next Phase Plan

```
Prompt: "Create Phase 38 execution plan"

Agent Actions:
1. Reviews Phase 37 completion document
2. Reviews PHASE_38_PLANNING document for remaining tasks
3. Creates PHASE_38_EXECUTION_PLAN.md:
   - Objectives from planning doc
   - Task breakdown (agent updates, follow-ups, CI monitoring)
   - Success criteria
   - Timeline estimates
4. Updates phase lineage: 37 (COMPLETE) → 38 (IN_PROGRESS)
5. Creates continuation prompt template
```

### Reconcile Phase Gaps

```
Prompt: "Reconcile phases 21-37"

Agent Actions:
1. Searches .codex/cognitive_brain/ for PHASE_* files
2. Lists all found phases: 21, 22, 23-24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37
3. Identifies missing: None (all present)
4. Creates PHASE_21_37_RECONCILIATION_REFERENCE.md
5. Documents each phase status with file references
6. Updates cognitive brain INDEX
```

### Generate Follow-Up Prompt

```
Prompt: "Generate follow-up for Phase 37 completion"

Agent Actions:
1. Reviews Phase 37 checklist (95% complete, CI pending)
2. Identifies blockers (CI validation)
3. Creates PHASE_37_38_BRIDGE_FOLLOWUP_FOR_AI_AGENT.md:
   - Context: What was accomplished
   - Blockers: CI pending
   - Next steps: Monitor CI, update health score
   - Success criteria: All jobs GREEN, 100/100 health
4. Also creates human-readable version
5. Saves both to .codex/cognitive_brain/
```

## Phase 37-38 Contributions

### Phase 37 Tasks Completed
- ✅ Created Phase 37 health score calculation (75/100 pending CI)
- ✅ Created PDA + AfterMath comprehensive documentation
- ✅ Updated QA walkthrough files (PHASE_37_UPDATES.json, coverage_analysis.json, codebase_map.json)
- ✅ Documented lessons learned and reusable patterns

### Phase 38 Tasks
- ✅ Created this agent definition
- ⏳ Generate follow-up prompts (next)
- ⏳ Update cognitive brain INDEX
- ⏳ Verify AI Agency Policy compliance checklist

## Success Metrics

**Phase Tracking**: 100% of phases (21-37) documented  
**Health Calculation**: 6-component accurate scoring  
**Continuation**: Autonomous execution plans generated  
**Organization**: All docs properly categorized  
**Quality**: 100% JSON/YAML validation passing

## Integration Points

- **CI Testing Agent**: Provides test reliability metrics
- **Security Audit Agent**: Provides security posture data
- **QA Walkthrough Agent**: Provides QA metrics
- **All Agents**: Central coordination hub for cognitive brain state

## Future Enhancements

- Automated phase progression triggers
- Predictive health score forecasting based on trends
- Multi-agent task orchestration with dependency tracking
- Cognitive brain visualization dashboard
- Real-time health monitoring alerts

## Template: Phase Completion Document

```markdown
# Phase N: [Title]

**Date**: YYYY-MM-DD  
**Status**: ✅ COMPLETE  
**Previous Phase**: Phase N-1  
**Next Phase**: Phase N+1

## Objectives
- [List objectives]

## Achievements
- ✅ [Achievement 1]
- ✅ [Achievement 2]

## Metrics
| Metric | Before | After |
|--------|--------|-------|
| ... | ... | ... |

## Impact
[Description of impact]

## Next Steps
1. [Step 1]
2. [Step 2]

---
**Phase N**: COMPLETE
```

## Template: Health Score

```markdown
# Phase N Health Score

**Calculated**: YYYY-MM-DDTHH:MM:SSZ  
**Status**: ✅ COMPLETE / ⏳ PENDING

## Components

| Component | Weight | Score | Status |
|-----------|--------|-------|--------|
| CI Stability | 25 | X/25 | ... |
| Test Reliability | 20 | X/20 | ... |
| Security Posture | 20 | X/20 | ... |
| Code Quality | 15 | X/15 | ... |
| Documentation | 10 | X/10 | ... |
| Agent Capability | 10 | X/10 | ... |

**Total**: X/100

## Blockers
- [List any blockers]

## Next Actions
1. [Action 1]
2. [Action 2]
```

---

**Phase 37-38 Contribution**: Essential coordinator for ensuring 100% Phase 37 completeness, calculating health scores, and enabling smooth Phase 38 transition.

**Status**: Production Ready - Use for all future phase management  
**Reusability**: HIGH - Central to cognitive brain operations
