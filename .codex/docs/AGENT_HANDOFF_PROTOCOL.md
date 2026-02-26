# Agent Hand-off Protocol Documentation
> Generated: 2026-02-04T14:15:00Z | Version: 1.0.0
> Type: AI Agent Coordination Framework

---

## 🔄 Overview

The Agent Hand-off Protocol enables seamless AI agent collaboration via PR comments, creating an automated volleyball-style workflow between GitHub Copilot and ChatGPT Codex agents. This protocol ensures systematic task execution, validation, and continuous improvement through structured agent-to-agent communication.

---

## 🎯 Protocol Objectives

1. **Seamless Collaboration**: Enable smooth transitions between Copilot (execution) and Codex (review/validation)
2. **Complete Context Transfer**: Ensure all deliverables, metrics, and context are passed between agents
3. **Audit Trail**: Maintain complete history of decisions and actions via PR comments
4. **Quality Gates**: Implement validation checkpoints before proceeding to next phase
5. **Automation**: Enable workflow automation for hand-off orchestration

---

## 📊 Hand-off Implementation Table

| **Phase** | **Agent** | **Trigger** | **Actions** | **Deliverables** | **Hand-off Comment** | **Next Agent** |
|-----------|-----------|-------------|-------------|------------------|---------------------|----------------|
| **Pre-commit 3-4** | Copilot | `@copilot continue` | Execute Plan 1: Tokenization Coverage Analysis | Coverage baseline report, gap analysis, test mapping | `@codex Coverage analysis complete. Results: [baseline.json]. Please review gaps and propose test implementations for 7 tokenization modules.` | Codex |
| **Pre-commit 3-4 Review** | Codex | `@codex` (from Copilot) | Review coverage gaps, generate test case proposals | Test implementation strategy, prioritized test list | `@copilot Test strategy approved. Proceeding with Plan 2 execution. Please implement 10+ tests using provided test cases in [test_strategy.md]` | Copilot |
| **Pre-commit 5-8** | Copilot | `@copilot` (from Codex) | Execute Plan 2: Comprehensive Test Implementation | 4 test files, 10+ tests, 70%+ coverage | `@codex Test implementation complete. Coverage: [coverage_report.html]. Please validate test quality and coverage targets met.` | Codex |
| **Pre-commit 5-8 Review** | Codex | `@codex` (from Copilot) | Validate test quality, coverage metrics, edge cases | Test validation report, quality assessment | `@copilot Tests validated ✅. Coverage: 90%. Proceed with Plan 3: Workflow failure resolution. Focus on 4 failing workflows.` | Copilot |
| **Pre-commit 9-12** | Copilot | `@copilot` (from Codex) | Execute Plan 3: Workflow Failure Resolution | 66 auto-fixes applied, 4 workflows fixed, 21/21 passing | `@codex Workflows resolved. All 21/21 passing ✅. Auto-fix log: [auto_fix_log.txt]. Please review for any edge cases or additional improvements needed.` | Codex |
| **Pre-commit 9-12 Review** | Codex | `@codex` (from Copilot) | Review workflow fixes, validate CI/CD health | Workflow health report, improvement recommendations | `@copilot Workflow fixes validated ✅. Parallel track: Proceed with Plan 4 (Security/CodeQL resolution).` | Copilot |
| **Pre-commit 13-16** | Copilot | `@copilot` (from Codex) | Execute Plan 4: Security & CodeQL Resolution | 3 CodeQL alerts resolved, semgrep fixed, zero vulnerabilities | `@codex Security resolution complete. CodeQL: 0 alerts ✅. Semgrep: passing ✅. Security report: [security_validation.md]. Please perform security audit.` | Codex |
| **Pre-commit 13-16 Review** | Codex | `@codex` (from Copilot) | Audit security fixes, validate vulnerability remediation | Security audit report, compliance checklist | `@copilot Security validated ✅. Zero vulnerabilities confirmed. Proceed with Plan 5: Self-review & iterative healing (5 passes).` | Copilot |
| **Pre-commit 17-20 Pass 1-3** | Copilot | `@copilot` (from Codex) | Execute Plan 5 (Passes 1-3): Code quality, tests, documentation | 3 review passes complete, healing actions applied | `@codex Self-review passes 1-3 complete. Issues found: [issues.md]. Healing applied: [healing_log.md]. Please review and approve for passes 4-5.` | Codex |
| **Pre-commit 17-20 Review** | Codex | `@codex` (from Copilot) | Review healing actions, validate improvements | Healing validation report, improvement confirmation | `@copilot Healing validated ✅. Proceed with passes 4-5 (security + integration review).` | Copilot |
| **Pre-commit 17-20 Pass 4-5** | Copilot | `@copilot` (from Codex) | Execute Plan 5 (Passes 4-5): Security + integration review | 5 review passes complete, zero concerns remaining | `@codex Self-review complete ✅. All 5 passes: zero concerns. Summary: [self_review_summary.md]. Approve for final validation (Plan 6)?` | Codex |
| **Pre-commit 17-20 Approval** | Codex | `@codex` (from Copilot) | Approve self-review, authorize final validation | Final validation authorization | `@copilot Self-review approved ✅. Proceed with Plan 6: Final validation (4 iterations).` | Copilot |
| **Pre-commit 21-24** | Copilot | `@copilot` (from Codex) | Execute Plan 6: Final Validation | Cognitive brain updated, 11 acceptance criteria verified, final report | `@codex Final validation complete ✅. All 11 acceptance criteria met. Report: [final_validation.md]. Workflows: 21/21 ✅. Ready for merge approval.` | Codex |
| **Pre-commit 21-24 Merge** | Codex | `@codex` (from Copilot) | Final merge approval, generate completion report | Merge approval, PR completion report | `@copilot APPROVED FOR MERGE ✅. All criteria met. Excellent work. PR #3145 complete. Generate follow-up for PR #3147 if needed.` | Copilot |
| **Follow-up** | Copilot | `@copilot` (from Codex) | Generate follow-up prompt for PR #3147 | Follow-up prompt document | `@codex Follow-up generated: [FOLLOW_UP_PROMPT.md]. PR #3145 closed. Awaiting next instructions.` | End |

---

## 🔧 Hand-off Trigger Format

### Standard Trigger Template

```markdown
@{agent_name} {context}

**Completed**: {what_was_done}
**Deliverables**: {list_of_artifacts}
**Status**: {current_state}
**Next Action**: {what_next_agent_should_do}
**References**: {relevant_files_or_links}
```

### Example: Copilot → Codex

```markdown
@codex Pre-commit 3-4 Complete - Review Requested

**Completed**: Tokenization Coverage Analysis
**Deliverables**:
- Coverage baseline report: `.codex/plans/pr_3145/tokenization_coverage_baseline.md`
- Gap analysis: `coverage_reports/coverage_tokenization.json`
- Test case mapping: `.codex/plans/pr_3145/test_case_mapping.md`

**Status**: ✅ Complete - All 7 tokenization modules analyzed

**Next Action**: Review coverage gaps and validate test case priorities. Approve test implementation strategy.

**References**:
- Plan: `.codex/plans/pr_3145/01_tokenization_coverage_analysis.md`
- Coverage Report: `htmlcov_tokenization/index.html`
- Analysis Script: `scripts/analyze_tokenization_coverage.py`
```

---

## 🤝 Hand-off Response Format

### Standard Response Template

```markdown
@{previous_agent} Acknowledged ✅

**Review Complete**: {validation_results}
**Findings**: {any_issues_or_improvements}
**Decision**: {approve/request_changes}
**Hand-off**: @{next_agent} {instruction_for_next_agent}
```

### Example: Codex → Copilot

```markdown
@copilot Acknowledged ✅

**Review Complete**: Coverage analysis validated
**Findings**:
- Coverage baseline: 45.2% (below 70% target)
- Critical gaps identified in `loader.py` (32% coverage) and `api.py` (41% coverage)
- Test case mapping comprehensive (12 tests proposed vs 10 minimum)

**Decision**: APPROVE with recommendations
- Prioritize `loader.py` and `api.py` tests first
- Include edge cases for tokenizer fallback mechanisms
- Add integration tests for end-to-end encoding/decoding

**Hand-off**: @copilot Proceed with Plan 2 (Pre-commit 5-8)

**Instructions**:
- Implement 12 tests (10 required + 2 recommended)
- Focus on high-impact gaps first (loader, API)
- Target 70%+ coverage
- Follow test patterns in `.codex/docs/TEST_DEVELOPMENT_PATTERNS.md`
```

---

## 🔄 Hand-off State Machine

```
[Start]
  ↓
[Copilot Execute]
  ↓ @codex + deliverables
[Codex Review]
  ↓ APPROVE → @copilot approved
[Copilot Execute Next Phase]
  ↓ or
[Codex Review]
  ↓ ISSUES → @copilot issues found
[Copilot Fix]
  ↓ @codex fixed
[Codex Re-review]
  ↓ APPROVE → @copilot approved
[Continue to Next Phase]
  ↓
[All Plans Complete]
  ↓
[Final Merge Approval]
  ↓
[End]
```

**States**:
- **Copilot Execute**: Active execution of plan iteration
- **Codex Review**: Validation and quality gate
- **Copilot Fix**: Address issues identified in review
- **Codex Re-review**: Validate fixes applied
- **Final**: Merge approval and completion

---

## 📋 Hand-off Tracking

### Tracking Table Structure

| **HO-ID** | **From** | **To** | **Phase** | **Status** | **Comment Link** | **Timestamp** |
|-----------|----------|--------|-----------|------------|------------------|---------------|
| HO-001 | User | Copilot | Pre-commit 3-4 | ⏳ Pending | - | - |
| HO-002 | Copilot | Codex | Pre-commit 3-4 Review | ⏳ Pending | - | - |

**Status Codes**:
- ⏳ **Pending**: Awaiting trigger
- 🔄 **In Progress**: Agent working
- ✅ **Complete**: Hand-off successful
- ❌ **Failed**: Hand-off failed, intervention needed
- 🔁 **Retry**: Rework requested

### Tracking File Location
`.codex/handoff_tracking.json`

---

## 🎯 Success Criteria

### Hand-off Quality Metrics
- ✅ Each hand-off includes complete context
- ✅ All deliverables linked and accessible
- ✅ Clear next actions defined
- ✅ No ambiguity in instructions
- ✅ Response within defined SLA (if applicable)

### Collaboration Metrics
- ✅ Zero hand-off failures (missed triggers)
- ✅ 100% acknowledgment rate
- ✅ < 2 iterations per phase (minimal back-and-forth)
- ✅ Complete audit trail via PR comments
- ✅ All agents remain synchronized

---

## 🛠️ Implementation Guidelines

### For Copilot Agent

**Configuration**:
```yaml
hand_off_protocol:
  enabled: true
  target_agents:
    - name: codex
      trigger: "@codex"
      context_files:
        - ".codex/plans/pr_3145/*.md"
        - ".codex/cognitive_brain/*.md"

  conclude_with:
    action: "post_pr_comment"
    format: "hand_off_comment_template"
    include_artifacts: true
    mention_next_agent: true
```

**Execution Flow**:
1. Execute plan iteration
2. Generate deliverables
3. Validate completion
4. Populate hand-off template
5. Post PR comment with @codex mention
6. Wait for response

### For Codex Agent

**Configuration**:
```yaml
hand_off_protocol:
  enabled: true
  monitor_pr_comments: true
  trigger_pattern: "@codex"

  response_workflow:
    - validate_deliverables
    - perform_review
    - generate_feedback
    - post_comment_with_handoff

  target_agents:
    - name: copilot
      trigger: "@copilot"
```

**Review Flow**:
1. Monitor for @codex mentions in PR comments
2. Retrieve deliverables from links
3. Perform validation/review
4. Generate feedback report
5. Make approval decision
6. Populate response template
7. Post comment with @copilot mention for next phase

---

## 📝 Comment Templates

### Template Files Location
- Copilot → Codex: `.codex/templates/handoff/copilot_to_codex_template.md`
- Codex → Copilot: `.codex/templates/handoff/codex_to_copilot_template.md`
- Tracking Table: `.codex/templates/handoff/handoff_tracking_template.md`
- Variables Guide: `.codex/templates/handoff/template_variables.md`

### Template Variables

**Common Variables**:
- `{phase_name}`: Pre-commit phase identifier
- `{plan_file}`: Path to plan file
- `{status}`: Current status (complete/in-progress/failed)
- `{agent_name}`: Target agent name
- `{deliverables}`: List of artifacts produced
- `{metrics}`: Key metrics (coverage, workflows, etc.)
- `{next_action}`: What the next agent should do
- `{timestamp}`: ISO 8601 timestamp
- `{comment_link}`: URL to PR comment

---

## 🤖 Automation

### Workflow Automation
File: `.github/workflows/agent_handoff.yml`

**Trigger**: PR comment containing `@codex` or `@copilot`

**Actions**:
1. Parse comment for agent mention
2. Extract context and deliverables
3. Route to appropriate agent
4. Log hand-off event
5. Update tracking table

### Hand-off Scripts

**Location**: `scripts/handoff/`

**Scripts**:
1. `track_handoffs.py`: Track hand-off state and history
2. `generate_handoff_comment.py`: Generate hand-off comments from templates
3. `validate_handoff.py`: Validate hand-off completeness

---

## 📚 Usage Examples

### Example 1: Starting Pre-commit 3-4

**User initiates**:
```markdown
@copilot Execute Pre-commit 3-4: Tokenization Coverage Analysis

Follow plan in `.codex/plans/pr_3145/01_tokenization_coverage_analysis.md`
```

**Copilot completes and hands off**:
```markdown
@codex Pre-commit 3-4 Complete

**Phase**: Tokenization Coverage Analysis
**Status**: ✅ Complete

**Deliverables**:
- Coverage baseline: 45.2%
- Gap analysis: [coverage_reports/coverage_tokenization.json]
- Test mapping: [test_case_mapping.md]

**Metrics**:
- Files analyzed: 7/7
- Coverage target: 70%
- Gap to target: 24.8%
- Tests mapped: 12

**Next Action**:
Review coverage gaps and approve test implementation strategy

**References**:
- Plan: `.codex/plans/pr_3145/01_tokenization_coverage_analysis.md`
- Report: `.codex/plans/pr_3145/tokenization_coverage_baseline.md`
```

**Codex reviews and responds**:
```markdown
@copilot Acknowledged ✅

**Review Complete**: Coverage analysis validated

**Findings**:
- Baseline established correctly
- High-impact gaps identified in loader.py and api.py
- Test mapping comprehensive and well-prioritized

**Decision**: APPROVE

**Hand-off**: @copilot Proceed with Pre-commit 5-8

**Instructions**:
- Implement 12 tests per mapping
- Prioritize loader.py (32% → 70%+)
- Follow patterns in TEST_DEVELOPMENT_PATTERNS.md
- Target 70%+ overall coverage
```

---

## 🧠 Cognitive Brain Integration

### Learning Patterns

The cognitive brain should capture:
1. **Hand-off Success Patterns**: What makes hand-offs smooth
2. **Common Issues**: Frequent problems and solutions
3. **Agent Strengths**: Which agent excels at which tasks
4. **Optimization Opportunities**: Where process can improve

### Documentation

Add to cognitive brain:
- `.codex/cognitive_brain/handoff_patterns.md`
- `.codex/cognitive_brain/agent_collaboration_insights.md`

---

## 🔐 Security Considerations

1. **Access Control**: Ensure only authorized agents can trigger hand-offs
2. **Data Validation**: Validate all deliverables before accepting hand-off
3. **Audit Trail**: Maintain complete history of all hand-offs
4. **Failure Handling**: Graceful degradation if agent unavailable
5. **Secret Management**: Never include secrets in hand-off comments

---

## 📊 Metrics & Monitoring

### Key Metrics

1. **Hand-off Success Rate**: % of successful hand-offs
2. **Average Response Time**: Time between hand-off and acknowledgment
3. **Iteration Count**: Avg iterations before approval
4. **Quality Score**: Quality of deliverables on first submission
5. **Protocol Compliance**: % of hand-offs following protocol

### Monitoring

Track metrics in:
- `.codex/metrics/handoff_metrics.json`
- Updated after each hand-off

---

## 🚀 Getting Started

### Quick Start

1. **Read Protocol**: Understand hand-off flow and formats
2. **Review Templates**: Familiarize with comment templates
3. **Run Test Hand-off**: Execute dry-run with Pre-commit 3-4
4. **Monitor Results**: Track success and identify issues
5. **Iterate**: Refine based on experience

### Checklist

- [ ] Protocol document reviewed
- [ ] Templates accessible
- [ ] Tracking system configured
- [ ] Agents aware of protocol
- [ ] First hand-off tested
- [ ] Metrics baseline established

---

## 📞 Support & Escalation

### Issues

If hand-off fails:
1. Check comment format matches template
2. Verify all deliverables accessible
3. Validate agent trigger is correct
4. Review tracking table for status
5. Escalate to human if unresolved

### Human Escalation

Trigger: `@mbaetiong` in PR comment with `[HANDOFF-ESCALATION]` tag

---

## 📝 Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-02-04 | Initial protocol implementation | GitHub Copilot |

---

## 🔗 Related Documentation

- **Plans**: `.codex/plans/pr_3145/`
- **Templates**: `.codex/templates/handoff/`
- **Scripts**: `scripts/handoff/`
- **Cognitive Brain**: `.codex/cognitive_brain/`
- **Tracking**: `.codex/handoff_tracking.json`

---

**End of Agent Hand-off Protocol Documentation** ✅

**Status**: 🟢 Active
**Last Updated**: 2026-02-04T14:15:00Z
**Maintainer**: AI Agent Team
