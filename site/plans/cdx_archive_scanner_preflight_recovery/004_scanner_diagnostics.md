# 004 — Recover the real scanner failure without inventing a baseline

Branch: `copilot/resume-cdx-archive-scanner-preflight-recovery`

Read [the index](INDEX.md), current policy and
`/home/runner/work/_codex_/_codex_/.codex/tasks/issue5757/checkpoint-003.json`.
Its final SHA-256 is
`2236e4b3bf586c56190c8a0909d8d2458425caeab94e8e168dd44310c1c1e5cb`.

## Actual handoff

Preparation tooling is implemented, but **the real-source baseline is BLOCKED**.
One real preflight raised `RuntimeError` before publishing an inventory. Neither
the failing scanner stage nor its originating diagnostics were retained by that
first implementation. Do not infer a timeout, complete scanner execution, zero
findings or historical counts. No semantic batch was assigned or completed.

The measured full tree contained 16,533 entries and 124,233,523 regular-file bytes.
Source SHA-256:
`d12f54c089876c1ef65fa2ea3f182a2d093d26448bdb3e419309c8a85cddc5cf`.
Source and private snapshot matched after failure and source remained unchanged
after cleanup. This is a historical endpoint measurement, not tomorrow's identity.

Implementation commits:

- `41d0a6860215c6dc5ccb57673f6b99f9f92f43d2`: measured full-tree producer,
  explicit selection/configuration/tool bindings, private observation retention,
  conservative batch assessment and Gitleaks partial-scan rejection.
- `8097abbff4b0277992c69fee5a0e44a82e3d3fd8`: private per-subprocess report
  retention before status/parsing and sanitized failure records.

The second increment was verified synthetically, **not by retrying the archive**.
A harmless one-file smoke test completed with both verified pinned scanners and
zero observations; it establishes interface compatibility only.

All 104 focused tests passed; scoped Black, isort, Ruff, mypy, in-memory compilation,
secret checks and whitespace checks passed. CodeQL twice skipped analysis because
its database was too large. This is not a successful security-analysis result.
Three read-only custom-agent lanes, one adversarial join and a bounded two-turn
implementation review were actually used; the parent performed all edits.

The prior evidence directories were absent. This session provisioned owner-only
nondurable context before its attempt, then removed only its failed snapshot/key
and verified temporary tool directory. There is no retained current inventory,
complete namespace, keyed identity continuity or approved durable escrow.

## Execute the next unfinished increment

1. Record status, HEAD and available branch/base comparison. Preserve dirty work.
   The previous mandatory progress helper committed existing startup metadata
   without changing its bytes; avoid assuming the original dirty status survived.
2. Read the maintained contracts and implementation:
   `/home/runner/work/_codex_/_codex_/scripts/archive/CDX_SQLITE.md`,
   `/home/runner/work/_codex_/_codex_/scripts/archive/cdx_common.py`,
   `/home/runner/work/_codex_/_codex_/scripts/archive/cdx_review.py`,
   `/home/runner/work/_codex_/_codex_/scripts/archive/cdx_preflight.py`.
   Independently measure the exact current source; do not restore historical
   timestamps or substitute the checkpoint's fingerprint.
3. Use bounded lanes for provenance, private diagnostic interpretation and
   demonstrated tooling defects. Keep source excerpts, keys, private locations,
   matched values, hashes of matched values and raw reports out of prompts/logs.
4. Verify the new failure-retention path with synthetic tests first. An incomplete
   directory is never a baseline. Raw reports remain owner-only; public output
   contains only known error codes, stage availability and aggregate results.
5. Establish actual retention before another justified diagnostic attempt:
   approved private storage if genuinely available, otherwise explicitly
   nondurable session retention. Fresh keys imply a fresh epoch, not recovered
   historical identities.
6. Reverify existing Gitleaks 8.30.1 and detect-secrets 1.5.0. If needed, obtain
   only the official matching session-local Gitleaks release and independently
   verify published checksum/API metadata and `dir`. Previous digests do not
   authenticate a new executable. No global installation or dependency churn.
7. Perform **at most one** diagnostic full-tree preflight through the maintained
   producer and `cdx_common.run_secret_scanners`, never the packer. Keep all
   private context outside scanned roots, isolate scanner configuration and
   disable credential verification. Never print the key, its location or raw
   exceptions/reports.
8. If it fails, inspect the retained reports privately using bounded no-follow
   reads. Establish the exact failing stage and safe failure reason; implement
   only demonstrated corrections and synthetic regression tests. Do not retry
   for orientation or claim counts from absent/partial output.
9. Only if the complete current bundle passes live binding and HMAC checks may
   [002](002_semantic_review.md) begin. The implemented first-batch routine records
   conservative offline predicates and explicit gaps, not harmlessness proof.
   Genuine independent review authority is still missing; no accepted states,
   dispositions, signing personas or evidence-digest shortcuts are authorized.
10. Atomically create the next unused sanitized checkpoint and continuation;
    preserve history and append the actual introducing SHA afterward using the
    index protocol. Record actual scanner totals or **unavailable**, never zero
    by default. Keep synthetic results separate from real evidence.

## Stop conditions

Missing pins, unverifiable artifacts, errors/partial reports, malformed data,
source/config/tool drift, missing private observations/key or unavailable exact
evidence block dependent review. No archive creation, source edits, credential
testing, issuer contact, workflow actions, deployment or finding approvals.

## Commit provenance

The actual plan-body creation SHA will be appended after its introducing commit,
in a separate metadata commit; no self-referential SHA is claimed here.
