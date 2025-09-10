# Workflows Disabled by Default
These workflows are disabled to avoid accidental CI costs.
To re-enable:
1) Move a file back to `.github/workflows/`.
2) Require self-hosted runners only: `runs-on: self-hosted`.
3) Prefer `workflow_dispatch:` or restricted branches for triggers.
