# Archive & Deprecation Policy Index

> Last updated: 2025-10-24
> Status: Canonical policy consolidated; historical summaries retained for reference only.

This directory hosts the authoritative guidance for archiving and deprecating code or documentation within the repository. The
materials here replace the prior scattering of notes across audit artifacts and planning documents.

## Canonical Policy

- 📄 [Canonical Archiving Policy](./canonical-archiving-policy.md)
  - Covers governance, cadence, evidence logging, PR checklist expectations, hygiene passes, repository archival, and retention
    practices.
  - References required evidence artifacts such as `.codex/evidence/archive_ops.jsonl` and ADRs in `docs/arch/`.

## Deprecated Summaries

Historical summaries from the earlier consolidation effort remain available for traceability. Do not rely on these for future
work; the canonical policy above is the single source of truth.

| Variant | Deprecated On | Notes |
| --- | --- | --- |
| [v2 Summary](./_deprecated/v2-archiving-summary.md) | 2025-10-24 | Condensed excerpt retained only for provenance. |
| [v3 Summary](./_deprecated/v3-archiving-summary.md) | 2025-10-24 | Alternative phrasing superseded by canonical guidance. |
| [v4 Summary](./_deprecated/v4-archiving-summary.md) | 2025-10-24 | Legacy abstraction kept for audit trails. |

## Related Artifacts

- ADR: [Root Docs Cleanup](../adr-Previous Cycle-10-17-root-docs-cleanup.md)
- Evidence log: [Archive operations](../../../.codex/evidence/archive_ops.jsonl)
- Branch protection requirements: [Archive PR checklist](../../policies/branch-protection-checklist.md)
- Runbook: [Codex archive workflow](../../guides/codex_archive_runbook.md)

## Operational Playbooks

- [Archive policy consolidation PR plan](./archive-policy-pr-plan.md): step-by-step workflow for publishing commit `cfba4786`.

## Validation Checklist

When applying this policy in a pull request:

1. Draft or reference an ADR documenting the archival decision.
2. Replace removed artifacts with tombstone stubs that cite the evidence entry.
3. Append an event to `.codex/evidence/archive_ops.jsonl` with the tombstone metadata.
4. Update the CHANGELOG with the deprecated or removed items.
5. Run archive hygiene tooling (planner, vacuum) for batch cleanups as needed.
6. Request CODEOWNERS review to validate provenance.

## Maintainers

- Codex platform operations
- Repository stewards responsible for archive hygiene

If questions arise, open an issue referencing this index and the associated ADR.
