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
- Recovery source: `204b81043da6a50639697a81c3e646aec8d7944c`.
  The prior implementation is now committed, not missing dirty work.
  The only initial dirty file was the startup packet; its bytes were preserved
  by orientation commit `48290eaaa9802b4143e75a9debc8b8ed257504db`.
  The current recovery selection passed **619 tests in 21.58s** on Python
  3.12.10 before continuation edits. This is local evidence only.
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
cross-process file locking. Production breakers reconstruct from qualified
durable receipts; unqualified observations make eligibility unknown. Fixture
history is separate and cannot reset production breakers.
Learning checks event/pattern/patch/observation identity, claims observations
durably, and refuses ambiguous replay. Separate evidence and brain files are
**not** one atomic transaction: pending learning intents require reconciliation.
An EMA is not a calibrated probability. Synthetic fixture learning must be
explicitly isolated and cannot establish production provenance.

Private Git metadata and read-only candidate access use Linux Landlock ABI 4+
on supported architectures. Independent filesystem byte/type inventory does
not trust a gate-controlled index. TCP bind/connect are denied; UDP, Unix
sockets and escaped-session lifecycle containment remain limitations. Process
groups, resource limits and scrubbed HOME/PATH are partial boundaries,
**not** a full sandbox or general network isolation.
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
| T12 | Independent of local composition | Explicit dependency cherry-picks from PR #5744: MCP 2.2.0 and pyasn1 0.6.5 | Advisory/manifest checks; preserve unrelated startup bytes; no merge of source branch |

Integrating owner: direct parent execution. No two lanes edit the SDK,
executor, common ledger or pattern store concurrently. Independent supported
agents received explicit paths, baseline, negative tests, dependencies and
three-cycle stop limits. Actual agents: `integrity-contract-review`,
`durable-evidence`, `shared-skill-invariants`, `approval-transition-integrity`,
`installed-release-integrity`, and `legacy-record-integrity`.
This is supported local delegation, not proof of a hosted swarm runtime.

Current continuation lanes: `compose-local-path`, `release-build-proof`,
`monitor-truthfulness`, `legacy-durable-write`, and read-only
`continuation-authority-review`. Additional owner-requested T12 is assigned to
`dependency-pr5744-review` for independent dependency verification; the parent
exclusively applies its cherry-picks to this working branch.
PR #5744 source commits are `3f246e7a5e6b7fca80e20cf8437660f6dcfc95dc`
(MCP) and `1b3d96b7293b2d43274483e332f6918d76674d10` (pyasn1).
The latter also changes the startup timestamp; that unrelated change is excluded.
The source branch merge commit is not an intended dependency patch.
Advisory checks returned no vulnerabilities for both target versions.

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

### PR-preparation continuation

Recovered `2a47c400cfdebc9d502ed3578015dcb8e99029dd`; orientation
`985ed3c1e9795089843ccbd4e594715cc046897d` preserves the newly dirty startup
packet without overwriting it. Current focused regression selection:
**694 passed in 45.27s**. Independent monitor transport lane:
**78 passed**, configured formatting/type/compile checks passed, and an
independent read-only reviewer found no significant issues. Transport uses
only explicit caller credentials, fixed-origin validated paths, no redirects
or ambient proxies, bounded bodies and sanitized error logging. No live
credential operation or workflow dispatch was performed.

The parent closed the earlier local release-placement/retention gap: all
six real distributions built as wheel and sdist, installed in twelve clean
virtual environments physically under `/tmp`, and passed their public
functions from cwd `/` with isolated interpreters. The retained source
manifest binds 2,269 permitted tracked build inputs to snapshot
`c8f844fa128f65b0336bb9ce4a87444b95f29d07f154f74a066f8ed661048a4d`;
their bytes still match current build inputs. Actual artifacts, logs and
results remain under `/tmp/codex-release-985ed3c1`. All twelve digests and
recreation commands are recorded in `checkpoint.json`. This is not a
full-checkout snapshot, resolved runtime-dependency installation, actual
TestPyPI publication or hosted provenance. Retained `/tmp` files are session
artifacts, not uploaded durable GitHub artifacts.

Read-only legacy revalidation confirms 444 raw objects and an unchanged
SHA-256: 77 failures, 57 caller-labelled repairs, 267 sessions, 42 unknown and
one malformed record; zero verified attempts means an unknown verified rate.
The ledger now supplies an owner, next action and stop condition for every
remaining gap, grouped by T01–T12. It preserves exact G01–G40 acceptance
criteria, fourteen negatives and unavailable B01–B10 meanings. Incomplete
calibration, SQLite adapters, actual health/healing integration, recovery,
merged-SHA observations, inventory and owner-controlled publishing decisions
remain incomplete; they are not waived by preparing a PR.

Requested PR integration base is `0D_base_`, observed at
`31f117c768a743e4e79633c67b9844e923019030`; common ancestor is the original
`4a7d955b8b214d6002932261afdebd60f37ede8e`. No base merge, rebase or main
push was performed. PR preparation uses the existing WEC template and
requests `wec:auto-approve` without treating template text as a fresh label,
independent approval, passing hosted CI or merge permission. The creation
tool has no base/label arguments, so actual routing must be verified from
its returned PR rather than assumed. Current hosted approval run
`41338406715` is `action_required` with zero jobs, not green product CI.

Scoped source continuation and intended PR #5744 dependency changes are
committed at `26e285a0fc3bbc093ce87ad2c8d5df7a046507e9`.
Local results: recovery 619 tests; composition 75; monitor 50; legacy 108
with one unchanged baseline test deselected; approval 94; packaging 7.
These selections overlap and must not be summed. Composition/monitor/legacy
configured formatting, type and compile checks passed. Secret scans found
no secrets. Actions CodeQL found no alerts; Python CodeQL was skipped for
database size. Bandit's two final medium static findings and owners are
classified in `checkpoint.json`, not presented as a clean security scan.

Twelve real distributions passed installed public-function checks for the
captured permitted export identified in the checkpoint. Three cycles exhausted
the release lane's budget; later source drift, checkout-local venv placement
and removed disposable artifact files leave final-source/outside-checkout
release acceptance open. Artifact digests are retained, not downloadable builds.
No package was published. Latest source CI requires action and has zero jobs;
the owner's approval of an earlier workflow attempt resulted in a skipped
attempt, not green product CI.

The maintained local composer and read-only convergence contracts exist.
Calibration, SQLite adapters, actual health/evolution/local-fixer integration,
merged-SHA observation, permitted inventory and the original B01–B10 review
remain open. The repository scheduler remains explicitly human-mediated; tool
delegation is not lane-runtime overlap/cancellation/recovery evidence.

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
