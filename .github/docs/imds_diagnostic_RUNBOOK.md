# IMDS Diagnostic Runbook
> Generated: 2025-11-14 21:33:15 UTC | Author: mbaetiong  
> Script Version: 1.6 | Last Updated: 2025-11-14T23:14:07Z UTC

## Purpose
This runbook describes the IMDS diagnostic script added to the repository to detect and (optionally) remediate issues that block access to the Azure Instance Metadata Service (IMDS - 169.254.169.254). The script is intended to run on affected hosts (runners or VMs) and helps resolve failures observed in issue #2226.

## Files added
- .github/scripts/imds_diagnostic.sh — main script (read-only by default; remediation behind `--apply`)
- .github/docs/imds_diagnostic_RUNBOOK.md — this runbook

## Safety & Operational Notes
- Default behavior is read-only diagnostics; the script will not change system configuration unless `--apply` is provided.
- Use `--dry-run` to simulate remediation steps without applying them.
- Remediation requires root privileges and should be run only after approval from the CODEOWNER or on maintenance windows.
- The script produces `diagnostic_results.txt` in the current working directory. Attach this file to issue #2226 for triage.
- Remediation steps are intentionally minimal and reversible when possible (e.g., /etc/hosts backup).

## How to run
1. Clone the repo and check out the branch:
   ```bash
   git fetch origin
   git checkout imds/diagnostic-2226-20251114T213200
   ```

2. Run diagnostics (read-only):
   ```bash
   bash .github/scripts/imds_diagnostic.sh
   # or:
   ./.github/scripts/imds_diagnostic.sh
   ```

3. Simulate remediation (no changes):
   ```bash
   bash .github/scripts/imds_diagnostic.sh --dry-run
   ```

4. Apply remediation (REQUIRES root; must have explicit approval from @mbaetiong):
   ```bash
   sudo bash .github/scripts/imds_diagnostic.sh --apply
   ```

## Expected outputs
- `diagnostic_results.txt` — full log of checks and any remediation attempts
- Exit codes:
  - `0` = diagnostics ran and no remediation required
  - `2` = remediation recommended but not applied
  - `3` = remediation applied successfully
  - `1` = error occurred

## Example PR & Issue update text (for maintainers / agents)
- PR title: `Add IMDS diagnostic script + runbook (relates to #2226)`
- PR body:
  - What: Adds `.github/scripts/imds_diagnostic.sh` and runbook.
  - Why: Address firewall/IMDS-block issues observed in issue #2226.
  - How to test: run script in read-only mode on affected host; attach `diagnostic_results.txt` to #2226.
  - Remediation: `--apply` flag available but requires explicit approval from @mbaetiong.
  - Request reviewers: @mbaetiong, @Copilot
  - Labels: `bug`, `needs-triage`

- Issue #2226 comment (sample):
  > I added an IMDS diagnostic script and a runbook: `.github/scripts/imds_diagnostic.sh` and `.github/docs/imds_diagnostic_RUNBOOK.md`.
  > Please run the script in read-only mode on any affected hosts:
  > ```
  > bash .github/scripts/imds_diagnostic.sh
  > ```
  > Attach `diagnostic_results.txt` to this issue. If remediation is required, discuss and approve `--apply` remediation with @mbaetiong before running.

## Contacts
- Primary contact for approval: @mbaetiong
- Reviewer: @Copilot
