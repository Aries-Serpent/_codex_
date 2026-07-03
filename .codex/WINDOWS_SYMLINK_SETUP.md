# Windows Symlink Setup Guide

This repository uses symlinks for convenience and code organization. However, Windows does not support symlinks natively without admin privileges or special configuration. This guide provides setup instructions for different platforms.

## Background

The following symlinks were tracked in git but have been removed for cross-platform compatibility:

| Symlink | Target | Purpose |
|---------|--------|---------|
| `.codex/security_vulnerability_scan_latest.md` | `security_vulnerability_scan_*.md` | Latest security scan report |
| `configs/data` | `training/data/` | Training data directory |
| `configs/model` | `training/model/` | Model directory |
| `configs/tracking` | `training/tracking/` | Tracking directory |
| `configs/train` | `training/profiles/` | Training profiles |
| `scripts/audit_pipeline.py` | `../src/codex_ml/cli/audit_pipeline.py` | Audit pipeline script |
| `scripts/ci/session_preload.py` | `../../.github/scripts/session_preload.py` | Session preload script |

## Setup Instructions

### Linux/macOS (Automatic)

Run the setup script after cloning:

```bash
scripts/setup/create_symlinks.sh
```

Or manually create symlinks:

```bash
cd /home/runner/work/_codex_/_codex_
ln -s security_vulnerability_scan_2025-12-26.md .codex/security_vulnerability_scan_latest.md
ln -s training/data configs/data
ln -s training/model configs/model
ln -s training/tracking configs/tracking
ln -s training/profiles configs/train
ln -s ../src/codex_ml/cli/audit_pipeline.py scripts/audit_pipeline.py
ln -s ../../.github/scripts/session_preload.py scripts/ci/session_preload.py
```

### Windows 10+ (Administrator)

#### Option 1: Git AutoCRLF (Recommended)

This is handled automatically by git's symlink support:

```powershell
# Enable symlink support (requires admin)
git config core.symlinks true
git checkout
```

#### Option 2: Manual Junctions (Not Recommended)

On Windows, use `mklink` to create directory junctions (admin required):

```powershell
# For directory symlinks only
cd configs
mklink /D data training\data
mklink /D model training\model
mklink /D tracking training\tracking
mklink /D train training\profiles
```

#### Option 3: Use Direct Paths

For script symlinks, update your Python path or use absolute imports:

```python
# Instead of importing from symlink:
# from scripts.audit_pipeline import ...

# Import from actual location:
from src.codex_ml.cli.audit_pipeline import ...
```

### Windows Without Admin Rights

If you don't have admin privileges:

1. Use **Git Bash** or **WSL (Windows Subsystem for Linux)** to work with the repository
2. Run `scripts/setup/create_symlinks.sh` from WSL
3. All development work will then work correctly

## CI/CD Handling

GitHub Actions workflows automatically handle symlink creation on their runners:

- **Linux runners**: Symlinks created by `git checkout`
- **Windows runners**: Uses Git's built-in symlink support with `core.symlinks = true`
- **macOS runners**: Symlinks created by `git checkout`

## Troubleshooting

### "Permission denied" on Windows

You need to either:
- Run as Administrator and use `mklink`
- Use WSL or Git Bash
- Update imports to use actual paths instead of symlink paths

### "Symlink not found" when importing

This typically occurs on Windows when the symlink wasn't set up. Either:
1. Create the symlink manually (see options above)
2. Update your import to use the actual path instead

## Post-Checkout Hook

A post-checkout hook is available in `.githooks/post-checkout` that automatically creates symlinks on Unix systems after git operations.

To enable it:

```bash
git config core.hooksPath .githooks
```

## Future Recommendations

To avoid symlink issues entirely in future work:

1. **Avoid tracked symlinks** in version control
2. **Use Python imports** instead of filesystem symlinks for code organization
3. **Document relative paths** clearly in README files
4. **Use environment variables** for configurable paths
5. **Test on multiple platforms** during development

## References

- [Git Symlink Documentation](https://git-scm.com/docs/git-config#Documentation/git-config.txt-coresymlinks)
- [Windows Symlink Limitations](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-sandbox/windows-sandbox-guide)
- [WSL as Alternative](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
