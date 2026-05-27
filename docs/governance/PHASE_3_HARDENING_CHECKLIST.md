# Phase 3 Hardening Checklist

## Objective

Close the Phase 3 hardening gap with explicit gap-artifact generation and a higher score gate.

## Required checks

- Assigned-agent validation is complete.
- `audit_artifacts/capabilities_scored.json` exists.
- `audit_artifacts/gaps.json` exists.
- `audit_artifacts/component_gaps.json` exists.
- Minimum capability score threshold is `0.85`.

## Execution path

Run the completion governance workflow with `phase=phase-3-hardening`.

## Current intended verdict rule

- **Complete**: all required artifacts exist and all capabilities meet `0.85`
- **Partial**: artifacts exist but one or more capabilities are below `0.85`
- **Incomplete**: required artifacts are missing or assigned-agent validation fails
