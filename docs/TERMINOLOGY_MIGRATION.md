# Terminology Migration Guide: Week-Based → Iteration-Based

> **Status**: Active Migration  
> **Version**: 1.0  
> **Last Updated**: 2025-12-24

---

## Overview

The _codex_ project is migrating from week-based timelines to iteration-based workflows to better align with incremental development practices. This guide documents the terminology shift and provides guidance for updating existing documentation.

---

## Terminology Mapping

### Timeline References

| ❌ Old Term | ✅ New Term | Example Usage |
|------------|------------|---------------|
| Pre-commit 1-2, Pre-commit 3-4 | Iteration 1, Iteration 2 | "Iteration 1: Foundation" |
| Day 1, Day 2 | Commit Step 1, Commit Step 2 | "Commit Step 3: Integration" |
| Sprint 1-3 (6-9 weeks) | Iteration Cycles 1-3 | "Cycles 1-3 (flexible timeline)" |
| 2-week timeline | Iteration cycle | "Complete in one iteration cycle" |
| Weekly milestone | Iteration checkpoint | "Iteration checkpoint review" |
| Daily tasks | Pre-commit checkpoints | "Pre-commit checkpoint tasks" |

### Phase References

| ❌ Old Term | ✅ New Term |
|------------|------------|
| Phase 1 (Pre-commit 1-4) | Iteration 1 |
| Phase 2 (Pre-commit 5-8) | Iteration 2 |
| Week-based Phase N | Iteration N |

---

## Migration Strategy

### Priority Levels

1. **High Priority** (Immediate Update):
   - New documentation and plans
   - Templates and examples
   - User-facing guides
   - README files

2. **Medium Priority** (Update as Modified):
   - Active development plans
   - Recent implementation guides
   - Current roadmaps

3. **Low Priority** (Archive Reference):
   - Historical status reports
   - Completed milestone summaries
   - Legacy documentation
   - Archived plans (keep as-is for historical accuracy)

### Migration Approach

**New Documents**: Use iteration-based terminology exclusively

**Existing Documents**:
- **Active Plans**: Update during next revision
- **Historical Documents**: Add migration note at top
- **Archived Content**: Preserve original terminology

---

## Template Usage

All new plans should use the standard iteration template:

```markdown
### **Iteration [N]: [Phase Name]** [Symbol: 🛤️🔄👁️🔀⚖️]

#### Pre-commit Checkpoint
- [ ] [Task 1]
- [ ] [Task 2]

#### Commit Tasks

**[N.1] [Task Name]**

[Description]

**Files to Modify**:
- `path/to/file.ext` ([change description])
```

See: `docs/templates/ITERATION_PLAN_TEMPLATE.md`

---

## Migration Examples

### Before (Week-Based)

```markdown
## Timeline: 6-8 Weeks

### Pre-commit 1-4: Foundation
- Day 1: Setup
- Day 2: Configuration
- Day 3-4: Core implementation

### Pre-commit 5-8: Integration
- Day 5-6: API development
- Day 7-8: Testing
```

### After (Iteration-Based)

```markdown
## Timeline: Flexible Iterations

### Iteration 1: Foundation 🛤️
#### Pre-commit Checkpoint
- [ ] Setup environment
- [ ] Review configuration

#### Commit Tasks
**1.1 Core Implementation**
- Core features
- Basic functionality

### Iteration 2: Integration 🔄
#### Pre-commit Checkpoint
- [ ] Foundation complete
- [ ] API design approved

#### Commit Tasks
**2.1 API Development**
- REST endpoints
- Authentication
```

---

## Status: Current Documentation

### Updated Files
- ✅ `docs/templates/ITERATION_PLAN_TEMPLATE.md` - Created
- ✅ `docs/reporting/REPORTING.md` - Uses iteration terminology
- ✅ Recent PHASE2 documents - Already use iteration terminology
- ✅ Most completion reports - Use iteration structure

### Files with Week References (508 occurrences)

**Primary Categories**:
- AST implementation plans (legacy)
- Architecture design documents (reference timelines)
- Project guides with estimated durations
- Audit improvement plans

**Recommendation**: Update on-demand as these documents are revised. For historical accuracy, preserved completed project timelines Phase 5 retain original week-based references.

---

## Guidelines for New Content

### ✅ DO:
- Use "Iteration N" for phases
- Use "Pre-commit Checkpoint" for prerequisites
- Use "Commit Tasks" for action items
- Use physics symbols (🛤️🔄👁️🔀⚖️) for iteration phases
- Include flexible timelines without fixed dates
- Focus on deliverables over duration

### ❌ DON'T:
- Use "Week N" or "Day N" for new plans
- Specify fixed calendar durations
- Create rigid time-based schedules
- Use sprint terminology from other methodologies

---

## Physics Alignment Symbols

Use these symbols to indicate the physics principle aligned with each iteration:

- 🛤️ **Path** - Clear forward momentum, foundational work
- 🔄 **Fields** - Transformation, data flow, state changes
- 👁️ **Patterns** - Recognition, observation, analysis
- 🔀 **Redundancy** - Fallbacks, alternatives, resilience
- ⚖️ **Equilibrium** - Balance, stability, validation

---

## Historical Context

**Previous Approach** (2024-Previous Cycle Cycle 1):
- Week-based timelines (Pre-commit 1-16)
- Day-level task breakdowns
- Fixed sprint durations
- Calendar-bound milestones

**Current Approach** (Previous Cycle Cycle 2+):
- Iteration-based cycles
- Commit-level granularity
- Flexible duration
- Deliverable-focused checkpoints

**Rationale**:
- Better aligns with actual development patterns
- Reduces pressure from arbitrary deadlines
- Emphasizes incremental progress
- More adaptable to changing requirements

---

## References

- **Template**: `docs/templates/ITERATION_PLAN_TEMPLATE.md`
- **Example**: `docs/plans/PHASE2_CYCLE2_ITERATION1_COMPLETE.md`
- **PR**: #2613 (Security Suite Failures Resolution)
- **Issue**: #3690482394 (Template Standardization Request)

---

## Questions?

For questions about terminology migration or template usage, refer to:
- `AGENTS.md` - Project conventions
- `docs/templates/` - Standard templates
- Recent implementation plans in `docs/plans/` for examples

---

**Approved By**: [@mbaetiong]  
**Effective Date**: 2025-12-24  
**Review Cycle**: Quarterly
