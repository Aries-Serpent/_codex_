# Isolated Deployment Guide

## Default Security Posture

- `CODEX_NETWORK_MODE=isolated`
- Outbound networking uses fail-closed policy enforcement
- Default allowlist: localhost only

## Network Policy Configuration

Policy file: `.codex/network-policy.yaml`

```yaml
version: 1
default_mode: fail_closed
allow_localhost: true
allowed_hosts:
  - localhost
  - 127.0.0.1
  - ::1
```

To allow approved hosts, add exact hosts or wildcard patterns (for reviewed domains only).

## Runtime Validation

```bash
python - <<'PY'
from safety.network_policy import enforce_network_policy

enforce_network_policy("http://localhost:8765")
print("localhost allowed")
PY
```

## Persistence Defaults

Use local filesystem/SQLite storage only for isolated environments.
Do not rely on external stores for core operation.
