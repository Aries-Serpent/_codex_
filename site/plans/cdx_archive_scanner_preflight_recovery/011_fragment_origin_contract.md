# 011 — Negative fragment proof; actual report adapter still needed

Entry HEAD: `4ac133c5c46a719c4fd17c3c004bcf1f380598f1`.
Implementation commit: `d221daf11bef92f538c1b74a36c7860afcd1e56b`.
Checkpoint009 status: **NEGATIVE_FRAGMENT_PROOF_COMPLETE_BLOCKED_REPORT_ADAPTER**.
This is a preparation checkpoint, not a scanner epoch. `archive_created: false`.

## What actually changed

The existing private span helper still rejects files at least 100,000 bytes.
Its reason is now `unsupported_fragment_origin`, distinct from small-file
encoding failures. No acceptance, disposition or scanner-mode bypass was added.
New tests prove why global line numbers plus fragment-local columns are
insufficient: LF/CRLF later-fragment first lines can map one byte early, and
midline fragments can alias identical report coordinates at different byte
intervals. Unicode byte positions and exact threshold/encoding cases are covered.
Assessment stays indeterminate; origin/use proofs and approvals remain unavailable.

208 focused tests passed (125 preflight, 53 review, 30 SQLite). Scoped
Ruff/Black/isort/mypy, compilation and diff checks passed. Four actual pinned
Gitleaks synthetic checks returned six observations and confirmed the negative
examples; those observations are not real archive findings. No raw report bytes,
matched values or source lines were published. Code review found no significant
issue. CodeQL analysis was skipped because its database was too large.

Linux x86_64: official Gitleaks 8.30.1 artifact verification used both release API
asset digests and separately fetched official checksum metadata before extraction.
Artifact SHA-256:
`551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`;
executable SHA-256:
`88f91962aa2f93ac6ab281d553b9e125f5197bbbce38f9f2437f7299c32e5509`.
Version and `dir --help` passed. No signature authority was established.
Detect-secrets reported 1.5.0; its previously supplied launcher digest requirement
remains waived. The official-wheel package comparison from checkpoint008 was
not repeated and is historical, not a new verification claim.

Fresh measurement of `/home/runner/work/_codex_/_codex_/.codex/archive`:
16,533 entries, 124,233,523 bytes; content identity version 1:
`2698b3c9f06c38d2bc87497ac149c251f969a0db6fb7c1c35ab1f2e281cd83f7`;
live SHA-256:
`ef7a1bdb43b224995d99de2699074a622867ef9fa67b73e7390aa52b036b0d19`.
The content digest matches checkpoint008, while live identity differs. This does
not restore historical keyed continuity or prove scan coverage.

No real-source scan, semantic batch, approval or packing ran. Current inventory,
mapping and replay counts are **unavailable, not zero**. Historical epoch007 only:
6,737 observations; 128 indeterminate; 6,609 unreviewed; one unsupported
large-file span. Its private bundle was not recovered. Initial publication
captured preexisting startup metadata without changing its bytes.

## Exact next dependency, not a blind rescan

The missing implementation is an execution-bound producer of actual fragment
origins. A span digest proves consistency, not what input the scanner observed.
A standalone mapper populated with caller-selected intervals would not solve this.
Stock CLI reports do not contain the missing origin; replaying CLI slices, even
with overlaps, changes regex context and cannot guarantee original observations
or arbitrary multi-line/unbounded rule coverage. Do not silently rechunk or dedup.

**Owner decision requested:** authorize development and synthetic validation of
a separately measured **Gitleaks v8.30.1 library report adapter**, plus review of
its maintained scanner/packer integration before real-source use. This means a
new explicit report mode, not a different scanner version or an approval to pack.

The adapter must retain actual byte intervals or explicit whole-file input at
acquisition and bind every observation privately to that invocation's input/output,
measured file, run namespace, selection, configuration and pinned toolchain.
It needs resource limits, correct LF/CRLF/UTF-8 mapping, explicit encoding/nested/
decoded-source limitations, tamper/staleness/ambiguity rejection, and fresh
observation identities. Whole-file mode changes detection context; historical
counts must not be forced. Its findings cannot be assumed compatible with the
existing packer's later independent stock scan. Resolve that compatibility before
using such records for clearance. No adapter is implemented or activated here.

## Next Iteration Follow-Up Prompt for Copilot Cloud Agent

Continue in `/home/runner/work/_codex_/_codex_` on the existing branch.
Read current policy, this handoff, checkpoint009 and the existing 002/003 contracts.
Record actual HEAD/status; preserve dirty work and historical archive bytes.

1. Do not repeat restore-only or real-scan loops. Obtain the concrete report-mode
   authorization described above, or actual authorized private retention and
   genuine authenticated review inputs. Metadata labels are not that authorization.
2. Before any real-source epoch, implement and synthetically prove actual
   acquisition-bound fragment origins and maintained packer compatibility. Keep
   stock large-file rejection intact until that complete contract exists.
   The renamed rejection code is not COORDINATE_SCOPE resolution or a zero count.
3. Keep pinned Gitleaks 8.30.1/detect-secrets 1.5.0. If Gitleaks is absent,
   verify official matching-platform release bytes against separately obtained
   official metadata before session-only extraction/execution. The historical
   missing Git tarball lookup is not working provisioning. Do not restore the
   waived supplied detect-secrets launcher digest; measure actual tool identity.
4. Keep version-1 content digest separate from live snapshot/finding bindings.
   Never rewrite timestamps, resurrect old keys, copy IDs or infer approval from
   matching content. Generate fresh identities only under an authorized new epoch.
5. Advance batches only from a new complete current bound inventory. Real
   origin/consumer evidence and attributable authenticated independent review
   remain required. Agents, fixtures, dead-code labels and HMAC possession are not
   approval. Packing needs separate authorization and maintained integrity/Merkle
   verification after its independent snapshot/rescan.
6. Save and conclude with an updated factual fenced Markdown block titled
   `### Next Iteration Follow-Up Prompt for Copilot Cloud Agent` until genuine
   authorized archive creation and verification. Include actual commit/checkpoint
   provenance, current-versus-historical measurements, exact remaining dependency
   and retention limits; never fabricate progress, counts or success.

## Commit provenance

The actual introducing commit and checkpoint009 digest will be appended after
the first publication, in a separate metadata commit.

Introducing commit: `5e0430d643f42f9ad1c753e77e9d2f0fd2fe7c28`.
Checkpoint009 SHA-256:
`384db3a1f9e077187a02d00432b8b6f4c1b4a762b7f2af628b1d06142eea3310`.
This footer is appended afterward in a separate metadata commit.
