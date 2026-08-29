# Session and agent-state guide

The repository's **operational intelligence layer** records how agent work is planned,
executed, checked, and carried between sessions. It complements git history; it does
not replace source code or package configuration as the implementation authority.

## State surfaces

| Surface | Purpose | Typical examples |
|---|---|---|
| `.codex/` | Policy, machine-readable state, operational references, and dated evidence | `agent_context.json`, `CODEBASE_AGENCY_POLICY.md` |
| Agent memory | Retained observations and patterns used to recover context | STM/LTM stores, pattern records, session context |
| Checkpoints | Explicit resumable boundaries for a process or session | `.codex/checkpoints/`, checkpoint utilities under `src/` |
| Session artifacts | Evidence generated while work runs | session logs, startup packets, diagnostics, reports |
| PDA/AfterMath | Plan/do/assess outcomes and learned patterns | `.codex/aftermath/pda_iterations.jsonl` |
| Accountability | Human-readable record of objectives, actions, agents, and validation | `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` |

```mermaid
flowchart LR
    P[Policy and repository state] --> S[Session]
    M[Memory and prior patterns] --> S
    S --> C[Checkpoint]
    S --> E[Artifacts and evidence]
    E --> A[Accountability record]
    E --> PDA[PDA / AfterMath]
    PDA --> M
```

## Authority and lifecycle

1. Read policy and repository state before starting.
2. Use memory and prior evidence as context, not as proof of current implementation.
3. Create checkpoints at meaningful resumable boundaries.
4. Treat generated session artifacts as evidence with timestamps and provenance.
5. Record completed work and validation in accountability and PDA/AfterMath records.
6. Re-check source, manifests, and live workflow state when historical records disagree.

## Parallel agent lanes

Give every independent lane a named objective and owner. Run lanes concurrently, then
synchronize before edits that touch shared files. Record which agents contributed and
which evidence was accepted in the final accountability entry.

## Multi-lane cost gating (Chronicle)

Chronicle normalizes lane labels to the repo's canonical buckets: `P1`, `P2`, `S1`,
and `Seq`. The lane name is metadata; the gate is the live budget state. The
`chronicle cost-tips` view defaults to a warning budget of `16,000` credits and a hard
budget of `20,000` credits, and it flags heavy sessions lacking checkpoints.

- `P1`: primary or urgent work. Keep it moving only while the lane stays under the warning
  threshold and a checkpoint exists for the last verified state.
- `P2`: secondary or follow-up work. Queue this after `P1` stabilization or after a checkpoint;
  do not start new `P2` work once the warn threshold is crossed.
- `S1`: support work. Limit to bounded follow-up, cleanup, or validation tasks that can be
  resumed cleanly from the most recent checkpoint.
- `Seq`: sequential gate. Treat this as the validation/review boundary that must pass before any
  new exploration or follow-on lane begins.

In short: warning budgets stop broadening the lane, hard budgets stop further execution, and
checkpointing is the handoff boundary. Save a checkpoint after each independently verifiable
lane and resume from that checkpoint instead of rehydrating the full session state.

## `/chronicle search` keywords

`/chronicle search` is the conceptual search surface used in task descriptions. The
repository CLI invocation is `python -m aries_serpent_core.cli chronicle search`.
Use these stable terms when searching session history:

| Topic | Suggested search keywords |
|---|---|
| Workflow compliance | `workflow compliance`, `WEC`, `governance gate` |
| Self-healing CI | `self-healing CI`, `CI pattern healer`, `recovery loop` |
| Coverage gaps | `coverage gap`, `coverage ratchet`, `untested module` |
| Session memory | `session memory`, `STM`, `LTM`, `AfterMath` |
| Checkpoint behavior | `checkpoint`, `resume`, `session recovery` |
| Parallel agent lanes | `parallel lanes`, `multi-lane`, `agent delegation` |
| CI optimization | `CI optimization`, `progressive validation`, `workflow telemetry` |

Search with the narrowest useful phrase first, then add a component path, issue number,
PR number, or session identifier.
