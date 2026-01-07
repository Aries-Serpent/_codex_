# Wiki Templates

This directory contains templates for auto-generating GitHub Wiki pages.

## Template Structure

| Template | Generated Page | Source |
|----------|---------------|--------|
| `Home.md.j2` | Home | README.md + project metadata |
| `Getting-Started.md.j2` | Getting Started | docs/QUICKSTART.md |
| `Architecture.md.j2` | Architecture | docs/ARCHITECTURE.md |
| `Security.md.j2` | Security | SECURITY.md + security docs |
| `API-Reference.md.j2` | API Reference | Auto-generated from docstrings |
| `Contributing.md.j2` | Contributing | CONTRIBUTING.md |
| `Changelog.md.j2` | Changelog | CHANGELOG.md |
| `Implementation-Plans.md.j2` | Implementation Plans | docs/implementation/ |
| `_Sidebar.md.j2` | Navigation Sidebar | Auto-generated |

## Template Variables

Templates have access to:

```python
{
    "repo_name": "Aries-Serpent/_codex_",
    "version": "1.0.0",
    "generated_at": "2025-12-24T10:00:00Z",
    "docs": {...},  # Parsed documentation files
    "api": {...},   # Auto-generated API documentation
}
```

## Regenerating Wiki

```bash
python scripts/space_traversal/wiki_generator.py
```

Or trigger the workflow:
```bash
gh workflow run wiki-assemble.yml
```

## Adding New Templates

1. Create `NewPage.md.j2` in this directory
2. Update `wiki_generator.py` to process the new template
3. Test locally before committing
