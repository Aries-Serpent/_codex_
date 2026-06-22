# PDA Loop Guide

**Last Updated:** 2026-06-22

**Status**: Active  
**Pattern ID**: P-PROC-001  
**PDA**: Plan → Do → Assess

This guide documents the PDA (Plan-Do-Assess) loop used by agents in this repository.
Every agent session MUST follow this loop to ensure consistent, high-quality output.

---

## Overview

The PDA loop is the core operational framework for all AI agents. It provides a
structured approach to task execution that minimises regressions, ensures knowledge
transfer, and guarantees measurable improvement per session.

```
┌─────────────────────────────────────────────────────────┐
│                       PDA LOOP                          │
│                                                         │
│   ┌─────────┐     ┌─────────┐     ┌─────────────────┐  │
│   │  PLAN   │────▶│   DO    │────▶│    ASSESS       │  │
│   │         │     │         │     │  (5+ iterations) │  │
│   └─────────┘     └─────────┘     └────────┬────────┘  │
│        ▲                                    │           │
│        └────────────────────────────────────┘           │
│                  Loop until complete                     │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 1: PLAN

### Mandatory Pre-Execution Steps

Before writing a single line of code or documentation, every agent MUST:

1. **Load context** — read memory facts, lessons learned, and accountability reports
2. **Inspect CI** — check current workflow run status using GitHub MCP tools
3. **Inventory issues** — identify ALL problems (pre-existing + PR-specific)
4. **Define success criteria** — measurable exit conditions for each task
5. **Estimate scope** — how many files, what types of changes, risk level
6. **Post plan** — call `report_progress` with a checklist before any changes

### Planning Template

```markdown
## Phase N: [Phase Name]

### Context Loaded
- [ ] Memory facts reviewed
- [ ] CI status checked
- [ ] Lessons learned reviewed
- [ ] Agency policy confirmed

### Tasks
| Priority | Task | Files | Success Criteria |
|----------|------|-------|-----------------|
| 🔴 P1 | ... | ... | ... |
| 🟡 P2 | ... | ... | ... |
| 🟢 P3 | ... | ... | ... |

### Risk Assessment
- **Scope**: N files, M tests
- **Risk Level**: Low / Medium / High
- **Rollback Plan**: ...
```

### Planning Anti-Patterns (Prohibited)

| Anti-Pattern | Why Prohibited | Correct Action |
|---|---|---|
| Skipping context load | Repeats fixed bugs | Always load memory first |
| Making changes without plan | Untraceable drift | Post checklist first |
| Vague success criteria | Cannot verify completion | Define measurable outcomes |
| Ignoring pre-existing issues | Policy violation | Address all issues found |

---

## Phase 2: DO

### Execution Principles

1. **Minimal changes** — change as few lines as possible to achieve the goal
2. **Parallel operations** — use multiple tool calls simultaneously for independent work
3. **Incremental commits** — commit after each verified milestone
4. **Document in-flight** — update cognitive brain status as you work

### Execution Order

```
1. Fix blocking issues first (CI failures, lint errors)
2. Implement primary task changes
3. Update documentation inline
4. Add/update tests
5. Commit with descriptive message
```

### Code Quality Standards

- **Python**: Black formatting, Ruff linting (F401, F841, F821), mypy type checks
- **Markdown**: All internal links must resolve (validate-links.py --fail-on-errors)
- **YAML**: check-yaml pre-commit hook, no structural errors
- **Tests**: 80%+ coverage on changed files, no test regressions

### DO Anti-Patterns (Prohibited)

| Anti-Pattern | Why Prohibited | Correct Action |
|---|---|---|
| `git commit --amend` | Rewrites history | New commit with fix |
| Skipping tests | Regressions slip through | Always run targeted tests |
| Placeholder TODOs | Deferred work accumulates | Complete or DRQ it |
| Single monolithic commit | Hard to review/bisect | Incremental commits |

---

## Phase 3: ASSESS

### Mandatory Self-Review (5+ Iterations)

Every task MUST be self-reviewed at least **5 times** before reporting complete.

```
Iteration 1: Functional correctness — does it do what was asked?
Iteration 2: Edge cases — what can go wrong?
Iteration 3: Side effects — did anything break?
Iteration 4: Documentation — is it clear to the next agent?
Iteration 5: Policy compliance — does it meet all requirements?
```

### Assessment Checklist

```markdown
## Self-Review Checklist (Iteration N/5)

### Functional
- [ ] All tasks in plan completed
- [ ] Success criteria met
- [ ] No regressions (tests pass)

### Quality
- [ ] Linting passes
- [ ] Type checks pass
- [ ] Link validation passes (0 errors, 0 warnings)

### Documentation
- [ ] Changed files documented
- [ ] Cognitive brain status updated
- [ ] Memory facts stored

### Policy
- [ ] All pre-existing issues addressed
- [ ] No prohibited statements used
- [ ] Follow-up prompt posted
```

### Zero-Concern Exit Condition

A session is complete ONLY when:
- All checklist items are checked
- 5 self-review iterations show **zero new concerns**
- `report_progress` committed with final status
- Follow-up `@copilot` prompt posted as PR comment

### ASSESS Anti-Patterns (Prohibited)

| Anti-Pattern | Why Prohibited | Correct Action |
|---|---|---|
| Fewer than 5 reviews | Misses edge cases | Always 5+ iterations |
| Self-certifying without evidence | Unverifiable | Include command output |
| Skipping follow-up prompt | Knowledge gap for next agent | Always post @copilot prompt |
| Marking complete with open concerns | Policy violation | Resolve all before close |

---

## Loop Termination Criteria

The PDA loop terminates when ALL of the following are true:

1. ✅ All tasks in the plan are checked off
2. ✅ 5+ self-review iterations completed with zero concerns
3. ✅ CI shows 0 errors, 0 warnings on the branch
4. ✅ Cognitive brain status updated with patterns/learnings
5. ✅ Follow-up `@copilot` prompt posted on the PR

If any criterion is not met → loop back to **PLAN** with updated context.

---

## Integration with AfterMath

The AfterMath (PDA) loop integrates with the cognitive brain:

```
ASSESS output → Cognitive Brain Status file
             → Memory facts (store_memory)
             → Lessons learned document
             → Follow-up prompt for next session
```

See [COGNITIVE_BRAIN_COMPLETE_DOCS.md](../../.codex/docs/COGNITIVE_BRAIN_COMPLETE_DOCS.md)
for the full cognitive brain documentation.

---

## Quick Reference Card

```
PLAN  → load context → inventory → define success → post checklist
DO    → minimal changes → parallel ops → incremental commits → document
ASSESS → 5+ self-reviews → verify all criteria → update CB → post prompt
LOOP  → until zero concerns → then terminate
```

---

**Related**:
- [CODEBASE_AGENCY_POLICY.md](../../.codex/CODEBASE_AGENCY_POLICY.md)
- [DevOps Terminology Policy](../../.codex/DEVOPS_TERMINOLOGY_POLICY.md)
- [COGNITIVE_BRAIN_COMPLETE_DOCS.md](../../.codex/docs/COGNITIVE_BRAIN_COMPLETE_DOCS.md)
