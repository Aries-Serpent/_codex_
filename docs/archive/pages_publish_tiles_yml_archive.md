# Archive Record: pages_publish_tiles.yml

**Archived**: 2025-11-02T23:29:34Z  
**Actor**: copilot  
**Reason**: legacy (violates repository policy prohibiting GitHub Actions workflows)

## Tombstone Details

| Property | Value |
|----------|-------|
| Tombstone ID | `7b799ac3-9da9-4d47-9d51-9e052c74a9d1` |
| SHA256 | `f9abea9ee43487a639343027cf399d6fb36e3ab36a38afd4f60d69d01bc1fd68` |
| Original Path | `.github/workflows/pages_publish_tiles.yml` |
| Size | 1217 bytes |
| Compressed | 568 bytes |
| Commit | `295acc84fccd6b8d35780695e7b37f159be7b747` |

## Restoration

To restore this file from the archive:

```bash
python -m codex.cli archive restore 7b799ac3-9da9-4d47-9d51-9e052c74a9d1 --out .github/workflows/pages_publish_tiles.yml
```

## Replacement

Functionality has been relocated to comply with repository policy:
- **New Location**: `.codex/scripts/publish_dashboard_tiles.sh`
- **Policy Compliance**: Automation artifacts confined to `.codex/` directory
- **Documentation**: See `docs/ops/pages_publish_tiles.md`

## Archive Evidence

The archival operation was logged in `.codex/evidence/archive_ops.jsonl`:

```json
{
  "action": "ARCHIVE",
  "actor": "copilot",
  "commit": "295acc84fccd6b8d35780695e7b37f159be7b747",
  "path": ".github/workflows/pages_publish_tiles.yml",
  "repo": "_codex_",
  "sha256": "f9abea9ee43487a639343027cf399d6fb36e3ab36a38afd4f60d69d01bc1fd68",
  "size": 1217,
  "tombstone": "7b799ac3-9da9-4d47-9d51-9e052c74a9d1",
  "ts": "2025-11-02T23:29:34Z"
}
```

## Policy Reference

Per repository archiving policy (docs/agents.md, docs/guides/AGENTS.md):
- **Prohibited**: Creating or activating GitHub Actions workflows
- **Required**: Automation artifacts must be confined to `.codex/` directory
- **Archival Process**: Files must be properly archived before deletion
  1. Archive using `codex.archive.api.store()`
  2. Log to `.codex/evidence/archive_ops.jsonl`
  3. Create tombstone stub
  4. Only then remove original file
