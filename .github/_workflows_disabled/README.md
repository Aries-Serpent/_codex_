# Workflows Disabled (cost gating)
To re-enable a workflow: move it back to `.github/workflows/` **and** ensure each job uses:
  runs-on: self-hosted
Prefer `workflow_dispatch:` triggers or restricted branches.
