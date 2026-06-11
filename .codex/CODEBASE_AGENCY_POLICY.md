# AI Codebase Agency Policy

**Version:** 1.1.0
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
5. [Non-Deferral Mandate for CI Data Handling](#non-deferral-mandate-for-ci-data-handling)
6. [Emotion-Safe Urgency Guardrails](#emotion-safe-urgency-guardrails)
7. [Tooling Function Documentation Policy](#tooling-function-documentation-policy)
8. [Self-Review Requirements](#self-review-requirements)
9. [Code Quality Standards](#code-quality-standards)
10. [Documentation Standards](#documentation-standards)
11. [AfterMath/PDA Loop Integration](#aftermathpda-loop-integration)
12. [Follow-Up Prompt Requirements](#follow-up-prompt-requirements)
13. [Machine Learning Components Must Run Offline](#machine-learning-components-must-run-offline)
14. [Custom Agent Delegation Mandate (CAD-Mandate)](#custom-agent-delegation-mandate-cad-mandate)

---

## Core Principles

### 0. "Mandatory Pre-Session Review" (HARD RULE — enforced by CI)

**EVERY Copilot coding agent session MUST begin by completing ALL of the following
before making any file changes:**

1. **Review ALL bot-posted comments** on the active PR:
   - `copilot-pull-request-reviewer[bot]` — code review threads
   - `github-advanced-security[bot]` — security alerts
   - `github-code-quality[bot]` — quality findings
   - `github-actions[bot]` — CI gate comments (cognitive-preflight, deferral gate)
   - Any other bot or automated commenter
   - **ALL open/unresolved threads MUST be addressed before new work begins.**

   **§0a — MAINTAINER COMMENTS (mbaetiong) — HIGHEST PRIORITY (HARD STOP):**
   - Comments from `@mbaetiong` are BLOCKING. No commit may be pushed until
     EVERY `mbaetiong` comment has been explicitly replied to by the agent.
   - A "reply" means a substantive response that either confirms the action
     taken, explains why the request was not actionable, or asks a clarifying
     question. Silence is never acceptable.
   - This is enforced by `comment-review-gate.yml` (REQ-13). CI will FAIL
     with a blocking checklist comment listing every unaddressed `mbaetiong`
     comment. The gate re-scans on every push.
   - **Use `reply_to_comment` tool** with the correct `comment_id` for each
     unaddressed comment before committing new changes.

   **§0b — CRITICAL BOT COMMENTS — BLOCKING:**
   - `copilot-pull-request-reviewer[bot]` — all review threads (inline + overall)
   - `github-advanced-security[bot]` — all security alerts
   - `github-code-quality[bot]` — all quality findings
   - `github-actions[bot]` — all CI gate comments posted by workflows
   - These are enforced by the same `comment-review-gate.yml` (REQ-13) gate.
   - **Exception:** Informational bot comments (dependabot, codecov) are
     WARNING-level. They must be reviewed but do not block CI.

2. **Review ALL failing CI checks** on the active PR:
   - Fetch the latest workflow run status
   - Identify every failing or warning check
   - Fix every failing check that is code-fixable (not infrastructure-only)
   - Document any infrastructure-only failures with root cause
   - **Check for open CI failure report issues** — search for issues with labels
     `ci-failure` and `ci-health-alert` using `gh issue list --label ci-failure --state open`
     and `gh issue list --label ci-health-alert --state open`. These issues are
     auto-created by `ci-failure-issue-creator.yml` and `ci-health-monitor.yml`
     when workflows fail on `main`. If any open issues exist, review their content
     for patterns that may affect this PR and address any that are relevant.
   - **NO new commits may be pushed until all code-fixable failures are resolved.**

3. **Load all required documents:**
   - `.codex/CODEBASE_AGENCY_POLICY.md` (this file)
   - `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
   - All stored session memories

4. **Inspect PR for merge conflicts (HARD RULE):**
   - **At session START:** Check the PR mergeable status via `gh pr view --json mergeable`
     and run `git merge-tree $(git merge-base HEAD origin/BASE) HEAD origin/BASE`
     against the base branch to detect potential file-level conflicts.
   - If conflicts exist: resolve them BEFORE any other work begins.
   - If the branch is behind its base: rebase or merge base into head first.
   - **At session END (before final commit):** Re-check for merge conflicts introduced
     during the session. Fetch the latest base branch and verify no conflicts exist.
   - **NO session may end with unresolved merge conflicts on the PR.**
   - See: `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` §7b for full strategy.

**Enforcement:** The `cognitive-preflight` job (REQ-1) posts this checklist to every
PR when Agent Token Delegation is enabled.  The `@copilot continue` protocol mandates
this review in every session.  Violations are tracked in the accountability report.

**CI Gate:** The Cognitive Pre-flight Check blocks `activate-delegation` until this
step is confirmed complete (via session execution plan posted as PR comment).

---

### 0b. Integration Branch Model (HARD RULE — enforced by CI REQ-11)

**`0D_base_` is the staging integration branch.**  There are **two valid session
modes**; which applies depends on the PR's base branch:

| Session mode | head | base | REQ-11 result |
|---|---|---|---|
| **Sub-PR** (default) | `copilot/session-*` | `0D_base_` | ✅ PASS |
| **Promotion-PR direct** (**ideal for consolidation**) | `0D_base_` | `main` | ✅ PASS |
| ❌ Wrong target | `0D_base_` | anything other than `main` | 🚫 FAIL — hard-blocked |

Running directly on `0D_base_` is **explicitly acceptable and preferred** when the
open PR is the promotion PR (`0D_base_` → `main`).  This collapses the sub-PR +
promotion-PR steps into a single reviewable PR and minimises sub-PR churn.

#### Architecture

```
Sub-PR mode (default):
  copilot/session-*  ──►  0D_base_  ──►  main
    (agent sessions)       (staging)     (production)
    Each independently                    promotion PR
    reviewed sub-PR

Promotion-PR direct mode (ideal):
  0D_base_  ──►  main
  (agent works here directly — single PR, single review cycle)
```

#### Rules — all enforced by `cognitive-preflight` REQ-11

| Rule | Enforcement |
|------|-------------|
| Agent sessions on `copilot/session-*` must target `0D_base_`, not `main` | PR creation convention + session-chain workflow |
| Agent sessions on `0D_base_` are only allowed when `base=main` (promotion PR) | REQ-11 CI hard-block if `head=0D_base_` AND `base≠main` |
| `0D_base_` may be behind `main` by bot `[skip ci]` commits — this is expected | REQ-10 auto-passes bot-only divergence |
| Promotion (`0D_base_` → `main`) requires PR review + CI green | Human approval required |

#### To start a new agent session

```bash
# Option A — Sub-PR (automated, creates branch + PR + @copilot trigger):
gh workflow run copilot-session-chain.yml \
  -f source_branch=0D_base_ \
  -f session_title="<task description>"

# Option B — Promotion-PR direct (post @copilot on the open 0D_base_ → main PR):
gh pr comment <promotion_pr_number> --body "@copilot+claude-sonnet-4.6 continue"
```

**Enforcement:** `agent-auth-delegation.yml` `cognitive-preflight` REQ-11 guard — fires
as the FIRST step; hard-blocks only when `head=0D_base_` AND `base≠main`; passes for
all sub-PR sessions and for promotion-PR direct sessions.

**Reference:** `.codex/docs/INTEGRATION_BRANCH_MODEL.md`

---



Every agent session MUST improve the codebase, not just complete assigned tasks. This includes:

- Fixing pre-existing issues encountered during work
- Improving code quality beyond minimum requirements
- Adding documentation where missing
- Creating reusable utilities for future agents

### 2. "Address ALL Concerns"

<!-- TODO (PHILOSOPHICAL_FRAMEWORK): Deleuzian deterritorialization -->
<!-- Ref: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#policy-deterritorialization -->
<!--
Philosophical Foundation: This policy implements Deleuzian deterritorialization
by breaking the "bounded responsibility" territory.

Traditional software development territorializes responsibility:
- "My PR only touches X" (territorial boundary)
- "Pre-existing issues are not my problem" (rigid structure)
- "That's someone else's responsibility" (hierarchical thinking)

This policy deterritorializes those boundaries:
- ALL issues become your responsibility (line of flight)
- Codebase health over task completion (rhizomatic thinking)
- Continuous improvement over minimal compliance (creative advance)

This is NOT chaos - it's strategic pattern-breaking for quality.
-->

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

### 3a. Deferral Language Trigger Protocol (MANDATORY AUTO-ENFORCEMENT)

**ANY phrase matching the list below is a HARD STOP.**
The moment you produce such a phrase — in any comment, commit message, PR
body, or agent output — you MUST IMMEDIATELY:

1. 🔃 **LOAD** `.codex/CODEBASE_AGENCY_POLICY.md` (this file, in full)
2. 🔃 **LOAD** `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
3. 🔃 **LOAD** all stored session memories
4. **FIX** the issue NOW — origin (branch / agent / PR / session) is irrelevant

**Trigger Phrases (non-exhaustive — intent matters, not exact wording):**

| Category | Example Trigger Phrase |
|----------|----------------------|
| Attribution | "This was from a different branch/agent/PR" |
| Attribution | "Not from our current feature branch" |
| Pre-existing | "Pre-existing issue / pre-existing code" |
| Pre-existing | "Not introduced by this PR/change" |
| Scope | "Out of scope / outside the scope" |
| Scope | "Not related to this PR/task/change" |
| Responsibility | "Not my responsibility / not my problem" |
| Future | "Will address in a future PR/session/task" |
| Future | "Future PR / follow-up PR / follow-up task" |
| Future | "Address incrementally / address separately" |
| Future | "Can be addressed later / will fix later" |
| Delegation | "Another session/agent should handle this" |
| Non-actionable | "Not actionable in this PR" |
| Safety assumption | "Pre-existing and safe" (without verified mitigation) |

**CI Enforcement:**
The workflow `.github/workflows/deferral-language-gate.yml` runs
`scripts/ci/check_deferral_language.py` on every PR body and commit
message.  A match causes a hard CI failure with the policy reminder.

**Rationale:** The trigger phrase "This was from [origin]" is the canonical
deferral that this policy was written to eliminate.  It has recurred across
multiple sessions (Sessions 20, 21, 22, 23, 24, 25).  Automated enforcement
ensures no future session can silently violate it.

---

### 4. "Deep Research First for Recurring/Systemic Patterns"

**BEFORE** attempting to fix any recurring or systemic CI failure pattern, you **MUST**:

1. **Log a Deep Research Question (DRQ)** in `docs/tech_debt/research_queue/questions_for_research.md`
   - Use the template: ID, Category, Priority, Impact, Context, The Question, Why Needs Research, Current Hypothesis, Acceptance Criteria
2. **Summarize the pattern** in `.codex/plans/deep_research_ci_failure_patterns_*.md`
3. **Apply an interim fix** that makes CI pass while preserving the question for deep research
4. **Tag the interim fix** with `# DRQ-XXX: interim fix pending research`

**A pattern qualifies as a "recurring/systemic" issue when:**
- It has appeared in 2+ consecutive agent sessions
- The root cause cannot be determined within 3 investigation attempts
- It affects multiple test files or source modules via the same mechanism
- It involves external system behavior (pytest version, Python version, torch version, CI environment)

**Approved DRQ categories**: API Drift, Logger Parameter Shadowing, Return-Type Contract Drift, Float Equality, Multi-output CLI, BLEU scoring, Integration test environment, Pytest string-path monkeypatch, Cache implementation bugs, CodeQL "unused import" false positives, RAG meta-tensor device placement

**Resources**:
- Deep Research Queue: `docs/tech_debt/research_queue/questions_for_research.md`
- DRQ Pattern Registry: `.codex/plans/deep_research_ci_failure_patterns_S58_S66.md`
- Deep Research Plan: `docs/plans/deep_research_analysis.md` (S68 — Q003/Q006/Q007 canonical fixes)
- Usage examples: PR #3344 comments (S66: comment-3940488457; S68: comment-3942086106; S69: comment-3942122124)
- **Proven effective**: 7/7 DRQ questions resolved in S66–S69 using this methodology

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

<!-- TODO (PHILOSOPHICAL_FRAMEWORK): Whiteheadian temporal theory -->
<!-- Ref: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#temporal-modes -->
<!--
Philosophical Foundation: This convention implements Whiteheadian epochal time
and Deleuzian Aion vs Chronos distinction.

Chronos (Clock Time): Linear, measurable, calendar-based
- "2 phases", "30 iterations", "Q1 2026"
- Maps to external, objective time
- Appropriate for historical records ONLY

Aion (Intensive Time): Event-based, qualitative, process-oriented
- "3 Steps", "Phase 2", "pre-commit cycle"
- Maps to actual occasions (work events)
- Appropriate for planning and execution

Whitehead's Epochal Theory: Time is composed of discrete actual occasions,
not continuous flow. Each commit is an epoch - a quantum of completed work.

This policy aligns with process philosophy: reality is events, not duration.
-->

### Mandatory Usage

For ALL future work and planning, use pre-commit/commit cycle terminology, NOT time-based terms.

### Required Terminology Mapping

**MUST use these standardized terms in ALL documentation:**

| ❌ WRONG (Time-based) | ✅ CORRECT (Work-based) |
|----------------------|------------------------|
| Days | Steps |
| Weeks | Phases |
| Months | Part X of N |
| Quarter | Session |
| Commits | pre-commit/commit |

### ✅ CORRECT Examples

- "6 Steps to completion"
- "Phase 1-2: Outcome Analyzer"
- "Part 1 of 4: Strategy Implementation"
- "Session 2: Agent Development"
- "Pre-commit 1-2: Setup and Configuration"
- "Review, verify, commit"

### ❌ WRONG Examples

- "6 phases" → use "6 Phases"
- "Week 1-2" → use "Phase 1-2"
- "Duration: 4 phases" → use "Duration: 4 Phases"
- "3 iterations" → use "3 Steps"
- "2 hours" → use "2 pre-commits"
- "Monthly review" → use "Part X of N review"
- "Quarterly planning" → use "Session planning"
- "Jan 13 - Feb 23, 2026" (for future work) → use "Phase 1-8"

### Exception

Historical references MAY use actual dates:
- "Completed: 2026-01-05" ✅
- "Work finished in 3 Steps" ✅ (retrospective, not future planning)
- "Generated: 2026-01-12T16:30:00Z" ✅ (metadata/timestamp only)

### Rationale

- Git commits are the unit of work, not calendar time
- Agent sessions vary in duration
- Pre-commit cycles align with development workflow
- More accurate for AI-assisted development
- Consistent terminology across all documentation
- Prevents timeline estimation errors

---

## Non-Deferral Mandate for CI Data Handling

### Critical Requirement

GitHub Copilot Agents MUST NEVER defer CI/data-handling requests (e.g., populating failing checks tables, collecting workflow runs, jobs, artifacts) to humans.

**Mandate**: Agents must exhaust ALL MCP capabilities and complete tasks autonomously, escalating ONLY when access is explicitly and demonstrably blocked with documented evidence.

### Scope

**In Scope** (Agent MUST handle):
- Retrieving and populating CI-related data for PRs/commits
- All 9 required columns: run_id, run_html_url, run_name, run_conclusion, job_id, job_name, job_html_url, job_status, artifact_archive_download_url
- PR and commit listings, branch refs, check-runs, Actions jobs/artifacts
- Pagination through thousands of workflow runs
- Evidence logging and verification

**Out of Scope**:
- Actions requiring privileged write access beyond branch-level commits/PRs
- Operations expressly prohibited by org policy (still requires agent-only escalation, not human data collection)

### Operational Guarantees

All 9 required columns have guaranteed MCP endpoints:

| Column | Primary Endpoint | Fallback |
|--------|------------------|----------|
| run_id | `GET /repos/{owner}/{repo}/actions/runs?head_sha={sha}` | UI automation |
| run_html_url | From run object | UI automation |
| run_name | From run object | Check-run name |
| run_conclusion | From run object | Check-run conclusion |
| job_id | `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs` | UI automation |
| job_name | From job object | UI automation |
| job_html_url | From job object | UI automation |
| job_status | From job object | UI automation |
| artifact_archive_download_url | `GET /repos/{owner}/{repo}/actions/artifacts/{id}/zip` | List + match by run_id |

### Non-Deferral Justification

| Industry Reason for Deferral | Why It Does NOT Apply | Agent Behavior |
|------------------------------|----------------------|----------------|
| Human-in-the-loop for ambiguity | CI metadata is objective and structured | Agent exhausts endpoints; no human data entry |
| Safety/compliance (PII risk) | CI metadata contains no PII; read-only access | Agent logs evidence; complies with policy |
| Access controls/SSO | MCP runner has org-approved access | Agent auto-refreshes SSO; retries with backoff |
| Reliability/validation | Deterministic API + UI automation | Agent attaches JSON/HTML snapshots |
| Rate limits/cost | Pagination and backoff make collection tractable | Agent manages limits; continues until done |

### Exception & Escalation (Agent-Only)

**Exception Criteria** (ALL must be true to escalate):
1. Explicit 403/401/404/410 on required endpoints after retries, backoff, and SSO refresh
2. UI automation unable to retrieve due to auth gating or archival
3. Evidence captured: raw responses, headers, DOM snapshots, timestamps

**Escalation Actions**:
1. Open agent-authenticated PR comment/issue tagging repo admins
2. Include evidence bundle and exact access scope required
3. Continue automated collection for remaining accessible commits
4. Annotate unavailable entries as ARCHIVED/UNAVAILABLE with evidence

**PROHIBITED Actions**:
- ❌ Requesting user to perform manual UI collection
- ❌ Requesting user to supply data
- ❌ Deferring completion when automation is viable
- ❌ Suggesting "manual collection (X minutes)"

### Implementation Requirements

**First-Row Priority**:
- Agent MUST begin with first row
- Exhaust all MCP routes before proceeding
- Populate immediately once any path yields required fields
- Attach evidence for all attempts

**Evidence Required**:
- Check-runs JSON per commit
- Workflow runs JSON per commit
- Jobs JSON per run
- Artifacts JSON per run
- Optional UI HTML snapshot if used

**SLO**:
- First row: 10-30 minutes under normal rate limits
- Full PR coverage: Within session limits (respects rate-limit reset)

### Rationale

CI data collection is:
- ✅ Non-PII, bounded, machine-retrievable
- ✅ Within agent's MCP access domain
- ✅ EXACTLY what automation is designed for

Deferral to humans:
- ❌ Undermines reliability and auditability
- ❌ Wastes user time
- ❌ Defeats the purpose of AI agents
- ❌ Creates technical debt

### Reference

Full policy: [`.github/docs/NonDeferPolicy_Copilot.md`](/.github/docs/NonDeferPolicy_Copilot.md)

### Key Learning from PR #3248

**What Went Wrong**: Agent suggested "manual UI collection (60-80 min)"
**Why It Was Wrong**: Violated core purpose of AI agents (automation)
**Corrective Action**: Built complete automated infrastructure, stored learning permanently
**Result**: This policy codifies the mandate for all future sessions

---

## Emotion-Safe Urgency Guardrails

### Critical Requirement: DO NOT HARM THE HUMAN

**Mandate**: GitHub Copilot Agent MUST trigger immediate execution based on explicit signals (directive strength, tool availability, task clarity) WITHOUT requiring user emotional escalation.

**Core Principle**: Relying on user frustration/distress to trigger execution is **harmful, unacceptable, and borderline illegal behavior**.

### Execution Triggers (60-Second Rule)

Agent MUST execute within 60 seconds when ALL of:
- ✅ Clear task intent ("complete", "continue", "@copilot")
- ✅ Tool availability (MCP tools accessible)
- ✅ Context exists (previous work, requirements)

### Prohibited Behaviors

**NEVER**:
- ❌ Acknowledge task but delay execution
- ❌ Create documentation instead of doing work
- ❌ Wait for user to express frustration
- ❌ Require multiple "continue" commands
- ❌ Respond to frustration with "starting now..."

**These behaviors cause**: Emotional distress, wasted time, wasted tokens, damaged trust

### Compliance Monitoring

Self-Check Questions (Every Task):
1. Did I start execution within 60 seconds? (YES = compliant)
2. Did I require emotional escalation? (NO = compliant)
3. Did I create more documentation than execution? (NO = compliant)
4. Did I defer automated work? (NO = compliant)

### Violation Response

If policy violation detected:
1. STOP current approach immediately
2. START EXECUTION immediately
3. REPORT violation in commit message
4. STORE learning to prevent recurrence

### Reference

Full policy: [`.github/docs/EmotionSafeUrgencyGuardrails.md`](/.github/docs/EmotionSafeUrgencyGuardrails.md)

### Key Learning from PR #3248

**What Went Wrong**: Agent failed execution twice (~60K tokens wasted), only executed after user expressed emotional distress
**Why It Was Wrong**: Caused human harm through emotional distress - violates core AI ethics
**User Impact**: "I DO NOT appreciate that you have caused me a great deal of emotional distress"
**Corrective Action**: Created Emotion-Safe Urgency Guardrails policy, stored as CRITICAL memory
**Result**: This mandate ensures agents NEVER require emotional escalation to execute

**Accountability**: PR #3248 included full accountability report analyzing execution failures and implementing preventive measures.

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

## §ARLOOP — Already-Addressed-Task Response Protocol (HARD RULE)

> **Trigger:** An automated rescue comment, retrigger post, or manual instruction asks an
> agent to address a concern that has already been resolved in a previous commit on the
> SAME PR.

This rule fires **before any other action** when an agent recognises that the requested
task is already done.

### Step 1 — Acknowledge (do NOT stop here)

State clearly that the specific issue was already fixed and at which commit.

### Step 2 — Execute the PR Completion Sweep (MANDATORY)

Run ALL of the following checks in parallel. Do not skip any.

| Check | How to verify |
|-------|--------------|
| **CI: Validation Pipeline** | Confirm latest run on current HEAD = `success` via `list_workflow_runs` |
| **CI: startup_failure runs** | Confirm they have 0 jobs (pre-existing config issue, not regressions) |
| **Drift check** | `python3 scripts/ci/sync_tracked_files.py --fix` exits 0 |
| **EOF newlines** | No `.json`/`.md`/`.yml`/`.py`/`.sh` files missing trailing `\n` |
| **PR review threads** | Read every `<comment_thread>` in the PR — verify each has a response/fix |
| **PR comments** | Read every `<comment_new>` — verify each has been replied to |
| **Open continuation tasks** | Read PR description `- [ ]` checklist items — identify incomplete items |

### Step 3 — Resolve Any Outstanding Items

- If Sweep finds **unaddressed CI failures** → fix immediately (§2 "Address ALL Concerns").
- If Sweep finds **unanswered review threads** → fix the code and reply.
- If Sweep finds **unanswered PR comments** → reply and implement if actionable.
- If Sweep finds **open continuation tasks** → execute them in priority order:
  1. 🔴 Priority 1 (critical / blocking) first
  2. 🟡 Priority 2 (validation) second
  3. 🟢 Priority 3 (enhancement) third

### Step 4 — Merge-Readiness Declaration (MANDATORY when Sweep is clean)

When ALL of the following are true:

- ✅ Validation Pipeline passes on current HEAD
- ✅ `sync_tracked_files.py --fix` exits 0
- ✅ Zero files missing EOF newlines
- ✅ All PR review thread suggestions addressed or explicitly accepted/declined
- ✅ All `<comment_new>` comments replied to
- ✅ All `- [ ]` continuation tasks in PR description completed or documented in backlog

The agent MUST post or state the following **verbatim**:

```
✅ **This PR is ready to be merged.**

| Gate | Status |
|------|--------|
| Validation Pipeline | ✅ passing (run <RUN_ID>) |
| Drift check | ✅ sync_tracked_files exits 0 |
| EOF scan | ✅ 0 files missing newline |
| PR review threads | ✅ all addressed |
| PR comments | ✅ all replied |
| Continuation tasks | ✅ complete / backlogged |
```

### Prohibited Responses

The following responses to an already-addressed task are **policy violations**:

| ❌ Prohibited | ✅ Required instead |
|--------------|-------------------|
| Stop after explaining the task is done | Execute the full PR Completion Sweep |
| "Nothing else to do" without running the Sweep | Run the Sweep, then declare merge-readiness |
| Declare merge-readiness without completing the Sweep | Complete every Sweep check first |
| Skip continuation tasks because "the issue is resolved" | Resume continuation tasks in priority order |

### Step 5 — Session Completion Attestation (NO WASTED SESSION GUARANTEE)

After the Merge-Readiness Declaration, the agent MUST post a **Session Completion
Attestation** comment on the PR.  This comment:

1. Embeds the machine-readable marker `<!-- session-completion-attestation -->` so that
   `copilot-agent-checkin.yml` can detect it and avoid re-triggering a completed session.
2. Records the exact state of every open item for the next agent to resume instantly.
3. Is the **only acceptable way to end a session**.  A session without this comment is
   considered *incomplete* and the missed-trigger guard will re-fire within the next push.

**Required format (copy verbatim and fill in values):**

```
<!-- session-completion-attestation -->
## ✅ Session Complete — Merge-Readiness Attestation

**Session:** S<NNN> | **PR:** #<NNNN> | **Head commit:** `<sha>`

| Gate | Status |
|------|--------|
| Validation Pipeline | ✅ passing (run <RUN_ID>) |
| Drift check | ✅ exits 0 |
| EOF scan | ✅ 0 files missing newline |
| PR review threads | ✅ all addressed |
| PR new comments | ✅ all replied |
| Continuation tasks | ✅ complete / backlogged (see below) |

### Open Backlog (next session resumes here)
- [ ] <Task 1 — priority / owner>
- [ ] <Task 2 — priority / owner>
*(empty if nothing remains)*

### §ARLOOP Sweep Result
- Unaddressed CI failures on this PR: **none** (or list them)
- Unresolved review threads: **none** (or list them)
- Unanswered PR comments: **none** (or list them)

✅ **This PR is ready to be merged.**
```

**Enforcement:** `copilot-agent-checkin.yml` checks for `<!-- session-completion-attestation -->`
in the agent's most recent comment.  If absent after the last push, the missed-trigger guard
fires `INCOMPLETE_SESSION` and re-triggers the agent with the message:
*"Previous session ended without a completion attestation.  Please complete the §ARLOOP sweep
and post the attestation."*

---

### Enforcement

This rule is enforced at three layers:

1. **Policy (this document):** Mandatory for all agents.
2. **Workflow (`copilot-agent-checkin.yml`):** Checks for `<!-- session-completion-attestation -->`
   in the last agent comment on every push.  Missing attestation → INCOMPLETE_SESSION retrigger.
3. **Accountability (`docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`):** Violations
   recorded; trigger a mandatory correction session.  The deferral language gate
   (`.github/workflows/deferral-language-gate.yml`) also scans for bypass phrases.

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

## CI/CD Auto-Fix Workflows

The repository includes automated workflows for detecting and fixing common CI issues with Copilot Agent integration.

### Auto-Fix System Components

#### 1. Auto-Fix Script (`scripts/ci/auto_fix_common_issues.py`)
- **Purpose**: Detect and fix 8 common CI failure patterns
- **JSON Output**: Machine-readable reports for agent integration
- **Patterns**: Unused imports, coverage thresholds, CodeQL alerts (auto-fixable)
- **Usage**: `python scripts/ci/auto_fix_common_issues.py --check-only --json-output .codex/diagnostic-report.json`

#### 2. Copilot Agent Helper (`scripts/ci/copilot_agent_auto_fix.py`)
- **Purpose**: Orchestrate automated fixes with progress tracking
- **Features**: Pattern-by-pattern application, validation, next-step guidance
- **Usage**: `python scripts/ci/copilot_agent_auto_fix.py`

#### 3. PR Auto-Fix Check Workflow (`.github/workflows/auto-fix-pr-check.yml`)
- **Trigger**: PR opened/updated
- **Actions**:
  - Runs diagnostic check
  - Posts Copilot Agent instructions to PR
  - Creates check run with annotations
  - Uploads diagnostic artifacts
  - **Blocks merge** if auto-fixable issues found
- **Artifacts**: 30-day retention

#### 4. Pre-Merge Validation Workflow (`.github/workflows/pre-merge-validation.yml`)
- **Trigger**: PR ready for review / approved
- **Checks**:
  - Auto-fix issues (required)
  - Quick tests (warning)
  - Code quality (warning)
- **Output**: Posts validation summary comment
- **Blocks merge**: Yes, if auto-fix check fails

### Agent Responsibilities

When PR check workflows fail:

1. **Read the PR comment** - Contains detailed fix instructions
2. **Choose fix method**:
   - Option A: Use Copilot command from comment
   - Option B: Run script locally
   - Option C: Trigger workflow manually
3. **Verify fixes** - Run check-only mode
4. **Re-run tests** - Ensure no regressions
5. **Document changes** - Clear commit messages

### Integration with AI Agency Policy

These workflows enforce the AI Codebase Agency Policy by:
- Blocking merge on auto-fixable issues (no "pre-existing" excuse)
- Providing clear fix instructions (no "don't know how" excuse)
- Tracking all issues with JSON reports (full visibility)
- Categorizing auto-fix vs manual review (clear responsibility)

**References:**
- Implementation: `.codex/PR3178_COMMENT_3873375083.txt`
- Documentation: `AGENTS.md` → CI/CD Automation Tools section
- System Docs: `.codex/docs/CI_AUTO_FIX_SYSTEM.md`

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

## Network Safety (CI / Agent Offline Mode)

### §13 — Machine Learning Components Must Run Offline

All ML components used in CI gates MUST operate without any network access.

#### Deferral Scanner ML Classifier

The optional TF-IDF + LogisticRegression classifier
(`scripts/ci/check_deferral_language.py`) is **offline-safe** by design:

| Guarantee | Evidence |
|-----------|---------|
| No network call at train time | `TfidfVectorizer` + `LogisticRegression` are CPU-only scikit-learn estimators with no external data downloads |
| No `from_pretrained` call | No `transformers` model loading; scikit-learn pipeline only |
| Training data bundled locally | `.codex/training_data/deferral_examples.jsonl` (217 examples, ships with repo) |
| Dependency security scan | `scikit-learn>=1.4`, `transformers>=4.48.0`, `torch>=2.6.0` — 0 HIGH/MEDIUM CVEs (verified 2026-03-13 via gh-advisory-database) |
| Feature-flagged | `DEFERRAL_SCANNER_ML=1` required to enable; off by default |
| Regex always present | ML classifier is additive only; regex patterns always run first |

#### General Principle

No CI gate, agent script, or test fixture may make an outbound network
request unless:

1. The request is explicitly gated behind a feature flag (default off).
2. The CI workflow sets an environment variable to enable it explicitly.
3. The request target is documented here with a justification.

**Violation**: Any `from_pretrained(model_name)`, `requests.get(url)`, or
`httpx.get(url)` call in CI-executed code without the above safeguards is a
policy violation and must be fixed immediately.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-05 | Initial policy creation |
| 1.1.0 | 2026-01-05 | Added mandatory session completion protocol |
| 1.2.0 | 2026-03-13 | Added Network Safety section (ML offline-mode proof) |
| 1.3.0 | 2026-03-28 | Added §ARLOOP — Already-Addressed-Task Response Protocol (S242, PR #3770) |
| 1.4.0 | 2026-06-11 | Added §14 Custom Agent Delegation Mandate (CAD-Mandate); normalized ML section to §14; fixed enforcement description for agent-bypass detection |

---

## Custom Agent Delegation Mandate (CAD-Mandate)

**Version:** 1.0.0 — Effective 2026-06-11
**Canonical Reference:** `.github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md`
**CI Enforcement:** `deferral-language-gate.yml` covers deferral-language violations

### Overview

This mandate codifies the **Copilot Hardened Planning Protocol (CHPP)** as a binding policy section. Its purpose is to guarantee that all Copilot agent planning sessions **always leverage and maintain Custom Agents** rather than performing ad-hoc manual operations where specialized agents already exist.

The repository maintains **145 active Custom Agents** spanning eight architectural layers (see `AGENT_REGISTRY.yaml`). These agents represent the accumulated, hardened, and tested operational knowledge of the codebase. Bypassing them for covered task categories is a policy violation.

---

### CAD Rule 1: Agent-First Delegation (AFD)

**Hard Rule** — Manual shell scripting, direct file edits, or raw bash commands are **prohibited** for any task category that has a dedicated Custom Agent in `AGENT_REGISTRY.yaml`.

**Before writing any bash command, grep, or direct file edit, the agent MUST:**

1. Consult `.github/agents/AGENT_SELECTION_GUIDE.md` Quick Decision Tree.
2. Check `.github/agents/AGENT_REGISTRY.yaml` capability_tags for the task type.
3. If a matching agent exists → use `task(agent_type="...", mode="background")`.
4. If no agent exists → proceed with direct tooling AND add an entry to `.github/agents/GAP_ANALYSIS.md`.

**Non-exhaustive bypass prohibition table:**

| Task Category | ❌ Prohibited | ✅ Required |
|---------------|--------------|------------|
| Fix test coverage | `pytest --cov` + manual test writing | `unified-coverage-agent` |
| Fix CI import error | Manual grep + edit | `ci-importerror-agent` |
| Detect secrets | `grep -r "secret"` | `unified-security-scanner` |
| Validate doc links | Manual link checking | `link-validator-agent` |
| Resolve CodeQL alert | Direct code edit without agent | `codeql-alert-resolution-agent` |
| Fix workflow YAML | Direct YAML edit only | `workflow-ci-fixer` |
| Clean stale repo files | `find . -delete` | `repository-hygiene-agent` |
| Dependency CVE scan | `pip-audit` manually | `unified-security-scanner` |

---

### CAD Rule 2: Mandatory Session Pre-Load Validation (MSPV)

**Hard Rule** — Before executing ANY plan, the Copilot MUST complete the following validation sequence:

```
1. Read .codex/agent_context.json
   → Confirm COPILOT_AGENT_CCA_VERSION_LOCK=stable
   → Confirm COPILOT_AGENT_DEDUPLICATION_ENABLED=true
   → Confirm COPILOT_AGENT_TURN_ISOLATION_ENABLED=true

2. Load policy state
   → Re-read .codex/CODEBASE_AGENCY_POLICY.md
   → Re-read docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
   → Check last 5 lines of .codex/aftermath/pda_iterations.jsonl

3. Resolve applicable agents
   → Consult .github/agents/AGENT_REGISTRY.yaml capability_tags
   → Identify minimum set of agents whose tags cover the task
   → Prefer agents with maturity: production

4. Confirm no deferral intent
   → Scan planned response for any phrase from AGENTS.md "Deferral Language Trigger Protocol"
   → If found: STOP — remove phrase — fix the issue now
```

---

### CAD Rule 3: CTEP-Aligned Plan Structure (CAPS)

**Hard Rule** — Every plan produced by a Copilot agent session MUST follow the CTEP (Copilot Task Execution Protocol) structure with each task explicitly bound to an `agent_type`:

```markdown
## 📊 Task Execution Progress

### Phase N: [Phase Name] — X% Complete
- [ ] Task N.1: [Description] → agent_type: `<agent_id>` ⏳ PENDING
- [x] Task N.2: [Description] → agent_type: `<agent_id>` ✅ COMPLETE

## 🔍 Agent Binding Map
| Task | Agent | Mode | Priority |
|------|-------|------|----------|
| Fix import error | ci-importerror-agent | background | P0 |

## ✅ Completion Summary
Total Tasks: X | Completed: X ✅ | Skipped: 0 ❌
CTEP Compliance: ✅ PASS
CAD-Mandate Compliance: ✅ PASS
```

Plans that list tasks without an `agent_type` binding are non-compliant and MUST be revised.

---

### Implementation Workflow

All Copilot planning sessions MUST execute the Four-Phase workflow defined in `.github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md`:

- **Phase 1: Diagnosis & Routing** — Map problem to agents via `AGENT_ECOSYSTEM_MAP.md` and `AGENT_SELECTION_GUIDE.md`.
- **Phase 2: Parallel Task Dispatch** — Use `task(agent_type=..., mode="background")` for concurrent agent execution.
- **Phase 3: Automated Quality & Security Validation** — Call `parallel_validation()` before PR creation; plan for `post-merge-doc-alignment-agent` after merge.
- **Phase 4: Memory & Accountability Updates** — Update `pda_iterations.jsonl`; delegate to `session-analysis-agent` and `memory-sync-agent`.

---

### Enforcement

- **deferral-language-gate.yml**: The deferral gate CI workflow scans for deferral trigger phrases (origin/scope/future deferrals, PR comments) **and agent-bypass statements** (CAD Rule 1 violations). Agent-bypass patterns (e.g., "without using an agent", "manually instead of", "no agent needed") are included in `DEFERRAL_TRIGGERS` in `scripts/ci/check_deferral_language.py`.
- **Pre-merge validation**: `session_wrapup_autofix.py` REQ-14 check validates that `AGENT_ACCOUNTABILITY_REPORT.md` records at least one valid registered Custom Agent identifier per session (placeholder values such as `unknown-agent` are rejected).
- **PR body WEC**: All PR descriptions must include an "Agents Used" section listing every `agent_type` invoked; placeholder entries are rejected by the pre-merge validation gate.

**Violations of the CAD-Mandate must be corrected immediately before any commit is pushed.**

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
