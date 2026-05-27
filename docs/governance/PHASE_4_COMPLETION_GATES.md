# Phase 4 Completion Gates

## Objective

Close the Phase 4 completion-governance gap with a final threshold gate, manifest requirement, and regression check against the remediation baseline.

## Required checks

- Assigned-agent validation is complete.
- `audit_artifacts/capabilities_scored.json` exists.
- `audit_artifacts/gaps.json` exists.
- `audit_artifacts/component_gaps.json` exists.
- `audit_run_manifest.json` exists.
- Minimum capability score threshold is `0.90`.
- No capability regresses by more than `0.02` against `baseline/capabilities_scored_post_remediation.json`.

## Execution path

Run the completion governance workflow with `phase=phase-4-completion-governance`.

## Current intended verdict rule

- **Complete**: all required artifacts exist, all capabilities meet `0.90`, and no excessive regression is detected
- **Partial**: artifacts exist but either the threshold or regression rule fails
- **Incomplete**: required artifacts are missing or assigned-agent validation fails
