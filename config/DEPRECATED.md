# ⚠️ DEPRECATED DIRECTORY

This directory (`config/`) is deprecated. Please use `configs/` instead.
SBOM workflows still read from this location for compatibility, but new
configuration should live in `configs/`.

## Migration Guide

Move all files from `config/` to:
- `configs/` - Main configuration directory
- `configs/production/` - Production configurations
- `configs/hydra/` - Hydra-specific configs

## Timeline

This directory will be removed in v2.0.0.

## What to Do

1. Copy your configuration files to `configs/`
2. Update any references in your code to use `configs/`
3. Test your configuration still works
4. Remove files from this directory

## Need Help?

See `configs/README.md` and `configs/CONFIGURATION_STRUCTURE.md` for the canonical configuration structure.
