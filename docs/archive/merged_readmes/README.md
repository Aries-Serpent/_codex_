# Merged README Files

**Phase 13**: These README.md files were merged into their respective index.md files to resolve MkDocs warnings about conflicts.

## Files Archived

| Original Location | Merged Into | Archive Location |
|-------------------|-------------|------------------|
| `docs/README.md` | `docs/index.md` | `README_docs_root.md` |
| `docs/api/README.md` | `docs/api/index.md` | `README_api.md` |

## Reason

MkDocs treats both README.md and index.md as the directory index. When both exist, MkDocs excludes README.md with a warning:

```
WARNING - Excluding 'README.md' from the site because it conflicts with 'index.md'.
```

## Resolution

The content from README.md files was merged into their respective index.md files, and the original README.md files were archived here for reference.

---

*Archived: 2026-01-17 (Phase 13 - Strict Mode Enablement)*
