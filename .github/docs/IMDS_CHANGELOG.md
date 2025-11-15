# IMDS Tooling CHANGELOG
> Generated: 2025-11-14 23:14:07 UTC | Updated: 2025-11-15 02:56:00 UTC | Author: mbaetiong

## [1.6.1] - 2025-11-15 🔴 CRITICAL BUG FIX
### Fixed
- **CRITICAL P1**: Fixed status reporting bug where failed remediations were incorrectly reported as `status:"ok"` in JSON output while script exited with code 2
  - Added new status value: `"remediation-failed"` for scenarios where `--apply` is used but no remediation actions could be applied
  - Added enhanced logging to status determination logic for better diagnostics
  - Added warning when partial remediation occurs (actions applied but issues persist)
  - **Impact**: Workflows gating on JSON status now correctly fail when remediation fails
  - **Root Cause**: Missing branch in status determination logic (lines 635-649)
  - **Test Coverage**: All 4 status scenarios validated (ok, recommended, applied, failed)

### Changed
- Enhanced JSON schema documentation with complete field descriptions and examples
- Updated status field to include all 4 values: `"ok"`, `"remediation-recommended"`, `"remediation-applied"`, `"remediation-failed"`
- Added CI/CD workflow gating examples to schema documentation

### Security
- No security impact; fix improves CI/CD safety gates

### Backward Compatibility
- ✅ **FULLY COMPATIBLE**: New `"remediation-failed"` status is treated as failure by existing workflows
- Workflows checking `status != "ok"` continue to work correctly
- No breaking changes to existing status values

## [1.6] - 2025-11-14
### Added
- Config loader (`.github/imds_config.yml`) for defaults: strict_approval, API version, default modes, issue_id.
- UFW & firewalld detectors (detection-only) with new error codes (`ufw_block_rule`, `firewalld_rule_imds`).
- Issue reference (`issue_ref`) now appears in JSON summary and audit JSONL.
- Workflow `imds_comment_on_issue.yml` to run diagnostics and comment results to the configured issue.

### Improved
- YAML parsing without external tools; graceful fallback when keys missing.
- Result summary line includes `issue_ref`.

### Security
- Approval token governance unchanged (hash only, no raw storage).

## [1.5] - 2025-11-14
- Env classification, runtime_ms, memory snapshot, HTML report.

## [1.4] - 2025-11-14
- Approval token governance, audit JSONL, self-test harness, metrics summary line.

## [1.3] - 2025-11-14
- Consolidation of overlapping PR variants, initial metrics output.

## [1.2] - 2025-11-14
- Routing, nftables inspection, DNS heuristic.

## [1.1] - 2025-11-14
- JSON summary, WALinuxAgent journal tail.

## [1.0] - 2025-11-14
- Initial diagnostic script & runbook.

Relates to: #2226
