---
name: Agent Session Priority Directive
about: Post as a PR comment when approving an agent session to set the primary directive
title: "Session Priority Directive"
labels: agent-directive
assignees: ''
---

## 🎯 Priority for this session: [DESCRIBE THE ONE THING YOU NEED]

> **To the Copilot Agent reading this:**
> This comment is your **PRIMARY directive** for this session.
> Treat it as a hard override above ALL inferred context.
> You MUST accomplish the task above before any other work.
> The `cognitive-preflight` job will surface this as a `::notice` annotation in the Actions log
> and as an inline callout in the mandatory checklist comment.

### Session Scope

- **Priority Task:** <!-- One sentence: what MUST be done this session -->
- **Acceptable Scope Expansion:** <!-- What adjacent work IS allowed -->
- **Hard Boundaries:** <!-- What is OUT OF SCOPE this session — do not touch -->

### Success Signal

> How will the human approver know the priority task is done?

- [ ] <!-- Measurable outcome 1 -->
- [ ] <!-- Measurable outcome 2 -->
- [ ] <!-- Measurable outcome 3 (optional) -->

### Policy Reminder for Agent

You MUST follow `.codex/CODEBASE_AGENCY_POLICY.md`:
- Plan before execution — post plan as PR comment first
- 5+ self-review iterations before session close
- Post `@copilot ...` follow-up PR comment if work is incomplete
- Use pre-commit/commit terminology — NOT days/weeks
- Update `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` in every commit
