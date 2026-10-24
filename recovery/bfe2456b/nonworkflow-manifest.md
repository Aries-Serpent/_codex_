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

The evidence commit's reachability must be rechecked after cleanup. Do not
rewrite shared history or claim an external archive was created.

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

At the current pre-commit snapshot, the proposed PR tree differs from the base
in 337 paths. By root: `.codex` 14, `.github` 21, `docs` 10, `recovery` 2,
`scripts` 19, `src` 177, `tests` 82, and the remaining root/configuration
paths 12. No workflow path differs from the base. The 16 synthetic campaign
records and timestamp-only startup-packet change are absent from the proposed
base diff. The only tracked recovery paths are the two documents listed above.

The current staged prune deletes exactly the 1,423 tracked paths under
`recovery/bfe2456b/validation/`; the independent fetch and complete inventory
verification are documented above. Recheck the remote PR tip after publishing
the cleanup: prove `e15df253c7f0facc2bbeda1e552ada1f0e050360` is an ancestor and
recompute the full path/mode/blob/size/content-hash inventory before claiming
post-cleanup retention.

## Current acceptance status

- R1 remains blocked: the instruction-contract selection reports 67 passed and
  2 failed because the two held workflows do not yet have the required
  `--warn-only` integration. No workflow was modified and the test was not
  weakened.
- R2 pruning is prepared; after push, remote ancestry and inventory verification
  are still required. The Git history fallback is not an independent archive.
- R3 metrics output is isolated to a temporary path in tests. The campaign
  tests passed twice (43 each), and neither generated campaign records nor
  startup timestamp churn appears in the proposed base diff.
- R4 distinguishes ordinary-workflow compatibility from the held hosted setup
  contract, reports the retained filtered environment listing, and rejects
  added broad environment dumps in safe mutation tests.
- Current full-source mypy: 855 errors in 278 files, 1,972 checked, exit 1.
  Base comparison failed during package discovery (`self-healing` is not a
  valid Python package name), so this is not a regression delta or waiver.
- Complete suite/80% coverage, post-cleanup remote verification, remaining
  final checks, R1 companion integration, and hosted check execution remain
  open. `action_required`/zero-job workflow states are not successful runs.
