# Phase 2 Stabilisation Checklist

## Objective

Close the Phase 2 stabilisation gap with an explicit score gate and artifact check.

## Required checks

- Assigned-agent validation is complete.
- `audit_artifacts/capabilities_scored.json` exists.
- Minimum capability score threshold is `0.70`.

## Execution path

Run the completion governance workflow with `phase=phase-2-stabilisation`.

## Current intended verdict rule

- **Complete**: all required artifacts exist and all capabilities meet `0.70`
- **Partial**: artifacts exist but one or more capabilities are below `0.70`
- **Incomplete**: required artifacts are missing or assigned-agent validation fails
