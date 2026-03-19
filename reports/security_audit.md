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
- Inputs: `requirements/lock.txt` and `uv.lock` are parsed locally; no network calls are made.

### aiohttp Security Analysis (2026-01-06)
**Status:** ✅ ALL RESOLVED - No action required

Comprehensive analysis of 8 Dependabot security alerts for aiohttp transitive dependency:
- **Current Version:** aiohttp 3.13.3 (latest stable, released 2026-01-03)
- **Transitive Dependency Chain:**
  - `ray[serve]` → `aiohttp-cors` → `aiohttp==3.13.3`
  - `dvc==3.64.2` → `dvc-http` → `aiohttp-retry` → `aiohttp==3.13.3`
- **Location:** `requirements/lock.txt:17`

**Vulnerabilities Addressed:**
| Alert # | Severity | CVE | Status |
|---------|----------|-----|--------|
| #50 | High | CVE-2025-69223 | ✅ Patched (zip bomb vulnerability) |
| #56 | Moderate | CVE-2025-69229 | ✅ Patched (DoS via chunked messages) |
| #55 | Moderate | N/A | ✅ Patched (DoS via large payloads) |
| #54 | Moderate | N/A | ✅ Patched (DoS when bypassing asserts) |
| #57 | Low | N/A | ✅ Patched (cookie parser warning storm) |
| #53 | Low | N/A | ✅ Patched (static file path brute-force) |
| #52 | Low | N/A | ✅ Patched (unicode regex in ASCII protocols) |
| #51 | Low | N/A | ✅ Patched (unicode header processing) |

**Resolution:** All vulnerabilities patched in aiohttp 3.13.3. Dependabot alerts dismissed (2026-01-06). No code changes required.

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

## CVE-2026-33154 — dynaconf RCE via Insecure @jinja Resolver

**Date:** 2026-03-19
**Severity:** High (CVSS 7.5)
**Advisory:** GHSA-pxrr-hq57-q35p
**Package:** dynaconf (pip)
**Affected versions:** ≤ 3.2.12
**Fixed in:** 3.2.13

### Description

Dynaconf evaluated Jinja2 template expressions in the `@jinja` resolver (and
object-graph traversal via `@format`) without a sandbox, allowing an attacker
who can influence configuration sources (env vars, `.env` files, CI/CD
secrets, container config) to execute arbitrary OS commands.

### Status: ✅ ALREADY PATCHED

`requirements/lock.txt` was updated to `dynaconf==3.2.13` in session S154
(PR #3628, commit bumping dynaconf from 3.2.12 → 3.2.13).  The project is
not vulnerable.

| Item | Status |
|------|--------|
| `requirements/lock.txt` | ✅ `dynaconf==3.2.13` |
| SBOM `configs/development/artifacts/sbom/packages.txt` | ✅ Updated 3.2.12 → 3.2.13 (PR #3633) |
| Dependabot alert #117 | ✅ Resolved — using patched version |

### Action Taken

1. Confirmed `requirements/lock.txt` already pins `dynaconf==3.2.13`.
2. Updated stale SBOM entry (`configs/development/artifacts/sbom/packages.txt`)
   from `dynaconf==3.2.12` to `dynaconf==3.2.13` (the SBOM was not updated
   when the lock file was bumped in S154, which caused Dependabot alert #117).
3. Closed issue #3631 via this documentation update.

**No code logic changes required** — the fix is purely a version bump already
present in the lock file.
