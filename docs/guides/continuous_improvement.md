# Continuous Improvement
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated: 2026-06-22

This project includes maintenance utilities for pruning logs and keeping the repository tidy. The `tools/codex_maintenance.py` script is meant to run on a regular schedule so that artefacts do not accumulate.

## Local scheduling with cron

Use `cron` to run the maintenance script at an interval of your choice. The example below runs it every iteration at midnight:

```cron
0 0 * * * /usr/bin/env python /path/to/repo/tools/codex_maintenance.py >> /path/to/repo/.codex/maintenance.log 2>&1
```
Replace `/path/to/repo` with the absolute path on your machine. The script's output is appended to a local log file so you can review past runs.

## Local scheduling with a runner script

If you prefer not to modify your system's `cron` table, create a lightweight runner that you invoke manually or from another scheduling tool:

```bash
#!/usr/bin/env bash
python /path/to/repo/tools/codex_maintenance.py
```
Invoke this runner from `launchd`, `systemd`, or any other local scheduler you control. All resources remain on your machine; **do not** enable or rely on GitHub Actions or other hosted services.

## Rationale

Keeping the maintenance workflow local avoids exposing repository data to external services and keeps automation simple. Run the job on a workstation or server you manage, and adjust the interval to match your cleanup requirements.

## Evidence-gated proposal assessment

`python -m codex.cognitive_brain.improvement_loop_runner --help` describes
the existing PDA-log runner and its optional `--evidence-bundle` mode.
By default this mode reads local JSONL exports, not live GitHub or Chronicle services,
and prints one assessment per valid input record. Each record contains:

- `repo` and immutable `sha`, matching the caller's `--repo` and `--sha`;
- `signal`, using the cognitive SDK's `SignalEvidence` fields, with
  timezone-aware `measured_at` and an explicit availability;
- `brief`, containing the evidence-to-improvement skill's hypothesis,
  metrics, scope, lane/dependencies, acceptance criteria, commands, budget,
  stop condition and falsification;
- `author` and optional `validation`, plus `correction_cycle` from zero to three.

Code proposals require a finite `signal.details.baseline_metric` matching the
brief baseline. Assessment time and freshness are controlled by the caller,
not the exported brief. Missing, stale or unavailable observations do not
reach pattern retrieval. Chronicle productivity observations must be marked
`category: session-productivity` in the brief and remain signal-only.

The existing `ImprovementPipeline` still enforces its authority envelope.
Without caller-supplied approval it returns a blocked proposal; approval
fields in exported records cannot grant authority. Validation must bind the
generated `proposal_id`, event proposal `patch_hash`, SHA and author.
Both the validation envelope and every command observation must carry the
assessment's `evidence_digest`, binding the exact signal, generated proposal,
file scope and context; every observation also carries the proposal/content IDs.
Command observations require a timezone-aware `timestamp` and a nonempty
`evidence_ref`; missing measurements cannot be replaced with NaN or empty strings.
It must supply the declared verification commands and complete independent
negative, boundary and regression observations. Reassessment does not change
the proposal ID merely because observation time advances.

Complete supplied observations produce `ready-for-human-review`, **not**
authenticated approval or an executed/merged improvement. The assessment CLI never
executes commands, patches, agents, releases or confidence updates. Its output
always denies execution and integration authority. A non-ready or malformed
record or empty bundle produces a nonzero CLI exit; valid records remain available on stdout.
Sanitize exported source evidence before use; do not include credentials or
personal information. Actual isolated verification and measured post-merge
outcome tracking remain separate authorized stages.

### Explicit local composition

`compose_local_improvement` in the same maintained runner joins assessment,
eligible retrieval, task review, canonical patch preparation, isolated
verification, retained execution evidence and read-only evaluation. Unlike
the assessment CLI, this API can make one disposable local attempt only when
the caller explicitly authorizes execution, supplies human approval, a
matching executor and a trusted independent review verifier.

The verifier must affirm the bound review with exactly `True`; distinct names
in an exported record are not independent approval. The actual UTF-8 patch
bytes, SHA-256, immutable base and reviewed commands must agree. Template
descriptions are never executable patches. Production freshness uses the UTC
clock; injected observation time requires explicit synthetic fixture mode.

The result retains event/attempt/base/patch identities, gate outputs and
candidate tree identity for a human handoff. Local passing gates still produce
partial evaluation without independently observed PR, merge and post-merge
outcome evidence. Negative/boundary review observations are not a claim that
each review category mechanically re-ran as a separate executor gate.

Replay never executes a recorded event again. A crash after event persistence
but before execution requires an owner to inspect the exact journal and claim
identities and authorize reconciliation; do not delete records or automatically
retry. Cross-store pending learning intents likewise stay blocked. No result
authorizes PR creation, integration, publishing or automatic confidence learning.

### Optional live CI metadata collection

Add `--collect-ci-run RUN_ID` together with `--evidence-bundle` to read public
GitHub Actions metadata for one run and replace exported signals in the
input records. The positional JSONL file still supplies repository/SHA,
briefs and any previously recorded validation. All records share the same
collected snapshot. Caller-supplied write boundaries provide candidate files;
GitHub metadata never supplies patch content or write scope.

`codex.cognitive_brain.ci_signal_collection.collect_ci_run` also accepts an
injected authorized JSON reader for private repositories. The default reader
uses the existing optional `requests` dependency lazily, does not resolve
credentials, and does not inherit proxy/netrc settings. It performs only
fixed-origin HTTPS GETs with redirects disabled, no retries, ten-second
connect/read timeouts and a one-MiB response cap. A disposable process bounds
DNS, TLS, response headers and slow-stream body reads to twenty seconds or
the remaining sixty-second collection budget, whichever is smaller; timeout
cleanup permits two additional one-second joins. Caller-injected readers must
provide their own blocking-operation cancellation; the collector checks their
elapsed time but cannot interrupt arbitrary caller code.

Collection is bounded to five pages, 500 jobs and seven reads. It uses the
attempt-specific jobs endpoint and checks the run again after pagination.
Repository, immutable SHA, run ID, every job's attempt, timestamps, job IDs and complete
pagination must agree. Pending, gated, cancelled, denied, empty or entirely
skipped inventories are explicitly unavailable; malformed or changing
metadata is an error. Neither produces a synthetic zero-failure baseline.

A completed measurable attempt produces `failed_jobs_in_run_attempt`,
with its failure count, structured job IDs/outcomes and source references.
Successful attempts remain non-actionable metric samples. Skipped/neutral
jobs cannot refresh the age of an old executed-job measurement. Remote logs,
job/step names, actor details and error response text are not copied.

Collection success is not independent validation, C2 hosted enforcement
proof, approval or execution authority. The existing freshness, measured
baseline, scoped proposal and per-observation digest checks still apply.
Private access, Chronicle/package collectors, isolated verification and
post-merge outcomes remain separate integrations.

## Local candidate and durable evidence integrity

`IsolatedExecutor` resolves an immutable base commit, hashes the actual patch
bytes, and reconciles Git's actual path/line inventory before applying anything
to the disposable private Git snapshot. It has independent Git metadata, not
a writable link to the source repository. Declared paths are not proof of scope.
Binary, rename, symlink, mode-only and no-op repairs are conservatively rejected.
Empty, unknown or compile-only gate contracts cannot verify a repair.
The default contract runs real unittest discovery: behavior must fail on the
baseline and pass on the candidate. Bare `python`/`python3` gates resolve to the
running supported interpreter; launch errors are not timeout results.

Patch bytes, attempt identities and bounded gate output are retained under
`.codex/improvement/artifacts/<actual-sha256>`. No candidate is copied back or
automatically integrated. Supported Linux execution requires Landlock ABI 4+
with read-only runtime paths and private writable checkout/HOME. Rules are
inherited by descendants; source files and Git metadata are inaccessible.
TCP bind/connect is denied. UDP/Unix sockets, process counts and escaped-session
lifecycle containment are unsupported: this is not a full sandbox.
Address-space/output limits and process groups also apply. Legacy declared line counts
remain a ceiling; explicit base inputs must be immutable commit SHAs.

Execution claims and observation consumption survive restart. Breakers
reconstruct from durable outcomes, and proposal callers can inject the
authoritative evidence store to exclude disabled patterns. Wrong event,
pattern or patch identities are errors, not learning. Replayed observations
cause zero additional learning; new regression/rollback observations require
distinct identities. A pending cross-file learning intent requires
reconciliation: evidence JSONL and the brain JSON file are not one atomic
transaction, and their EMA is not a calibrated success probability.

### Explicit learning-intent reconciliation

`EvidenceStore.inspect_learning(snapshot_reader)` exposes pending consumption
and consumption completed before its separate qualification append. Inspection
does not create missing journals, lock files or directories; corrupt or
unterminated evidence remains an error with original bytes preserved.
The returned `LearningRecovery` binds the persisted observation/event/pattern,
patch and merge identities, any actually recorded attempts, the journal digest
and the external-store snapshot identity. Missing attempt IDs remain absent.

The injected snapshot context must yield an `ExternalSnapshot(identity, recheck)`
for a present, readable external store and exclude **all** external writers
until it exits. `recheck` freshly reads the same store identity under the held
boundary and must raise if that store disappears or becomes unreadable; it must
not return a cached digest. Acquire this external boundary before the evidence
transaction, in the same order as the tracker. Its tracker lock alone does not
exclude arbitrary SDK writers.
The API does not discover credentials, infer consumption from an EMA value,
or supply a production authorization/receipt provider.

`MaintainedWriterRecovery` supplies a snapshot adapter for cooperating maintained
`AgentBrainInterface` writers: `submit_pattern`,
`submit_learning`/`_update_pattern_stats`, and `_save_patterns`. Their common
protocol locks the existing parent directory across replacement and reloads
persisted patterns before mutations; direct stale-cache saves are rejected.
The directory-level POSIX lock creates no sidecar and serializes stores sharing
that directory. Unsupported locking platforms fail closed.

This advisory protocol cannot exclude filesystem edits, older SDK processes or
other nonparticipating writers. Recovery stays unavailable by default unless the
caller explicitly limits coverage to participating writers. That scope assertion
is **not** policy authorization or proof of consumption. Inject actual owner
policy, observation-specific consumption receipts and measurement verification
separately; none is derived from an application count, EMA, actor label or hash.
Acquire this external exclusion before any journal transaction. Missing,
unreadable or malformed external stores remain explicit failures; inspection
does not create them. Atomic replacement visibility and confirmed durability are
distinct: a post-replace failure must not invite replay of a learning update.

`EvidenceStore.reconcile_learning` defaults to dry-run and denies decisions
without an explicitly injected trusted policy verifier. A supplied identity,
actor string or digest is not authorization. A real decision rechecks exact
journal/observation/external identities under the transaction boundary:

- `already_applied` additionally requires independent observation-specific
  consumption proof and the existing trusted measurement contract. It never
  invokes the learner again.
- `abandoned` permanently consumes only that learning identity, creates no
  qualification or success, and does not reset a breaker. Unknown eligibility
  stays unknown; later observations need their own identities and proof.
- Ambiguous external writes remain unresolved. Completed consumption without
  qualification is not silently qualified during load.

Recovery is append-only, with restart validation and no cross-file atomic
exactly-once guarantee. It cannot reset or reuse cancelled/interrupted execution
claims. Implementing this API does not authorize applying it to live journals
or brain files; use new disposable copies unless the relevant owners separately
authorize a specific recovery.

### SQLite session pattern identities

The maintained `SessionDatabase` and `SessionDB` adapters store session pattern
IDs as opaque `TEXT`. Their insertion and `PatternEventRecorder` paths preserve
nonnumeric and leading-zero strings across reopen and propagate SQLite write
failures. Existing numeric inputs use SQLite text affinity; this is not a
reason to normalize `"0012"` into `"12"`. CI issue-pattern integer identifiers
in the cognitive app are a separate domain and must not be blanket-migrated.
These scoped round-trip checks do not establish compatibility of untraced stores.
Database construction initializes/optimizes schemas and may handle corruption;
never open a live database merely to inspect its schema.

The separate `scripts/ci/pattern_recorder.py` CLI accepts `--pattern-id` as an
integer and binds it into the cognitive app's `patterns.pattern_id INTEGER`.
Its query/export paths preserve that numeric domain: `"0012"` and `"12"` both
mean integer 12 here, while the session filter is still opaque bound text.
Opaque IDs such as `RP-019` are rejected by this CLI before database creation,
not silently converted into session IDs. Disposable tests exercise close/reopen,
export/query and trigger-denied writes with existing rows preserved. This trace
does not authorize a migration or turn recorded CI repair labels into qualified
learning measurements.

Shared skill handlers reject nonfinite measurements, empty references,
holdout-only replay and mismatched handoff/validation SHAs. Supplied
observations still do not authenticate their observer. Production outcomes
require a trusted measured-merge verifier; labelled synthetic fixtures cannot
establish production success.

### Separate post-attempt handoff

`improvement_loop_runner.compose_post_attempt_handoff` explicitly joins persisted
event/proposal and available execution identity to scanner observation and exact
pattern calibration diagnostics. It is not invoked by
`compose_local_improvement`; local preparation remains read-only by default and
does not acquire a network or learning dependency.

The handoff rejects contradictory identities instead of inventing PR/attempt
associations. Its default observation is unavailable: no bounded live transport
is supplied by this integration. `RecordedFixtureReader` accepts only bounded
offline JSON bytes for allowlisted repository paths, with aggregate/per-response
limits and a read/deadline budget. It cannot turn a historical PR/run fixture
into fresh live evidence. Arbitrary callbacks and caller-supplied live labels
cannot establish a hard transport deadline or authenticated origin.

Scanner observations remain `compliance-scanners`, never learning-eligible;
calibration remains diagnostic-only, with insufficient/expired/disabled/unknown
states preserved rather than replaced by the public EMA. Source identities are
retained without remote headers or credentials. Neither this stage nor its
runner wrapper claims observations, completes consumption, reconciles learning,
or invokes `submit_learning`. Its output is a human handoff, not authority to
execute, learn, merge, or recover an ambiguous write.

### Retained execution evidence in skills

The optional `retained_evidence` input uses `repo_path` and the existing executor
outcome to validate retained canonical patch/base/scope/attempt, manifest and gate
output identities before relevant deterministic handlers use command/replay
observations. An arbitrary `evidence_ref` is not a retained artifact identity.
Missing, tampered, denied or cancelled evidence cannot become passing replay.

This adapter reads artifacts; it never runs commands. Real-process disposable
fixtures use `IsolatedExecutor`, not a second skill-layer runner. A coherent
local artifact collection is not authenticated independent review or production
measurement, and the adapter cannot authenticate an entirely fabricated local
collection. Author/observer labels do not resolve that limitation. Package
promotion, absent permitted profile mappings and genuine reviewer evidence
remain separate handoffs; no packaging matrix is rebuilt by this stage.

PDA summaries preserve mixed legacy raw records and distinguish caller-labelled
repair rates from uniquely attempt-linked verified-result rates. With no
verified attempts, the verified rate is unknown, not zero or success. Unknown,
session, malformed and unsupported-schema records remain explicit.

See the requested task bundle under
`/home/runner/work/_codex_/_codex_/.codex/tasks/AGENT-SELF-IMPROVEMENT-001/`
for all forty gaps, remaining owner decisions and source-bound validation.

## Read-only transition evidence

`python -m scripts.ci.e_to_d_gate --help` describes assessment of an explicitly
supplied registry and optional `--manifest` path. It validates registry entries
against `configs/schemas/agent_spec.schema.json`, rejects empty populations
and duplicate IDs, and reuses the manifest generator's canonical SHA-256
verification. Inputs are never written, including when output aliases an input.

A matching local manifest hash is not hosted provenance. The active Tier-1
hosted-gate condition remains unknown without verified hosted evidence, so
local schema/hash success cannot authorize promotion. Registry/profile access,
promotion and hosted activation still require their applicable authority.
