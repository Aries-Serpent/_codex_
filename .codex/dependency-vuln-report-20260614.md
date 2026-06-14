# Dependency Vulnerability Scan Report
**Campaign:** PROD-READINESS-CAMPAIGN-20260614 | **Date:** 2026-06-14 | **Branch:** `copilot/dep-security-fixes-20260614`

## Summary — 7 CVEs Fixed (2 Critical, 3 High, 2 Medium)

| Package | Severity | Advisory | Fix |
|---------|----------|----------|-----|
| `ray[serve]` | CRITICAL | RCE via DNS rebinding + Parquet Arrow deserialization | `>=2.55.0` |
| `chromadb` | CRITICAL | Pre-auth code injection (≤1.5.9) | `>=1.5.10` |
| `sentencepiece` | HIGH | Heap buffer overflow | `>=0.2.1` |
| `aiohttp` | HIGH | Zip bomb DoS (≤3.13.2) | `>=3.13.3` |
| `setuptools` | HIGH | Path traversal / arbitrary file write (<78.1.1) | `>=78.1.1` |
| `black` | MEDIUM | Arbitrary file write via cache | `>=26.3.1` |
| `GitPython` | MEDIUM | Windows untrusted search path (≤3.1.32) | `>=3.1.33` |

## Files Modified
- `pyproject.toml`: ray, sentencepiece (×6), chromadb (×2)
- `requirements-ml-lite.txt`, `requirements-optional.txt`: sentencepiece
- `requirements-minimal.txt`, `requirements/agent.txt`, `.github/ai-evolution/requirements.txt`: black + setuptools
- `.github/copilot-cascade/requirements.txt`, `.github/copilot-security/requirements.txt`: aiohttp
- `.github/agents/ci-testing-agent/requirements.txt`: GitPython

## Non-Actionable
- `wandb` SSRF: WITHDRAWN advisory — no action
- `ray` auth/jobs API RCE: no upstream patch — accepted risk

## Methodology
Scanned 95 unique packages from 29 requirements files using GitHub Advisory Database (12 batches).
