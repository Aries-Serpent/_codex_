# LFS Policy — Large-File Storage

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
- `copilot-setup-steps.yml` only re-enables LFS on `workflow_dispatch` runs when `lfs_mode=targeted` or `lfs_mode=full` is explicitly requested.

## Guardrails

- The `.dvcignore` file excludes common large-file patterns from DVC tracking.
- Pre-commit hooks flag files >10 MB that are not tracked by LFS or DVC.
- Artifacts uploaded to GitHub Actions are subject to the 2 GB per-artifact limit under the GitHub Team plan.

## Compliance Check

```bash
git lfs ls-files           # list LFS-tracked files
git lfs status             # show pending LFS transfers
```
