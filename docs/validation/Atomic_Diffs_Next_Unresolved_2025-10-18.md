# [Validation]: Atomic Diffs — Next/Unresolved (v1.1.0)
> Generated: 2026-06-22 (audited) | Author: mbaetiong

 Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## Remaining Gaps (Minor)

| Gap | Impact | Proposed Patch | Status |
|-----|--------|----------------|--------|
| Detector meta in report | Low | Surface `meta` in detail sections | in-progress |
| Component caps | Low | Optional `scoring.component_caps` clamp | in-progress |
| Dup heuristic v2 | Low | Token-similarity (scaffold in dup_similarity.py) | deferred (opt-in) |

## Notes
- Meta rendering and component caps are being implemented in S4 and template.
- Dup heuristic v2 ships as scaffold, opt-in via config; defaults remain "simple".
