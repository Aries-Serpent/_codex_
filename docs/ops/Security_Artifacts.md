# [Guide]: Security Artifacts (Opt-in, Offline-Friendly)
> Generated: 2025-10-14 21:10:31 UTC | Author: mbaetiong
🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Overview
Run local security scans and persist artifacts under audit_artifacts/security/ when explicitly enabled.

## Commands
- Quick local sweep (no artifacts):
```bash
nox -s sec_scan
```

- Deep sweep with artifacts (opt-in):
```bash
CODEX_AUDIT=1 nox -s sec
ls audit_artifacts/security/
# bandit.json, semgrep.json, detect-secrets.json, pip-audit.json (if requirements.txt present)
```

- Container hygiene (optional tools):
```bash
make docker-hadolint
CODEX_AUDIT=1 CODEX_IMAGE=codex:local make docker-trivy
```

## Notes
- Tools must be installed locally (see docs/ops/Local_Tooling_Prereqs.md).
- semgrep runs only if semgrep_rules/ exists.
- pip-audit runs only when CODEX_AUDIT=1 to avoid surprises.

*End*
