# [Doc]: Import Contracts — Layers and Independence (Advisory Mode)
> Generated: 2025-10-14 21:10:31 UTC | Author: mbaetiong
🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Purpose
Enforce modular boundaries with import-linter while allowing incremental adoption.

## Contracts (summary)
- Layers: utils -> data -> models -> training -> api
- Independence: api <-> data (no back-refs)
- Forbidden: api → training.internal

See .importlinter for exact rules.

## Running locally (advisory)
```bash
nox -s lint
# import-linter runs in advisory mode; violations emit non-zero (1) but do not fail the session.
```

## How to fix violations
1. Identify the violating import in the output (source → target).
2. Choose one:
   - Move shared code to a lower layer (e.g., utils).
   - Introduce a small adapter/port in the dependent layer.
   - In rare cases, add an allowlist in .importlinter (temporary).

## Suggested workflow
- Keep advisory mode until violations shrink below an agreed threshold.
- Flip to strict mode (fail on any violation) after a stabilization milestone.

*End*
