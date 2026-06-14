# Dependency Vulnerability Scan Report
**Campaign:** PROD-READINESS-CAMPAIGN-20260614  
**Agent:** Dependency Vulnerability Scanner Agent v1.0  
**Branch:** `copilot/dep-security-fixes-20260614`  
**Date:** 2026-06-14  
**Scope:** 29 requirements files + pyproject.toml across entire repository  

---

## Executive Summary

Scanned **95 unique packages** from **29 requirements files** and `pyproject.toml` using the GitHub Advisory Database.  
Found **7 CVEs** requiring remediation (2 Critical, 3 High, 2 Medium). All 7 have been fixed.

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 2 | ✅ Fixed |
| High | 3 | ✅ Fixed |
| Medium | 2 | ✅ Fixed |
| **Total** | **7** | **✅ All Fixed** |

---

## Findings & Fixes

### 🔴 CRITICAL

#### 1. `ray` — RCE via DNS Rebinding (GHSA-XXX)
- **Affected:** `ray[serve]>=2.9,<2.52.0`
- **CVE:** DNS rebinding attack enables remote code execution on dashboard port
- **Fix:** `ray[serve]>=2.55.0` (also resolves Parquet Arrow deserialization RCE ≥2.49.0,<2.55.0)
- **Files:** `pyproject.toml`

#### 2. `chromadb` — Pre-Auth Code Injection (GHSA-XXX)
- **Affected:** `chromadb<=1.5.9`
- **CVE:** Unauthenticated code injection via crafted requests
- **Fix:** `chromadb>=1.5.10`
- **Files:** `pyproject.toml` (2 occurrences: [ml], [all])

---

### 🟠 HIGH

#### 3. `sentencepiece` — Heap Buffer Overflow (GHSA-XXX)
- **Affected:** `sentencepiece<0.2.1`
- **CVE:** Heap overflow in model loading — potential RCE
- **Fix:** `sentencepiece>=0.2.1`
- **Files:** `pyproject.toml` (6 occurrences), `requirements-ml-lite.txt`, `requirements-optional.txt`

#### 4. `aiohttp` — Zip Bomb DoS (GHSA-XXX)
- **Affected:** `aiohttp<=3.13.2`
- **CVE:** Decompression bomb leading to memory exhaustion
- **Fix:** `aiohttp>=3.13.3`
- **Files:** `.github/copilot-cascade/requirements.txt`, `.github/copilot-security/requirements.txt`

#### 5. `setuptools` — Path Traversal / File Write (GHSA-XXX)
- **Affected:** `setuptools<78.1.1`
- **CVE:** Path traversal allows arbitrary file write during package installation
- **Fix:** `setuptools>=78.1.1`
- **Files:** `requirements/agent.txt`
- **Note:** `pyproject.toml` build-system already had `setuptools>=78.1.1,<82` — no change needed

---

### 🟡 MEDIUM

#### 6. `black` — Arbitrary File Write in Cache (GHSA-XXX)
- **Affected:** `black<26.3.1`
- **CVE:** Cache directory traversal allows arbitrary file write
- **Fix:** `black>=26.3.1`
- **Files:** `requirements/agent.txt`, `requirements-minimal.txt`, `.github/ai-evolution/requirements.txt`
- **Note:** `pyproject.toml` already had `black>=26.3.1,<27.0.0` — no change needed

#### 7. `GitPython` — Windows Untrusted Search Path (GHSA-XXX)
- **Affected:** `gitpython<=3.1.32`
- **CVE:** Untrusted search path on Windows allows binary hijacking
- **Fix:** `GitPython>=3.1.33`
- **Files:** `.github/agents/ci-testing-agent/requirements.txt`

---

## Non-Actionable Advisories

| Package | Advisory | Reason |
|---------|----------|--------|
| `wandb` | SSRF <=0.17.0 | **WITHDRAWN** by GitHub Advisory DB |
| `ray` | Auth disabled | No upstream patch available — documented accepted risk |
| `ray` | Jobs API RCE | No upstream patch available — documented accepted risk |

---

## Files Scanned

### Root-level
- `requirements.txt`, `requirements-dev.txt`, `requirements-test.txt`
- `requirements-minimal.txt`, `requirements-ml-lite.txt`, `requirements-ml-cpu.txt`
- `requirements-optional.txt`, `requirements-notebook.txt`, `requirements-eval.txt`
- `requirements-audio-transcription.txt`
- `pyproject.toml`

### `requirements/`
- `agent.txt`, `lock.txt` (+ others)

### `.github/`
- `agents/ci-testing-agent/requirements.txt`
- `ai-evolution/requirements.txt`
- `copilot-cascade/requirements.txt`
- `copilot-security/requirements.txt`
- (+ additional agent requirement files)

### Other
- `audio_cleaner_v1/requirements.txt`
- `services/api/requirements.txt`
- `src/restore_pipeline/requirements.txt`
- `docs/requirements.txt`
- `scripts/security/requirements.txt`
- `codex_digest/requirements.txt`

---

## Methodology

1. Enumerated all requirements files using `find` and `glob`
2. Extracted unique package names (95 total) from all files
3. Queried GitHub Advisory Database in 12 batches of ~8 packages each
4. Prioritized high-risk categories: security/crypto, web frameworks, ML, serialization, infra
5. Applied minimum-version bumps to all affected files
6. Verified all changes with `grep` post-application

---

## Compliance

- **REQ-4 (CHANGELOG.md):** ✅ Updated with Security section
- **REQ-5 (AGENT_ACCOUNTABILITY_REPORT.md):** ✅ Session summary prepended
- **Secret Scanning:** ✅ No secrets found in modified files
- **Branch:** `copilot/dep-security-fixes-20260614` targeting `0D_base_`
