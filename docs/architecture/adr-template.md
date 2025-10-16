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

<!-- References:
ADRs: https://adr.github.io/
Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/
Keep a Changelog: https://keepachangelog.com/en/1.1.0/
SLSA / in-toto: https://slsa.dev/provenance , https://in-toto.io/docs/specs/
SBOM: SPDX https://spdx.github.io/spdx-spec/v3.0.1/model/Software/Classes/Sbom/ ; CycloneDX https://cyclonedx.org/specification/overview/
-->
