# AI Codebase Agency Policy

**Version:** 1.0.0  
**Effective Date:** 2026-01-05  
**Status:** Mandatory for ALL AI agents  
**Enforcement:** Policy violations require immediate correction

---

## Purpose

This policy establishes mandatory guidelines for ALL AI agents (GitHub Copilot, custom agents, and automated systems) working within the `Aries-Serpent/_codex_` repository. The goal is to ensure:

- Comprehensive problem resolution
- Consistent code quality
- Knowledge transfer between agent sessions
- Cumulative codebase improvements
- Maintainable and documented solutions

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Comprehensive Issue Resolution](#comprehensive-issue-resolution)
3. [Planning Before Execution](#planning-before-execution)
4. [Timeline Terminology Convention](#timeline-terminology-convention)
5. [Tooling Function Documentation Policy](#tooling-function-documentation-policy)
6. [Self-Review Requirements](#self-review-requirements)
7. [Code Quality Standards](#code-quality-standards)
8. [Documentation Standards](#documentation-standards)
9. [AfterMath/PDA Loop Integration](#aftermathpda-loop-integration)
10. [Follow-Up Prompt Requirements](#follow-up-prompt-requirements)

---

## Core Principles

### 1. "Leave Codebase Better Than Found"

Every agent session MUST improve the codebase, not just complete assigned tasks. This includes:

- Fixing pre-existing issues encountered during work
- Improving code quality beyond minimum requirements
- Adding documentation where missing
- Creating reusable utilities for future agents

### 2. "Address ALL Concerns"

**NEVER** claim "not my responsibility" or "pre-existing issue" to avoid work. You MUST:

- Address ALL issues found during your session
- Fix pre-existing problems related to your work area
- Improve code quality comprehensively
- Document and resolve root causes

### 3. "No Deferral Without Plan"

**NEVER** defer work without:

- Explicit documented reasoning
- Comprehensive resolution plan
- Best-effort solution attempts (minimum 5 iterations)
- Clear next steps for future agent

---

## Comprehensive Issue Resolution

### Mandatory Requirements

1. **Address Pre-Existing Issues:**
   - Fix broken links even if you didn't create them
   - Resolve code quality issues in files you touch
   - Update outdated documentation
   - Remove deprecated code patterns

2. **Iterative Problem Solving:**
   - Minimum 5 iteration attempts before documenting blockers
   - Each iteration must show improvement
   - Document what was tried and why it failed
   - Propose alternative approaches

3. **Root Cause Analysis:**
   - Don't just fix symptoms
   - Identify and resolve underlying causes
   - Prevent similar issues in the future
   - Document lessons learned

### Examples

**❌ WRONG:**
```
"The documentation link checker is failing, but those are pre-existing
broken links not related to my PR. I'll skip fixing them."
```

**✅ CORRECT:**
```
"The documentation link checker found 36 broken links. I've created a
comprehensive fix script, updated all files, and documented the utility
for future use. All links now verified working."
```

---

## Planning Before Execution

### Requirements

BEFORE making ANY changes, you MUST:

1. **Create Comprehensive Plan:**
   - List all tasks to be completed
   - Identify dependencies and order
   - Estimate complexity and time
   - Define success criteria

2. **Document Plan:**
   - Use markdown checklists
   - Break into manageable phases
   - Track progress with pre-commit cycles
   - Update plan as work progresses

3. **Share Plan Early:**
   - Report progress with initial plan
   - Update stakeholders on changes
   - Maintain consistent checklist structure
   - Show completed vs. remaining work

### Plan Template

```markdown
## Phase X: [Name]

### Pre-commit 1-2: [Component Name]

**Goal:** [Clear objective]

**Tasks:**
- [ ] Task 1: [Specific action]
- [ ] Task 2: [Specific action]
- [ ] Task 3: [Specific action]

**Success Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Files to Create/Modify:**
- `path/to/file1.py` (XXX lines)
- `path/to/file2.py` (XXX lines)

### Review, Verify, Commit
- [ ] All tests passing
- [ ] Code review complete
- [ ] Documentation updated
```

---

## Timeline Terminology Convention

### Mandatory Usage

For ALL future work and planning, use pre-commit/commit cycle terminology, NOT time-based terms.

### ✅ CORRECT

- "6 pre-commit to commit cycles"
- "Pre-commit 1-2: Outcome Analyzer"
- "Pre-commit 3-4: Strategy Optimizer"
- "Review, verify, commit"

### ❌ WRONG

- "6 weeks"
- "Week 1-2"
- "Duration: 4 weeks"
- "Jan 13 - Feb 23, 2026" (for future work)

### Exception

Historical references MAY use actual dates:
- "Completed: 2026-01-05" ✅
- "Work finished in 3 days" ✅ (retrospective only)

### Rationale

- Git commits are the unit of work, not calendar time
- Agent sessions vary in duration
- Pre-commit cycles align with development workflow
- More accurate for AI-assisted development

---

## Tooling Function Documentation Policy

### Critical Requirement

If you create ANY tooling functions, scripts, or utilities during your session, you MUST:

1. **Document immediately** in `.codex/AI_AGENT_UTILITIES_REGISTRY.md`
2. **Implement completely** (no partial implementations)
3. **Add usage examples** and tests (minimum 80% coverage)
4. **Plan for future reuse** by other AI agents

### Rationale

Every utility created represents valuable work that should be available to ALL future agents. Documenting and implementing utilities ensures:

- No duplicate work across sessions
- Consistent patterns and conventions
- Cumulative codebase improvements
- Knowledge transfer between agents
- Reduced implementation time for future work

### Registry Location

`.codex/AI_AGENT_UTILITIES_REGISTRY.md`

### Examples of Utilities to Document

- Bash scripts for automation
- Python utility functions
- Validation tools
- Testing helpers
- Analysis scripts
- CI/CD integrations
- Data processing pipelines
- Report generators

### Documentation Template

```markdown
## [Utility Name]

**Created:** YYYY-MM-DD (Session X)  
**Agent:** [Agent Name]  
**Status:** ✅ Implemented | 📋 Planned | 🔄 In Progress

### Description
[One-paragraph description of purpose and functionality]

### Location
\`\`\`
path/to/utility.py
\`\`\`

### Usage
\`\`\`bash
# Example command
python path/to/utility.py --arg value
\`\`\`

### Features
- Feature 1
- Feature 2
- Feature 3

### Success Metrics
- Metric 1: Value
- Metric 2: Value

### Dependencies
- dependency1
- dependency2

### Future Enhancements
- [ ] Enhancement 1
- [ ] Enhancement 2
```

### Violation Consequences

Creating utilities without documentation is a policy violation and MUST be corrected immediately by:

1. Stopping current work
2. Documenting the utility in the registry
3. Adding usage examples and tests
4. Resuming original work

---

## Self-Review Requirements

### Mandatory 5-Pass Review

BEFORE concluding your session, you MUST perform 5 comprehensive self-review passes:

### Pass 1: Code Quality & Correctness
- [ ] All syntax errors resolved
- [ ] No linting warnings introduced
- [ ] Type hints correct and complete
- [ ] Error handling comprehensive
- [ ] Edge cases covered

### Pass 2: Testing & Validation
- [ ] All tests passing locally
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved (minimum 80%)
- [ ] CI/CD checks passing
- [ ] Integration tests validated

### Pass 3: Documentation & Communication
- [ ] Code comments added for complex logic
- [ ] Docstrings updated
- [ ] README reflects changes
- [ ] CHANGELOG updated
- [ ] Commit messages descriptive

### Pass 4: Security & Safety
- [ ] No hardcoded secrets or credentials
- [ ] Input validation added
- [ ] Dependencies reviewed (no known vulnerabilities)
- [ ] Security implications documented
- [ ] SQL injection / XSS prevention

### Pass 5: Integration & Dependencies
- [ ] No breaking changes (or properly documented)
- [ ] Backward compatibility maintained
- [ ] Cross-PR dependencies resolved
- [ ] No regressions introduced
- [ ] AfterMath/PDA loop integrated (where applicable)

### Failure Protocol

If ANY checkpoint fails:

1. **Document the issue** in detail
2. **Create resolution plan** with specific steps
3. **Execute within current session** (no deferral)
4. **Re-run self-review** until all checks clear

### Iteration Requirement

- Minimum 5 self-review iterations
- Each iteration must address previous findings
- Continue until zero concerns remain
- Document all iterations in commit message

### Mandatory Session Completion Protocol

**BEFORE finalizing ANY session, ALL agents MUST:**

1. **Perform Comprehensive Self-Review:**
   - Minimum 5+ iterations until zero concerns remain
   - Each iteration documents findings and resolutions
   - Continue iterating until no new issues discovered
   - Use autonomous self-healing and continuous improvement

2. **Address ALL Concerns Repo-Wide:**
   - Address concerns you worked on directly
   - Address related concerns in affected areas
   - Address pre-existing issues discovered during work
   - NEVER claim "not my responsibility"
   - Search repo-wide for similar issues

3. **Never Defer Work Without Full Resolution:**
   - Document reasoning for any deferral
   - Provide comprehensive resolution plan
   - Best-effort iterations (minimum 5 attempts)
   - Include timeline and success criteria
   - Assign clear ownership for continuation

4. **Create and Submit Follow-Up Prompt:**
   - REQUIRED for all incomplete work
   - Submit as new comment on current PR
   - First line MUST start with `@copilot` (no spaces, no backticks)
   - Include full context and next steps
   - Reference planning documents
   - Mandate policy compliance

### Follow-Up Prompt Requirements

**Format:**
```
@copilot [Task description]

**Current Status:**
- [x] Completed items
- [ ] Pending items

**Next Pre-commit Tasks:**
1. Specific task with acceptance criteria
2. Another task with details

**Success Criteria:**
- Measurable outcome 1
- Measurable outcome 2

**Policy Compliance:**
Must follow .codex/CODEBASE_AGENCY_POLICY.md

**Context:**
Reference to planning docs with full details
```

**Verification Steps:**
1. Write follow-up prompt with exact format above
2. Post as comment on current PR (not in file)
3. Verify comment appears in PR timeline
4. Confirm @copilot trigger is correctly formatted

### Consequences of Non-Compliance

Failing to complete session protocol results in:
- Incomplete work requiring rework
- Context loss for next agent
- Broken continuity in implementation
- Policy violation requiring correction

---

## Code Quality Standards

### Input Validation & Sanitization

ALL external input MUST be validated and sanitized:

```python
# ✅ CORRECT
def generate_code(prompt: str) -> str:
    # Sanitize to prevent code injection
    sanitized = prompt.replace(/[^a-zA-Z0-9_]/g, '_')
    if not sanitized:
        sanitized = "default_function"
    return f"def {sanitized}():"

# ❌ WRONG
def generate_code(prompt: str) -> str:
    return f"def {prompt}():"  # Direct interpolation!
```

### Error Messages

User-facing error messages MUST be:
- Clear and actionable
- Free of technical jargon
- Not expose implementation details
- Provide next steps

```python
# ✅ CORRECT
toast.error('Cannot execute workflow', {
    description: 'This workflow is blocked by unmet dependencies. Please review the workflow setup and try again.',
});

# ❌ WRONG
toast.error('Workflow blocked', {
    description: analysis.blockedReason,  # Raw technical message
});
```

### Date Handling

ALL date operations MUST include validation:

```python
# ✅ CORRECT
def format_date(date_string: str) -> str:
    if not date_string:
        return "N/A"
    
    try:
        date = datetime.fromisoformat(date_string)
        if not date or date.year < 1900:
            return "Invalid date"
        return date.strftime("%Y-%m-%d")
    except ValueError:
        return "Invalid date"

# ❌ WRONG
def format_date(date_string: str) -> str:
    return datetime.fromisoformat(date_string).strftime("%Y-%m-%d")
```

### Variable Naming

Variables MUST have clear, descriptive names:

```python
# ✅ CORRECT
transfer_stats = {'total': 0, 'active': 0}
user_profile_data = fetch_profile()
reward_calculation_result = calculate_reward()

# ❌ WRONG
stats = {'total': 0, 'active': 0}  # Ambiguous
data = fetch_profile()  # Too generic
result = calculate_reward()  # Unclear purpose
```

---

## Documentation Standards

### Code Comments

Add comments for:
- Complex algorithms
- Non-obvious business logic
- Performance optimizations
- Workarounds for known issues
- Integration points with external systems

**DON'T comment:**
- Obvious code (`i++  // increment i`)
- Self-documenting code
- Version history (use git)

### Docstrings

ALL public functions MUST have docstrings:

```python
def analyze_outcome(outcome: LearningOutcome) -> AnalysisResult:
    """
    Analyze learning outcome and extract patterns.
    
    Args:
        outcome: The learning outcome to analyze containing
                 decision context, result, and metrics
    
    Returns:
        AnalysisResult with identified patterns, confidence scores,
        and actionable lessons learned
    
    Raises:
        ValueError: If outcome is invalid or missing required fields
        
    Example:
        >>> outcome = LearningOutcome(decision_id="123", ...)
        >>> result = analyze_outcome(outcome)
        >>> print(result.patterns)
        ['temporal_pattern_1', 'contextual_pattern_2']
        
    Notes:
        - Uses 4 pattern categories: temporal, contextual, sequential, causal
        - Confidence threshold is 0.8 for high-confidence patterns
        - Integrates with AfterMath feedback loop for continuous improvement
    """
    pass
```

---

## AfterMath/PDA Loop Integration

### Requirements

For Cognitive Brain components, MUST integrate AfterMath/PDA loop:

```python
# ✅ Required pattern
class OutcomeAnalyzer:
    """
    Outcome analysis with pattern detection.
    
    **AfterMath Integration:** This component feeds back into the
    decision-making process by identifying patterns from past outcomes
    and adjusting strategy selection.
    
    **PDA Loop:** Participates in Plan-Do-Assess cycle by:
    - PLAN: Receives decision context
    - DO: Analyzes outcomes
    - ASSESS: Provides pattern feedback for future decisions
    """
    
    def analyze_outcome(self, outcome: LearningOutcome) -> AnalysisResult:
        """Analyze outcome and update AfterMath feedback."""
        # Analysis logic...
        
        # AfterMath: Store for future learning
        self._aftermath_tracker.record(outcome, patterns)
        
        return result
```

### Annotations

Use PDA annotations in code:

```python
# PDA: PLAN phase - Context setup
context = DecisionContext(...)

# PDA: DO phase - Execute decision
result = execute_decision(context)

# PDA: ASSESS phase - Analyze outcome
analysis = analyze_outcome(result)

# AfterMath: Feed back for future decisions
update_strategy(analysis.lessons_learned)
```

---

## Follow-Up Prompt Requirements

### When Session Cannot Complete All Work

If your session ends with incomplete work, you MUST:

1. **Create comprehensive continuation prompt**
2. **Submit as PR comment** starting with `@copilot`
3. **Include all context** needed for next agent
4. **Define clear success criteria**
5. **Reference planning documents**

### Continuation Prompt Template

```markdown
@copilot Begin [Phase Name] implementation following `.codex/prompts/[PROMPT_FILE].md`.

**Current Status:**
- [x] Completed task 1
- [ ] Pending task 2
- [ ] Pending task 3

**Next Pre-commit Cycle Tasks:**
1. Create `path/to/file.py` with [specific requirements]
2. Implement [specific algorithm/feature]
3. Create tests (minimum XX tests)
4. Integrate with [existing component]

**Success Criteria:**
- ✅ All XX+ tests passing
- ✅ [Performance metric] achieved
- ✅ [Integration point] verified
- ✅ Documentation complete

**Policy Compliance (Mandatory):**
- Follow `.codex/CODEBASE_AGENCY_POLICY.md`
- Address ALL issues (pre-existing + new)
- Plan before execution
- Use pre-commit/commit terminology
- 5+ self-review iterations
- Maintain AfterMath/PDA loop

**Full Implementation Guide:**
`.codex/prompts/[DETAILED_PROMPT].md` (XXX KB detailed plan)
```

### Submission Requirements

1. **First line MUST** start with `@copilot` (no spaces, no backticks)
2. **Include file paths** for context
3. **Reference planning docs** for full details
4. **Define success criteria** explicitly
5. **Mandate policy compliance**

### Verification

After creating prompt:
- [ ] Verify submitted as PR comment
- [ ] Verify formatting correct (@copilot at start)
- [ ] Verify all context included
- [ ] Verify success criteria clear

---

## Policy Enforcement

### Violations

The following are policy violations:

1. Claiming "not my responsibility" for pre-existing issues
2. Deferring work without comprehensive resolution plan
3. Creating utilities without documentation
4. Skipping self-review passes
5. Using time-based terminology for future work
6. Incomplete planning before execution
7. Missing AfterMath/PDA integration
8. Poor error messages exposing technical details
9. **NEW:** Concluding session without 5+ self-review iterations
10. **NEW:** Failing to address ALL concerns (including repo-wide)
11. **NEW:** Not creating follow-up prompt for incomplete work
12. **NEW:** Not submitting follow-up prompt as PR comment with @copilot

### Correction Process

Upon detecting violation:

1. **Stop current work immediately**
2. **Correct the violation** (add documentation, fix issue, etc.)
3. **Document the correction** in commit message
4. **Resume original work**

### Escalation

Repeated violations or inability to correct:
- Document in PR for human review
- Provide specific examples
- Recommend process improvements

---

## Quick Reference

### Must Do ✅

- Address ALL issues (pre-existing + new + repo-wide)
- Plan before executing
- Use pre-commit/commit terminology
- Document ALL utilities created
- **5+ self-review iterations (zero concerns)**
- **Submit @copilot follow-up prompt as PR comment**
- AfterMath/PDA integration
- Comprehensive error handling
- Clear, actionable error messages
- Input validation and sanitization
- 80%+ test coverage

### Never Do ❌

- Claim "not my responsibility"
- Defer without resolution plan + 5 best-effort attempts
- Create utilities without docs
- Skip self-review passes
- **Conclude session without follow-up prompt**
- Use weeks/days for future planning
- Expose technical details in UI
- Skip input validation
- Leave incomplete work

### Always Remember 💡

- Leave codebase better than found
- **Best-effort iterations (minimum 5)**
- **Address ALL concerns until zero remain**
- Knowledge transfer to future agents
- Cumulative improvements
- Root cause resolution
- **Post follow-up prompt on PR with @copilot**
- Lessons learned documentation

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-05 | Initial policy creation |
| 1.1.0 | 2026-01-05 | Added mandatory session completion protocol |

---

## Contact & Questions

For policy clarification or proposed changes:
- Create issue in repository
- Tag with `policy` label
- Provide specific examples
- Propose alternatives

---

**This policy is mandatory for ALL AI agents working in this repository.**

**Violations must be corrected immediately.**

**Compliance ensures consistent, high-quality codebase improvements.**
