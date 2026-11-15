# 02 — CodeQL Findings and Analysis Coverage

**Objective:** Resolve current CodeQL findings, if any, and confirm the analyzed source/configuration scope for PR #5766 without confusing a successful gate with complete alert coverage.

## 1. Refresh and bind evidence

1. Record current PR head/base SHAs and locate the exact check-run referenced by the user. The supplied ID `132676430005` did not resolve as an Actions job during the 2026-11-15 inspection; use current PR check-run/artifact metadata to identify its owning workflow and run.
2. Inspect the latest CodeQL gate logs, SARIF artifacts, language list, analysis invocation diagnostics, run attempt and source SHA through authorized GitHub tooling.
3. The observed gate run `43669524413` on `f6d4223cb94b255d1c6082deae761ce246255cfe` succeeded and logged 0 critical, 0 high and 0 medium findings. Retain this as historical evidence only. If no current alerts are available, report “inventory unavailable” rather than “zero alerts.”
4. The GitHub alert-list API returned 403 during the prior inspection. If still denied, request a current SARIF/alert export from an authorized security owner. Do not use a shell token, personal credential, or alternate endpoint.

## 2. Verify analyzer coverage

1. Inspect the active CodeQL workflow/configuration and compare the PR branch configuration to `main`. Record languages, paths, exclusions, query suites, action versions, and whether the run analyzes the PR head or a synthetic merge.
2. Confirm that analysis completed and SARIF was uploaded for every configured language. A skipped secondary workflow job is not a successful analysis for that language.
3. Verify that PR #5766 changes do not leave required source directories outside configured coverage. The repository continuation notes a prior `copilot/extension/` CodeQL-scope question; re-evaluate it against current workflow/configuration and changed paths rather than assuming it remains omitted or changing scope automatically.
4. Distinguish the three missing `container-scan.yml` GHAS configuration entries (handled in plan 01) from CodeQL analyzer coverage. Do not “fix” Trivy's configuration warning by weakening CodeQL or deleting a scanner.
5. If coverage expansion requires GitHub-side configuration or a security-owner choice, document the precise choice and owner; do not change repository settings without authorization.

## 3. Remediate only verified findings

1. For each current CodeQL alert, capture rule ID, severity, file/line, source and sink, dataflow, alert state, and the exact analyzed SHA.
2. Trace the finding through the affected code. Implement the smallest safe source fix and add a focused regression test demonstrating the unsafe path is rejected/contained.
3. If and only if a finding is demonstrated to be a false positive, document the specific invariant and evidence and request/record the authorized disposition. Do not add blanket suppressions or lower the gate threshold.
4. Run the focused tests, relevant Python/JavaScript checks, and existing static checks for changed files. Re-run CodeQL through normal authorized PR checks after changes; do not attempt a local full scan if the repository's supported environment cannot run it.
5. Bind the resulting SARIF and gate result to the final PR head SHA and run attempt. Check that the alert is resolved by a new analysis rather than by a missing/failed/empty SARIF upload.

## Completion criteria

- The exact current CodeQL check and all analyzer runs are identified and bound to the final SHA.
- Each current finding is fixed with tests or has an evidence-based owner disposition; missing alert access remains explicitly unresolved.
- Configured path/language coverage and SARIF upload are verified. No coverage gap is hidden by a successful summary job.
- The existing threshold and workflow permissions remain unchanged unless separately reviewed and authorized.
