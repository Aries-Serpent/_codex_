# .config.legacy/ — Historical Configuration Reference

This directory contains historical configuration files and deprecated
versions archived during Phase 3 root cleanup (2026-06-30).

## Purpose
- Traceability of configuration evolution
- Historical reference for pattern analysis
- Audit trail of legacy configurations
- Compliance and governance documentation

## NOT FOR ACTIVE USE
Current active configurations live in:
- `.codex/` - Active Codex configuration
- `.github/` - Active GitHub Actions configuration
- `docs/` - Active documentation
- `configs/` - Active application configs
- `config/` - Active configuration module

## Contents
See INVENTORY.txt for complete file listing.

## Legacy Configuration Archive
All files in this directory are read-only references.
DO NOT modify or depend on these files for active operations.

## Archive Policy
- **Access**: Read-only reference
- **Modification**: Prohibited
- **Retention**: Permanent (for governance)
- **Lifecycle**: Historical reference only
- **Created**: 2026-06-30T15:00:27Z

## Usage

To view legacy configurations:
```bash
ls -la .config.legacy/
cat .config.legacy/INVENTORY.txt
```

**IMPORTANT**: This directory is for historical traceability only.
For active configuration work, use the directories listed above.
