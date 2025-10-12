# Zendesk Docs Capture Pipeline (Offline)

## TL;DR
```bash
codex zendesk docs-sync --dry-run   # Inspect URLs
codex zendesk docs-sync             # Download HTML snapshots
codex zendesk docs-catalog          # Regenerate Markdown catalog index
```

## Notes
- Sources come from `data/zendesk_docs_manifest.json`.
- Outputs go under `docs/vendors/zendesk/<YYYY-MM-DD>/...`.
- This pipeline never triggers CI and is safe for air-gapped/offline use later.
