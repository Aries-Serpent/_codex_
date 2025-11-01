# MSP Audit Gap Remediation Execution Blueprint (v1.2.0)

## Overview
This blueprint documents the implementation of gap surfacing, policy gates, enhanced reporting, and remediation guidance for the Copilot Space Capability Audit workflow.

## Version History
- v1.2.0 (2025-11-01): Gap remediation implementation with missing patterns, component gaps, policy gates
- v1.1.0: Component caps and duplication heuristic options
- v1.0.0: Initial capability audit framework

## Scope of Change

### Policy Extensions (.copilot-space/workflow.yaml)
- Added `options.fail_on_low_maturity` (default: true)
- Added `options.fail_on_missing_detector` (default: true)
- Retained `options.fail_on_score_regression` with `regression_delta_threshold: 0.02`

### Orchestrator Enhancements (audit_runner.py)
**Stage 4 (Scoring)**
- Propagate `required_patterns` into `capabilities_scored.json`

**Stage 5 (Gaps)**
- Compute `missing_patterns` per capability (required - found)
- Generate `component_gaps.json` with zero-value component inventory
- Include `missing_detectors` list (overrides not present in scored capabilities)
- Enhanced `gaps.json` with `low_maturity`, `missing_detectors`, and summary counts

**Stage 7 (Manifest)**
- Include `thresholds` snapshot for provenance
- Include `missing_detectors` list

**New Command: validate**
- Check low maturity gate (fail if any capability below threshold and flag enabled)
- Check missing detector gate (fail if overrides IDs missing and flag enabled)
- Emit deterministic markdown summary to stdout and GITHUB_STEP_SUMMARY

### Validators Module (validators.py)
New reusable module with:
- `check_low_threshold(gaps_path)` → (count, low_list)
- `check_missing_detectors(scored_path, overrides)` → missing_ids
- `emit_summary(low_list, missing_ids, thresholds)` → markdown text

### Template Updates (capability_matrix.md.j2)
- Show `Missing Patterns` column in low maturity table
- Display `(ZERO)` markers for zero-value components inline
- Use `thresholds.low` in summary (not heuristic approximation)
- Enhanced capability detail sections with missing patterns display

### CI Workflow (.github/workflows/capability-audit.yml)
- Run full S1–S7 pipeline
- Download baseline artifact (optional, continue-on-error)
- Regression gate: diff old vs new scores
- Validate gates: low threshold + missing detectors
- Upload artifacts with 90-day retention
- Upload new baseline for next run

### Developer Experience (space.mk)
- Added `space-validate` target for local gate checks

### Documentation
**Remediation Playbooks (docs/remediation/)**
- README.md: Index and usage guide
- components.md: How to improve each component score
- detectors.md: Detector contract, quality checks, troubleshooting
- policy.md: Gate tuning scenarios and defaults

**Validation Scripts (docs/validation/)**
- Gaps_Coverage_Checklist_And_Scripts.md: Ready-to-run validation scripts for completeness, primary deficit, zero components, missing patterns, missing detectors

**Copilot Grounding (.github/docs/)**
- Copilot_Audit_InstructionEnhancement.md: Suggested prompts and grounding sources

## Implementation Details

### Determinism Guarantees
- Sorted traversal of all collections
- Truncated file reads (MAX_READ_BYTES = 200,000)
- Template hash embedded in manifest
- No network calls; local-only operations
- Consistent (ZERO) text markers for automation

### Exit Codes
- 0: Success
- 1: General error
- 2: Missing files or invalid arguments
- 3: Score regression detected (diff command)
- 4: Gate validation failed (validate command)

### Artifact Retention
- CI artifacts: 90 days
- Baseline artifact: 90 days (uploaded after successful run)

## Testing Strategy

### Local Testing
```bash
make space-audit
make space-validate
# Run validation scripts from docs/validation/Gaps_Coverage_Checklist_And_Scripts.md
```

### CI Testing
**First run:**
- Diff step logs "No baseline found" (expected)
- Validate passes unless current repo has low maturity or missing detectors

**Subsequent runs:**
- Diff gate fails on regression beyond threshold
- Validate fails on policy violations

## Rollback Plan
- Toggle gates in .copilot-space/workflow.yaml (set fail_on_* flags to false)
- Revert audit_runner.py and template changes via single revert commit
- Disable CI workflow temporarily by renaming file or scoping to non-default branch

## Acceptance Criteria
- [x] component_gaps.json generated with zero components
- [x] gaps.json extended with missing_patterns and missing_detectors
- [x] validate command implemented with proper exit codes
- [x] CI wired to enforce gates
- [x] Template renders missing_patterns and (ZERO) markers
- [x] Template summary uses thresholds.low
- [x] Manifest includes thresholds and missing_detectors
- [x] Template_hash present in manifest
- [x] Remediation and validation docs created

## Risk Mitigation
| Risk | Mitigation |
|------|-----------|
| Aggressive gating fails builds | Adjust options.* flags in workflow.yaml; phased rollout |
| Detector drift over time | Follow docs/remediation/detectors.md; unit tests + overrides |
| False positives in patterns | Tune required_patterns; refine detectors; use explain command |
| Template changes affect determinism | Retain pure text markers; use template_hash detection |

## Future Enhancements
- Weighted component gates (not just zero checks)
- Historical trend tracking
- Automated remediation suggestions
- Integration with PR comments
