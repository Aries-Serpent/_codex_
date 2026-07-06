# Install Guide (External Local Usage)

## Prerequisites

- Python 3.12+
- `pip`
- Release artifact: `codex_ml-0.1.0-py3-none-any.whl`

## Installation Profiles

Codex ML uses a 3-profile packaging strategy:

| Profile | Size | Use Case | Install Command |
|---------|------|----------|-----------------|
| **core** | 8-15 MB | Lightweight, offline-first | `pip install codex-ml[core]` |
| **runtime** | 20-35 MB | Production inference + services | `pip install codex-ml[runtime]` |
| **full** | 100+ MB | Development + all features | `pip install codex-ml[full]` |

## Standard Install (Local Wheel)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Install from wheel file
python -m pip install codex_ml-0.1.0-py3-none-any.whl

# Or install with profile
python -m pip install 'codex-ml[runtime]'

# Verify installation
codex --help
```

## Offline Install (Air-Gapped)

Use `OFFLINE_BOOTSTRAP.sh` with a local wheelhouse.
The bootstrap flow uses the offline bootstrap module directly.

```bash
./OFFLINE_BOOTSTRAP.sh \
  --wheelhouse ./wheelhouse \
  --artifact ./dist/codex_ml-0.1.0-py3-none-any.whl
```

## Verify Isolated Networking

By default, networking is fail-closed via `.codex/network-policy.yaml`.
Only localhost is allowlisted until explicitly expanded.

```bash
python - <<'PY'
from safety import PolicyViolationError, enforce_network_policy

try:
    enforce_network_policy("https://example.com")
except PolicyViolationError:
    print("policy enforcement active")
PY
```
