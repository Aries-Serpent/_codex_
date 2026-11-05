# 005 — Establish a corrected baseline, then enter exact semantic review

Branch: `copilot/resume-cdx-archive-scanner-preflight-recovery`

Read [the index](INDEX.md), current policy and
`/home/runner/work/_codex_/_codex_/.codex/tasks/issue5757/checkpoint-004.json`.
Its final SHA-256 is
`64e594baacc06e4d90cfba5db90a0d80fae3e3d0d825f2587ea8048f9319d2f3`.

## What actually completed

001's maintained preparation and an **exact blocked outcome** are established,
not an unconditional clean/current baseline. 002's entry predicates failed:
no batch was assigned, no observations were semantically assessed, and no
dispositions or approvals were created. 003 was evaluated only as unresolved
evidence/authority blocking, not successful clearance.

The dependency recovery in [004](004_scanner_diagnostics.md) was executed before
semantic review because 001/002 require returning to preparation on failed entry.
Exactly one real diagnostic attempt ran. Both pinned scanners returned reports:
Gitleaks exit 2 with 123 observations; detect-secrets exit 0 with 6,614.
These are freshly parsed **report counts**, not a completed keyed inventory or
exclusive review-state reconciliation. Their equality to historical counts does
not establish continuity.

The producer failed before inventory publication: detect-secrets reported relative
paths against its private subprocess cwd, but finding mapping tried the parent cwd
or source root. All 6,614 relative paths failed; all 123 absolute Gitleaks records
mapped successfully. The proposed Tags-null hypothesis was not observed and was
not substituted for measured evidence.

Commit `1a78653a834f8d221d23173f1239a173bd731ec5` fixes both mappers to use the
explicit scanner cwd, without fallback into lookalike files. It also retains
private pre-scan measurements and provides specific safe path failure codes.
Offline remapping of all 6,737 retained records succeeded. **That was not a
rescan, baseline reconstruction or semantic review.** No real rerun followed.

Validation: 110 focused tests passed; scoped Black/isort/Ruff/mypy, in-memory
compilation, secret and whitespace checks passed. An actual pinned-tool smoke
test on a synthetic fixture produced one detect-secrets observation, published
and revalidated a private bundle, and remained BLOCKED_FINDINGS. Synthetic results
are excluded from real evidence. CodeQL analysis skipped because its database was
too large; it did not establish a successful security review.

The full source remained unchanged throughout this execution: 16,533 entries,
124,233,523 regular-file bytes, SHA-256
`7a47f5cdda7821a1e6d3fc47c7a76848f4d636598044da14fbf8af293d2b4b48`.
This is historical metadata-sensitive identity, not a value to restore.

Only failed-run diagnostics remain owner-private and session-local, with no
durability guarantee. The task-owned provisional key, snapshot and temporary
verified tool directory were removed after diagnosis. No completed run namespace,
inventory or keyed continuity survives. Ordinary deletion is not secure erasure.

## Execute the next dependency-ready work

1. Record status, HEAD, available base comparison and latest checkpoint. Preserve
   dirty bytes and metadata; do not reset, stash, clean or rewrite source.
   The previous required progress helper committed existing startup metadata
   without changing its bytes; do not assume its original dirty status persisted.
2. Read current archive contracts and applicable instructions. Inspect
   `/home/runner/work/_codex_/_codex_/scripts/archive/cdx_preflight.py`,
   `/home/runner/work/_codex_/_codex_/scripts/archive/cdx_common.py`,
   `/home/runner/work/_codex_/_codex_/scripts/archive/cdx_review.py`,
   `/home/runner/work/_codex_/_codex_/scripts/archive/CDX_SQLITE.md`.
   Recompute source identity using the maintained no-exclusions fingerprint.
3. Use bounded independent lanes for provenance, exact evidence and demonstrated
   tooling needs. Parent owns private processing/checkpoints. Never send source
   excerpts, key locations/values, scanner reports or matched-value hashes to
   prompts, public files or logs.
4. Verify the child-cwd regression tests and diagnostic retention synthetically.
   Existing failed reports, if still available through safe private reads, remain
   diagnostic history only. Do not promote them using retroactively supplied
   provenance or manufacture a completed baseline.
5. Establish actual key/evidence retention before scanning: an approved private
   mechanism if available, otherwise clearly nondurable owner-only session
   storage. Create a fresh context; never transfer old IDs or approvals.
6. Verify Gitleaks 8.30.1 and detect-secrets 1.5.0. If Gitleaks is unavailable,
   use only the matching official session-local artifact with independently
   obtained official checksum/release metadata and a successful `dir` check.
   No global installs, dependency changes or unverified sources.
7. Perform at most **one** justified full-tree preflight through the corrected
   maintained producer and `cdx_common.run_secret_scanners`, never the packer.
   Isolate scanner configuration, disable credential verification and retain raw
   reports only privately. Require before/after source/snapshot/config/tool
   checks and `complete.json`; loading must independently recheck the complete
   private bundle and matching HMAC identities.
8. If it fails, inspect available private reports and sanitized failure codes,
   record the exact blocker and continue only independent synthetic/tooling work.
   Do not rescan for orientation, count partial reports as clearance, or weaken
   the gate. If it succeeds, enter [002](002_semantic_review.md) with its **new**
   current inventory, exact observations and matching retained key.
9. Actually investigate at most 32 observations, initially 16 per scanner where
   available. Establish detector semantics, exact candidate context and relevant
   provenance privately. The current advisory batch routine's structural/context
   predicates alone are not affirmative harmlessness evidence; Gitleaks exact
   semantics and general remaining-batch scheduling may need demonstrated scoped
   support. Record a named gap where proof is unavailable.
10. Keep each observation in one exclusive state and reconcile against both
    scanner totals without subtracting overlaps. No authenticated independent
    review contract has been established; evidence candidates must remain
    separate from accepted dispositions. HMAC possession, another persona or a
    digest of irrelevant evidence is not authority.
11. Enter [003](003_clearance_revalidation.md) only for genuinely complete review
    or a decisive evidence/authority/sensitive-content blocked conclusion.
    No original archive bytes may be edited and no archive creation is authorized.
12. Run focused validation for actual changes, atomically publish the next unused
    sanitized checkpoint and continuation, report the final checkpoint digest,
    and append the real introducing SHA afterward using the index protocol.

## Commit provenance

The actual plan-body creation SHA will be appended after its introducing commit,
in a separate metadata commit; no self-referential SHA is claimed here.
