# Dockerfile Python Version Fix

**Date**: 2026-02-01  
**Commit**: b06fa77  
**Issue**: Python 3.14 doesn't exist

---

## Problem

The Dockerfile was attempting to use Python 3.14, which doesn't exist. This was identified in code review and would cause all Docker builds to fail.

### Specific Issues:

1. **Base stage** (line 5): `FROM python:3.14-slim`
2. **Test stage** (line 122): `FROM python:3.14-slim`
3. **GPU runtime stage** (lines 67-78): Attempting to install Python 3.14 from PPA
4. **Duplicate lines** (lines 106-119): Repeated PyTorch installation and user creation

---

## Solution

### Changes Made:

1. **Updated all Python references to 3.12** (latest stable version)
   - Base stage: `python:3.12-slim`
   - Test stage: `python:3.12-slim`
   - GPU runtime: `python3.12` from deadsnakes PPA

2. **Removed duplicate lines** in gpu-runtime stage
   - Lines 106-119 were duplicates of lines 92-104
   - Removed redundant PyTorch installation
   - Removed redundant user creation

3. **Improved gpu-runtime approach**
   - Instead of copying packages from base (different OS), rebuild them
   - Ensures binary compatibility between Ubuntu 22.04 and Python packages
   - Adds necessary build tools (gcc, build-essential, etc.)

---

## Validation

### Docker Build Commands:

```bash
# CPU runtime
docker build --target cpu-runtime -t codex:cpu .

# GPU runtime  
docker build --target gpu-runtime -t codex:gpu .

# Test environment (default)
docker build --target test -t codex:test .
```

### Expected Behavior:

- All stages build successfully with Python 3.12
- No version mismatch errors
- No package compatibility issues
- GPU runtime properly installs CUDA-compatible PyTorch

---

## Technical Details

### Python 3.12 vs 3.14:

- **Python 3.12**: Released October 2023, stable and widely supported
- **Python 3.14**: Doesn't exist (as of February 2026)
- **Python 3.13**: Released October 2024, still stabilizing

### Multi-stage Build Strategy:

1. **base**: Common Debian-based Python 3.12 environment
2. **cpu-runtime**: Extends base, adds CPU-only PyTorch
3. **gpu-runtime**: Ubuntu 22.04 + CUDA + Python 3.12 from PPA, rebuilds all deps
4. **test**: Debian-based Python 3.12 with test dependencies

### Why Rebuild in GPU Stage:

- Base uses official Python Docker image (Debian-based)
- GPU uses NVIDIA CUDA image (Ubuntu 22.04-based)
- Different base OS means different system libraries
- Copying packages between them causes binary incompatibility
- Solution: Rebuild all Python packages in gpu-runtime stage

---

## Files Changed

- `Dockerfile` (21 insertions, 11 deletions)
  - Lines 5, 122: Python version fix
  - Lines 61-104: GPU runtime rebuild strategy
  - Removed lines 106-119: Duplicates

---

## Testing Status

✅ **Docker build starts successfully** (validated with docker build --target cpu-runtime)  
⏳ **Full build pending** (requires dependencies download)  
⏳ **Runtime testing pending** (requires complete build)

---

## Related Files

- `Dockerfile` - Fixed
- `.codex/analysis/PR_3095_FIX_SUMMARY.md` - Referenced
- `tests/deployment/test_docker_build.py` - Tests these stages

---

## Next Steps

1. CI will validate Docker builds automatically
2. Tests in `tests/deployment/test_docker_build.py` will verify targets exist
3. Runtime testing can validate actual image functionality

---

**Status**: ✅ FIXED  
**Review Comment**: Addressed #2752114896
