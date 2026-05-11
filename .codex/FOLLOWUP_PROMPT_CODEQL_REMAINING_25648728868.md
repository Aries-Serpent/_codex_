# Follow-up Prompt — CodeQL Verification Sweep (Artifact run 25648728868)

Use this prompt in the next Copilot session to continue from S930:

```text
@copilot continue and verify all CodeQL alerts from artifact
`codeql-alerts-open-codeql-25648728868` (sha256:9ab2851104147588b9abb2f47eaf550e0a7286a84945600417b947724c34cd33).

Completed in S930:
- Resolved all 50 alerts listed in alerts_fixable.md directly in code/workflows.
- Resolved the remaining artifact classes by:
  - pinning all remaining unpinned third-party workflow actions to immutable SHAs.
  - reducing CodeQL Advanced to security-focused packs and loading
    `./.codeql/codeql-config.yml` (which excludes test/doc/config noise).
  - removing the `actions` language leg from `codeql.yml` advanced matrix
    to stop non-actionable workflow-style findings from resurfacing.

Completed in S932:
- Added PR-time rebase-churn guard in `agent-auth-delegation.yml` so housekeeping
  commits (`chore(auth)` / `chore(d00)`) are skipped on `pull_request` events.
- Added sweep-push guard in `iterative-self-healing-ci.yml` so universal baseline
  sweep does not auto-push to active PR branches or protected branches with open PRs.

Execution requirements:
1) Use the already-green CodeQL verification point:
   - `codeql-analysis.yml` run `25649802257` (success on `d0d1aea`)
   - `codeql.yml` run `25649802298` (success on `d0d1aea`)
2) Trigger `codeql-alert-fetcher.yml` on the latest branch head and download `alerts_raw.json`.
3) Confirm no carryover from the original 249-alert set.
4) If any residual alerts remain, patch only residuals and re-run fetcher.
5) Update CHANGELOG + AGENT_ACCOUNTABILITY_REPORT with final post-run count.
```
