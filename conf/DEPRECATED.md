# ⚠️ DEPRECATED DIRECTORY

This directory (`conf/`) is deprecated. Please use `configs/` instead.

## Migration Guide

**For detailed migration instructions, see: [`misc/repo-owner-review/MIGRATION_GUIDE.md`](../misc/repo-owner-review/MIGRATION_GUIDE.md)**

### Quick Mapping

| Old Path (conf/) | New Path (configs/) |
|------------------|---------------------|
| `conf/config.yaml` | `configs/base/config.yaml` |
| `conf/data/local.yaml` | `configs/base/local.yaml` |
| `conf/evaluation/minimal.yaml` | `configs/evaluation/base.yaml` |
| `conf/experiment/basic.yaml` | `configs/experiments/basic.yaml` |
| `conf/experiment/default.yaml` | `configs/experiments/default.yaml` |
| `conf/experiment/sweep.yaml` | `configs/experiments/sweep.yaml` |
| `conf/minimal_eval.yaml` | `configs/development/minimal_eval.yaml` |
| `conf/minimal_train.yaml` | `configs/development/minimal_train.yaml` |
| `conf/model/base.yaml` | `configs/training/model/base.yaml` |
| `conf/training/minimal.yaml` | `configs/development/minimal.yaml` |

## Timeline

- **Current**: Deprecation warnings added (Dec 2025)
- **Grace Period**: 6 months (through Jun 2026)
- **Removal**: v2.0.0 (Q2 2026)

## What to Do

1. Check your code for references to `conf/` directory
2. Update references to use the equivalent `configs/` paths
3. Test your configuration still works
4. Report any issues to the repository maintainers

## Need Help?

- See [`misc/repo-owner-review/MIGRATION_GUIDE.md`](../misc/repo-owner-review/MIGRATION_GUIDE.md) for comprehensive instructions
- See `configs/README.md` for the new configuration structure
- Use `scripts/remediation/consolidate_configs.py` for automated migration
