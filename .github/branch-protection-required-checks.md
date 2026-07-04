# Branch Protection Required Checks (main)

Require the following status checks before merge:

1. `premerge-triage-gate / triage-gate`
2. `agentic-diff-guard / deterministic-diff-guard`
3. `codeql-fix-verification / enforce-codeql-fix-discipline` (when label applies)
4. Existing validation checks (`mypy`, manifest drift, rust-ffi, etc.)

Also require:
- Pull request review before merge
- Dismiss stale approvals on new commits
- Restrict direct pushes to `main`