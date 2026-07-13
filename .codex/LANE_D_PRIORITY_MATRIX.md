# Lane D: Priority Matrix

**Generated:** 2026-07-13T13:14:45Z  
**Total Findings:** 302 unique findings  
**Severity Breakdown:** C=69, H=51, M=155, L=42

---

## PRIORITY 1: CRITICAL (69 findings) 🔴

**Must fix before any merge. Security risk is ACTIVE.**

### P1.1: Clear-Text Sensitive Data Logging (30 findings)

| File | Lines | Issue | Effort | Status |
|------|-------|-------|--------|--------|
| scripts/decode_workflow_secrets.py | 166,168,170,172 | Secret logging | 1.5h | ⬜ Pending |
| .github/agents/admin-automation-agent/src/agent.py | 166,168,170,172 | Secret logging | 1.5h | ⬜ Pending |
| scripts/ci/aggregate_security_findings.py | 281,287 | Sensitive data logging | 0.5h | ⬜ Pending |
| scripts/fix_security_issues.py | Multiple | Sensitive logging | 0.5h | ⬜ Pending |
| scripts/github_secrets_sync.py | Multiple | Secret logging | 0.5h | ⬜ Pending |
| scripts/analyze_workflows.py | 319 | Log injection | 0.3h | ⬜ Pending |
| .github/scripts/ci_failure_crossref.py | 169 | Log injection | 0.3h | ⬜ Pending |
| scripts/ops/codex_mint_tokens_per_run.py | 401 | Secret logging | 0.3h | ⬜ Pending |
| scripts/ops/codex_repo_admin_bootstrap.py | 575 | Secret logging | 0.3h | ⬜ Pending |
| scripts/ci/copilot_security_agent_handoff.py | Multiple | Log injection | 0.3h | ⬜ Pending |
| scripts/observability/core_telemetry_collector.py | Multiple | Secret logging | 0.3h | ⬜ Pending |
| src/security/logging.py | Various | Configuration issue | 0.3h | ⬜ Pending |
| **Additional files** | **13 more** | **Clear-text logging** | **~2h** | ⬜ Pending |

**Sub-total:** 30 findings, ~8.5h effort

**Fix Pattern:**
```python
def mask_token(token):
    return token[:8] + '***' if len(token) > 8 else '***'
logger.info(f"Token: {mask_token(token)}")
```

---

### P1.2: Dynamic URL Handling Vulnerabilities (33 findings) 🔴

**OWASP A01:2024 - Broken Access Control**  
**CWE-939**

| File | Count | Risk | Effort | Status |
|------|-------|------|--------|--------|
| .github/agents/codex_reviewer/github_client.py | 4 | CRITICAL | 1.5h | ⬜ Pending |
| .github/agents/github-guru-agent/github_client.py | 3 | CRITICAL | 1h | ⬜ Pending |
| src/aries_serpent_core/autonomy/token_broker.py | 2 | CRITICAL | 1h | ⬜ Pending |
| utils/safe_pickle.py | 1 | CRITICAL | 0.3h | ⬜ Pending |
| services/msp_gateway/middleware/tenant_context.py | 1 | CRITICAL | 0.3h | ⬜ Pending |
| **Additional locations** | **22 more** | **CRITICAL** | **1.5h** | ⬜ Pending |

**Sub-total:** 33 findings, ~5.5h effort

**Fix Pattern:**
```python
from urllib.parse import urlparse
parsed = urlparse(user_input)
if parsed.scheme not in ('http', 'https'):
    raise ValueError(f"Invalid URL scheme")
```

---

### P1.3: Exec/Code Injection (2 findings) 🔴

**OWASP A03:2024 - Injection**  
**CWE-95**

| File | Count | Risk | Effort | Status |
|------|-------|------|--------|--------|
| Multiple | 2 | CRITICAL | 3-4h | ⬜ Pending |

**Fix:** Code sandbox or reject dynamic execution

**Sub-total:** 2 findings, ~3.5h effort

---

## PRIORITY 2: HIGH (51 findings) 🟠

**Must fix before production release.**

### P2.1: Pickle Deserialization (23 findings)

**OWASP A08:2024 - Data Integrity Failures**  
**CWE-502**

| File | Lines | Risk | Effort | Status |
|------|-------|------|--------|--------|
| mutants/tests/test_cache_management.py | Multiple | HIGH | 1.5h | ⬜ Pending |
| tests/test_cache_management.py | Multiple | HIGH | 1.5h | ⬜ Pending |
| mutants/src/codex_ml/utils/safe_pickle.py | 3 instances | HIGH | 1h | ⬜ Pending |
| src/codex_ml/utils/safe_pickle.py | 3 instances | HIGH | 1h | ⬜ Pending |
| utils/safe_pickle.py | 3 instances | HIGH | 1h | ⬜ Pending |
| **Additional files** | **9 more** | **HIGH** | **2.5h** | ⬜ Pending |

**Sub-total:** 23 findings, ~8.5h effort

**Fix Pattern:**
```python
# UNSAFE: pickle.loads(untrusted_data)
# SAFE: json.loads(untrusted_data)
```

---

### P2.2: Log Injection Attacks (11 findings) 🟠

| File | Count | Risk | Effort | Status |
|------|-------|------|--------|--------|
| Multiple files | 11 | HIGH | ~2h | ⬜ Pending |

**Fix:** Input sanitization
```python
sanitized = user_input.replace('\n', '\\n').replace('\r', '\\r')
```

---

### P2.3: Weak Password Hashing (6 findings) 🟠

| File | Count | Risk | Effort | Status |
|------|-------|------|--------|--------|
| Multiple files | 6 | HIGH | ~1.5h | ⬜ Pending |

**Fix:** Replace SHA256 with bcrypt

---

### P2.4: Clear-Text Secret Storage (6 findings) 🟠

| File | Count | Risk | Effort | Status |
|------|-------|------|--------|--------|
| Multiple files | 6 | HIGH | ~2h | ⬜ Pending |

**Fix:** Use cryptography.Fernet

---

### P2.5: Token Broker Security Issues (5 findings) 🟠

| File | Count | Risk | Effort | Status |
|------|-------|------|--------|--------|
| src/aries_serpent_core/autonomy/token_broker.py | - | HIGH | 2h | ⬜ Pending |
| mutants/src/codex/autonomy/token_broker.py | - | HIGH | 2h | ⬜ Pending |

**Sub-total P2:** 51 findings, ~16h effort

---

## PRIORITY 3: MEDIUM (155 findings) 🟡

**Recommended for next maintenance cycle.**

### P3.1: MD5/Weak Cryptographic Algorithms (18 findings)

**OWASP A02:2024 - Cryptographic Failures**

**Fix:** Replace MD5 with SHA256  
**Effort:** ~4h across multiple files  
**Status:** ⬜ Pending

---

### P3.2: Credential Disclosure in Logs (19 findings)

**OWASP A09:2024 - Logging and Monitoring Failures**

**Effort:** ~3h  
**Status:** ⬜ Pending

---

### P3.3: File Permission Issues (5 findings)

**OWASP A04:2024 - Insecure Design**

**Effort:** ~1h  
**Status:** ⬜ Pending

---

### P3.4: Stack Trace Exposure (5 findings)

**Effort:** ~2h  
**Status:** ⬜ Pending

---

### P3.5: Additional MEDIUM Issues (108 findings)

**Various code quality and security pattern issues**

**Sub-total P3:** 155 findings, ~12h effort

---

## PRIORITY 4: LOW (42 findings) 🟢

**Optional improvements. Can be automated or deferred.**

### P4.1: Code Quality Issues

- Unused variables: 20 findings (ESLint/Prettier auto-fix)
- Automatic semicolon insertion: 5 findings (auto-fix)
- Trivial conditionals: 3 findings (1-2h manual)
- Other formatting: 14 findings (auto-fix)

**Automation:** 95% can be automated  
**Manual effort:** ~1h  
**Status:** ⬜ Pending

---

## Summary Table

| Priority | Count | Effort (Hours) | Wall Time | Phase |
|----------|-------|---|---|---|
| **P1: CRITICAL** | 69 | 17.5 | 4-5h | Week 1 |
| **P2: HIGH** | 51 | 16 | 8-10h | Week 2 |
| **P3: MEDIUM** | 155 | 12 | 6-8h | Week 3 |
| **P4: LOW** | 42 | 1 | 0.5h (auto) | Optional |
| **TOTAL** | 302 | 46.5 | 18-23h | 3 weeks |

---

## Quick Reference by File

### Files Requiring Immediate Attention (P1-P2)

```
scripts/decode_workflow_secrets.py ⚠️ 7 CRITICAL
.github/agents/admin-automation-agent/src/agent.py ⚠️ 4 CRITICAL
.github/agents/codex_reviewer/github_client.py ⚠️ 4 CRITICAL
mutants/tests/test_cache_management.py ⚠️ 5 HIGH
tests/test_cache_management.py ⚠️ 5 HIGH
src/aries_serpent_core/autonomy/token_broker.py ⚠️ 4 HIGH
mutants/src/codex/autonomy/token_broker.py ⚠️ 4 HIGH
```

### Large Files with Many Low-Priority Issues

```
site/assets/javascripts/lunr/wordcut.js 🟢 32 LOW (auto-fixable)
site/assets/javascripts/lunr/tinyseg.js 🟢 5 LOW (auto-fixable)
```

---

**Generated:** 2026-07-13T13:14:45Z  
**Status:** Ready for Phase 5.3 Implementation
