# Status Updates

Use this folder to track repeatable, ring-by-ring progress for reasoning enablement.

## Template
- **Start from**: `docs/status_updates/TEMPLATE_status_update.md`
- **Save instances as**: `docs/status_updates/<slug>-<YYYY-MM-DD>.md`
- **Store attachments under**: `docs/status_updates/artifacts/<YYYY-MM-DD>-<slug>/`

## Quick Start
1) Copy the template:
```bash
cp docs/status_updates/TEMPLATE_status_update.md \
   docs/status_updates/m1-curriculum-2025-10-29.md
```
2) Fill all `<placeholder>` fields with actual data.
3) Compute readiness:
```text
R = α·E + β·T + γ·D
```
…with α+β+γ=1 and E,T,D ∈ [0,1].
4) Attach artifacts (metrics NDJSON, logs, reports) to:
```text
docs/status_updates/artifacts/2025-10-29-m1-curriculum/
```

## Best Practices
- Anchor each update to a specific branch/PR/commit
- Attach NDJSON metrics, logs, and generated reports as artifacts for auditability
- Keep “Gaps & Remediations” short, specific, and assigned to owners
- Update the changelog section to reference the previous status update file

## References
- Survey example: see any `docs/status_updates/survey-*.md` for structure
- Ring mentions: search for `0A_base_`, `0B_base_`, `0C_base_`, `0D_base_`, `main`
