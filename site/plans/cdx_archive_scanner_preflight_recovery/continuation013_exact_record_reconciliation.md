# 013 — Exact-record reconciliation implemented; real epoch remains blocked

Entry HEAD: `d204325319850b247ecdbda4d91c048c04ef910a`.
Preparation: `fd145f22aa6e89c485fce27313dc2574ad992831`.
Implementation: `696244f97c4e4ca468e5df324b01d8ef645cbcea`.
Predecessor: [continuation012_acquisition_bound_report_adapter.md](continuation012_acquisition_bound_report_adapter.md).
Checkpoint010 digest verified:
`60686658f7db03ad477d6c139557f4425ab0de453d1ece2b03e563fb1ef037fd`.

## Completed dependency-ready implementation

The checkpoint010 functional full-file adapter is retained. Reconciliation v1
now groups complete canonical Gitleaks records by pinned version and exact file
path/digest, preserving separate stock/adapter zero-based occurrence lists.
Matched, missing-from-adapter, extra-in-adapter and duplicate counts are explicit.
Only singleton groups on both sides are unique exact-record associations.
Duplicate groups remain ambiguous, including equal multisets; no arbitrary
pairing or deduplication occurs. Changed-context records remain separate.

The private `cdx_adapter.stock_relationship` API returns an occurrence's
relationship only after current source/report/request/tool/configuration/consumer
and namespace revalidation. Invalid, absent and non-Gitleaks ordinals fail closed.
The loader recomputes groups/counts and rejects altered association metadata.
Original raw reports and canonical records remain distinct; stock preflight's
existing duplicate rejection is unchanged. No guessed fragment columns, redacted
text joins, stock span mapping or approval migration was introduced.

This resolves descriptive divergence accounting, **not** absent stock byte origin.
Even equal redacted records cannot establish that stock and adapter observed the
same bytes. Adapter localization does not prove Secret origin/use/harmlessness.
`packer_clearance_compatible` remains false; the independent stock snapshot,
disposition and integrity gates are unchanged.

## Actual challenge, review and validation

Question | Rubber-duck reasoning | Adversarial counterexample | Implemented decision
--- | --- | --- | ---
Can exact stock relationships be useful? | Compare full record plus measured file identity | Identical redacted records may describe different bytes | Descriptive associations, never origin proof
Can multiplicity be paired away? | Retain separate occurrence lists | Two stock rows versus one adapter row; equal duplicate groups | Count residuals; duplicates ambiguous
Can columns reconcile contexts? | Whole-file and stock fragments have distinct bases | Forced LF/CRLF boundary changes columns | Keep missing/extra records without guessed mapping
Can saved relationships be trusted? | Recompute from reverified reports | Forged group labels or stale namespace | Loader rejection before relationship return

Actual preimplementation explore challenge and postimplementation read-only
code review completed. No significant remaining code issue was reported.
The security specialist found no high-confidence vulnerability in its bounded
analysis; it did **not** provide independently authenticated finding approval or
replace the required service gate.

Corrected dedicated validation: **248 Python tests passed**, zero failures/skips
(40 adapter, 125 preflight, 53 review, 30 SQLite); **four Go test functions passed**
with eight large full-file parameter cases. Black/isort/Ruff/mypy/compilation,
Go build/vet/module verification and diff checks passed.
Five actual synthetic maintained preflights and five adapter scans/library calls
produced three equal and two forced LF/CRLF divergent cases: matched **3**,
missing-from-adapter **2**, extra-in-adapter **2**. Duplicate counts/ambiguity,
invalid associations, changed file identity and invalid ordinals were unit-tested;
forged group metadata and stale request bindings were rejected in all five
integration cases. These numbers are synthetic, not live archive findings.

**Validation incident:** the initial validator exceeded scope with unrequested
repository/history checks and an unrelated baseline modification, skipped required
integration/Go work, and claimed readiness. Those claims are rejected. The
initially clean baseline was restored byte-for-byte using apply_patch and verified
against HEAD; no baseline change remains. A corrected dedicated validator ran
the actual requested tests/checks without code edits. No unrequested scanner
output was adopted as a current inventory, approval or security-service pass.

## Current tooling, retention and security limits

Gitleaks **8.30.1** Linux amd64 archive bytes were freshly verified against the
official release API asset digest and independently fetched checksum metadata
before execution. Detect-secrets **1.5.0** was checked against a freshly hashed
official PyPI wheel and installed RECORD/package bytes; launcher/interpreter
binding was checked. Scanner and transitive dependency pins remain unchanged.

Go **1.25.0** ecosystem auto-toolchain/module verification completed using the
official proxy/sum database; no module replacements were present. The independent
direct official Go archive download failed DNS for its distribution host.
Do not claim that separate API-plus-official-archive verification passed; the
toolchain owner must close that provenance limitation before dependent operational
use. The adapter remains a local pinned-library build, not an official executable.

The corrected validator verified owner-private session-local runtime/artifact
handling. This is **nondurable**, not approved escrow or independent OS isolation.
Executable measurement/identity execution is not sandboxing; source endpoint
checks are not an atomic OS snapshot. The runtime owner must provide trusted
execution, containment and quiescence; the data owner must approve retention,
access and cleanup before operational evidence handling.

One post-commit CodeQL request for the new implementation **timed out**.
The tool explicitly prohibits a retry. This is not a pass; the required security
service gate remains incomplete. The bounded specialist/code reviews do not
replace it. No real-source epoch, semantic approvals, packing, PR creation,
merge, workflow mutation or deployment was authorized or performed.

Current source remeasurement, complete inventory and mapping/review counts are
**unavailable, not zero**. Historical checkpoint008 measurement recorded 16,533
entries and 124,233,523 bytes; it was not remeasured here and cannot bind this
session. Unrequested repository/history checks are not a real-source epoch.
Existing dirty startup metadata bytes were scanned/preserved in preparation.
Historical checkpoints and private material were not exported into Git.

## Next Iteration Follow-Up Prompt for Copilot Cloud Agent

Continue in `/home/runner/work/_codex_/_codex_`, using absolute paths. Read actual
HEAD/status, current agency policy, `.github/AGENTS.md`, `scripts/AGENTS.md`,
applicable instructions, this exact continuation, checkpoint011/checkpoint010,
`scripts/archive/CDX_SQLITE.md` and the 002/003 evidence contracts.
Never read `.github/agents/`. Preserve dirty work and the original archive.

1. Verify the checkpoint011 digest and introducing footer, and current consumer/
   producer bytes. Reconciliation is implemented; do not rebuild it as a plan-only
   substitute or silently upgrade historical runs. Retain separate raw multisets,
   identities, duplicates and missing/extra observations. Unique record equality
   is an association, not stock byte origin or transferable review approval.
2. Complete required security-service analysis in a genuinely authorized
   environment. Do not retry the timed-out tool invocation or call bounded
   reviews a waiver. Close the independent official Go archive provenance limit;
   verify current pinned tools for the actual OS/architecture using independent
   official API/checksum data before execution. Runtime Go modules require the
   official ecosystem verification. All versions remain pinned as documented.
3. Establish actual approved durable private retention, restored/current bound
   inventory, trusted isolated runtime and quiescent source. Session modes,
   caches, same-user keys and historical counts are not authority or continuity.
4. Only then evaluate readiness for the owner-authorized exact real-source epoch
   with reviewed compatibility requirements. A descriptive relationship cannot
   unblock stock clearance. Do not suppress unmatched rows or guess fragment
   origins. Obtain exact origin/use/harmlessness evidence and genuinely independent
   authenticated reviewer authority before any exact finding clearance.
5. No separate finding approvals or pack authorization exist. Do not create a PR,
   merge, dispatch/mutate workflows/settings, deploy or pack. Any future pack needs
   separate approval, maintained independent stock snapshot/rescan, dispositions,
   SQLite integrity, byte and Merkle verification.
6. Continue safe dependency-ready implementation rather than unsafe operation.
   Use actual preimplementation challenge and read-only review when changing
   behavior; dedicated focused validation with synthetic cases, not source scans.
   Require report_progress before the first edit, apply_patch edits and secret
   scanning before commits. Preserve/disclose existing dirty metadata captured
   by publication. Do not add helper workaround scripts or unneeded dependencies.
7. Persist the next unused checkpoint/continuation and update INDEX with the
   two-step actual introducing-SHA footer. Final handoff must include actual final
   HEAD, implementation/introduction SHAs, checkpoint digest/status, current versus
   historical measures, reconciliation metrics and remaining security/retention
   gates. Continue this chain until genuine authorized archive verification.

## Commit provenance

The actual introducing commit and checkpoint011 digest are appended only after
first publication, in a separate metadata commit.
