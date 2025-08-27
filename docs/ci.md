# CI Policy (Codex Environment)

- **Web search:** allowed for research/documentation.
- **Remote CI / GitHub Actions on hosted runners:** **disallowed** by default to avoid cost.
- All workflows in `.github/workflows/` are configured for manual runs only via `workflow_dispatch`, and **every job** is guarded with:
  ```yaml
  if: ${{ false }}
  ```

This prevents automatic execution on GitHub-hosted runners.

## How to re-enable *manually* (rare)

If you intentionally need to run a workflow, you may replace a job guard with a condition using manual inputs, still via `workflow_dispatch`. See GitHub docs for manual workflows and conditions. (2025-08-26T20:17:49Z)

For extra assurance, repository administrators can disable Actions entirely in **Settings → Actions → Disable Actions**.

