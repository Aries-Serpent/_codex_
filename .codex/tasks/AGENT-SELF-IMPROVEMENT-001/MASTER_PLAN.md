# AGENT-SELF-IMPROVEMENT-001 — v6 integrity continuation

Status: **implementation partial; production readiness not established**.
The machine-readable ledger is `plan.json`; `checkpoint.json` records the
tested source snapshot and actual results. These supersede historical completion
claims only for this continuation, not the preserved checkpoints 0–7.

## Baseline and boundaries

- Checkout: `/home/runner/work/_codex_/_codex_`.
- Reviewed baseline: `933dbf77bbc91a8cb45edbc0064533b3c2158e4a`.
- Original baseline and observed default-branch SHA:
  `4a7d955b8b214d6002932261afdebd60f37ede8e`.
- Orientation snapshot: `829b999326a7470f85f4ad8aa043b86a859f6a6b`.
  The intervening progress commit captured the pre-existing startup-packet
  timestamp change. Its working bytes were not overwritten or hidden.
- Four supplied baseline regressions passed here before product edits:
  **4 passed in 2.60s**, using the existing `.venv_ci` Python 3.12.10.
  The earlier failing bare-interpreter environment is not this baseline result.
- Preparation is not permission to activate, approve, rerun, merge, promote,
  publish, change credentials/settings, or bypass owners. Restricted agent
  registry/profile files were not accessed; their counts remain unverified.

## Architecture and shared contracts

Reuse the existing pipeline, executor, store, tracker, evaluator, collector,
six manifest-discovered skills and human-mediated scheduler. Do not introduce
a competing engine or pretend that task scheduling metadata is execution.

The executor retains actual SHA-256 patch bytes, immutable resolved base,
attempt identity, inventory, bounded gate output and candidate hashes.
Actual Git inventory must agree with declared paths before patch application.
Behavior must fail on the baseline and pass on the disposable candidate.
Empty/unknown/malformed gates and launch errors cannot verify a repair.

The event store remains a versioned JSONL audit trail. Execution claims use
cross-process file locking. Breakers reconstruct from durable observations.
Learning checks event/pattern/patch/observation identity, claims observations
durably, and refuses ambiguous replay. Separate evidence and brain files are
**not** one atomic transaction: pending learning intents require reconciliation.
An EMA is not a calibrated probability. Synthetic fixture learning must be
explicitly isolated and cannot establish production provenance.

Local process groups, resource limits and scrubbed HOME/PATH are enforceable
partial boundaries, **not** network isolation or a full filesystem sandbox.
Unsupported rename/binary/symlink operations fail closed. Behavioral gate
names alone do not establish an authenticated independent validator.

## Dependency graph and task cards

| Task | Prerequisites | Owned integration surface / output | Remaining stop gate |
|---|---|---|---|
| T00 | None | This requested artifact directory; baseline, forty-gap ledger, task cards | Missing original B01–B10 review evidence remains explicit |
| T01 | T00 | Authority/executor and execution fixtures; patch/gate/interpreter/claim proof | Unsupported sandbox guarantees and canonical proposal composition |
| T02 | T01 shared identities | Evidence store/tracker/evaluator and durable integrity fixtures | Cross-store reconciliation, complete chronology/authentic production proof |
| T03 | T02 for learning; T00 for independent legacy adapter | Brain/persistence adapters, PDA summary/export fixtures | Canonical ownership, calibration and all mixed legacy-store migrations |
| T04 | T00 | Approval/transition helpers and prepared workflow fixture truth tables | Owner credential identity, post-merge routing, hosted/tier authority |
| T05 | T00 | Existing publishing helper/workflow, exact installed-artifact fixtures | Twelve clean functional installs and external same-artifact promotion evidence |
| T06 | T02 | Existing six assurance handlers and direct/default-registry fixtures | Authentic command execution/profile integration and real disjoint incident sets |
| T07 | T01,T02,T03,T06 | Existing improvement runner; composed measured-source-to-human-handoff path | Complete real-process composed fixture and authorized merged-SHA observer |
| T08 | T03,T07; T04 for shared governance | Existing health/healing/monitor/fixer/evolution adapters | No placeholder success, true read-only monitoring, maintained caller |
| T09 | T01,T02,T06 | Existing lane scheduler/runtime or complete human handoffs | Dependency-aware isolation, overlap/cancellation/checkpoint proof |
| T10 | T00; T06 for mappings | Permitted inventory and evidence-backed consolidation recommendations | Registry/profile access restriction; no indirect workaround |
| T11 | All implemented local tasks | Integrated replay, independent review, exact validation and handoff | Externally blocked work remains incomplete |

Integrating owner: direct parent execution. No two lanes edit the SDK,
executor, common ledger or pattern store concurrently. Independent supported
agents received explicit paths, baseline, negative tests, dependencies and
three-cycle stop limits. Actual agents: `integrity-contract-review`,
`durable-evidence`, `shared-skill-invariants`, `approval-transition-integrity`,
`installed-release-integrity`, and `legacy-record-integrity`.
This is supported local delegation, not proof of a hosted swarm runtime.

## Review and verification

The actual independent architecture review identified declared-scope trust,
non-atomic claims, restart-reset breakers, outcome identity trust and
unauthenticated merge labels. Those findings drive T01/T02 changes.
An independent adversarial review must inspect the integrated diff before
the final source checkpoint; deterministic review questions do not substitute.

Run existing focused positive and negative tests, configured Ruff/Black/isort,
scoped mypy, Python compilation, workflow YAML validation, secret scanning,
diff checks and the supported security checker. Record actual limitations,
including unavailable actionlint or Python CodeQL, rather than inventing green
CI. The observed hosted run `41276311097` is `action_required`, with zero jobs
and no failed-job logs: it provides no product verification.

## Continuation and rollback

First complete T02 identity/chronology and fixture-only learning boundaries,
then T03/T06 integration into the maintained T07 runner. Implement T08/T09
only after shared contracts are published. Keep T04/T05 external activation,
credential migration and promotion blocked until operation-specific owner
evidence exists. Obtain the missing original B01–B10 review before mapping
its meanings; do not fabricate a ten-item parallel project.

Recovery must preserve raw evidence and user work. Do not automatically
re-enable breakers or retry unresolved claims/learning intents. An authorized
recovery must reconcile the exact attempt/observation and append evidence.
For code rollback, the owner may revert the scoped implementation commit
after reviewing compatibility; do not reset, stash, rebase or delete ledgers.
