# Code Scanning Configuration Notes

> Last Updated: 2024-12-17
> Maintained by: Copilot Agent / @mbaetiong

## Current Configuration

| Setting | Value |
|---------|-------|
| **Configuration Type** | Organization Default |
| **Scanning Tool** | CodeQL |
| **Languages** | Python, JavaScript |
| **Schedule** | Weekly (Sunday 3 AM UTC) + Push/PR triggers |

## Migration History

### Previous Cycle-12-17: Migrated to Org Default

**Reason**: Resolve "Advanced setup conflict" with organization-level default code scanning.

**Changes Made**:
1. Created backup branch: `backup/codeql-advanced-YYYYMMDD-XXXXXXX`
2. Moved advanced workflows to `.github/disabled/`
3. Enabled organization default CodeQL workflow

**PRs**:
- Disable PR: #TBD
- Enable PR: #TBD

**Validation**:
- [ ] CodeQL workflow runs successfully
- [ ] Security alerts are being created
- [ ] Org conflict message cleared

## Rollback Procedure

If custom configuration is required:

1. **Restore from backup**:
   ```bash
   git checkout main
   git checkout backup/codeql-advanced-YYYYMMDD -- .github/workflows/
   git commit -m "restore: advanced CodeQL configuration"
   git push
   ```

2. **Request org exclusion**:
   - Open issue in `Aries-Serpent/.github`
   - Title: "Exclude _codex_ from org default code scanning"
   - Explain need for custom configuration

## Custom Query Preservation

If the repository had custom CodeQL queries:

1. **Location**: `.github/disabled-config/` (preserved)
2. **Future home**: `Aries-Serpent/codeql-packs` (to be created)
3. **Integration**: Reference packs in CodeQL init step

## Contact

- Security questions: @Aries-Serpent/security
- Configuration questions: @mbaetiong
