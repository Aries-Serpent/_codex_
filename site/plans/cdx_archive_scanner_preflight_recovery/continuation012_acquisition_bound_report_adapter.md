# 012 — Functional acquisition-bound report adapter; clearance remains blocked

Entry HEAD: `0a05a21653ba9f7a345b396f64222b552d5e7cf4`.
Implementation: `593f9c5ab4e0d5b291610d3d7c05137bed370fbb`.
Checkpoint010: **FUNCTIONAL_REPORT_ADAPTER_SYNTHETIC_MVP_COMPLETE_CLEARANCE_BLOCKED**.
Predecessor checkpoint009 digest was verified:
`384db3a1f9e077187a02d00432b8b6f4c1b4a762b7f2af628b1d06142eea3310`.

## Implemented and actually used

The authorized PoC now contains a genuine ecosystem-verified pinned
`github.com/zricethezav/gitleaks/v8 v8.30.1` library adapter. It is locally built,
not an official Gitleaks release executable. Acquisition records the complete
bounded no-follow file input `[0, size)` immediately around its single library
call. Match intervals are checked against the actual acquired bytes before
redaction, not invented from caller metadata or CLI slice replay.

Maintained preflight integration is an optional advisory supplement: both
original pinned scanners still complete first. Fresh request/report/file/run/
selection/config/tool/consumer bindings, private create-only completion/failure
artifacts and a reverified observed-span consumer are implemented. Resource/
encoding limits block instead of skip. No adapter deduplication, disposition
bypass, historical identity migration or origin/use/harmlessness claim was added.
See `scripts/archive/CDX_SQLITE.md` for the actual API and explicit limits.

Primary module provenance was checked through `go mod download`; module version,
sum and replacement absence are verified from adapter build information.
Advisory findings in transitive crypto/compression dependencies were remediated
with `golang.org/x/crypto v0.52.0` and `github.com/klauspost/compress v1.18.7`,
without changing scanner pins. Go >=1.25 is required; actual build used go1.25.0.
Declared runtime dependency versions were advisory-checked.
Official Gitleaks Linux x86_64 bytes were independently checked using release API
asset digests and separately fetched official checksum metadata before extraction.
Detect-secrets 1.5.0 and its actual launcher were measured; the supplied launcher
digest remains waived. Official wheel provenance was not freshly reverified.

## Rubber-duck, adversarial design and development validation

Question | Options/reasoning | Adversarial counterexample | Selected result
--- | --- | --- | ---
Missing origin | Digests and overlapping CLI slices cannot prove observed context; acquisition-bound library input can | Same report coordinates can alias different fragments | One full-file library call; exact pre-redaction Match check
Independent scan compatibility | Compare full canonical record multisets without deduplication | Forced LF/CRLF fragment boundaries change stock columns | Three equal synthetic cases; two explicit divergence cases
Consumer safety | Reuse acquired bytes instead of pathname rereads | Replacement can follow symlinks or allocate oversized files | Pure shared canonicalizer; no adapter pathname reread
Resource safety | Index/decode once per acquisition | Per-observation full-file work multiplies byte budgets | Cached indices/rune boundaries and cumulative Match-byte budget

An actual preimplementation design task challenged the plan. Actual code review
found the two consumer safety/resource issues above; they were fixed, and a
focused follow-up review confirmed remediation with no significant remaining bug.
Those agent reviews are code quality checks, not independently authenticated
reviewer authority over real findings.

Final dedicated validation: **226 Python tests passed**, no failures/skips
(18 adapter, 125 preflight, 53 review, 30 SQLite); **4 Go test functions passed**
covering eight full-file LF/CRLF/threshold/Unicode cases. Go build/vet/module
verification and configured Black/isort/Ruff/mypy/compilation/diff checks passed.
Initial atime and type-inference failures were fixed before the final pass.
Secret scanning passed before publication. Post-commit CodeQL was cancelled due
to timeout and explicitly prohibited a retry: **not a pass**.

Final end-to-end validation performed **five** actual maintained synthetic
preflights plus **five** actual adapter subprocess scans: five library calls,
five adapter observations, all five mapped, five independent stock Gitleaks
observations. Three complete-record multiset comparisons matched; two deliberately
forced fragment-boundary cases diverged. Across the session's two Python
validation rounds, eight actual synthetic adapter subprocess scans ran; two
successful Go validation rounds covered 16 direct full-file cases.

## What is still needed, explicitly

The acquisition/report/consumer/producer PoC components are functional, but the
adapter is **not packer-clearance compatible**. Stock large-file rejection and
the packer's independent stock scan/disposition gate remain unchanged. Matching
synthetic records establish only those snapshots; divergence is never hidden,
deduplicated or converted into approval. A reviewed exact divergence-handling
contract is required before adapter identities could support stock clearance.

Still missing for actual archive clearance:

1. Current complete real-source inventory and approved durable private retention.
2. Actual exact-finding origin, consumer-use and affirmative harmlessness evidence.
3. Genuine attributable independently authenticated reviewer authority.
4. Completed applicable security analysis; CodeQL timed out, not passed.
5. Separately authorized packing and the maintained independent snapshot/rescan
   gate, followed by actual integrity/Merkle verification.

No real-source scan, new real epoch, semantic batch, approval or archive creation
ran. The historical original was not remeasured or changed. Current inventory,
mapping/replay and review counts are **unavailable, not zero**. Past transcript
was not loaded; the parent's optional query returned no rows. Existing dirty
startup metadata bytes were preserved and captured by the required initial
progress helper. Private test artifacts are owner-only session-local/nondurable.
Same-user endpoint/HMAC integrity is not OS isolation or external authentication.

## Next Iteration Follow-Up Prompt for Copilot Cloud Agent

Continue in `/home/runner/work/_codex_/_codex_` on the current branch. Read current
policy, this continuation, checkpoint010, and the 002/003 evidence contracts.
Recheck HEAD/status and checkpoint digest; preserve original archive and dirty work.

1. Do not reimplement missing origins: the functional pinned adapter now exists.
   Verify executable/module/config/consumer identities before authorized use;
   caches and historical hashes are not current provenance or credentials.
2. Keep Gitleaks 8.30.1 and detect-secrets 1.5.0. Do not replace full-file
   acquisition with CLI slicing, caller intervals, deduplication or stock bypasses.
3. Resolve the demonstrated stock/adapter divergence contract before claiming
   clearance compatibility or starting a dependent real epoch. Synthetic report
   equality does not migrate stock identities or approve findings.
4. Establish actual safe retention and a complete current bound inventory before
   evidence batches. Localization is not origin/use/harmlessness proof.
5. Obtain genuinely independently authenticated exact review; never manufacture
   approvals from HMAC possession, agent personas or fixture predicates.
6. Treat CodeQL timeout as incomplete security analysis; use an authorized bounded
   analysis environment without blindly retrying the failed tool invocation.
7. Do not pack, mutate workflows/PRs, approve, merge or deploy. Packing needs
   separate authorization and independent maintained integrity/rescan gates.
8. Persist the next factual checkpoint/continuation and retain this follow-up
   chain until genuine authorized archive creation and verification. Include
   actual HEAD, implementation/introducing SHAs, checkpoint digest and execution
   counts; never substitute unavailable real findings with synthetic zeroes.

## Commit provenance

The actual introducing commit and checkpoint010 digest will be appended after
first publication, in a separate metadata commit.

Actual introducing commit: `ad2526e5bddb2508c5c4fc8ec22cd89416a5eb6c`.
Checkpoint010 SHA-256:
`60686658f7db03ad477d6c139557f4425ab0de453d1ece2b03e563fb1ef037fd`.
Checkpoint path:
`/home/runner/work/_codex_/_codex_/.codex/tasks/issue5757/checkpoint-010.json`.
This footer was appended afterward, separately from the introducing commit.
