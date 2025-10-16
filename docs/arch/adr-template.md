# ADR: <Title — imperative, short>

- **Status**: Proposed | Accepted | Superseded by ADR-XXXX | Rejected
- **Date**: YYYY-MM-DD
- **Decision Type**: Archive | Rescue | Deprecate
- **Related Issues/PRs**: #123, #456
- **Owners**: @team/owners

## Context
What problem are we solving? List signals: age, refs/usage, coverage/ownership, deprecation markers, planner score. Link to planner report, SBOM reverse-deps, and any consumer impact analysis.

## Decision
Explain *what* we chose (e.g., archive with tombstone), scope (files/modules), and the effective version/date. Attach the evidence log `id` and tombstone paths.

## Consequences
- **Positive**: leaner tree, faster CI, reduced cognitive load.
- **Negative**: loss of local history; potential consumer churn.
- **Risks/Mitigations**: migration notes, compatibility shims, communication plan.

## Alternatives Considered
- Keep as-is
- Partial rescue (owner assigned, TODOs)
- Fork or split package

## Provenance & Compliance
- **Provenance**: attestation path(s) for the archival operation.
- **SBOM impact**: consumers reviewed (SPDX/CycloneDX reports).
- **Change log**: link to CHANGELOG entry.
