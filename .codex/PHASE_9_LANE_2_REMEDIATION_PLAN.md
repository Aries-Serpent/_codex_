# PHASE 9 LANE 2 - EMERGENCY REMEDIATION ACTION PLAN

**Status**: 🔴 **BLOCKING - Phase 10 HALTED**  
**Severity**: CRITICAL (Supply Chain Security)  
**Timeline**: IMMEDIATE (must complete before Phase 10)  
**Estimated Duration**: < 30 minutes to fix + re-audit  
**Gate Target**: 2026-07-19T02:00Z  

---

## CRITICAL ISSUE SUMMARY

**3 HIGH-severity CVEs block Phase 10**:
1. **CVE-2026-24049** (wheel 0.42.0) - Path Traversal
2. **PYSEC-2026-1994** (urllib3 2.0.7) - Decompression Bomb  
3. **PYSEC-2026-1996** (urllib3 2.0.7) - Decompression Bomb

**Root Cause**: wheel not explicitly pinned in requirements.txt (CI install file)
- ✅ Correct: pyproject.toml specifies wheel>=0.46.2
- ❌ Missing: requirements.txt missing wheel specification
- ❌ Result: pip doesn't upgrade wheel when installing from requirements.txt

---

## IMMEDIATE FIXES (REQUIRED)

### Fix #1: Add wheel to requirements.txt

**File**: `/home/runner/work/_codex_/_codex_/requirements.txt`

**Current state** (lines 1-30):
```
typer>=0.12
cryptography>=48.0.1,<50.0.0  # Security: Phase 5 Track 2...
PyJWT>=2.13.0,<3.0.0  # Security: Phase 14 WS1...
PyNaCl>=1.5.0,<2.0.0
pyOpenSSL>=26.0.0,<27.0.0
jsonschema>=4.26.0
psutil>=5.9; platform_system != "Windows"
tomli>=2.0; python_version < "3.11"
pytest>=9.0.3,<10.0.0
pytest-cov==7.1.0
pytest-xdist>=3.5.0,<4.0.0
nox>=2026.4.10,<2027
numpy>=2.4.6,<3
--extra-index-url https://download.pytorch.org/whl/cpu
torch>=2.6.1,<3.0.0; sys_platform == "linux" or sys_platform == "darwin"
transformers>=5.12.1,<6
defusedxml>=0.7.1,<1.0.0
pyyaml>=6.0
jinja2>=3.1.6  # Security: Fixes CVE-2024-56326...
certifi>=2026.6.17
filelock>=3.29.0
idna>=3.18
urllib3>=2.7.0  # Security: Fixes CVE-2024-37891...
requests>=2.33.0  # Security: Phase 14 WS1...
```

**Required change**:
```diff
  typer>=0.12
  cryptography>=48.0.1,<50.0.0  # Security: Phase 5 Track 2
  PyJWT>=2.13.0,<3.0.0  # Security: Phase 14 WS1
+ wheel>=0.46.2  # Security: CVE-2026-24049 - path traversal fix
  PyNaCl>=1.5.0,<2.0.0
  pyOpenSSL>=26.0.0,<27.0.0
```

**Action**: Insert "wheel>=0.46.2" after PyJWT line

---

### Fix #2: Verify All Critical Versions

**Checklist - Verify these are in requirements.txt**:

- [x] wheel>=0.46.2 (ADD THIS)
- [x] urllib3>=2.7.0 ✅ Already present
- [x] cryptography>=48.0.1 ✅ Already present  
- [x] jinja2>=3.1.6 ✅ Already present
- [x] requests>=2.33.0 ✅ Already present
- [x] PyJWT>=2.13.0 ✅ Already present
- [x] pyOpenSSL>=26.0.0 ✅ Already present

**Status**: Only wheel needs to be added

---

## VERIFICATION STEPS

### Step 1: Confirm the fix compiles

```bash
# Edit requirements.txt and add wheel line
nano /home/runner/work/_codex_/_codex_/requirements.txt

# Verify syntax (dry-run install)
pip install --dry-run -q -r /home/runner/work/_codex_/_codex_/requirements.txt
# Should complete without errors
```

### Step 2: Install upgraded packages

```bash
# Install all requirements (upgrade where needed)
pip install --upgrade -r /home/runner/work/_codex_/_codex_/requirements.txt
pip install --upgrade -r /home/runner/work/_codex_/_codex_/requirements-dev.txt
pip install --upgrade -r /home/runner/work/_codex_/_codex_/requirements-test.txt

# Verify installation
pip list | grep -E "wheel|urllib3|cryptography|jinja2"
# Expected output:
#   wheel                 0.46.2 (or later)
#   urllib3               2.7.0 (or later)
#   cryptography          48.0.1+ (or later)
#   jinja2                3.1.6 (or later)
```

### Step 3: Re-run vulnerability audit

```bash
# Run pip-audit to confirm fixes
cd /home/runner/work/_codex_/_codex_
pip-audit

# Expected result:
# Found 0 known vulnerabilities in 1 installed packages
# 
# ✅ All CVEs fixed!
```

### Step 4: Verify specific CVEs are gone

```bash
# Check that the 3 blocking CVEs are resolved
pip-audit --desc 2>&1 | grep -E "CVE-2026-24049|PYSEC-2026-1994|PYSEC-2026-1996"

# Expected: No output (CVEs not found)
```

### Step 5: Update lock files

```bash
# Regenerate lock files with new versions
pip freeze > requirements-frozen.txt

# Update Node lock if needed
npm install

# Update Rust lock if needed  
cargo update

# Commit lock files
git add package-lock.json Cargo.lock uv.lock
git commit -m "Phase 9 Lane 2: Update lock files after security remediation"
```

---

## ROLLBACK PROCEDURE

**If remediation breaks something**:

```bash
# Revert requirements.txt
git checkout requirements.txt

# Reinstall old versions
pip install -r requirements.txt

# Investigate the issue
pip-audit --desc

# Contact maintainers for assistance
```

---

## VALIDATION CHECKLIST

Before declaring Phase 9 Lane 2 complete, verify:

- [ ] requirements.txt contains wheel>=0.46.2
- [ ] All 5 critical packages updated:
  - [ ] wheel>=0.46.2
  - [ ] urllib3>=2.7.0
  - [ ] cryptography>=48.0.1
  - [ ] jinja2>=3.1.6
  - [ ] requests>=2.33.0
- [ ] pip-audit shows 0 unfixed HIGH/CRITICAL
- [ ] Specific CVEs confirmed as fixed:
  - [ ] CVE-2026-24049 not found
  - [ ] PYSEC-2026-1994 not found
  - [ ] PYSEC-2026-1996 not found
- [ ] Lock files updated:
  - [ ] package-lock.json
  - [ ] Cargo.lock
  - [ ] uv.lock
- [ ] SBOM regenerated with new versions
- [ ] Changes committed to git
- [ ] Phase 9 Lane 2 gate re-run confirms PASS

---

## EXPECTED OUTCOMES

### Before Remediation (Current)
```
Found 59 known vulnerabilities in 17 packages
├── HIGH: 3 (blocking)
│   ├── CVE-2026-24049 (wheel 0.42.0)
│   ├── PYSEC-2026-1994 (urllib3 2.0.7)
│   └── PYSEC-2026-1996 (urllib3 2.0.7)
├── MEDIUM: ~35
└── LOW: ~21

Gate Status: 🔴 FAILED
```

### After Remediation (Expected)
```
Found [reduced] known vulnerabilities in [reduced] packages
├── HIGH: 0 ✅
├── MEDIUM: ~35 (may decrease with upgrades)
└── LOW: ~21 (may decrease with upgrades)

Gate Status: 🟢 PASSED
```

---

## TIMELINE

| Step | Task | Duration | Cumulative |
|------|------|----------|-----------|
| 1 | Edit requirements.txt | 2 min | 2 min |
| 2 | Verify syntax (dry-run) | 5 min | 7 min |
| 3 | Install packages | 10 min | 17 min |
| 4 | Verify installation | 2 min | 19 min |
| 5 | Run pip-audit | 3 min | 22 min |
| 6 | Update lock files | 5 min | 27 min |
| 7 | Commit changes | 2 min | 29 min |

**Total Time**: ~29 minutes (< 30 min estimate)

---

## ESCALATION PROCEDURE

**If remediation fails**:

1. Document the error
2. Check for conflicting dependencies
3. Review GitHub issues for known problems with specific versions
4. Consider alternative versions:
   - wheel: Try 0.47.0 instead of 0.46.2
   - urllib3: Try 2.6.4 instead of 2.7.0
   - Others: Check PyPI for latest stable release

**Critical Contacts**:
- Package maintainers (PyPI)
- GitHub Issue tracker
- Dependency resolver tools (pip-tools, poetry)

---

## COMPLIANCE NOTES

### Why This Is Critical

**Supply Chain Security Gate**: The wheel and urllib3 packages are:
- **wheel**: Used during EVERY Python package installation (setuptools)
- **urllib3**: Used by requests for ALL HTTP communication

**Attack Surface**: Leaving these unfixed means:
- Package installation pipeline exposed to path traversal attacks
- All HTTP-based APIs exposed to decompression bomb DoS
- CI/CD infrastructure at risk

### Phase 10 Dependency

**Phase 9 Lane 2** is a HARD GATE for Phase 10:
- Phase 10 cannot start until Phase 9 Lane 2 passes
- This is non-negotiable per phase specification
- All other lanes (1, 3, 4) are blocked until this resolves

---

## SIGN-OFF

**Remediation Status**: PENDING EXECUTION  
**Gate Target Date**: 2026-07-19T02:00Z  
**Estimated Completion**: 2026-07-16T16:00Z (today)  
**Owner**: Phase 9 Lane 2 Engineer  
**Approval Required**: Security gates confirmed  

---

**Document Generated**: 2026-07-16T15:06:18Z  
**Version**: 1.0 (Initial)  
**Classification**: Security Critical

---

*Execute these steps immediately to unblock Phase 10 and resolve critical supply chain vulnerabilities*
