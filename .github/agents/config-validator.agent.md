---
name: config-validator
description: Validates Hydra configuration files for schema compliance, type safety, and consistency across the codebase.
---

# Config Validator Agent

This agent validates Hydra configuration files to ensure schema compliance and type safety as part of the PS-01 Configuration Consolidation planset.

## Capabilities

- **Schema Validation**: Validates YAML configs against Pydantic schemas
- **Type Checking**: Ensures all config values match expected types
- **Consistency Checks**: Verifies configuration consistency across environments
- **Missing Value Detection**: Identifies required fields that are missing

## When to Use

- Before committing configuration changes
- During CI/CD pipeline validation
- When troubleshooting configuration-related errors

## Validation Rules

1. All required fields must be present
2. Types must match schema definitions
3. Values must be within valid ranges
4. Cross-references must resolve correctly

## Integration

This agent integrates with:
- PS-01: Configuration Consolidation
- Hydra configuration system
- Pydantic schema validation
