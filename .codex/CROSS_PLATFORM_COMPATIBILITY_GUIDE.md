# Cross-Platform Compatibility Guide

**Version**: 1.0.0  
**Last Updated**: 2026-01-23  
**Applies to**: _codex_ repository (all branches)

---

## Overview

This guide documents cross-platform compatibility for the _codex_ project across Windows, macOS, and Linux development environments and CI/CD pipelines.

---

## Platform Support Matrix

| Component | Linux | macOS | Windows* | WSL |
|-----------|:-----:|:-----:|:--------:|:---:|
| Repository Checkout | ✅ | ✅ | ✅ | ✅ |
| Python Development | ✅ | ✅ | ✅ | ✅ |
| Bash Scripts | ✅ | ✅ | ⚠️ | ✅ |
| Symlinks | ✅ | ✅ | ⚠️ | ✅ |
| Temp Files | ✅ | ✅ | ✅ | ✅ |
| Path References | ✅ | ✅ | ✅ | ✅ |
| CI/CD Workflows | ✅ | ✅ | ✅ | ✅ |
| Docker | ✅ | ⚠️ | ⚠️ | ✅ |

\* Windows: Use WSL, Git Bash, or native with Git's symlink support  
⚠️: Requires additional configuration or limitations

---

## Key Compatibility Rules

### 1. Paths (✅ FIXED - Phase 2)

**Rule**: Always use dynamic path resolution, never hardcoded paths

✅ **DO**:
```python
from src.codex.utils.path_extended import get_repo_root
repo_root = get_repo_root()
config_path = repo_root / "config" / "settings.yaml"
```

❌ **DON'T**:
```python
config_path = "/home/runner/work/_codex_/_codex_/config/settings.yaml"
```

**Why**: Hardcoded paths fail on any other system (different CI runner, local dev, etc.)

---

### 2. Temporary Files (✅ FIXED - Phase 3)

**Rule**: Always use `tempfile` module or system environment variables

✅ **DO** (Python):
```python
import tempfile
import os

# Method 1: Use tempfile module (recommended)
temp_dir = tempfile.gettempdir()
temp_file = os.path.join(temp_dir, "myfile.txt")

# Method 2: Create with tempfile
with tempfile.NamedTemporaryFile(delete=False) as f:
    f.write(b"data")
    temp_path = f.name
```

✅ **DO** (Bash):
```bash
# Use TMPDIR environment variable with fallback
TEMP_DIR="${TMPDIR:-/tmp}"
TEMP_FILE="$TEMP_DIR/myfile.txt"

# Or use mktemp (portable)
TEMP_DIR=$(mktemp -d)
```

❌ **DON'T**:
```python
temp_file = "/tmp/myfile.txt"  # Unix only!
```

**Why**: Windows uses `%TEMP%`, not `/tmp`

---

### 3. Bash Portability (✅ FIXED - Phase 3)

**Rule**: Use POSIX-compatible commands, avoid GNU-specific options

| Command | GNU Option | POSIX Alternative | Notes |
|---------|------------|-------------------|-------|
| `sed` | `-r` | `-E` | Extended regex |
| `grep` | `-P` | POSIX patterns | No PCRE on macOS |
| `date` | `--iso-8601` | `+%Y-%m-%dT%H:%M:%SZ` | Custom format |
| `readlink` | `-f` | Use `realpath` or custom | Symlink resolution |

✅ **DO**:
```bash
#!/usr/bin/env bash
set -e

# Use POSIX options
sed -E 's/pattern/replacement/g' file.txt
grep '^PATTERN' file.txt  # Use POSIX regex

# Use environment variables
TEMP_DIR="${TMPDIR:-/tmp}"
echo "Config: ${CONFIG_HOME:-.config}"
```

❌ **DON'T**:
```bash
#!/bin/bash  # Non-portable shebang
sed -r 's/pattern/replacement/g'  # GNU-only
grep -P '\d+' file.txt  # PCRE not on macOS
```

**Why**: macOS uses BSD tools, Windows uses Git Bash, Linux uses GNU tools

---

### 4. Symlinks (✅ FIXED - Phase 2)

**Rule**: Don't track symlinks in git; create locally or with hooks

✅ **DO**:
```bash
# Local setup (after git clone)
scripts/setup/create_symlinks.sh
```

✅ **DO** (if tracked symlinks needed):
```bash
git config core.symlinks true  # Enable for git
```

❌ **DON'T**:
```bash
# Don't track symlinks in git
ln -s target link
git add link  # ❌ Breaks on Windows
```

**Why**: Windows doesn't support symlinks without admin privileges

---

### 5. Line Endings

**Rule**: Git handles via `.gitattributes` (already configured)

Configuration (in `.gitattributes`):
```
# All files normalized to LF on commit
* text=auto eol=lf

# Windows batch scripts use CRLF
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf

# Shell scripts always LF
*.sh text eol=lf
*.bash text eol=lf
```

✅ **Result**: 
- Windows developers: Scripts auto-converted to CRLF in working directory
- Unix developers: Scripts auto-converted to LF in working directory
- Git history: All files stored as LF (consistent)

---

### 6. Filenames (✅ Partially Fixed)

**Rule**: Avoid Windows-illegal characters in filenames

Windows-illegal characters in filenames: `< > : " / \ | ? *`

✅ **DO**:
```python
from src.codex.utils.path_extended import windows_safe_timestamp

# Generate safe timestamp for filenames
timestamp = windows_safe_timestamp(fmt="compact")  # 20260123_143045
filename = f"report_{timestamp}.json"
```

❌ **DON'T**:
```python
import datetime
timestamp = datetime.now().isoformat()  # 2026-01-23T14:30:45 (has colons!)
filename = f"report_{timestamp}.json"  # ❌ Fails on Windows
```

**Why**: Colons are illegal in Windows filenames

---

## Platform-Specific Setup

### Linux

```bash
# Standard Python venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

**Status**: ✅ No special configuration needed

---

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+ (if not installed)
brew install python@3.11

# Create venv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Create symlinks (auto-created after git operations via hook)
scripts/setup/create_symlinks.sh

# Run tests
pytest tests/
```

**Status**: ✅ Fully supported

**Known Limitations**:
- Docker: Use Docker Desktop or UTM for M1/M2 Macs
- Homebrew Python: Use `python3.11` not `python3.12` if issues occur

---

### Windows (Native)

#### Option 1: WSL (Recommended)

```powershell
# Install WSL2
wsl --install

# Open Ubuntu terminal
wsl

# Then follow Linux instructions above
```

**Status**: ✅ Fully supported (recommended)

---

#### Option 2: Git Bash

```bash
# Install Git for Windows (includes Bash)
# https://gitforwindows.org/

# Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git

# Create venv
python -m venv venv
source venv/Scripts/activate  # Note: Scripts not scripts

# Install dependencies
pip install -r requirements-dev.txt

# Create symlinks (optional, some may fail)
bash scripts/setup/create_symlinks.sh

# Run tests
pytest tests/
```

**Status**: ⚠️ Mostly supported

**Known Limitations**:
- Symlinks: Some may not work without admin
- Performance: Slower than WSL
- Line endings: Auto-handled by Git

---

#### Option 3: Native Windows (Advanced)

```powershell
# Install Python 3.11+ from python.org
# https://www.python.org/

# Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git

# Create venv
python -m venv venv
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements-dev.txt

# Create symlinks (requires admin, use mklink)
# See .codex/WINDOWS_SYMLINK_SETUP.md

# Run tests
pytest tests\
```

**Status**: ⚠️ Partial support

**Known Limitations**:
- Symlinks: Requires admin privileges
- Case sensitivity: Windows is case-insensitive (might cause issues)
- Shell scripts: Use WSL or Git Bash instead

---

### CI/CD Runners

#### GitHub Actions

**Linux Runner** (Ubuntu):
```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'

- name: Install dependencies
  run: |
    pip install -r requirements-dev.txt
    scripts/setup/create_symlinks.sh
```

**Status**: ✅ Fully supported

---

**macOS Runner** (macOS 12+):
```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'

- name: Install dependencies
  run: |
    pip install -r requirements-dev.txt
    scripts/setup/create_symlinks.sh
```

**Status**: ✅ Fully supported

**Note**: Symlinks auto-created by `.githooks/post-checkout`

---

**Windows Runner** (Windows Server 2022):
```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'

- name: Install dependencies
  run: |
    pip install -r requirements-dev.txt
    # Symlinks auto-created by Git with core.symlinks=true
```

**Status**: ✅ Fully supported

**Note**: No special setup needed; Git handles symlinks automatically

---

## Troubleshooting

### Problem: "Permission denied" on checkout (Windows)

**Cause**: Git symlink support not enabled

**Solution**:
```bash
git config core.symlinks true
git checkout .
```

---

### Problem: "sed: invalid option" (macOS)

**Cause**: Using GNU sed option `-r` instead of BSD `-E`

**Solution**: Use `-E` instead (now fixed in Phase 3)

---

### Problem: "/tmp/ not found" (Windows)

**Cause**: Scripts hardcoded `/tmp/`

**Solution**: Use `tempfile.gettempdir()` (now fixed in Phase 3)

---

### Problem: "grep -P not found" (macOS)

**Cause**: PCRE patterns not available

**Solution**: Use POSIX regex instead (now fixed in Phase 3)

---

### Problem: "symlink is not a junction" (Windows)

**Cause**: Symlink created incorrectly

**Solution**:
```bash
# Delete and recreate with correct type
git rm --cached symlink_path
rm symlink_path
# Add to .gitignore instead
```

---

## Testing

### Run Tests Across Platforms

**Locally on Linux/macOS**:
```bash
pytest tests/ -v
```

**Locally on Windows (WSL)**:
```bash
wsl pytest tests/ -v
```

**In GitHub Actions** (all platforms simultaneously):
```bash
git push origin feature-branch
# Actions automatically test on Linux, macOS, Windows
```

---

### Test Coverage by Platform

| Test Type | Linux | macOS | Windows |
|-----------|:-----:|:-----:|:-------:|
| Unit tests | ✅ | ✅ | ✅ |
| Integration tests | ✅ | ✅ | ⚠️ |
| Docker tests | ✅ | ⚠️ | ⚠️ |
| Bash script tests | ✅ | ✅ | ⚠️ |
| Path tests | ✅ | ✅ | ✅ |
| Symlink tests | ✅ | ✅ | ⚠️ |

---

## Contributing Guidelines for Cross-Platform Work

### Before Submitting a PR:

1. **Test on Multiple Platforms** (if possible):
   - Linux: Native or Docker
   - macOS: Native if available
   - Windows: WSL or CI results

2. **Check Path Usage**:
   ```bash
   grep -r "/home/runner\|/tmp/\|C:\\\\" --include="*.py" --include="*.sh"
   ```

3. **Check Bash Portability**:
   ```bash
   grep -r "sed -r\|grep -P\|/usr/bin" --include="*.sh" --include="*.bash"
   ```

4. **Verify Line Endings**:
   ```bash
   git diff --check  # Should report no trailing whitespace issues
   ```

5. **Test Symlinks** (if added):
   ```bash
   git ls-files -s | grep "^120000"  # Should be empty (none tracked)
   ```

### Code Review Checklist:

- [ ] No hardcoded paths (`/home/runner/`, `/tmp/`, etc.)
- [ ] Uses `tempfile` module or `get_repo_root()`
- [ ] Bash scripts use POSIX-compatible options
- [ ] No symlinks tracked in git
- [ ] Line endings normalized via `.gitattributes`
- [ ] Tested on at least 2 platforms

---

## References

- [Git Documentation](https://git-scm.com/docs)
- [Python tempfile](https://docs.python.org/3/library/tempfile.html)
- [POSIX Shell Specification](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/sh.html)
- [Windows Filename Restrictions](https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file)
- [GitHub Actions Platforms](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners)

---

## FAQ

**Q: Do I need to support Windows development?**  
A: Yes, we support Windows via WSL and native. Use WSL for best experience.

**Q: Can I use hardcoded paths in tests?**  
A: No, use `get_repo_root()` or fixtures that handle paths dynamically.

**Q: Are symlinks mandatory?**  
A: No, they're convenience links. Files are accessible via direct paths.

**Q: How do I run bash scripts on Windows?**  
A: Use Git Bash, WSL, or port to Python.

**Q: What if I only develop on Linux?**  
A: Write code that works elsewhere too (use `get_repo_root()`, avoid `/tmp/`, etc).

---

**Document Status**: ✅ Complete

**Next Review**: 2026-02-23 (30 days)

**Maintainer**: @mbaetiong
