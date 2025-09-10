{
  "suggestions": [
    {
      "area": "changelog",
      "action": "consolidate-index",
      "why": "multiple CHANGELOG_* files exist; provide index and link canonical CHANGELOG.md",
      "paths": [
        "docs/changelog/CHANGELOG_SESSION_LOGGING.md",
        "docs/changelog/CHANGELOG_Codex.md",
        "docs/changelog/CHANGELOG_codex.md",
        "docs/changelog/CHANGELOG_CODEX.md"
      ]
    },
    {
      "area": "scripts",
      "action": "reclassify",
      "target": "scripts/maintenance/ or .codex/archive/",
      "paths": [
        "codex_ast_upgrade.py",
        "run_next_stage.py"
      ]
    }
  ]
}
# Structure Audit

- **changelog**: consolidate-index — ['docs/changelog/CHANGELOG_SESSION_LOGGING.md', 'docs/changelog/CHANGELOG_Codex.md', 'docs/changelog/CHANGELOG_codex.md', 'docs/changelog/CHANGELOG_CODEX.md'] → 
- **scripts**: reclassify — ['codex_ast_upgrade.py', 'run_next_stage.py'] → 
