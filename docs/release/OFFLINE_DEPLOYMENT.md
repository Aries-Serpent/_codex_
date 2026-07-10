# Offline Deployment Guide

This guide explains how to deploy Codex ML in air-gapped (offline) environments where external network access is restricted or unavailable.

## Overview

Offline deployment requires pre-staging all dependencies in a wheelhouse directory, then using the bootstrap script to install into isolated environments.

```
┌─────────────────────┐      ┌──────────────────────┐
│  Build Environment  │      │  Target Environment  │
│ (Network Access)    │      │ (Air-Gapped/Offline) │
│                     │      │                      │
│ 1. Download wheel   │──┬─→ │ 3. Bootstrap install │
│ 2. Build wheelhouse │  │   │ 4. Run application   │
│    (all deps)       │  │   │                      │
└─────────────────────┘  │   └──────────────────────┘
                         │
                    ┌────┴────┐
                    │ Wheelhouse
                    │ (USB, SCP,
                    │  S3, etc.)
```

## Prerequisites

**On build machine (with network):**
- Python 3.12+
- pip
- Access to PyPI or internal package repository

**On target machine (offline):**
- Python 3.12+
- pip
- No network access required

## Step 1: Prepare Wheelhouse (Build Machine)

### Download Codex ML Wheel

Download from your package repository or build from source:

```bash
# Option A: Download from PyPI
pip download codex-ml==0.1.0 -d ./wheelhouse --no-deps

# Option B: Use pre-built wheel
cp ./dist/codex_ml-0.1.0-py3-none-any.whl ./wheelhouse/
```

### Build Complete Wheelhouse

Generate all dependencies for your chosen profile:

```bash
# Core profile (8-15 MB) — minimal dependencies
pip download 'codex-ml[core]==0.1.0' \
  --dest ./wheelhouse \
  --no-binary :all:

# Runtime profile (20-35 MB) — includes torch, transformers
pip download 'codex-ml[runtime]==0.1.0' \
  --dest ./wheelhouse

# Full profile (100+ MB) — complete development
pip download 'codex-ml[full]==0.1.0' \
  --dest ./wheelhouse
```

### Verify Wheelhouse

```bash
# Check downloaded files
ls -lah ./wheelhouse | head -20
echo "Total wheels: $(ls ./wheelhouse/*.whl | wc -l)"

# Create checksums for verification
sha256sum ./wheelhouse/*.whl > ./wheelhouse/SHA256SUMS.txt
```

### Package for Transfer

```bash
# Create archive for transport
tar czf codex_ml_offline_core.tar.gz wheelhouse/

# Or for runtime
tar czf codex_ml_offline_runtime.tar.gz wheelhouse/

# Create transfer manifest
cat > OFFLINE_MANIFEST.txt <<EOF
Profile: core
Wheel: codex_ml-0.1.0-py3-none-any.whl
Dependencies: $(ls wheelhouse/*.whl | wc -l) wheels
Size: $(du -sh wheelhouse | cut -f1)
Checksum: $(sha256sum wheelhouse/SHA256SUMS.txt | cut -d' ' -f1)
Python: 3.12+
EOF
```

## Step 2: Transfer Wheelhouse

Choose your transfer method:

### USB Drive / External Storage

```bash
# Mount USB and copy
cp -r wheelhouse/ /mnt/usb/codex-wheelhouse/
sync  # Ensure written
```

### SCP to Target

```bash
scp -r wheelhouse/ user@target:/home/user/wheelhouse/
```

### S3 or Cloud Storage

```bash
aws s3 cp wheelhouse/ s3://my-bucket/codex-ml-offline/ --recursive
# On target machine
aws s3 cp s3://my-bucket/codex-ml-offline/ ./wheelhouse/ --recursive
```

### Local Filesystem (Same Machine)

```bash
# If build and target are on same machine
cp -r wheelhouse/ /path/to/target/wheelhouse/
```

## Step 3: Bootstrap Installation (Target Machine)

### Method A: Using OFFLINE_BOOTSTRAP.sh

The official bootstrap script handles venv creation and installation:

```bash
# Navigate to target directory
cd /path/to/deployment

# Run bootstrap
./OFFLINE_BOOTSTRAP.sh \
  --wheelhouse ./wheelhouse \
  --artifact ./wheelhouse/codex_ml-0.1.0-py3-none-any.whl \
  --venv ./.venv-offline \
  --python python3
```

### Method B: Manual Installation

If the bootstrap script is not available:

```bash
# Create virtual environment
python3 -m venv .venv-offline
source .venv-offline/bin/activate

# Install with wheelhouse
pip install \
  --no-index \
  --find-links ./wheelhouse \
  ./wheelhouse/codex_ml-0.1.0-py3-none-any.whl

# Verify installation
codex --help
python -c "from cognitive_brain import Planner; print('Installation successful')"
```

### Profile-Specific Installation

```bash
# Core profile (if wheelhouse includes all core deps)
pip install \
  --no-index \
  --find-links ./wheelhouse \
  'codex-ml[core]==0.1.0'

# Runtime profile
pip install \
  --no-index \
  --find-links ./wheelhouse \
  'codex-ml[runtime]==0.1.0'

# Full profile
pip install \
  --no-index \
  --find-links ./wheelhouse \
  'codex-ml[full]==0.1.0'
```

## Step 4: Verify Installation

```bash
# Activate venv
source .venv-offline/bin/activate

# Check installation
pip list | grep codex
pip show codex-ml

# Verify core imports
python -c "from codex_ml.config import Config; print('✓ Config module')"

# Verify runtime imports (if runtime/full installed)
python -c "from cognitive_brain import Planner; print('✓ Planner module')"

# Check CLI
codex --version
codex --help
```

## Step 5: Run Application

### Core Profile

```bash
# Configuration-only application
python3 -c "
from codex_ml.config import Config
from codex_ml.safety import PromptSanitizer

config = Config.from_env()
sanitizer = PromptSanitizer(strict_mode=True)
print('Core application running')
"
```

### Runtime Profile

```python
# inference_app.py
import asyncio
from cognitive_brain import Planner, ObservationData

async def main():
    planner = Planner()
    observation = ObservationData(
        context="Analyze this text",
        metadata={"offline": True}
    )
    result = planner.observe(observation)
    print(f"Result: {result}")

asyncio.run(main())
```

```bash
python3 inference_app.py
```

### Full Profile

```bash
# Run tests
pytest tests/

# Run CLI
codex train --config training.yaml
```

## Troubleshooting

### "No module named 'codex_ml'"

Check that pip install completed successfully:
```bash
pip show codex-ml
pip list | grep codex
```

If missing, reinstall:
```bash
pip install --no-index --find-links ./wheelhouse ./wheelhouse/codex_ml*.whl
```

### "ERROR: Could not find a version that satisfies the requirement"

The wheelhouse is incomplete or the wheel filename is wrong:
```bash
# List available wheels
ls -la wheelhouse/

# Try with explicit wheel path
pip install ./wheelhouse/codex_ml-0.1.0-py3-none-any.whl
```

### "ModuleNotFoundError: No module named 'torch'"

You need the runtime or full profile wheels:
```bash
# Check what's in wheelhouse
ls wheelhouse/ | grep -E "torch|transformers"

# If empty, rebuild wheelhouse with runtime profile on build machine
pip download 'codex-ml[runtime]==0.1.0' --dest ./wheelhouse
```

### Network Policy Violation

Codex ML enforces offline-first by default. If your application tries to access the network:

```bash
# Check network policy
cat .codex/network-policy.yaml

# Only localhost is allowed by default
# To enable external access, edit network-policy.yaml
```

### Slow Installation

Large wheels (runtime/full profiles) can take time:

```bash
# Monitor progress
pip install -v --no-index --find-links ./wheelhouse codex-ml[runtime]

# Or install core first to verify process
pip install --no-index --find-links ./wheelhouse codex-ml[core]
```

## Environment Variables

```bash
# Optional: Set custom config path
export CODEX_CONFIG_PATH=/etc/codex/config.yaml

# Optional: Enable debug logging
export CODEX_DEBUG=1

# Optional: Set offline mode (auto-detected)
export CODEX_OFFLINE=1
```

## Security Considerations

### Verify Wheel Integrity

```bash
# On build machine
sha256sum ./wheelhouse/*.whl > SHA256SUMS.txt

# On target machine (after transfer)
sha256sum -c SHA256SUMS.txt

# All should print "OK"
```

### Network Policy

Codex ML is fail-closed by default:
- ✅ localhost only (ports 8000-9999)
- ❌ External network blocked until explicitly configured

To allow external network:

```bash
# Edit network policy
cat > .codex/network-policy.yaml <<EOF
network:
  mode: strict  # or 'permissive'
  allowlist:
    - localhost
    - 127.0.0.1
    # Add external hosts if needed:
    # - example.com
EOF
```

## Example: Complete Offline Deployment

```bash
# === Build Machine (with network) ===
mkdir -p codex-offline
cd codex-offline

# Create wheelhouse
pip download 'codex-ml[runtime]==0.1.0' --dest ./wheelhouse
sha256sum ./wheelhouse/*.whl > ./wheelhouse/SHA256SUMS.txt

# Create manifest
echo "Created: $(date)" > MANIFEST.txt
echo "Wheels: $(ls wheelhouse/*.whl | wc -l)" >> MANIFEST.txt

# Create archive for transport
tar czf codex-ml-runtime.tar.gz wheelhouse/ MANIFEST.txt

# === Target Machine (offline) ===
# Extract archive
tar xzf codex-ml-runtime.tar.gz

# Bootstrap installation
pip install --no-index --find-links wheelhouse codex-ml[runtime]

# Verify
python -c "from cognitive_brain import Planner; print('Ready')"
```

## Advanced: Custom Repository

For enterprise environments with internal package repositories:

```bash
# On build machine
pip download 'codex-ml[full]==0.1.0' \
  --index-url https://internal-pypi.company.com/simple \
  --dest ./wheelhouse

# On target machine with same internal PyPI access
pip install -e . \
  --index-url https://internal-pypi.company.com/simple
```

---

## Next Steps

- **Core profile:** [docs/quickstart/QUICKSTART_BY_PROFILE.md](docs/quickstart/QUICKSTART_BY_PROFILE.md#-core-profile-lightweight--offline-first-8-15-mb)
- **Runtime profile:** [docs/quickstart/QUICKSTART_BY_PROFILE.md](docs/quickstart/QUICKSTART_BY_PROFILE.md#-runtime-profile-production-inference--apis-20-35-mb)
- **Configuration:** [docs/configuration/](docs/configuration/)
- **API Reference:** See [CONTRIBUTING.md](CONTRIBUTING.md#10-stable-public-apis-v010)

---

## Support

- **Issues:** https://github.com/Aries-Serpent/_codex_/issues
- **Discussions:** https://github.com/Aries-Serpent/_codex_/discussions
- **License:** MIT
