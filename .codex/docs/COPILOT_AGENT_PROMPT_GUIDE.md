# GitHub Copilot Agent — Prompt Guide

Use the relevant fragments below, adapted to the current task. They support
[AI Codebase Agency Policy](../CODEBASE_AGENCY_POLICY.md); they are not
credentials, universal startup gates, or authority to expand the user's request.

## Before work

```text
Confirm the objective, permitted edits, existing dirty work, acceptance criteria
and requested output. Read relevant current instructions/source before editing.
Respect read-only boundaries. Do not reset, stash, rebase or discard user work.
Use supplied/relevant memories when available; disclose missing retrieval
capabilities rather than pretending an exhaustive preload occurred.
```

```text
Work directly when appropriate. Use bounded delegates only when beneficial,
available and authorized; respect a no-nested-agents instruction. Do not require
first-response fan-out, a minimum lane count, or unsupported task arguments.
Repository registry/status flags do not prove hosted activation or permissions.
```

## During work

```text
Resolve issues relevant to the authorized change. Record other findings with
evidence, impact, mitigation/owner and the next decision. Accurate scope
explanations and documented handoffs are allowed. Do not silently waive security
owner/reason requirements or genuine review/execution approvals.
```

```text
Separate local preparation from GitHub writes and execution. A local/no-PR task
can produce an authorized patch and tests without comments or workflow activation.
For workflow patches use relevant actionlint/YAML, secrets/permission checks and
applicable review. Do not infer push, approval, merge, deploy or settings access
from cached flags, memories or a document.
```

Use risk-based review of correctness, tests, documentation, security and
integration. Stop when evidence is sufficient or a real limit is reached; do not
repeat five reviews/attempts or manufacture commits. Fix root causes when
practical and report exact unsuccessful attempts without claiming completion.

## Before reporting completion

- Inspect the actual diff and preserve unrelated changes.
- Run relevant focused tests; compile changed Python and check whitespace.
- Run appropriate available lint/type/security checks. An unavailable
  `codeql_checker`/`parallel_validation` tool is a limitation, not a reason to
  invent a scan or bypass real required checks.
- For PR readiness, verify relevant live CI/feedback when authorized and
  possible. Identify unknown, queued, running and failed states honestly.
- Record only agents actually invoked, or direct execution with none.
- Report changed files, commands/results, remaining findings and actual limits.

No PR comment, public continuation ping, cognitive-brain status file,
repository follow-up prompt or memory write is universally required.

## Handoff template

```text
Objective and authorized boundary:
Completed evidence:
Files changed (or read-only/no changes):
Checks and exact outcomes:
Delegation: actual agents, or none/direct execution:
Outstanding findings: source, impact, owner/mitigation, next decision:
Unavailable sources/tools and remaining validation:
```

Save handoff in the requested response/session location. Only post a PR comment
or retrigger `@copilot` when explicitly authorized and relevant. During an
authorized PR update preserve applicable maintainer WEC selections, while
distinguishing selection/attestation from real execution or platform approval.
