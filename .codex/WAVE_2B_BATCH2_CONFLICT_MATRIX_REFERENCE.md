# Wave 2B Batch 2: Conflict Resolution Reference

## Quick Reference: Batch 2 Packages

### Package: jinja2
- **Current:** >=3.1.6
- **CVEs Fixed:** CVE-2024-56326, CVE-2024-56201 (RCE via sandbox escape)
- **Status:** ✅ Pinned in requirements.txt
- **Known Conflicts:** None with P0 packages
- **Alternative Paths:** If conflict: jinja2>=3.0.0,<3.1.6 (partial mitigation, not recommended)

### Package: pip
- **Current:** 24.0 (environment default)
- **CVEs Fixed:** Package manager security updates
- **Status:** ✅ Current version adequate
- **Known Conflicts:** None expected (pip is meta-package)
- **Action if needed:** Upgrade via `python -m pip install --upgrade pip`

### Package: twisted
- **Current:** >=24.7.0
- **CVEs Fixed:** CVE-2024-41810, CVE-2024-41671 (XSS in redirectTo, HTTP pipelining)
- **Status:** ✅ Pinned in requirements-optional.txt
- **Known Conflicts:** Compatible with urllib3>=2.7.0, idna>=3.15
- **Alternative Paths:** twisted>=24.0.0,<24.7.0 (partial mitigation, check compatibility)

### Package: idna
- **Current:** >=3.15
- **CVEs Fixed:** CVE-2024-3651 (DoS via quadratic complexity)
- **Status:** ✅ Pinned in requirements.txt
- **Known Conflicts:** None with urllib3 or other packages
- **Alternative Paths:** idna>=3.0.0,<3.15 (partial mitigation, not recommended)

---

## Known Conflict Resolutions

### marshmallow 4.x ↔ great-expectations
**Status:** ✅ MITIGATED

**If conflict appears:**
```
Error: "great-expectations ... requires marshmallow<4.0.0"
       "pydantic ... requires marshmallow>=4.0.0"
```

**Resolution:**
1. Verify GE is in optional[ge] extra, not core
2. Pin GE version: `great-expectations>=0.18.7,<2`
3. Core keeps: `marshmallow>=4.0.0,<5` (supports pydantic)
4. Status: RESOLVED

---

## Pip Resolver Escalation Paths

### If circular dependency detected:
```bash
# Debug circular imports
python -m pip install --debug --dry-run -r requirements.txt

# Map dependency tree
pip install pipdeptree
pipdeptree --graph-output png
```

**Escalation:** Provide full dependency tree to @mbaetiong

### If resolver timeout:
```bash
# Reduce resolver backtracking
pip install --no-deps -r requirements.txt

# Check for unresolvable constraints
pip install -vv --dry-run -r requirements.txt 2>&1 | grep -A 10 "unresolvable"
```

**Escalation:** Document resolver output and affected packages

---

## P0 → P1 → P2 Sequencing Rules

**P0 Batch 1 (MUST complete first):**
- cryptography==49.0.0
- torch==2.6.0+cpu
- transformers>=5.10.2

**P1 Batch 2 (MUST follow P0):**
- jinja2>=3.1.6 ← currently being validated
- pip (latest)
- twisted>=24.7.0
- idna>=3.15

**P2 All Others (AFTER P1 complete):**
- All remaining dependencies
- Apply in parallel-safe groups

**If Agent 1 applies out of sequence:**
1. Alert immediately: "Sequence violation detected"
2. Document what was applied out of order
3. Recommend rollback to correct order
4. Escalate if ordering violated due to unresolvable conflict

---

## Test Validation After Patches

**Must Pass:**
```bash
nox -s tests --with-coverage
```

**Success Criteria:**
- ✅ ≥95% test pass rate
- ✅ Coverage ≥12%
- ✅ No new critical/high vulns introduced
- ✅ Zero circular dependencies in dependency tree

**If <95% pass rate:**
1. Identify newly-failing tests
2. Map failures to changed packages
3. Determine if conflict-related or patch-related
4. Provide remediation to Agent 1 or escalate

---

## Batch 2 Success Definition

- [x] All 4 packages (jinja2, pip, twisted, idna) verified in requirements
- [ ] Agent 1 applies any additional patches for Batch 2 CVEs
- [ ] Pip resolver passes without conflicts
- [ ] Test suite maintains ≥95% pass rate
- [ ] No new critical/high vulnerabilities introduced
- [ ] Coverage ≥12% maintained
- [ ] Conflict resolution documented and archived
