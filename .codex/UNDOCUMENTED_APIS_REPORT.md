# UNDOCUMENTED_APIS_REPORT

Date: 2026-07-07
Source: lane1-recon (recon-scout-agent)

## Executive Summary

High-priority documentation gaps are concentrated in cognitive APIs, services endpoint docs, and tool entrypoints.

## Findings

| ID | Area | Finding | Priority |
|---|---|---|---|
| UAPI-001 | cognitive_brain docs | Docs show imports that are not exported at package root | P0 |
| UAPI-002 | `src/codex/cognitive` | Exported cognitive API surface missing from docs/api | P1 |
| UAPI-003 | services | Service endpoint coverage in docs is incomplete vs implementation | P1 |
| UAPI-004 | `docs/codex/INDEX.md` | Placeholder-style index, weak API discoverability | P1 |
| UAPI-005 | `tools/docs_agent` CLI | Command catalog partially undocumented | P2 |
| UAPI-006 | general module docs | `[To be documented]` placeholders remain in high-traffic modules | P1 |

## Recommended Actions

1. Correct `cognitive_brain` import examples to match real exports.
2. Add canonical cognitive API reference under docs/api.
3. Add per-service endpoint matrix docs (`route`, auth, request, response, errors).
4. Replace placeholder codex index with curated module map.
5. Add docs for operational tool entrypoints (`tools/docs_agent`, `codex_run`, `codex_exec`).

## External Packaging Relevance

Accurate API contracts are required for external adopters to consume the downloadable repository without internal tribal knowledge.
