# GitHub Actions Gated
- Workflows are disabled by default to prevent costs.
- Repository OWNER must move selected YAMLs from `.github/workflows.disabled/`
  back into `.github/workflows/` when enabling CI.
- Every job must specify `runs-on: [self-hosted, linux]`.
- Use `[skip ci]` on commits that should not trigger CI.
