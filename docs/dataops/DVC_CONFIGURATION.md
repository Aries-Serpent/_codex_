# DVC Configuration for Knowledge Data

## Quick Setup

```bash
# Track knowledge data with DVC
dvc add data/knowledge/zendesk/

# Commit to git
git add data/knowledge/zendesk.dvc .gitignore
git commit -m "Track Zendesk knowledge with DVC"

# Push to DVC remote
dvc push
```

## Best Practices

1. **Metadata in Git, Data in DVC**
   - Git: `data/zendesk_api_index.json` (small)
   - DVC: `data/knowledge/zendesk/` (large)

2. **PII Scrubbing MANDATORY**
   - Crawler service handles automatically
   - Never commit unscrubbed data

3. **30-Day Retention**
   - Keep last 30 days of syncs
   - Clean up old data regularly

---

**Last Updated:** 2026-01-08
