# Agent Continuation Protocol

**Purpose**: Standardized protocol for AI agents to continue work across sessions using the cognitive brain for context and planning.

**Last Updated**: 2025-12-30  
**Version**: 2.0.0  
**Status**: 🟢 Active

---

## 🧠 Overview

This protocol enables AI agents (GitHub Copilot, ChatGPT, etc.) to:
1. Maintain context continuity across sessions
2. Discover and resume incomplete work  
3. Plan optimal next steps using duration-aware logic
4. Update the cognitive brain with progress

---

## 🎯 Session Workflow

### Phase 1: Context Loading (First 2K tokens)

```
1. Load Cognitive Brain
   → Read docs/system/CODEBASE_COGNITIVE_MAP.md (architecture)
   → Read docs/system/CODEBASE_DASHBOARD.md (current status)
   → Read docs/ROADMAP.md (planned work)

2. Identify Current Phase
   → Check Dashboard for "Active Initiatives"
   → Note completion percentages
   → Identify blocking issues

3. Assess Session Capacity
   → Estimate token budget (typical: 64K-128K)
   → Calculate work capacity (tokens / complexity)
   → Determine if quick wins or deep work
```

### Phase 2: Work Execution (Main session)

```
4. Execute Highest Priority Work
   → Follow roadmap priorities
   → Complete atomic units of work
   → Commit frequently with clear messages

5. Update Cognitive Brain
   → Mark completed tasks in Dashboard
   → Update completion percentages
   → Document decisions and blockers

6. Validate Changes
   → Run linters, tests, syntax checks
   → Verify no regressions
   → Check CI/CD status
```

### Phase 3: Session Closure (Last 5K tokens)

```
7. Self-Review Protocol
   → Perform 5-pass review (see below)
   → Address all concerns
   → Iterate until 0 issues

8. Prepare Continuation
   → If work remains: Generate continuation prompt
   → Update Dashboard with next steps
   → Post continuation comment to PR

9. Document Session
   → Update Dashboard with session summary
   → Commit final changes
   → Mark phase complete if done
```

---

## 📋 Self-Review Protocol (5 Passes)

**Critical**: Perform all 5 passes before ending session. **DO NOT SKIP**.

### Pass 1: Code Quality & Correctness
- [ ] All syntax errors resolved
- [ ] No linting warnings introduced
- [ ] Type hints correct and complete
- [ ] Error handling comprehensive
- [ ] Edge cases covered
- [ ] No hardcoded values (use config)

### Pass 2: Testing & Validation
- [ ] All existing tests passing
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved
- [ ] CI/CD checks passing
- [ ] No flaky tests introduced

### Pass 3: Documentation & Communication
- [ ] Code changes documented
- [ ] README updates if needed
- [ ] API docs updated
- [ ] Cognitive brain updated
- [ ] Commit messages clear
- [ ] No broken documentation links

### Pass 4: Security & Safety
- [ ] No secrets in code or logs
- [ ] No SQL injection vulnerabilities
- [ ] Input validation present
- [ ] Error messages don't leak sensitive data
- [ ] Dependencies vulnerability-free

### Pass 5: Integration & Dependencies
- [ ] No breaking changes to public APIs
- [ ] Backward compatibility maintained
- [ ] Dependencies properly declared
- [ ] No circular dependencies
- [ ] Integration tests passing

**Acceptance**: All passes complete with **0 concerns** remaining.

---

## 🎯 Duration-Aware Planning

### Token Budget Guidelines

| Tokens Used | Remaining | Action |
|-------------|-----------|--------|
| 0-8K | 56K-64K | Continue with major work |
| 8K-32K | 32K-56K | Continue with current phase |
| 32K-48K | 16K-32K | Wrap up current unit |
| 48K-60K | 4K-16K | Prepare continuation |
| 60K+ | <4K | Self-review & close |

### Never Stop Prematurely

**Rule**: If useful work can be done with available capacity, **always continue**.

**Priority Order**:
1. **Critical** - Blocking issues, security fixes
2. **High** - Incomplete features, failing tests  
3. **Medium** - Documentation, refactoring
4. **Low** - Nice-to-have improvements

**Example**:
```
Task requested: Fix typo (500 tokens used)
Remaining capacity: 63.5K tokens
Action: Fix typo, then continue with Phase 8 tasks
Rationale: Maximize session value
```

---

## 📝 Continuation Prompt Format

When posting continuation prompts to PR comments:

```markdown
@copilot Continue Phase [N]: [Phase Name]

## ✅ Session Summary

**Completed Work**:
- [x] Task 1 (commit abc123)
- [x] Task 2 (commit def456)

**Progress**:
- Phase [N]: [X]% complete
- [Component]: Updated with [changes]

**Commits**: abc123, def456, ghi789

## 🎯 Next Steps

**Priority Tasks**:
1. [ ] Task A - [Brief description]
2. [ ] Task B - [Brief description]

**Cognitive Brain Status**:
- Dashboard updated: [Yes/No]
- Roadmap updated: [Yes/No]
- Blockers: [None/List]

**Duration Estimate**: [X] sessions (~[Y]K tokens)

## 📚 Context References

- [Cognitive Map](docs/system/CODEBASE_COGNITIVE_MAP.md)
- [Dashboard](docs/system/CODEBASE_DASHBOARD.md)
- [Roadmap](docs/ROADMAP.md)
- [Related Doc](path/to/doc.md)

**Branch**: [branch-name]
**PR**: #[number]
**Current Phase**: Phase [N]
```

---

## 🧭 Cognitive Brain Integration

### Always Consult These Files First

1. **[Cognitive Map](../system/CODEBASE_COGNITIVE_MAP.md)** - Understand architecture
2. **[Dashboard](../system/CODEBASE_DASHBOARD.md)** - Check current status
3. **[Roadmap](../ROADMAP.md)** - See planned work
4. **[Master Index](../MASTER_INDEX.md)** - Find documentation

### Update After Each Session

**Dashboard Updates**:
```markdown
## [Phase Name] - [Status]
**Completion**: [X]%
**Last Updated**: [Date]
**Recent Commits**: [SHA list]

**Progress**:
- [x] Completed item
- [ ] Remaining item

**Next Session**: [Brief description]
```

**Roadmap Updates**:
```markdown
| Capability | Status | Completion | Notes |
|------------|--------|------------|-------|
| [Name] | 🟢 Active | 75% | Session [date] progress |
```

---

## 🚦 Session Handoff Protocol

### Between AI Agent Sessions

**Outgoing Agent** (end of session):
1. Complete self-review (5 passes, 0 concerns)
2. Update Dashboard with progress
3. Commit all changes
4. Post continuation prompt with:
   - Work completed (commits)
   - Work remaining (tasks)
   - Cognitive brain status
   - Known blockers

**Incoming Agent** (start of session):
1. Read continuation prompt
2. Load cognitive brain (Map, Dashboard, Roadmap)
3. Validate current state matches Dashboard
4. Resume from highest priority task

### Between Human and AI Agent

**Human Handoff**:
```
@copilot [Task description]

Context:
- Current phase: [Phase N]
- See Dashboard: docs/system/CODEBASE_DASHBOARD.md
- Priority: [High/Medium/Low]
- Blockers: [None/List]
```

**AI Agent Response**:
1. Acknowledge task
2. State current context (phase, status)
3. Outline approach
4. Execute work
5. Report completion or continuation

---

## 🎓 Best Practices

### Do's ✅
- **Always** load cognitive brain first
- **Always** perform 5-pass self-review
- **Always** update Dashboard with progress
- **Always** commit frequently with clear messages
- **Always** continue if capacity remains
- **Always** post continuation prompt if incomplete

### Don'ts ❌
- **Never** stop prematurely when capacity remains
- **Never** skip self-review passes
- **Never** leave Dashboard outdated
- **Never** commit without validation
- **Never** defer work without documented reason
- **Never** assume context without reading cognitive brain

---

## 📊 Success Metrics

### Session Quality
- Self-review: 5/5 passes complete, 0 concerns
- Commits: All validated, clear messages
- Tests: 100% passing
- Documentation: Updated and accurate
- Cognitive brain: Current and complete

### Continuity
- Context preserved: 100%
- No duplicate work: 100%
- Smooth handoffs: <2 minutes context load
- Work efficiency: >50% token utilization

---

## 🔄 Protocol Updates

**Version History**:
- 2.0.0 (2025-12-30) - Added cognitive brain integration, duration-aware planning
- 1.0.0 (2025-11-06) - Initial protocol

**Change Process**:
1. Propose changes via PR
2. Update this document
3. Update cognitive brain references
4. Notify active agents via PR comments

---

## 📚 Related Documentation

- [Cognitive Map](../system/CODEBASE_COGNITIVE_MAP.md) - Architecture
- [Dashboard](../system/CODEBASE_DASHBOARD.md) - Status
- [Roadmap](../ROADMAP.md) - Planning
- [Master Index](../MASTER_INDEX.md) - Documentation hub
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contribution guide

---

**Questions?** Open an issue with tag `agent-protocol` or consult the cognitive brain.
