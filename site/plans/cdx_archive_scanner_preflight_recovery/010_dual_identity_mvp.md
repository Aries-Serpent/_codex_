# 010 — Dual-identity MVP and fragment-origin prerequisite

Actual entry HEAD: `47db33587373e16a9a099f13733620e49d5f2ea6`, not the supplied
historical `046b021c86af676e702ce28e79ba7266af912ef9`.
Implementation commit: `9f1a249e84faf6b60ec59fc4a9555c79cff425d1`.
Checkpoint008 records **MVP_MEASUREMENT_COMPLETE_BLOCKED_COORDINATE_SCOPE**,
not a completed scanner epoch. `archive_created: false`.

## Executed MVP

- Waived only the previously supplied detect-secrets launcher digest requirement.
  Version 1.5.0 was checked; all 89 installed non-pyc package files matched the
  official pinned wheel, with zero mismatches/extras.
- Verified official Gitleaks 8.30.1 release bytes before session-local execution:
  release API asset digest and separately downloaded official checksums agreed.
  Artifact SHA-256:
  `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`;
  executable SHA-256:
  `88f91962aa2f93ac6ab281d553b9e125f5197bbbce38f9f2437f7299c32e5509`.
  Exact version and `dir --help` passed. No signature authority was established.
  No repository dependencies or persistent installation were changed.
- Both actual pinned scanners completed the existing contract on five synthetic
  clean files: both exit 0, zero findings. This is only a process smoke, not
  archive clearance or a producer epoch.
- Added version-1 `content_sha256` alongside unchanged live `sha256`.
  Sorted path/type/mode/size/payload rows omit only mtime. Empty directories and
  internal link targets remain bound. Producer/loader still require live identity;
  identical content cannot revive historical findings or approvals.
- Applied measurement read-only to
  `/home/runner/work/_codex_/_codex_/.codex/archive`: 16,533 entries,
  124,233,523 bytes; content digest
  `2698b3c9f06c38d2bc87497ac149c251f969a0db6fb7c1c35ab1f2e281cd83f7`;
  live digest
  `6877f93c0d084ee8110e5811e8ca68bf4016fd88e7cca92c9fa46ceca14cf2da`.
  No archived code was edited, classified as harmless, removed or packed.

Validation: 191 focused tests passed; scoped Ruff/Black/isort/mypy,
in-memory compilation and diff checks passed. Read-only code review found no
significant issue. CodeQL was skipped because its database was too large, not
successfully analyzed. Synthetic task-owned fixtures were cleaned up.
Initial publication captured preexisting startup metadata without changing bytes.

## Why large-file support was not fabricated

Official Gitleaks v8.30.1 `sources/file.go`, `sources/common.go`,
`detect/location.go`, `detect/detect.go` and `report/finding.go` demonstrate:
100,000-byte initial reads have variable lookahead, fragments can start mid-line,
and only line displacement is added to reported locations. Fragment-local first
line columns also differ from whole-file later-line origins. Ordinary redacted
reports omit the actual fragment byte origin. No stock CLI option forces
unfragmented full-file detection; max-target-size skips rather than fixes coverage.

Thus a whole-file LF index can return plausible but wrong spans. The existing
size guard remains intact. A future extension needs actual producer-bound fragment
origins or an explicitly unfragmented pinned report mode with synthetic proof and
resource limits. Either changes report provenance and requires fresh observations.
No new real-source scan was run while that pre-epoch condition remains unfinished.

## Next Iteration Follow-Up Prompt for Copilot Cloud Agent

Continue in `/home/runner/work/_codex_/_codex_` on the existing branch.
Read current policy, this handoff, checkpoint008, and the existing 002/003 contracts.
Record actual HEAD/status and preserve dirty work.

1. Do not reinstate the waived supplied detector launcher digest. Verify exact
   version and measure actual executable/package bytes; do not weaken pins.
2. If Gitleaks is absent, use official v8.30.1 Linux x64 bytes only on matching
   Linux x86_64 runners. Fetch release metadata and checksum metadata separately,
   verify the archive before bounded regular-member extraction to a session-only
   directory, then verify executable digest, version and `dir` support.
   The old `git show 15bff66a...` lookup was demonstrated unavailable; do not repeat
   it as working provisioning, install blindly, or persist tools in the repository.
3. Use content_identity_version 1 for descriptive cross-checkout identity; retain
   live filesystem identity for source/snapshot and finding bindings. New digests
   do not reconstruct absent epoch007 inputs or prove every byte was scanned.
4. Implement and prove an exact fragment-origin report contract before any
   conditionally authorized archive epoch. Do not remove the guard or reinterpret
   historical redacted columns. Resolve wrapper/tool/report authorization if a
   changed scanner mode is needed; no substitute binary version is authorized.
5. Alternatively ingest owner-supplied private retention and genuine authenticated
   review through authorized private access, validating every live binding.
   New epoch authorization is not authorization to copy IDs or advance stale
   queues. Select batches only from a new complete bound inventory.
6. Current archive inventory, mapping/replay counts and dispositions are unavailable,
   not zero. Historical epoch007 only: 6,737 observations; 128 indeterminate;
   6,609 unreviewed; one unsupported large-file span. No epoch008 was produced.
7. Keep exact origin/consumer evidence and attributable independent review gates.
   Agent labels, fixtures, apparent dead code and HMAC possession are not approval.
   Packing needs separate authorization and the existing independent rescan plus
   SQLite integrity/Merkle verification.
8. Save and conclude with the next factual fenced Markdown follow-up titled
   `### Next Iteration Follow-Up Prompt for Copilot Cloud Agent` until genuine
   authorized archive creation is verified. Report concrete remaining dependencies;
   do not fabricate resolution, current counts or automatic rescan loops.

## Commit provenance

Append the actual introducing commit and checkpoint digest after publication,
in a separate metadata commit; neither is self-referential.

Introducing commit: `11217b8185cd029c6c76bcaec2e5d490cc6b84c5`.
Checkpoint008 SHA-256:
`e18fbc51bbc3ff5fcd7f7439067eed17502e2d0dd4423ab1492cc5617c9b65cd`.
This footer is published in a subsequent metadata commit.
