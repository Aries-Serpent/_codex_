# ⚠️ DEPRECATED DIRECTORY

This directory (`conf/`) is deprecated. Please use `configs/` instead.

## Migration Guide

Move all files from `conf/` to:
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

See `configs/README.md` for the new configuration structure.
