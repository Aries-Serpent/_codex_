# Configuration Directory - Hydra-Managed Configs

**Status:** Active (PS-01 Configuration Consolidation)  
**Updated:** 2026-01-08

## Purpose

This directory (`conf/`) contains Hydra-managed configuration files following the [Hydra](https://hydra.cc/) framework conventions. This is the **preferred location** for new configuration files as part of the PS-01 Configuration Consolidation effort.

## Reversal of Previous Deprecation

**Previous Status:** This directory was previously marked as deprecated in favor of `configs/` (Dec 2025).

**New Status:** As of PS-01 (Jan 2026), this reversal is being implemented:
- `conf/` is now the **active** directory for Hydra-managed configs
- `configs/` will be gradually migrated here over 3 pre-commit cycles
- Both directories will coexist during the migration period (grace period: 6 months)

## Structure

```
conf/
├── config.yaml              # Root configuration with defaults
├── errors/
│   └── defaults.yaml        # Error definitions (PS-01 Cycle 1)
├── model/                   # Model configurations
├── data/                    # Data configurations  
├── training/                # Training configurations
├── evaluation/              # Evaluation configurations
├── experiment/              # Experiment configurations
└── ...                      # Additional config groups
```

## Usage

### Loading Configurations

Use the centralized config loader:

```python
from codex.utils.config_loader import load_config

# Load config with Hydra composition
cfg = load_config("base", config_dir="conf/training")

# With overrides
cfg = load_config("base", overrides=["model.hidden_size=768"])
```

### Creating New Configs

1. Place config files in appropriate group directory
2. Use Hydra defaults list for composition
3. Follow the schema in existing configs
4. Add tests for config loading

Example:
```yaml
# conf/training/my_config.yaml
defaults:
  - base
  - _self_

model:
  name: my_model
  hidden_size: 512
```

## Migration Status

See [`docs/configuration/MIGRATION_MAPPING.md`](../../docs/configuration/MIGRATION_MAPPING.md) for:
- Detailed migration plan
- Config inventory and mapping
- Timeline and priorities
- Testing strategy

### Quick Status

| Cycle | Focus | Status |
|-------|-------|--------|
| 1 | Error configs | ✅ Complete |
| 2 | Training/eval configs | 🔄 In Progress |
| 3 | Infrastructure configs | 📋 Planned |

## Backward Compatibility

The ConfigLoader supports both `conf/` and `configs/` during the migration period:

```python
# Both work during grace period
cfg1 = load_config("base", config_dir="conf/model")      # New
cfg2 = load_config("base", config_dir="configs/training/model")  # Legacy
```

Legacy paths will emit deprecation warnings starting Cycle 3.

## Documentation

- **Migration Guide:** `docs/configuration/HYDRA_MIGRATION_GUIDE.md`
- **Migration Mapping:** `docs/configuration/MIGRATION_MAPPING.md`
- **PS-01 Planset:** `.github/plans/PLANSET_01_CONFIGURATION_CONSOLIDATION.md`
- **ConfigLoader API:** `src/codex/utils/config_loader.py`

## Timeline

- **Current**: PS-01 Cycle 2 (Jan 2026) - Active migration
- **Grace Period**: Through Jul 2026 (both paths supported)
- **Final Migration**: v2.0.0 (Q3 2026) - `configs/` deprecated

## Contributing

When adding new configuration files:

1. ✅ **DO** place them in `conf/` with Hydra structure
2. ✅ **DO** use composition via defaults list
3. ✅ **DO** add unit tests for config loading
4. ❌ **DON'T** add new files to `configs/` (legacy path)
5. ❌ **DON'T** hardcode paths to config files

## Need Help?

- See migration documentation in `docs/configuration/`
- Check existing configs in this directory for examples
- Review tests in `tests/test_config_loader.py`
- File issues with "configuration" label

---

**Maintained By:** PS-01 Configuration Consolidation  
**Questions:** See migration documentation or file an issue

