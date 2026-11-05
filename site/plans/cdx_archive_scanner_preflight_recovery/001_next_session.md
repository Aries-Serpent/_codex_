# 001 — Execute authoritative preparation and continuity recovery

Branch: `copilot/resume-cdx-archive-scanner-preflight-recovery`

Read the [series index](INDEX.md) and follow its safety and SHA-recording contract.

## Copyable execution prompt

Copilot Cloud Agent: execute the safe dependency-ready work below, not another
planning-only turn. Preserve all original archive content. This prompt describes
local investigation, focused tooling/tests and sanitized checkpoints; it grants
no archive creation or unrelated publication authority.

### 1. Recover once, without startup churn

- Record `git status --short --branch`, current HEAD and relevant branch/base
  deltas. Preserve dirty metadata; do not reset, stash, clean or rewrite it.
- Read current policy at
  `/home/runner/work/_codex_/_codex_/.codex/CODEBASE_AGENCY_POLICY.md`,
  applicable instructions, and maintained contracts:
  `/home/runner/work/_codex_/_codex_/scripts/archive/CDX_SQLITE.md`,
  `/home/runner/work/_codex_/_codex_/scripts/archive/cdx_common.py`,
  `/home/runner/work/_codex_/_codex_/scripts/archive/cdx_review.py`,
  `/home/runner/work/_codex_/_codex_/scripts/archive/codex_packer.py`.
- Read the latest numbered checkpoint in
  `/home/runner/work/_codex_/_codex_/.codex/tasks/issue5757/`.
  Checkpoint 002 is a historical starting anchor, not proof of today's source.
- Independently measure the exact selected source:
  `/home/runner/work/_codex_/_codex_/.codex/archive`.
  Use the checkpoint's documented fingerprint method; never alter bytes or
  timestamps to recreate its historical digest. Record entry count and selection.
- Check authorized private retention locations with bounded, no-follow private
  processing. Report availability and digest/permission checks only. An absent
  inventory is unavailable, not zero findings. Never expose a key location or value.

### 2. Assign bounded lanes, parent owns integration

| Lane | Independent work | Output |
| --- | --- | --- |
| A — provenance | Source/run/config/tool provenance and private lifecycle | Sanitized binding evidence and continuity decision |
| B — evidence readiness | Existing review authority and safe exact-context requirements | Actual trust mechanism or precise missing dependency |
| C — maintained tooling | Missing producer/binding and private assessment support | Scoped changes plus synthetic tests |

Use actual available custom-agent tools; no compulsory nesting or invented
agents. Do not send sensitive source, matched values or raw reports to prompts.
Parent owns shared checkpoints; avoid overlapping writes. Join lane results in
one bounded rubber-duck/adversarial review before integration.

### 3. Implement the first missing maintained increment

- Produce bindings from the actual source/private snapshot, effective selection,
  scanner configuration and toolchain. Caller-supplied digest equality alone is
  not provenance. Inspect prior art before adding logic.
- Represent full-tree preflight and packer-default selection explicitly. Preserve
  their distinction; do not add exclusions to suppress findings.
- Support bounded private exact-observation context, retaining distinctions
  between findings on one line. A redacted inventory cannot reconstruct omitted
  scanner records or a discarded HMAC key.
- Reuse hardened bounded/no-follow I/O where appropriate. Separate private
  assessment from accepted disposition generation.
- Keep `cdx_review` advisory. It currently rejects evidence/accepted states;
  listing those states in reports does not mean they are implemented.
- Add synthetic tests before enabling any new evidence/trust acceptance:
  forged labels, irrelevant digest-matched evidence, source/config changes,
  same-line observations, stale IDs, synthetic provenance, unsafe references
  and interrupted writes. Do not implement invented reviewer credentials.

### 4. Choose continuity and retention before a real scan

| Option | Selection condition | Adversarial check |
| --- | --- | --- |
| Reuse private inventory/key | Only independently recovered, safe and fully bound artifacts | Matching counts/paths do not prove continuity |
| One new epoch | Artifacts/key lost or current bindings materially changed | Old identities/approvals stay historical |
| Repeated orientation scans | Rejected | Cost and new IDs do not create semantic evidence |

The preceding session found the evidence directory absent. Reuse is not a live
choice unless recovery actually succeeds. Establish key/evidence retention first:
use an existing approved private mechanism if available, otherwise label
owner-only session retention as nondurable. Do not invent escrow.

After preparation is verified, perform at most one justified fresh preflight:
verify existing Gitleaks 8.30.1 and detect-secrets 1.5.0. If Gitleaks is missing,
obtain only the matching official release into private session-local storage,
verify independently obtained official checksum/signature metadata, and check
the `dir` command. No global installation, unverified mirror, remote script or
dependency churn. If unavailable, block the scan and continue synthetic work.

Use an exact private snapshot and `cdx_common.run_secret_scanners`, not the
packer. Disable network credential verification, retain captured reports
privately, and never print scanner output. Provision the HMAC key outside argv,
logs, history and repository files. Verify source/snapshot/config/tool identities
before and after. Keep inventory and key outside all scanned roots.

### 5. Verify, checkpoint and continue

- Run the smallest existing archive/review tests for changed code, plus new
  synthetic cases; run configured scoped lint/type/compilation checks and
  `git diff --check`. Report actual results and security-analysis limitations.
- Require both scanners to complete; reject drift, malformed/partial reports,
  changed source and unsuccessful execution. Findings mean unresolved clearance,
  even when scanner execution completed successfully.
- Atomically write the next unused sanitized checkpoint number. Record measured
  identities, private-retention status, namespace, exclusive counts, actual lane
  use, decisions, tests, blockers and exact next batch. Never overwrite history.
- Validate the final checkpoint digest after its last write. Keep private
  artifacts outside the repository; clean only task-owned paths no longer needed.

## Exit and next session

Success here means authoritative preparation is implemented and verified, with
either a complete current inventory or an exact scanner/retention blocker.
It does not mean clearance. Continue to
[002 — semantic review](002_semantic_review.md) only with a valid current baseline.
If scanning is blocked, continue independent producer/trust/synthetic-test work.

Before ending, create the next unused numbered continuation prompt in this
directory, describing the actual unfinished increment rather than copying this
entire prompt. Follow the index's introducing-commit SHA footer protocol.

## Commit provenance

Plan-body creation commit SHA: `816abf71fcf1868c18b91b063ac84a669d8dd9b8`.
Appended after creation in a separate metadata commit; not a self-referential SHA.
