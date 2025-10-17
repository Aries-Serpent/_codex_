# ADR: Retire legacy status reports from the repository root

- **Status**: Accepted
- **Date**: 2025-10-17
- **Decision Type**: Archive
- **Related Issues/PRs**: N/A
- **Owners**: @mbaetiong

## Context
The repository root accumulated one-off status updates, audit exports, and planning notes that are no longer maintained. These
artifacts predate the current documentation structure in `docs/` and lacked an ownership model, which allowed the top level to
balloon with stale markdown. The October archive plan (`root-cleanup-2025-10-17`) evaluated the aged files, noted that they have
superseding runbooks or dashboards, and confirmed no active tooling depends on them. The codex archive evidence log captured the
removal intent alongside deterministic tombstone identifiers for traceability.

## Decision
Archive the following files from the repository root effective 2025-10-17, using the plan recorded at
`.codex/evidence/artifacts/archive_plan_root_cleanup_2025-10-17.json`:

- `Codex_Questions.md` → tombstone `8e3531b9-c839-4a07-9dec-507c36136eb1`
- `_codex_status_update-0C_base_-2025-09-27.md` → tombstone `ff1f4dc7-e9a9-4db1-9730-cd268ed4fd09`
- `_codex_status_update-2025-10-06.md` → tombstone `1bd4c1f1-6165-4d8e-8a25-5121b511d577`
- `_codex_status_update-2025-10-16.md` → tombstone `2d4d2f9d-e63f-4e69-8bb6-fe1158435431`
- `done_resolution_plans_10-6_to_10-7.md` → tombstone `b131ecc9-21a2-4cb0-bf75-e56921b157bd`
- `CODEBASE_AUDIT_2025-08-26_203612.md` → tombstone `f89cbae8-099b-4a4c-b016-9189ab6664b6`
- `CODEBASE_AUDIT_2025-09-27_ITERATION3.md` → tombstone `a778bb0d-fd03-4642-a92d-55f28c68b193`
- `_codex_codex-ready-sequence-and-patches-2025-09-27.md` → tombstone `94ba1b35-5745-40d6-8f08-8b3d0a62f786`
- `codex_ready_sequence-2025-10-16.md` → tombstone `4c758c95-3c0b-4b5d-8bc7-27cc5c6f79d9`
- `todo_resolution_plans_10-6_to_10-7.txt` → tombstone `a6195756-ef7c-42de-b7dc-435bbbdca91e`

The archive operations are tracked in `.codex/evidence/archive_ops.jsonl`, including the attestation pointer recorded at
`2025-10-17T06:36:49Z`.

## Consequences
- **Positive**: reduces noise in the repository root, clarifies the authoritative locations for status updates, and keeps
  newcomers focused on current documentation.
- **Negative**: local clones lose immediate access to historical status snapshots; contributors must consult the archive bucket
  when referencing historical planning material.
- **Risks/Mitigations**: communicated the change in the changelog, retained tombstone identifiers for recovery, and captured
  provenance artefacts so the audit trail links back to the decision and plan.

## Alternatives Considered
- Keep as-is
- Partial rescue (owner assigned, TODOs)
- Fork or split package

## Provenance & Compliance
- **Provenance**: `.codex/evidence/provenance/root-cleanup/intoto.jsonl`, `.codex/evidence/provenance/root-cleanup/slsa.json`
- **SBOM impact**: no executable components involved; SBOM unchanged.
- **Change log**: see `CHANGELOG.md` entry dated 2025-10-17 under the Unreleased section.
