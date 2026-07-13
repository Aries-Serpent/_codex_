# 🔧 Security Remediation Actions - Run #29222808051

**Generated:** 2026-07-13T04:34:29Z
**Total Findings:** 129 (28 Critical, 101 Medium)
**Status:** Ready for remediation

---

## 🔴 CRITICAL FINDINGS - 28 Total

### python.cryptography.security.mode-without-authentication.crypto-mode-without-authentication

**Count:** 4 findings

**Description:** An encryption mode of operation is being used without proper message authentication. This can potentially result in the encrypted content to be decrypted by an attacker. Consider instead use an AEAD mode of operation like GCM. 

**Affected Locations:**

  - `mutants/tests/security/test_cryptography_coverage_wave2a.py:190` (ID: SEMGREP-python.cryptography.security.mode-without-authentication.crypto-mode-without-authentication-043)
  - `mutants/tests/security/test_cryptography_coverage_wave2a.py:207` (ID: SEMGREP-python.cryptography.security.mode-without-authentication.crypto-mode-without-authentication-044)
  - `tests/security/test_cryptography_coverage_wave2a.py:190` (ID: SEMGREP-python.cryptography.security.mode-without-authentication.crypto-mode-without-authentication-101)
  - ... and 1 more


### python.jwt.security.jwt-hardcode.jwt-python-hardcoded-secret

**Count:** 22 findings

**Description:** Hardcoded JWT secret or private key is used. This is a Insufficiently Protected Credentials weakness: https://cwe.mitre.org/data/definitions/522.html Consider using an appropriate security mechanism to protect the credentials (e.g. keeping secrets in environment variables)

**Affected Locations:**

  - `mutants/tests/security/test_pyjwt_coverage_wave2a.py:93` (ID: SEMGREP-python.jwt.security.jwt-hardcode.jwt-python-hardcoded-secret-045)
  - `mutants/tests/security/test_pyjwt_coverage_wave2a.py:106` (ID: SEMGREP-python.jwt.security.jwt-hardcode.jwt-python-hardcoded-secret-046)
  - `mutants/tests/security/test_pyjwt_coverage_wave2a.py:127` (ID: SEMGREP-python.jwt.security.jwt-hardcode.jwt-python-hardcoded-secret-047)
  - ... and 19 more


### python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args

**Count:** 2 findings

**Description:** Detected subprocess function 'run' with user controlled data. A malicious actor could leverage this to perform command injection. You may consider using 'shlex.quote()'.

**Affected Locations:**

  - `mutants/tests/test_container_smoke.py:113` (ID: SEMGREP-python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args-062)
  - `tests/test_container_smoke.py:112` (ID: SEMGREP-python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args-120)

---

## 🟡 MEDIUM FINDINGS - 101 Total

**Unique Rules:** 7

**Top 10 Rules by Count:**

1. python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected: 33 findings
2. python.lang.security.deserialization.pickle.avoid-pickle: 23 findings
3. python.lang.security.audit.logging.logger-credential-leak.python-logger-credential-disclosure: 19 findings
4. python.lang.security.insecure-hash-algorithms-md5.insecure-hash-algorithm-md5: 18 findings
5. python.lang.security.audit.insecure-file-permissions.insecure-file-permissions: 5 findings
6. python.lang.security.audit.exec-detected.exec-detected: 2 findings
7. terraform.lang.security.eks-public-endpoint-enabled.eks-public-endpoint-enabled: 1 findings

---

## 📋 REMEDIATION SUMMARY

| Category | Count | Status |
|----------|-------|--------|
| Critical - JWT Hardcoded | 14 | Fix required |
| Critical - Crypto Issues | 2 | Fix required |
| Critical - Command Injection | 1 | Fix required |
| Critical - Mutant Duplicates | 11 | Audit/ignore |
| Medium Findings | 101 | Triage required |
| **TOTAL** | **129** | **In Progress** |

**Effort Estimate:** 1.5-2 hours to resolve all critical findings
