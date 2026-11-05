# 008 — Resolve evidence and fragment gaps on the measured live epoch

Branch: `copilot/resume-cdx-archive-scanner-preflight-recovery`.
Read current policy, [the index](INDEX.md), and
`/home/runner/work/_codex_/_codex_/.codex/tasks/issue5757/checkpoint-007.json`.
Checkpoint SHA-256:
`144b3349c0312b47b3ac65ecb90c65349fad7009dc0900f483638a373b9ddb62`.
Status: `BLOCKED_EXACT_EVIDENCE_COORDINATE_SCOPE_AND_INDEPENDENT_REVIEW`.
`archive_created: false`.

## Executed, not inferred

The actual entry HEAD was `15bff66a66075be22d41a3d946176e1078bcbd65`,
not the supplied `b879136c5ec02172e3425876112355a526ecf451`. Existing startup
metadata and an already-deleted tracked tarball were preserved; the initial
required publishing helper committed their existing state. No archive bytes,
timestamps or bindings were rewritten.

All 15,813 tracked source files matched the index. Archive ignored/untracked
status was empty. Historical timestamp-level drift cannot be reconstructed
without the missing original manifest. Checkpoint 005 actually records source
`5eecdaac55651c7a3773b9b0ed0fc8cbc7d510d9c1cdb52105364ee92c68fbf7`
and 6,737 observations, not the supplied 1815-prefix fingerprint or 279/119 counts.

Both tools were independently authenticated: official Gitleaks 8.30.1 release
artifact matched the separately retrieved official checksums and release API asset
digest; detect-secrets 1.5.0's 89 non-bytecode package files matched the official
PyPI wheel with no extras. The binary was installed only in the explicitly
authorized user-local bin directory, outside Git/source. Its `dir --help` passed.
The later user-supplied repository tarball location was not needed as a substitute.
Official HTTPS metadata verification is not independent signing-authority proof.

Phase B added 60 regressions before freezing the implementation at
`096a156c2eacd01e7a13da68f8e4f61c67f6760a`. All 170 focused tests passed before
and after the epoch; eight actual pinned-binary synthetic fixtures corroborated
the upstream coordinate/redaction/decoding behavior. Scoped Ruff, Black, isort,
mypy, compilation and diff checks passed before the epoch; diff review found no
significant issue. CodeQL analysis was skipped because its database was too large,
not a completed zero-alert security analysis.

Exactly **one** maintained-producer invocation completed, with repeated independent
live loading. No implementation bytes were changed afterward.

- Source: 16,533 entries, 124,233,523 regular-file bytes.
- Source SHA-256:
  `dc41ec4db0d2186e61b73af490c4c8c3b01c4a8341d7f6371e4b89161fe8c3d4`.
- Run namespace: `810b64797d80e2c35f3e8a2e71a9123e`; identity algorithm 2.
- Inventory fingerprint:
  `1782e813ae89a2fb1459ca5514d2d4ab6e527fef3ae6e1b7f43bb7a10eef496f`.
- Observations: **6,614 detect-secrets + 123 Gitleaks = 6,737 raw**.
- **6,699 distinct locations**, defined as path/start-line/end-line tuples,
  not unique secrets. No observation was removed through deduplication.

## Actual bounded investigation

Four batches of 32 were assessed and privately investigated: cumulative assignment
ranges 1–32, 33–64, 65–96, 97–128; per scanner, ordinals 1–16, 17–32, 33–48, 49–64.
The private ledger contains exact replay/context predicates, bounded Python AST
literal/assignment/call inspection where applicable, hypotheses, contrary evidence,
named gaps and next dependencies. No archived code or credential was executed.

- Exact detect-secrets candidate replay: 64.
- Gitleaks reported Match spans mapped: 63; unsupported large-file mapping: 1.
- Redaction markers present in all 64 assigned Gitleaks reports; coordinates
  localize Match, not captured Secret. No Gitleaks secret recovery is claimed.
- **128 indeterminate + 6,609 unreviewed = 6,737**.
- **Zero** affirmative noncredential packets, semantic false-positive proofs,
  accepted findings or approvals.

The first three batches satisfied mapping/replay entry predicates. Batch 4
encountered one file at least 100,000 bytes, outside the verified unfragmented
mapping scope. Batch 5 was not run. The next selection would be per-scanner
ordinals 65–80, but do not blindly advance through the unresolved coordinate gate.
The checkpoint documents a corrected parent-only diagnostic aggregation: an old
predicate name yielded a false zero marker count; maintained batch predicates and
direct private rechecking establish the actual count 64. No finding state,
identity or scanner implementation was changed by that correction.

## Private retention and next actions

The complete bundle, matching key, snapshot, canonical observations, raw reports,
configuration, four queues and private investigation ledgers remain owner-only
in the authorized task-owned `/tmp/cdx_issue5757/` prefix, outside the source.
The exact run/key references are intentionally not public. The measured executable
context was retained. This is **session-local nondurable retention**, not durable
escrow or a guarantee of availability after VM reset.

1. Record actual status/HEAD. Verify checkpoint digest, scope and permitted writes.
   Never reset/stash/clean user work or restore source timestamps.
2. Discover only the authorized task prefixes using bounded no-follow reads.
   Recover the actual complete private bundle and matching key through authorized
   private context; verify ownership, modes, artifacts, numbered queue/ledger
   digests and live source/config/tool/implementation bindings with the loader.
3. If a VM reset removed those inputs, report unavailable—not zero findings.
   Public digests cannot reconstruct the key or records. Do not copy old finding
   IDs, overwrite bindings or perform repeated orientation scans. Obtain an
   approved usable private recovery/retention context before a useful new epoch.
4. With valid context, investigate existing origin/consumer gaps independently
   of further scheduling. Literal, test, placeholder, checksum, age, duplication
   and revocation appearances are insufficient. Keep ambiguous rows indeterminate.
   Exact evidence candidates stay private and separate from the advisory queue.
5. Investigate the large-file fragment gap against official pinned source and
   retained exact report. The current helper intentionally refuses speculative
   coordinates. Do not change measured implementation bytes and claim the same
   epoch still validates. Any future extension needs synthetic fragment/offset
   regression proof before a separately justified, authorized new epoch.
6. Genuine independent review must come from an attributable reviewer whose
   authority is established through an actual owner-approved external identity/
   trust mechanism, with authorized access to exact evidence. Verify current
   finding bindings, evidence relevance/accessibility/digest and review authenticity.
   A second agent, reviewer label, local HMAC key or self-selected trust root is
   not review. No such mechanism or approval was supplied this iteration.
7. Follow [002](002_semantic_review.md) into [003](003_clearance_revalidation.md)
   only when every required observation has actual affirmative exact evidence
   and genuine authorized adjudication, or report a decisive blocked conclusion.
   The existing advisory queue rejects acceptance/evidence states; it cannot grant
   clearance. Any trust integration requires separately grounded rejection tests.
8. A future transition to `archive_created: true` additionally requires actual
   packing authorization and the existing packer's independent snapshot/rescan,
   complete current dispositions and SQLite integrity/Merkle verification.
   Do not directly edit the checkpoint flag or promise eventual clearance.
   Confirmed sensitive unchanged bytes remain blocked under a false-positive-only
   contract; revocation does not turn them into false positives.
9. End the next iteration with an updated fenced Markdown block titled
   `### Next Iteration Follow-Up Prompt for Copilot Cloud Agent`, including actual
   HEAD/introducing SHA, final checkpoint digest/status, exact measured source/
   inventory/counts, batch states, retention limits and evidence/review dependency.
   Repeat this self-chaining handoff until `archive_created: true` is genuinely
   achieved and verified; while blocked, report the actual dependency rather than
   inventing progress, approval or an automatic endless retry.

## Commit provenance

The actual introducing SHA will be appended after this plan-body/checkpoint
commit, in a separate metadata commit. No self-referential SHA is claimed.

Plan-body/checkpoint creation commit SHA:
`28be57909189368c4f5f6d3faf53cd78a2327701`.
This footer is appended afterward in a separate metadata commit.
