# Non-workflow snapshot and evidence manifest

## Provenance and scope

- Source tip: `5980258483d8f03b6385562fc0940c52e183fb87`.
- Base: `71613ee000808ab758cc2f8ddb07a05c5101f731`.
- Recovered snapshot: `053409ad98ff3dc40243d1e132a1139e83ffaef7`, copying 332
  non-workflow paths without requiring original merge topology.
- Workflow changes were deliberately held back:
  `.github/workflows/copilot-setup-steps.yml`,
  `.github/workflows/deferral-language-gate.yml`,
  `.github/workflows/pypi-publish.yml`, and
  `.github/workflows/strict-no-deferral-security.yml`.

The implementation snapshot, policy/docs and regression tests are distinct from
the generated validation payload. Keep the implementation; do not interpret the
historical test artifacts as current results. See [`CONTEXT.md`](CONTEXT.md) for
the concise R1–R4 status.

## Pre-cleanup diff classification

At pre-cleanup PR head `e15df253c7f0facc2bbeda1e552ada1f0e050360`, comparison
with the base contained 1,761 changed paths. This inventory is a scope
classification, not line-by-line semantic review.

| Classification | Paths |
|---|---:|
| Recovered runtime implementation | 176 |
| Regression tests | 82 |
| Dependency/configuration changes | 4 |
| Intentional policy/docs/reports | 46 |
| Generated telemetry and timestamp-only metadata | 2 |
| Recovery evidence tree | 1,425 |
| Other configuration and repository files | 26 |

## Verified historical evidence retention

Before pruning the recovery payload, the assigned PR branch was independently
fetched into a fresh temporary bare Git object store, without local alternates.
The pre-cleanup evidence commit is
`e15df253c7f0facc2bbeda1e552ada1f0e050360`; it was the remote branch tip at
verification and contains every payload path being removed.

| Inventory at evidence commit | Files | Uncompressed blob bytes |
|---|---:|---:|
| `recovery/bfe2456b/` | 1,425 | 164,917,699 |
| `recovery/bfe2456b/validation/` | 1,423 | 164,877,898 |
| Retained root documents | 2 | 39,801 |

The independently fetched tree matched the local source commit for every
relative path, file mode, Git blob ID, and size. The SHA-256 inventory was
computed from every remotely fetched blob's content. The deterministic JSONL
index is available as the local export
`/tmp/pr5708-evidence-inventory.jsonl` (1,425 records); its SHA-256 is
`6dbb4f38c90eea14d55632dabafa7930a1568bd9158e44288d5b058c301b39d2`.

The index records path, mode, Git blob ID, size, and content SHA-256. The
inventory digest is SHA-256 over the exact JSONL bytes, with keys sorted and
compact JSON encoding. The removed payload remains recoverable through the
normal PR-branch history while that repository history remains accessible; this
is not an independent or indefinite archive. The older
`copilot/recovery-artifacts-bfe2456b` branch preserves the original export/state,
not this newer 1,423-file evidence inventory.

To retrieve an individual file from the preserved evidence commit:

```bash
git fetch origin copilot/recover-unpushed-session-commits-again
git merge-base --is-ancestor e15df253c7f0facc2bbeda1e552ada1f0e050360 FETCH_HEAD
git show e15df253c7f0facc2bbeda1e552ada1f0e050360:recovery/bfe2456b/validation/<exact-relative-path>
```

After cleanup, a second fresh bare object store fetched the assigned branch
without shared alternates. At that verification point, cleanup commit
`ed235eb14ef9b88b6c7ae006498767e7e18d8c17` contained the pre-cleanup evidence
commit as an ancestor. The complete 1,425-path inventory matched path, mode,
blob ID, size, and SHA-256 for every blob. The recovery tree had only the two
allowlisted documents and no validation descendants. The history fallback is
verified; it is still not an independent or indefinite archive. Do not rewrite
shared history or claim an external archive was created.

After the subsequent recovery-status update, the live branch was fetched again
at `1719d9d44f41f8fa8d8b9807160e4a37aab9f2ef`; the evidence commit remained an
ancestor and all inventory entries again matched. This later update changed
only the already-listed checkpoint and recovery-status documents.

## Payload disposition

Final-tree allowlist under `recovery/bfe2456b/`:

- `CONTEXT.md`
- `nonworkflow-manifest.md`

Every other descendant, including all of `validation/`, is execution evidence
and is removed from this implementation diff only after the immutable-history
verification above. The validation subtree included 220 `.coverage*` files
(93,978,624 bytes), 346 `.log` files (37,214,295 bytes), 276 `.xml` files
(2,539,217 bytes), and 441 process markers (2,885 bytes), plus other manifests,
summaries, and repeated/partial run outputs. These categories do not exhaust
the subtree.

Selected historical outcome summaries and package-version files had identical
copies across different attempts. Their run associations belong in the archived
inventory, not repeated implementation-tree payloads. A frozen PID/start
marker is not current process authority; partial or interrupted runs do not
establish full-suite or coverage success.

## Proposed implementation-tree state

At published commit `ed235eb14ef9b88b6c7ae006498767e7e18d8c17`, the PR tree
differs from the base in 337 paths. By root: `.codex` 14, `.github` 21,
`docs` 10, `recovery` 2, `scripts` 19, `src` 177, `tests` 82, and the
remaining root/configuration paths 12. No workflow path differs from the base.
The 16 synthetic campaign
records and timestamp-only startup-packet change are absent from the proposed
base diff. The only tracked recovery paths are the two documents listed above.

The published cleanup deletes exactly the 1,423 tracked paths under
`recovery/bfe2456b/validation/`; the independent post-push fetch and complete
inventory verification are documented above. The recovery procedure remains:

```bash
git fetch origin copilot/recover-unpushed-session-commits-again
git merge-base --is-ancestor e15df253c7f0facc2bbeda1e552ada1f0e050360 FETCH_HEAD
git show e15df253c7f0facc2bbeda1e552ada1f0e050360:recovery/bfe2456b/validation/<exact-relative-path>
```

## Current acceptance status

- R1 remains blocked: the instruction-contract selection reports 67 passed and
  2 failed because the two held workflows do not yet have the required
  `--warn-only` integration. No workflow was modified and the test was not
  weakened.
- R2 pruning is published; post-push ancestry and all 1,425 inventory entries
  were independently reverified. The Git history fallback is not an independent
  archive.
- R3 metrics output is isolated to a temporary path in tests. The campaign
  tests passed twice (43 each), and neither generated campaign records nor
  startup timestamp churn appears in the proposed base diff.
- R4 distinguishes ordinary-workflow compatibility from the held hosted setup
  contract, reports the retained filtered environment listing, and rejects
  added broad environment dumps in safe mutation tests.
- Current full-source mypy: 855 errors in 278 files, 1,972 checked, exit 1.
  Base comparison failed during package discovery (`self-healing` is not a
  valid Python package name), so this is not a regression delta or waiver.
- Ruff, source Black, targeted validator mypy and the 57-test
  Chronicle/auth/memory selection pass. The bootstrap/instruction selector
  reports 67 passed and 2 R1 failures. Pre-commit exits 1 on five existing
  AST class-size findings; other applicable hooks pass. CodeQL was skipped
  because its database is too large.
- Hosted checks on the published commit are `action_required`; the Validation
  Pipeline, Copilot Setup Steps Validation, and Nox runs have zero jobs. No
  workflow approval or dispatch was performed. These states do not establish
  executed CI success.
- Complete suite/80% coverage, accepted full-source type disposition, R1
  companion integration, and executed hosted checks remain open. Requested
  reviewer @mbaetiong must identify/confirm the workflow owner and authorize
  integration of the held workflow changes; no second-branch write is implied.

## Current workflow/validation handoff

At session entry the live PR head was `3eb98e97ae071f9852adc6384c6dec894e18204e`
(base `71613ee000808ab758cc2f8ddb07a05c5101f731`). It added only the
`generated_at` field change in `.codex/session_startup_packet.json` after the
verified cleanup. A later status push created `4508b16cd12ad6b8696d784de70eb7016614e1b6`;
the current index stages the base packet so the final PR diff drops that
timestamp-only path. The session-entry worktree bytes are saved at
`/tmp/pr5708-session-startup-dirty-3eb.json` (SHA-256
`cd4a86487f27a8b69e120ffa1d4ea72b10453b2957026ff732b4e4607b836cb2`) and must
be restored as an uncommitted local change after the corrective push. The
previously reported `8138605f…` file was absent at this session's entry; do not
claim those different bytes were recovered.

The current WEC has the five always-required boxes checked and all opt-in boxes
unchecked, including Nox and security. PR label `wec:auto-approve` is present
and is persistent; it is not evidence of selected workflows, approval, or
authorization to approve every pending run. No one-session label is present.
The default-branch registered Nox, Workflow Execution Gate, and Auto-Approve
workflows exist. Nox supports pull_request/workflow_dispatch but is one
sequential 60-minute job (policy, lint, typing, tests, security); it does not
split validation or upload failure diagnostics. The gate's check step is
initialization only. Auto-Approve offers `target_pr`/`target_run_id` and
one-session inputs, but no run-scoped dispatch or approval has occurred.

At session-entry head `3eb98e9…`, relevant runs all concluded
`action_required` with zero jobs, attempt 1: Nox `40065023097`, Auto-Approve
`40065023096`, Workflow Execution Gate `40065023219`, Security
`40065023089`, Enterprise Compliance/CodeQL `40065023081`, and Code Quality &
Coverage `40065023065`. Artifact queries for Nox, security, Enterprise
Compliance, Code Quality/Coverage, WEC, and Auto-Approve returned zero.
Therefore there are no hosted logs, manifests, JUnit, coverage, SARIF, or
other artifacts to retrieve; do not represent these runs as executed.

The previous local Nox full-suite collection stopped with 37 errors on
`a76c9fb`; a separate raw pytest probe in a mismatched environment ended at
133 collection errors. The repository CI environment lacked NumPy and real
torch/transformers installs, and root-local optional-dependency shims were on
the import path. These runs do not isolate source regressions or prove an
Actions-hosted result. Neither produced a complete node inventory or coverage.
Do not rerun a monolithic local suite.

After the session-entry snapshot, the status push created head
`4508b16cd12ad6b8696d784de70eb7016614e1b6`. Its relevant attempt-1 runs are
Nox `40067306514`, Auto-Approve `40067306528`, WEC `40067306494`, Security
`40067306501`, Enterprise Compliance/CodeQL `40067306511`, and Code Quality &
Coverage `40067306496`; all are `action_required`. Nox, Auto-Approve, WEC and
Enterprise Compliance have zero jobs; artifact queries for Nox, Security,
Enterprise Compliance, and Code Quality/Coverage returned zero.

The next agent should obtain the exact authorized human selection and approval
for the validation run IDs and confirm the workflow owner can publish the R1
companion change. Then monitor actual jobs and retrieve bounded artifacts after
they exist; do not dispatch or approve the persistent all-pending path. Full
suite/coverage, R1, comparable mypy disposition, five AST findings, and
CodeQL remain open.
