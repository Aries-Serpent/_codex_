# Disabled Workflows

This directory contains workflows that have been disabled to resolve conflicts with organization-level default configurations.

## Reason for Disabling

The `Aries-Serpent` organization has enabled the "GitHub recommended (default) code scanning setup" at the organization level. Repositories with custom/advanced CodeQL configurations conflict with this setting.

## Backup Information

- **Backup Branch**: `backup/codeql-advanced-YYYYMMDD-XXXXXXX`
- **Disabled Date**: 2025-12-17
- **Disabled By**: Copilot Agent

## Restoration

To restore advanced CodeQL configuration:

1. Check out the backup branch:
   ```bash
   git checkout backup/codeql-advanced-YYYYMMDD-XXXXXXX
   ```

2. Copy files back:
   ```bash
   git checkout main
   git checkout backup/codeql-advanced-YYYYMMDD-XXXXXXX -- .github/workflows/codeql*.yml
   ```

3. Request exclusion from org-level defaults:
   - Open issue in `Aries-Serpent/.github` repository
   - Request `_codex_` be excluded from default code scanning

## Contact

For questions, contact @mbaetiong or the Aries-Serpent security team.
