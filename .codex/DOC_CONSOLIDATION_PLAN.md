# DOC_CONSOLIDATION_PLAN

Date: 2026-07-07
Source: lane1-doc-consolidate (documentation-consolidator)

## Snapshot

- Large doc footprint across `.codex/` + `docs/`.
- Multiple archive/deprecated markers still present in active docs.
- Case-collision and quickstart duplication risk observed.

## Phased Plan

### Phase 0 — Canonical Map (Immediate)
- Publish canonical vs redirect vs historical map.
- Freeze creation of new top-level report docs unless critical.

### Phase 1 — Quick Consolidation
- Normalize redirect stubs.
- Consolidate overlapping status files.
- Move phase-specific report bundles out of root into structured subtrees.

### Phase 2 — Canonicalization
- Select one canonical architecture doc path.
- Select one canonical documentation index owner.
- Align consolidated agent documentation claims with registry reality.

### Phase 3 — Archive Hygiene
- Time-bucket historical outputs.
- Keep manifest of source->archive mappings.

### Phase 4 — Guardrails
- Add CI checks for case collisions, stale/deprecated marker misuse, and malformed metadata.

## Success Criteria

- Reduced root doc clutter.
- Single authoritative index path.
- Historical docs preserved but separated from active onboarding.
