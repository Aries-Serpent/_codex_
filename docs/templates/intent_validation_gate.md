# Intent Validation & Plan of Action Approval Gate

This template is used to front-load alignment, risks, and acceptance criteria **before** any code or docs changes are executed.

> **Usage in _codex_**: Paste this in issues/PR descriptions when proposing changes, and get approval on the plan before execution. See also: `docs/decision_records/ADR-intent-approval-gate.md`.

---

## Generic template (copy and customize)
```text
Before you proceed, please do two things in this order:

1) INTENT VALIDATION (2–3 sentences):
   - Restate your understanding of my intent in your own words.
   - Identify the primary goal and the key constraints or scope boundaries.
   - Confirm you grasp what success looks like and what is explicitly out-of-scope.

2) PLAN OF ACTION (structured, reviewable):
   - Present a phased plan with clear decision gates and checkpoints.
   - For each phase, include:
     • Phase name and objective (1 sentence).
     • Concrete steps or tasks (bullet list).
     • Decision gate: What must be true for this phase to succeed? What do you need from me?
     • Estimated effort or dependencies.
   
   - Include these sections:
     • Assumptions: List key assumptions (derived from my request, conventions, or your inference). Mark each as ✓ (confirmed), ? (uncertain), or ⚠️ (needs clarification).
     • Open Questions: At least 3 questions you need answered to proceed confidently. Prioritize by criticality.
     • Risks and Mitigations: A table of Low/Medium/High risks with recommended mitigations.
     • Deliverables: What I will receive at each phase and at the end.
     • Acceptance Criteria: What must be in the final plan for me to approve execution.
     • Rollback / Fallback: How we can undo or recover if something goes wrong.

IMPORTANT: Do not execute, apply changes, or generate final output yet. 
Just present the plan for my review. I will either:
  a) Approve the plan and ask you to proceed.
  b) Ask for specific clarifications or adjustments.
  c) Provide feedback on phases, assumptions, or risks.

Use this context (you may propose adjustments, but do not execute):
  - Task/Request: [YOUR_TASK_DESCRIPTION_HERE]
  - Constraints: [LIST ANY CONSTRAINTS OR BOUNDARIES]
  - Success criteria: [WHAT DONE LOOKS LIKE]
  - Environment/Tech stack: [RELEVANT TOOLS LANGUAGES PLATFORMS]

Reply format (Markdown):
  - **Intent Validation** (paragraph, 2–3 sentences)
  - **Assumptions** (bulleted list with confidence markers: ✓ ? ⚠️)
  - **Open Questions** (numbered list, 1–2 sentences each, prioritized)
  - **Phases of Action** (numbered phases with sub-bullets, decision gates, effort estimates)
  - **Risks and Mitigations** (table: Risk | Severity | Mitigation)
  - **Deliverables** (per phase and final)
  - **Acceptance Criteria** (bulleted checklist for approval)
  - **Rollback / Fallback Plan** (brief steps to recover if needed)
  - **Next Step** (one sentence: "Awaiting your approval or feedback on the plan above.")
```text

---

## Example instantiation for _codex_
```text
Use this context:
  - Task/Request: Integrate local-only evaluator & fence checks; add approval-gate template and docs.
  - Constraints: Do not create/activate any GitHub Actions; keep changes small and reviewable.
  - Success criteria: Hooks run locally; evaluator enforces rubric & hard-fail rules; docs and ADR added.
  - Environment/Tech stack: Python 3.10+, pre-commit, pytest.
```text

**Tip:** Pair this with the local gates in `docs/ops/local_gates.md` to verify plans and messages before merging.
