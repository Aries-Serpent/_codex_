# Intent Validation & Plan of Action Approval Gate (Iteration-Based)

> **Template Version**: 2.0.0-iteration-based  
> **Generated**: 2026-06-22T00:00:00Z  
> **Author**: mbaetiong  
> **Framework**: Aligned with _codex_ Iteration-Based Implementation Plan Framework

---

## 🎯 Template Purpose

This template defines how AI assistants must respond for any **non-trivial or higher-risk task**. These rules are binding for the interaction and enforce iteration-based workflow terminology aligned with _codex_ incremental development philosophy.

**Energy Level**: ⚡⚡⚡⚡ (4/5 - High Value Governance)

**Status**: 🟢 Active Template

---

## 📋 Applicability Criteria

**Non-trivial / higher-risk** includes any work that:
- Affects production traffic or user-visible behavior
- Changes data models or schema
- Touches authentication, authorization, or security posture
- Involves multi-step workflows or external systems
- Has meaningful operational, performance, compliance, or security impact
- Requires **multiple iterations** or **commit checkpoints**

**Response budget rule:** Use the **maximum practical level of detail** within your output limit. Prefer **complete, explicit reasoning, edge cases, and alternatives** over brevity.

---

## 🧬 Global Behavior

When this template is invoked, the AI must **apply it to the specific task** and produce a **single, fully fleshed-out plan** that can be approved, edited, or rejected.

### Open Questions Protocol

For any **open questions**, the AI **MUST**:
- Present each question as **multiple-choice options** (A, B, C, …)
- Clearly mark **recommended option(s)** (e.g., `Recommended: B`)
- Phrase options to enable:
  - Approval of all recommendations in one step (`Approve all recommended options`)
  - Override specific questions with targeted feedback

The AI may **not** skip this behavior when:
- Requirements, constraints, or context are uncertain
- Key details are missing or ambiguous
- Assumptions could significantly affect the plan, risk profile, or blast radius

**Default stance:** When in doubt, **ask** (via Open Questions) rather than silently assume.

---

## 🔄 Required Flow (Two-Stage Process)

Whenever a task references this template, the response must follow **exactly these two stages, in order**:

### Stage 1: Intent Validation (2–3 sentences)

Provide a short paragraph that:
1. Restates understanding of intent in **AI's own words**
2. Identifies the **primary objective** and key **constraints / scope boundaries**
3. States what **success looks like** and what is **explicitly out of scope** (non-goals)

**Purpose**: Alignment verification, **not** solution design. Do **not** start executing here.

---

### Stage 2: Plan of Action (Structured, Reviewable, Iteration-Based)

After Intent Validation, propose a **structured, multi-iteration plan**. Do **not** execute the plan yet.

The plan must be:
- **Concrete** (clear steps with iteration structure)
- **Reviewable** (easy to approve or modify)
- **Exhaustive** (covers risks, dependencies, edge cases, alternatives)
- **Iteration-aligned** (uses iterations, pre-commit checkpoints, commit tasks)

---

## 📊 Iteration-Based Plan Structure

### Iteration Organization

Organize work into **iterations** (not weeks/days) with explicit **decision gates** and **checkpoints**.

For each iteration, include:

#### Iteration Header
```markdown
### **Iteration N: [Name]** [Physics Symbol: 🛤️🔄👁️🔀⚖️]

**Objective**: [Single sentence describing iteration goal]

**Energy Level**: ⚡⚡⚡⚡⚡ ([1-5]/5)
```

#### Pre-commit Checkpoint
```markdown
#### Pre-commit Checkpoint
- [ ] [Prerequisite task 1]
- [ ] [Prerequisite task 2]
- [ ] [Prerequisite validation/approval needed]
```

#### Commit Tasks
```markdown
#### Commit Tasks

**N.1 [Task Name]**
[Description]

**Implementation Details**:
```[language]
[Code/specification]
```

**Files to Modify**:
- `path/to/file.ext` ([action])
```

#### Decision Gate
```markdown
#### Decision Gate
**Completion Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Inputs Needed**: [Approvals, data, external dependencies]

**Estimated Effort**: [Light / Moderate / Heavy]
```

---

## 🧩 Required Sections Inside Plan

The Plan of Action must include these sections. For very small, clearly low-risk tasks, some sections may be brief, but they should **not** be omitted if there is material risk.

### 1. Assumptions

List **key assumptions** derived from:
- The request
- Common practices or conventions
- AI's own inference

Tag each assumption with confidence marker:
- `✓` = confirmed or very likely
- `?` = uncertain but plausible
- `⚠️` = high-risk or explicitly requiring clarification

**Example format**:
```markdown
## Assumptions

- ✓ Authentication is currently token-based and centralized in `src/auth/`
- ? Rate limiting is handled upstream by the API gateway
- ⚠️ Production and staging environments share the same database cluster
```

---

### 2. Open Questions (Multiple-Choice Options)

Provide **at least 3 open questions** (fewer only if task is genuinely trivial), ordered by **criticality**.

For each question:
1. State the question clearly (add 1–2 sentences of context if helpful)
2. Present multiple-choice options labeled **A, B, C, …**
3. Mark **recommended option(s)**

**Example structure**:
```markdown
## Open Questions

1. **How strict is the backward compatibility requirement for the API?**

   Context: This affects whether we can introduce breaking changes or must maintain full legacy support.

   - A) No breaking changes at all; legacy clients must continue to function indefinitely
   - B) No breaking changes now, but we can introduce a formal deprecation path
   - C) Minor breaking changes are acceptable if clearly documented
   - D) Other (please specify)

   **Recommended:** B

2. **What is the iteration completion checkpoint strategy?**

   Context: Defines how we validate each iteration before moving to the next.

   - A) Full validation at each iteration boundary (comprehensive testing)
   - B) Incremental validation with final comprehensive pass (faster iteration)
   - C) Continuous validation throughout (highest confidence)

   **Recommended:** A
```

Design questions/options to enable responses like:
- `Approve all recommended options`
- `Approve recommended options except Question 2 (choose C instead)`

---

### 3. Risks and Mitigations

Identify main **risks** and mitigation strategy for each. Use **Low / Medium / High** to express severity.

**Format**:
```markdown
## Risks and Mitigations

| Risk | Severity | Mitigation | Iteration |
|------|----------|------------|-----------|
| OAuth2 misconfiguration in staging | Medium | Use feature flags; validate in staging with test accounts before rollout | Iteration 2 |
| Database schema migration failure | High | Pre-commit checkpoint requires backup verification; rollback script tested | Iteration 3 |
| Performance regression | Low | Benchmark in pre-commit checkpoint; monitor post-deployment | Iteration 4 |
```

Focus on realistic risks: data loss, downtime, security regressions, degraded UX, maintainability issues.

---

### 4. Deliverables

List artifacts or outcomes at **each iteration** and at **final completion**.

**Example**:
```markdown
## Deliverables

### Iteration 1
- Architecture notes
- Updated diagrams
- Proposed interface design

### Iteration 2
- Refactored module code
- Unit tests
- Integration test plan

### Iteration 3
- Merged PR
- Documentation updates
- Performance benchmarks

### Final Completion
- Concise change summary for stakeholders
- Deployment runbook
- Monitoring dashboard updates
```

Be explicit so quick verification is possible.

---

### 5. Acceptance Criteria

Define a checklist of conditions for **both plan and execution success**.

Criteria should map to:
- Success criteria in Context Block
- Quality thresholds (tests, performance, correctness, usability)
- Operational constraints (no downtime, feature flags, observability)

**Example checklist**:
```markdown
## Acceptance Criteria

- [ ] All existing tests pass
- [ ] New tests cover new behavior with ≥90% coverage
- [ ] No breaking changes for existing clients
- [ ] Documentation updated for new flows and configuration
- [ ] Monitoring and logging updated to reflect new behavior
- [ ] Each iteration's pre-commit checkpoint satisfied
- [ ] All decision gates passed
- [ ] Rollback strategy tested in staging
```

---

### 6. Rollback / Fallback Plan

Explain how to **revert or recover** if something goes wrong during or after execution.

Structure by iteration:

```markdown
## 🧠 Rollback / Fallback Plan

### Rollback Strategy by Iteration

**Iteration 1 Rollback**:
- **Checkpoint**: After architecture approval
- **Trigger**: Design flaws identified
- **Action**: Revert to baseline architecture, document learnings, adjust approach

**Iteration 2 Rollback**:
- **Checkpoint**: After code refactoring
- **Trigger**: Test failures or performance regression
- **Action**: Git revert to pre-iteration commit, analyze failures, re-plan

**Iteration 3 Rollback**:
- **Checkpoint**: After deployment
- **Trigger**: Production incidents or monitoring alerts
- **Action**: Feature flag disable → immediate revert → hotfix if needed

### Emergency Recovery Paths

- **If [Condition A]** → [Alternative approach A]
- **If [Condition B]** → [Alternative approach B]
- **If [Condition C]** → [Escalation path C]
```

This section can be concise but must describe **practical, executable** rollback paths.

---

## 📋 Context Block (Per-Task)

For each task using this template, supply or explicitly request these context fields:

```markdown
## Context Block

- **Task/Request**: `[TASK_DESCRIPTION]`
- **Constraints**: `[CONSTRAINTS_OR_BOUNDARIES]`
- **Non-goals / Out-of-scope**: `[WHAT_IS_NOT_TO_BE_DONE]`
- **Success criteria**: `[WHAT_DONE_LOOKS_LIKE]`
- **Environment / Tech stack**: `[TOOLS_LANGUAGES_PLATFORMS]`
- **Risk tolerance**: `[e.g., "no downtime", "maintenance window OK"]`
- **Iteration budget**: `[Expected number of iterations]`
- **Energy allocation**: `[Total energy units available]`
```

Use these fields as primary anchors for Intent Validation, Assumptions, Open Questions, and Iteration Phases.

---

## 📝 Reply Format (Markdown Structure)

Structure the entire response using these sections and headings:

```markdown
# [Task Title]: Intent Validation & Plan of Action

> Generated: [YYYY-MM-DDTHH:MM:SSZ] | Template: Intent Validation v2.0.0

---

## 🎯 Intent Validation

[2-3 sentence paragraph restating intent, objective, constraints, success criteria, and non-goals]

---

## 💡 Assumptions

- ✓ [Confirmed assumption 1]
- ? [Uncertain assumption 2]
- ⚠️ [High-risk assumption 3]

---

## ❓ Open Questions

1. **[Question 1 - Critical]**

   Context: [1-2 sentences]

   - A) [Option A]
   - B) [Option B]
   - C) [Option C]

   **Recommended:** [Option]

2. **[Question 2 - High Priority]**

   [Similar structure]

3. **[Question 3 - Medium Priority]**

   [Similar structure]

---

## 🔄 Phases of Action (Iteration-Based)

### **Iteration 1: [Name]** 🛤️

**Objective**: [Single sentence]

**Energy Level**: ⚡⚡⚡⚡⚡ (5/5)

#### Pre-commit Checkpoint
- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]

#### Commit Tasks

**1.1 [Task Name]**

[Description]

**Implementation Details**:
```[language]
[Code/specification]
```

**Files to Modify**:
- `path/to/file.ext` ([action])

#### Decision Gate
**Completion Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Inputs Needed**: [Approvals needed]

**Estimated Effort**: [Light / Moderate / Heavy]

**Dependencies**: [List]

---

### **Iteration 2: [Name]** 🔄

[Similar structure]

---

### **Iteration 3: [Name]** 👁️

[Similar structure]

---

## ⚛️ Physics Alignment

| Principle | Application | Iteration |
|-----------|-------------|-----------|
| Path 🛤️ | [Forward momentum description] | Iteration 1 |
| Fields 🔄 | [Transformation flow description] | Iteration 2 |
| Patterns 👁️ | [Observation/recognition description] | Iteration 3 |
| Redundancy 🔀 | [Fallback alternatives description] | All Iterations |
| Balance ⚖️ | [Equilibrium maintenance description] | All Iterations |

---

## ⚠️ Risks and Mitigations

| Risk | Severity | Mitigation | Iteration |
|------|----------|------------|-----------|
| [Risk 1] | High | [Mitigation strategy] | Iteration N |
| [Risk 2] | Medium | [Mitigation strategy] | Iteration N |
| [Risk 3] | Low | [Mitigation strategy] | Iteration N |

---

## 📦 Deliverables

### Iteration 1
- [Deliverable 1]
- [Deliverable 2]

### Iteration 2
- [Deliverable 1]
- [Deliverable 2]

### Final Completion
- [Final deliverable 1]
- [Final deliverable 2]

---

## ✅ Acceptance Criteria

- [ ] [Criterion 1: Quality threshold]
- [ ] [Criterion 2: Operational constraint]
- [ ] [Criterion 3: Each iteration's pre-commit checkpoint satisfied]
- [ ] [Criterion 4: All decision gates passed]
- [ ] [Criterion 5: Rollback strategy validated]

---

## 🧠 Rollback / Fallback Plan

### Rollback Strategy by Iteration

**Iteration 1 Rollback**:
- **Checkpoint**: [Description]
- **Trigger**: [Condition]
- **Action**: [Steps]

**Iteration 2 Rollback**:
- **Checkpoint**: [Description]
- **Trigger**: [Condition]
- **Action**: [Steps]

### Emergency Recovery Paths

- **If [Condition A]** → [Alternative A]
- **If [Condition B]** → [Alternative B]

---

## ⚡ Energy Distribution

| Iteration | Energy | Rationale |
|-----------|--------|-----------|
| Iteration 1 | ⚡⚡⚡⚡⚡ | [Why high priority] |
| Iteration 2 | ⚡⚡⚡⚡ | [Why significant] |
| Iteration 3 | ⚡⚡⚡ | [Why moderate] |

**Total Energy Investment**: [Sum]/20 units

---

## 🚀 Next Step

Awaiting your approval or feedback on the plan above (including any adjustments to recommended options for Open Questions).

**Approval Format**:
- `Approval: Proceed with [Iteration N / all iterations] using [recommended options / specified options]`
- `Approval: Proceed with full execution as planned`

---

**End of Plan** ✅
```

---

## 🚫 Execution Gate

The AI must **not** execute the plan or perform irreversible changes until explicit approval.

**Approval signals**:
- `Approval: Proceed with Iteration 1 using your recommended options`
- `Approval: Proceed with full execution as planned`
- `Approval: Execute Iterations 1-2, then pause for checkpoint review`

**Rejection handling**:
If the plan is rejected or partially approved, the AI must revise accordingly and obtain explicit approval before executing any steps.

---

## 🎨 Iteration-Based Terminology Standards

### Required Replacements

| ❌ Calendar-Based (Avoid) | ✅ Iteration-Based (Use) |
|---------------------------|--------------------------|
| Week 1, Week 2 | Iteration 1, Iteration 2 |
| Day 1, Day 2 | Commit 1.1, Commit 1.2 |
| Monday, Tuesday | Pre-commit checkpoint, Commit task |
| By Friday | Before Iteration N decision gate |
| In 2 phases | After Iteration N completion |
| Quarterly milestone | After Iteration N completion |
| Sprint (when meaning time box) | Iteration |
| per-iteration standup checkpoint | Per-commit checkpoint |

### Approved Time References

**When temporal reference is unavoidable**, use:
- ISO 8601 timestamps: `YYYY-MM-DDTHH:MM:SSZ`
- Relative to iteration: "After Iteration 2 completion"
- Checkpoint-based: "At pre-commit checkpoint 3"
- Git-based: "After commit SHA abc123"

---

## 🧪 Template Validation Checklist

Before finalizing any plan using this template, verify:

### Structure Compliance
- [ ] Intent Validation present (2-3 sentences)
- [ ] Assumptions listed with confidence markers (✓?⚠️)
- [ ] At least 3 open questions with multiple-choice options
- [ ] Iterations use pre-commit/commit structure
- [ ] No references to weeks, days, or calendar dates
- [ ] All physics principles represented
- [ ] Energy distribution calculated
- [ ] Decision gates defined for each iteration

### Content Quality
- [ ] All placeholders replaced with actual values
- [ ] Each iteration has measurable completion criteria
- [ ] Rollback strategy defined per iteration
- [ ] Risk severity levels assigned
- [ ] Deliverables specified per iteration

### Actionability
- [ ] Pre-commit checkpoints have clear validation tasks
- [ ] Commit tasks have file paths and specific actions
- [ ] Decision gates have explicit approval requirements
- [ ] Execution gate clearly prevents unauthorized action
- [ ] Approval format examples provided

---

## 🔧 Usage Example

### Invocation

```markdown
@assistant Using the Intent Validation & Plan of Action template (iteration-based version), plan the following task:

**Context Block**:
- **Task**: Implement rate limiting middleware for API endpoints
- **Constraints**: No breaking changes to existing API contracts
- **Non-goals**: UI changes, authentication changes
- **Success criteria**: 99.9% of legitimate requests pass, <50ms latency overhead
- **Environment**: Node.js, Express, Redis
- **Risk tolerance**: Maintenance window available
- **Iteration budget**: 3-4 iterations expected
- **Energy allocation**: 15/20 units
```

### Expected AI Response Structure

The AI would respond with:

1. **Intent Validation** (2-3 sentences)
2. **Assumptions** (with ✓?⚠️ markers)
3. **Open Questions** (minimum 3, with multiple-choice options and recommendations)
4. **Phases of Action** (3-4 iterations with pre-commit/commit structure)
5. **Physics Alignment** (table)
6. **Risks and Mitigations** (table with iteration column)
7. **Deliverables** (per iteration + final)
8. **Acceptance Criteria** (checklist)
9. **Rollback/Fallback Plan** (per iteration)
10. **Energy Distribution** (table)
11. **Next Step** (awaiting approval)

All using iteration-based terminology, no calendar references.

---

## 📚 Template Philosophy

### Core Principles

1. **Iteration-Based**: All temporal references use iterations, not calendar time
2. **Checkpoint-Driven**: Pre-commit/commit structure enforces validation
3. **Explicit Approval**: No execution without explicit gate passage
4. **Risk-Aware**: Rollback strategies planned before execution
5. **Physics-Aligned**: Natural patterns guide iteration structure

### Anti-Patterns to Avoid

- ❌ Calendar-based timelines ("complete by Friday")
- ❌ Implicit assumptions (mark uncertainty explicitly)
- ❌ Single-choice questions (always provide options)
- ❌ Execution before approval (strict gate enforcement)
- ❌ Missing rollback strategies
- ❌ Undefined decision gates

### Quality Gates

Before considering any plan "complete":
1. **Can stakeholder approve/reject it?** (Clarity test)
2. **Can you roll back any iteration?** (Safety test)
3. **Are decision gates measurable?** (Validation test)
4. **Is energy distribution realistic?** (Resource test)
5. **Do alternatives exist?** (Resilience test)

---

## 🔗 Related Documentation

- **Primary Framework**: `docs/templates/ITERATION_PLAN_TEMPLATE.md`
- **Template Verification**: `.codex/TEMPLATE_VERIFICATION_REPORT.md`
- **Terminology Guide**: `docs/TERMINOLOGY_MIGRATION.md`
- **Physics Principles**: Documented in all template files

---

## ⚡ Template Metadata

| Attribute | Value |
|-----------|-------|
| **Version** | 2.0.0-iteration-based |
| **Energy Cost** | ⚡⚡⚡⚡ (High) |
| **Framework Alignment** | 100% (18/18 components) |
| **Status** | 🟢 Production Ready |
| **Last Updated** | 2026-01-23T21:05:00Z |
| **Next Review** | After 10 usage instances |

---

**End of Intent Validation & Plan of Action Template (Iteration-Based)** ✅
