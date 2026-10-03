# PRODUCTION DEPLOYMENT PLAN (DETAILED WORKING COPY)

Canonical source: `/home/runner/work/_codex_/_codex_/Aries-Serpent/_codex_/.codex/PRODUCTION_DEPLOYMENT_READINESS_PLAN.md`

## Immediate Execution Queue

1. Security track:
   - XXE/injection remediation validation
   - clear-text logging suppression audit
   - weak hash and deserialization triage
2. Coverage track:
   - 0%-coverage module targeting
   - ratchet checkpoints to 12%/15%/20%
3. CI track:
   - copilot-setup-steps hardening validation
   - session wrapup gate compliance
   - auto-fix cascade controls

## Current Session Actions

- Added `shlex.join` command rendering in `tests/test_container_smoke.py`.
- Added `defusedxml.minidom` stubs in `tests/test_readiness_remaining_modules.py`.
- Logged baseline run status and failure clusters for follow-up.
