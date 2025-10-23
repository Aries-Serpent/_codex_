# Security Sweep — Run 2025-01 (2025-01-18)

## Run Metadata
- Branch: current working tree
- Snapshot commit: _post-run_ (see git log for final SHA)
- Participants: automated sweep

## Secrets & Credentials Review
- [ ] Scan repositories (e.g., `detect-secrets`) across touched paths.
- Findings: not run in this sweep
- Remediation status: pending future scan

## Dependency & Supply-Chain Review
- Generate an offline CycloneDX SBOM via `nox -s sbom` (Makefile alias `make sbom`). Artifacts are written to `artifacts/sbom/` (`cyclonedx.json` + `packages.txt`).
- Inputs: `requirements.lock` and `uv.lock` are parsed locally; no network calls are made.

## Moderation Controls
- Training: set `training.safety.moderation.enabled=true` (with optional `rules_path`, `fail_open`, and `audit_log`) inside `TrainingRunConfig` to enable the moderation adapter.
- CLI: `python -m codex_ml.cli.infer --prompt ... --moderation [--moderation-audit-log artifacts/safety/moderation.ndjson]` enforces the same checks offline.
- Audit trail: moderation decisions append to the configured NDJSON file with sanitized payloads and digests.

## Security Testing
| Check | Command | Result | Follow-Up |
| --- | --- | --- | --- |
| Bandit SAST | `nox -s sec_scan` | Clean (post-fix) | Weak SHA1 hashing replaced with SHA-256/BLAKE2b in `src/codex/archive/similarity.py`. |

### Bandit high-severity findings (pre-fix)
- `B324`: `src/codex/archive/similarity.py` used `hashlib.sha1` for AST and SimHash calculations (lines 48, 56).

### Remediation
- `py_ast_hash` now emits SHA-256 digests and `simhash64` derives bits from an 8-byte BLAKE2b digest, removing the weak hash usage.

## Outstanding Risks
- None introduced in this sweep.

## Next Steps
- Schedule a secrets scan once new policies are validated.
- Review moderation audit files during the next quarterly security review.
