# Install Guide (External Local Usage)

## Prerequisites

- Python 3.12+
- `pip`
- Release artifact: `codex-core-0.1.0.whl`

## Standard Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install codex-core-0.1.0.whl
codex --help
```

## Offline Install (Air-Gapped)

Use `OFFLINE_BOOTSTRAP.sh` with a local wheelhouse.
The bootstrap flow uses the offline bootstrap module directly.

```bash
./OFFLINE_BOOTSTRAP.sh \
  --wheelhouse ./wheelhouse \
  --artifact ./dist/codex-core-0.1.0.whl
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
