# GitHub Actions Gated
- Workflows are disabled by default to prevent costs.
- To re-enable a workflow, move selected files back into `.github/workflows/`
  and ensure each job uses `runs-on: [self-hosted, linux]` and minimal triggers.
- Use `[skip ci]` on commits that should not trigger CI.
