# LFS Policy — Large-File Storage
**Last Updated:** 2026-10-22
**Version:** v0.3.0

Large binary artifacts must **not** be committed directly to Git. Use the guidelines below to handle any file that exceeds normal size limits or is unsuitable for text-based version control.

## When to Use Git LFS

Enable Git LFS for a file when **all** of the following are true:

1. The file is binary (model weights, compressed archives, datasets, audio/video).
2. The file must be version-controlled alongside code.
3. The file exceeds **50 MB** (hard limit) or **10 MB** (soft recommendation).

## Registering an LFS Track Pattern

```bash
git lfs track "*.safetensors"
git lfs track "data/*.parquet"
git add .gitattributes
```

Then commit the updated `.gitattributes`. All future files matching the pattern are stored in LFS.

## Preferred Alternatives

| Artifact Type | Preferred Storage |
|---------------|-------------------|
| Training run outputs | `.codex/` (gitignored) |
| Model checkpoints | External DVC remote or S3 |
| Datasets | DVC-tracked, not in Git |
| CI artifacts | GitHub Actions Artifacts (30-day retention) |

## Current Repository Baseline

- The repository does **not** force repo-wide Git LFS filters from `.gitattributes`; contributors opt in by adding explicit `git lfs track` patterns when needed.
- Copilot and Codespaces startup paths default to `GIT_LFS_SKIP_SMUDGE=1` so ordinary sessions do not fetch large blobs during checkout.
- Automatic setup accepts explicit narrow paths through
  `vars.COPILOT_LFS_INCLUDE_PATHS`; manual setup also accepts `lfs_include_paths`.
  An ML/RAG classification alone never authorizes downloads.
- Tasks can request required assets independently of dispatch:

  ```bash
  python scripts/ci/fetch_lfs_assets.py --include 'data/model.bin,artifacts/test fixture.bin'
  python scripts/ci/fetch_lfs_assets.py --include 'data/model.bin' --verify-only
  ```

  Patterns use Git LFS matching; commas separate patterns, spaces within paths
  are preserved. A concrete directory prefix is required. Every requested pattern
  must match a current-HEAD LFS pointer. Paths traversing symlinks, parent paths,
  control characters, and ambiguous comma/backslash/colon filenames are rejected.
- Default bounds: 32 paths/objects, 256 MiB **declared unique-object bytes**,
  180 seconds total including verification, two fetch attempts, two transfer
  workers, and no internal Git LFS retries. Budgets are checked before fetching;
  hashes/sizes are checked after materialization. These are expected-object
  budgets, not a server-side bandwidth/quota enforcement mechanism.
  CLI timeout overrides must remain finite, positive, and at most 600 seconds.
- Checkout uses positional selected paths, never `checkout --include`. Modified
  content is not overwritten; a mismatch fails verification. Missing objects,
  empty selections, unavailable access, timeouts and unresolved pointers are
  required failures, not warnings masked by `|| true`.
- Full mode is explicit opt-in:

  ```bash
  python scripts/ci/fetch_lfs_assets.py --mode full --allow-full
  ```

  It selects all **current-HEAD** LFS assets within the same budgets, not all
  historical refs. Automatic setup cannot implicitly enable full mode; manual
  `lfs_mode=full` is required there. Targeted failure never falls back to full.
- `--status PATH` writes machine-readable `ready`, `not-ready`, or `not-requested`
  status. A failed setup may still start the agent, so task-required assets must
  also be verified by task tests or `--verify-only`.
- HTTPS github.com setup authentication uses the short-lived setup token in
  memory, URL-scoped and never persisted. Other task CLI origins use their
  existing approved Git/LFS credentials. No token presence, local fixture, or
  checked-in snapshot proves real GitHub LFS authentication or quota.
- The audit found zero root LFS entries. Tiny local Git LFS fixtures validate the
  implementation, not hosted storage availability. Required hosts include the
  actual LFS batch/redirect storage endpoints, not just github.com. Do not disable
  firewall/approval controls to obtain assets; report denied/unavailable access.

## Guardrails

- The `.dvcignore` file excludes common large-file patterns from DVC tracking.
- Pre-commit hooks flag files >10 MB that are not tracked by LFS or DVC.
- Artifacts uploaded to GitHub Actions are subject to the 2 GB per-artifact limit under the GitHub Team plan.

## Compliance Check

```bash
git lfs ls-files           # list LFS-tracked files
git lfs status             # show pending LFS transfers
```
