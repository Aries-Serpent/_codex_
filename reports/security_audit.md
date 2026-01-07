# Security Sweep — Run Previous Cycle-01 (Previous Cycle-01-18)

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
- Inputs: `requirements/lock.txt` and `uv.lock` are parsed locally; no network calls are made.

### aiohttp Security Analysis (Current Cycle-01-06)
**Status:** ✅ ALL RESOLVED - No action required

Comprehensive analysis of 8 Dependabot security alerts for aiohttp transitive dependency:
- **Current Version:** aiohttp 3.13.3 (latest stable, released Current Cycle-01-03)
- **Transitive Dependency Chain:** 
  - `ray[serve]` → `aiohttp-cors` → `aiohttp==3.13.3`
  - `dvc==3.64.2` → `dvc-http` → `aiohttp-retry` → `aiohttp==3.13.3`
- **Location:** `requirements/lock.txt:17`

**Vulnerabilities Addressed:**
| Alert # | Severity | CVE | Status |
|---------|----------|-----|--------|
| #50 | High | CVE-Previous Cycle-69223 | ✅ Patched (zip bomb vulnerability) |
| #56 | Moderate | CVE-Previous Cycle-69229 | ✅ Patched (DoS via chunked messages) |
| #55 | Moderate | N/A | ✅ Patched (DoS via large payloads) |
| #54 | Moderate | N/A | ✅ Patched (DoS when bypassing asserts) |
| #57 | Low | N/A | ✅ Patched (cookie parser warning storm) |
| #53 | Low | N/A | ✅ Patched (static file path brute-force) |
| #52 | Low | N/A | ✅ Patched (unicode regex in ASCII protocols) |
| #51 | Low | N/A | ✅ Patched (unicode header processing) |

**Resolution:** All vulnerabilities patched in aiohttp 3.13.3. Dependabot alerts dismissed (Current Cycle-01-06). No code changes required.

**Detailed Analysis:** See `reports/security_analysis_aiohttp_2026-01-06.md` for CVE details, CVSS scores, patch commit references, and verification steps.

**Action Taken:** Manual dismissal of 8 stale Dependabot alerts in GitHub UI with reason "Already fixed - using patched version aiohttp 3.13.3".

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
