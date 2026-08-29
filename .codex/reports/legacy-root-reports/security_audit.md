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

### Hydra configuration-instantiation advisory (2026-08-22)

**Issue:** [#5498](https://github.com/Aries-Serpent/_codex_/issues/5498)  
**Severity:** High (CVSS 7.8)  
**Advisory:** CVE-2026-68508 / GHSA-2cp2-2r3c-7p7r  
**Package:** `hydra-core`  
**Affected versions:** through 1.3.3  
**Fixed in:** 1.3.4

**Status:** Remediated in dependency declarations and active lockfiles.

The project upgraded `hydra-core` 1.3.2 to the first patched release, 1.3.4.
The remediation covers the primary package manifests, requirements inputs, and
generated lock sets. No production call to `hydra.utils.instantiate()` with an
untrusted `_target_` was identified; trusted configuration remains a required
application boundary because the patched blocklist is defense in depth.

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

---

## Dependency Scan — 2026-05-13 (pip-audit + CycloneDX SBOM)

**Source files:** `reports/dependency-scan-results.zip` (pip-audit JSON) · `reports/sbom-reports.zip` (CycloneDX 1.6)
**Packages scanned:** 328 (pip-audit) · 329 (SBOM)
**Scan date:** 2026-05-13

### Vulnerability Summary

| CVE | Package | Version | Severity | Fix | Action |
|-----|---------|---------|----------|-----|--------|
| CVE-2025-71176 | pytest | 8.4.2 | Medium | 9.0.3 | ✅ Bounds tightened to `>=9.0.3` in all requirements files |
| CVE-2025-69872 | diskcache | 5.6.3 | High | None available | ✅ Already ignored — indirect dev dep, tracked Dependabot #89 |
| CVE-2024-35515 | sqlitedict | 2.1.0 | High | None available | ✅ Added to `[tool.pip-audit]` ignore — indirect dep, controlled storage |

### CVE Details

#### CVE-2025-71176 — pytest `/tmp` symlink privilege escalation (GHSA-6w46-j5rx-g56g)
- **Affected:** pytest ≤9.0.2 on UNIX — relies on `/tmp/pytest-of-{user}` directory naming, allowing local users to symlink-attack the tmp dir and gain privileges or cause denial of service.
- **Fix:** pytest 9.0.3
- **Changes made:** `requirements.txt`, `requirements-dev.txt`, `requirements-minimal.txt` lower bounds raised from `>=8.x` to `>=9.0.3`; `pyproject.toml` `[project.optional-dependencies]` entries for `dev`, `test`, and `security` extras updated to `>=9.0.3`.
- **Note:** `requirements-test.txt` already pinned `pytest==9.0.3` ✅; `pyproject.toml` `[dependency-groups.ci]` already had `pytest>=9.0.3` ✅.

#### CVE-2025-69872 — diskcache pickle RCE (GHSA-w8v5-vhqr-4h9v)
- **Affected:** diskcache ≤5.6.3 — uses Python `pickle` for serialization by default, allowing RCE if an attacker has write access to the cache directory.
- **Fix:** None available as of 2026-05-13.
- **Exposure:** Indirect dependency (`dvc → dvc-data → diskcache`); dev-only extra; not used in application code. Cache directory not writable by untrusted users.
- **Action:** Maintained in `[tool.pip-audit].ignore-vulns`; tracked in Dependabot alert #89.

#### CVE-2024-35515 — sqlitedict insecure deserialization (GHSA-g4r7-86gm-pgqc)
- **Affected:** sqlitedict ≤2.1.0 — uses `pickle` for deserialization, allowing RCE if an attacker can write to the database file.
- **Fix:** None available as of 2026-05-13.
- **Exposure:** Indirect lock-file dependency only (`requirements/lock.txt`); not imported directly in application code; database files stored in controlled locations inaccessible to untrusted users.
- **Action:** Added to `[tool.pip-audit].ignore-vulns` with documentation comment; tracked as Dependabot alert #90.

### SBOM — License Triage

**Format:** CycloneDX 1.6 · **Serial:** `urn:uuid:6bac7b67-13b1-4090-a4c7-dc31d4fdcdeb`

#### Copyleft / Restrictive Licenses

| Package | Version | License | Usage | Risk |
|---------|---------|---------|-------|------|
| grandalf | 0.8 | GPL-2.0-only | Indirect (dvc dev dep) | Low — not shipped in production |
| yamllint | 1.38.0 | GPL-3.0-or-later | CI lint tool only | Low — not linked into application |
| PyGithub | 2.9.1 | LGPL | Runtime lib | Low — LGPL permits use as library |
| chardet | 5.2.0 | LGPLv2+ | Runtime lib | Low — LGPL permits use as library |

**Assessment:** No GPL-licensed packages are shipped in production builds. `grandalf` and `yamllint` are developer/CI tools only. LGPL packages (`PyGithub`, `chardet`) are used as libraries per the LGPL exception and require no source disclosure.

#### NVIDIA Proprietary Packages

15 NVIDIA CUDA packages (`nvidia-cublas`, `nvidia-cuda-runtime`, `nvidia-cudnn-cu13`, etc.) carry NVIDIA proprietary licenses. These are optional runtime dependencies for GPU-accelerated training only and are never installed in CPU-only or production web-serving environments.

#### License Distribution (top 10)

| License | Count |
|---------|-------|
| MIT | 128 |
| Apache-2.0 | 44 |
| BSD-3-Clause | 35 |
| BSD-2-Clause | 4 |
| Python-2.0 | 4 |
| PSF-2.0 | 3 |
| MPL-2.0 | 3 |
| ISC | 2 |
| GPL-2.0-only | 1 |
| GPL-3.0-or-later | 1 |

**Overall license posture: ✅ Acceptable** — permissive licenses dominate; copyleft exposure limited to dev/CI tools.
