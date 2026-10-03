# CodeQL Remediation Action Plan — PR #5071

**Status:** ACTIVE REMEDIATION IN PROGRESS
**Date:** 2026-06-24T20:45Z
**Alerts:** 66 total (36 HIGH + 30 MEDIUM)
**Strategy:** Systematic fix-by-category approach with committed progress tracking

---

## PHASE 1: HIGH SEVERITY INFORMATION DISCLOSURE (36 alerts)

### Rule: py/clear-text-logging-sensitive-data (30 alerts)
**Files:** 11 files with logging of sensitive data
**Remediation:** Replace clear-text logging with masked/sanitized output or suppress with `# noqa: B110`

**Files to Fix:**
1. .github/agents/admin-automation-agent/src/agent.py (4 alerts: lines 155, 157, 159, 161)
2. .github/agents/github-security-validator-agent/src/agent.py (2 alerts: lines 268, 274)
3. .github/scripts/ci_failure_crossref.py (1 alert: line 167)
4. scripts/analyze_workflows.py (1 alert: line 315)
5. scripts/catalog_workflows.py (2 alerts: lines 280, 281)
6. scripts/ci/auto_fix_common_issues.py (2 alerts: lines 472, 478)
7. scripts/decode_workflow_secrets.py (1 alert: line 217)
8. scripts/fix_security_issues.py (2 alerts: lines 266, 270)
9. scripts/github_secrets_sync.py (2 alerts: lines 115, 118)
10. scripts/ops/codex_mint_tokens_per_run.py (2 alerts: lines 401, 449)
11. scripts/ops/codex_repo_admin_bootstrap.py (1 alert: line 572)
12. scripts/security/verify_token_scope.py (5 alerts: lines 211, 212, 221, 225, 226)
13. src/codex/knowledge/pii.py (2 alerts: lines 179, 180)
14. src/security/providers/github_provider.py (2 alerts: lines 481, 519)
15. tests/integration/test_admin_automation_agent.py (1 alert: line 226)

**Status:** 30/30 fixable

### Rule: py/clear-text-storage-sensitive-data (6 alerts)
**Files:** 4 files storing sensitive data in plain text
**Remediation:** Encrypt storage or suppress false positives

**Files:**
1. .codex/reports/ci_workflow_analysis_artifacts_2026_01_30/workflow_analyzer.py (1 alert: line 503) → SUPPRESS
2. .github/scripts/workflow_analyzer.py (2 alerts: lines 464, 468) → FIX
3. scripts/catalog_workflows.py (3 alerts: lines 297, 298, 319) → FIX

**Status:** 5/6 code-fixable, 1/6 suppress

---

## PHASE 2: MEDIUM SEVERITY (30 alerts)

### Log Injection (6 alerts)
**Remediation:** Sanitize user input before logging

**Files:**
1. scripts/catalog_workflows.py:350 → FIX
2. scripts/analyze_workflows.py:405 → FIX
3. .github/scripts/ci_failure_crossref.py:280 → FIX
4. scripts/security/verify_token_scope.py:189 → SUPPRESS
5. cognitive_app/src/server/cli_api_server.py:542 → FIX
6. services/msp_gateway/security.py:234 → FIX

**Status:** 5/6 fixable, 1/6 suppress

### Code Quality: Uninitialized Variables (8 alerts)
**Remediation:** Initialize variables before use

**Files:**
1. scripts/cognitive/tests/test_advanced_reasoning.py:145 → FIX
2. agents/physics_orchestrator.py:234 → FIX
3. scripts/ci/auto_fix_common_issues.py:189 → FIX
4. tests/tokenization/test_fast_tokenizer_wrapper.py:456 → FIX
5. tests/tokenization/test_roundtrip_basic.py:278 → FIX
6. src/security/core.py:112 → FIX
7. .github/agents/admin-automation-agent/src/agent.py:98 → FIX
8. tools/codex_secret_scan_stub.py:145 → SUPPRESS
9. cognitive_app/src/server/cli_api_server.py:356 → FIX

**Status:** 8/9 fixable, 1/9 suppress

### Cyclic Imports (2 alerts)
**Files:**
1. src/codex/__init__.py:5 → FIX
2. src/codex/utils/helpers.py:3 → FIX

**Status:** 2/2 fixable

### Unused Globals (2 alerts)
**Files:**
1. scripts/github_secrets_sync.py:45 → FIX
2. tests/codex/test_cli_maps.py:12 → SUPPRESS

**Status:** 1/2 fixable, 1/2 suppress

### Inherited Attribute Overwrite (2 alerts)
**Files:**
1. src/security/core.py:78 → FIX
2. .github/agents/github-security-validator-agent/src/agent.py:45 → SUPPRESS

**Status:** 1/2 fixable, 1/2 suppress

### Pythagorean (3 alerts)
**Files:**
1. scripts/ci/auto_fix_common_issues.py:567 → FIX
2. src/codex/utils/math_helpers.py:234 → FIX
3. tests/codex/test_math.py:89 → SUPPRESS

**Status:** 2/3 fixable, 1/3 suppress

### Path Injection (1 alert)
**Files:**
1. scripts/fix_security_issues.py:123 → FIX

**Status:** 1/1 fixable

### SQL Injection (1 alert)
**Files:**
1. src/db/query.py:456 → FIX

**Status:** 1/1 fixable

### Code Injection (1 alert)
**Files:**
1. scripts/ci/auto_fix_common_issues.py:678 → FIX

**Status:** 1/1 fixable

### Weak Crypto (2 alerts)
**Files:**
1. src/security/crypto.py:145 → FIX
2. scripts/ops/codex_mint_tokens_per_run.py:234 → FIX

**Status:** 2/2 fixable

### Insecure Randomness (1 alert)
**Files:**
1. src/security/token_generator.py:67 → FIX

**Status:** 1/1 fixable

---

## SUMMARY

- **Total:** 66 alerts
- **Code Fixes Required:** 60
- **Suppressions Required:** 6
- **Strategy:** Process by category, commit each wave, verify with CodeQL re-scan

---

## EXECUTION ORDER

1. HIGH severity (py/clear-text-logging): 30 fixes
2. HIGH severity (py/clear-text-storage): 5 fixes + 1 suppress
3. MEDIUM severity (log-injection, uninitialized, cyclic, etc.): 25 fixes + 5 suppress

**Total time estimate:** 2-3 hours for comprehensive remediation
