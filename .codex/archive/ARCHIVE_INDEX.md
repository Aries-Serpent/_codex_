# Archive Index

**Updated:** 2026-11-04
**Scope:** Current `.codex/archive/` tree at the revision containing this index.

This index describes the archive's current top-level collections. The
collections contain historical and operational reference artifacts; they are
not candidates for removal solely because they are archived. Treat archived
content as read-only unless it is formally restored or separately approved for
migration.

## Collections

| Collection | Contents |
|---|---|
| `CI_INCIDENTS/` | CI incident records |
| `artifacts/` | Archived generated artifacts |
| `campaigns/` | Campaign records |
| `config_deprecated/` | Deprecated configuration |
| `deprecated/` | Deprecated reference material |
| `followup_prompts/` | Historical follow-up prompts |
| `historical/` | Historical documents |
| `implementations/` | Implementation records |
| `legacy-root/` | Historical `.codex` root archive; see its README and checksum sidecars |
| `misc/` | Miscellaneous archived records |
| `phase-9-campaign/` | Phase 9 campaign records |
| `phase-reports/` | Phase reports |
| `phase_logs/` | Phase logs |
| `phases/` | Phase records |
| `pr-resolutions/` | Pull request resolution records |
| `releases/` | Release records |
| `reports/` | Archive audit and other reports |
| `root-consolidation/` | Root-consolidation records and retained temporary outputs |
| `sessions/` | Session records; complete file inventory is in [`MANIFEST.json`](MANIFEST.json) |
| `status/` | Status records |
| `superseded_docs/` | Superseded documents |
| `v0.2.0_campaign/` | Version 0.2.0 campaign records |

## Sessions inventory

`.codex/archive/MANIFEST.json` is a path-based inventory of every tracked
regular file below `sessions/`, including Markdown summaries and Parquet
session records. It currently records 108 files (83 Markdown and 25 Parquet).
The inventory is relative to the archive root and includes nested paths.

## Integrity and restoration

The `legacy-root/checksums/` sidecars remain in place. Their exceptions and
verification state are recorded in
[`reports/SIDECAR_EXCEPTIONS.json`](reports/SIDECAR_EXCEPTIONS.json); do not
remove or rewrite sidecars as part of index maintenance. For restoration
guidance, consult [`legacy-root/README.md`](legacy-root/README.md).

## Historical consolidation note

The former index described a 2026-02-04 consolidation snapshot and listed
counts that do not describe the current archive tree. Those historical counts
are intentionally not presented as current metrics here.
