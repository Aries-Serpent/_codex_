---
deprecated: true
deprecated_since: 2025-10-24
replaced_by: ../canonical-archiving-policy.md
summary: "Superseded condensed archive policy excerpt."
---

# Archive Policy Summary (v2, Deprecated)

This short-form summary captured the same governance, cadence, and evidence expectations that now live in the
[Canonical Archiving Policy](../canonical-archiving-policy.md). It is retained only for provenance so that historical audit
artifacts referencing the "v2" summary still resolve to a readable document.

Key guidance now maintained in the canonical policy includes:

- Tombstone-first deletions that reference entries in `.codex/evidence/archive_ops.jsonl`.
- ADR requirements before removing code or documentation with external impact.
- Quarterly archive hygiene passes, including planner and vacuum tooling.
- CHANGELOG updates noting deprecations and removals.

Refer to the canonical policy for authoritative direction. New work MUST NOT depend on this deprecated summary.
