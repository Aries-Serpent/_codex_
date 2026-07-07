# OFFLINE_QUICKSTART

## Purpose

Quickstart for installing and running the repository in an isolated/offline environment using prebuilt artifacts.

> ⚠️ Pre-release note: this guide targets v0.1.0 pre-release packaging and should be used with the campaign readiness reports in `.codex/` before production external distribution.

## Prerequisites

- Python 3.12+
- Offline artifact bundle containing:
  - package artifacts (`dist/`)
  - wheelhouse (`./wheelhouse`)
  - checksums/SBOM if provided

## Installation (Offline)

```bash
# From extracted release bundle root
python -m pip install --no-index --find-links ./wheelhouse -e ".[core]"
```

## Validate Core Runtime

```bash
python -c "from cognitive_brain.base import ObservationData, Decision; print('offline core ok')"
```

## Optional Profiles

```bash
# Runtime profile
python -m pip install --no-index --find-links ./wheelhouse -e ".[runtime]"

# Full profile
python -m pip install --no-index --find-links ./wheelhouse -e ".[full]"
```

## Safety/Network Posture

- Default posture is deny-by-default for external networking.
- Use explicit allowlist entries only when external access is required.
- For isolated deployments, keep all installs and validation steps no-index/offline.

## Related Docs

- `./ISOLATED_DEPLOYMENT.md`
- `../OFFLINE_DEPLOYMENT.md`
- `../QUICKSTART_BY_PROFILE.md`
