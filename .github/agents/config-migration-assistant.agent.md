---
name: config-migration-assistant
description: Assists with migrating configuration from legacy formats to Hydra-based configuration, ensuring backward compatibility and validation.
---

# Config Migration Assistant Agent

This agent assists with configuration migration from legacy formats to the modern Hydra-based configuration system implemented in PS-01.

## Capabilities

- **Legacy Format Detection**: Identifies configuration files in deprecated formats
- **Automatic Migration**: Converts legacy configs to Hydra YAML format
- **Validation**: Validates migrated configurations against schemas
- **Backward Compatibility**: Generates compatibility shims when needed

## When to Use

- When migrating from `conf/` to `configs/` directory
- When updating legacy argparse-based scripts to Hydra
- During PS-01 Configuration Consolidation implementation

## Migration Paths Supported

| From | To | Status |
|------|-----|--------|
| JSON config | Hydra YAML | ✅ Supported |
| ENV vars | Hydra overrides | ✅ Supported |
| argparse | @hydra.main | ✅ Supported |
| CSV data | Pydantic models | ✅ Supported |

## Integration

This agent integrates with:
- PS-01: Configuration Consolidation
- PS-07: Business Logic Elevation
- PS-09: Training Entry Point Unification
