# Python Version Policy

**Version:** 1.0.0  
**Effective Date:** 2026-01-25  
**Status:** Active  
**Owner:** @mbaetiong

---

## 🎯 Policy Statement

This repository **requires Python 3.12.10 or later** (but < 3.13) for all development, testing, and production deployments.

**Strict Requirement:** Python 3.11 and earlier versions are **not supported** and will **not** be accepted.

---

## 📋 Version Requirements

### Supported Version
- **Minimum:** Python 3.12.10
- **Maximum:** < Python 3.13.0
- **Recommended:** Python 3.12.10 (latest stable in 3.12 series)

### Configuration Files
All configuration files must specify Python 3.12:

```toml
# pyproject.toml
[project]
requires-python = ">=3.12,<3.13"
```

```
# .python-version
3.12.10
```

```
# runtime.txt (if applicable)
python-3.12.10
```

---

## 🚫 Prohibited Patterns

### Version Conditionals
**Not Allowed:**
```python
import sys

if sys.version_info >= (3, 12):
    # Python 3.12+ code
else:
    # Python 3.11 fallback
```

**Reason:** Single version standard eliminates need for conditionals.

---

### Compatibility Imports
**Not Allowed:**
```python
try:
    import tomllib
except ImportError:
    import tomli as tomllib
```

**Reason:** Python 3.12 has tomllib built-in; no fallback needed.

---

### Version-Specific Test Markers
**Not Allowed:**
```python
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12+ required")
def test_something():
    pass
```

**Reason:** All tests run on Python 3.12; no conditional skips needed.

---

## ✅ Enforcement Mechanisms

### 1. Pre-Commit Hooks

**Installation:**
```bash
pre-commit install
```

**Hooks enforce:**
- Python 3.12.10 version check
- No `sys.version_info` conditionals
- No compatibility imports
- Configuration file validation

**Hook failures block commits** until issues are resolved.

---

### 2. CI/CD Validation

**GitHub Actions:** All workflows run on Python 3.12 only.

```yaml
- name: Set up Python 3.12
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'

- name: Verify Python version
  run: |
    python --version
    python -c "import sys; assert sys.version_info[:2] == (3, 12)"
```

**Validation Job:** `validate-python-version` runs on every PR.

---

### 3. Automated Validation Script

**Script:** `scripts/validate_python_version.py`

**Usage:**
```bash
python scripts/validate_python_version.py
```

**Validates:**
- `.python-version` file exists and is correct
- `pyproject.toml` has correct `requires-python`
- `runtime.txt` (if exists) has correct version
- Current Python environment is 3.12.x

**Exit codes:**
- `0`: All validations passed
- `1`: Validation failed

---

### 4. Code Review Requirements

**Pull Request Checklist:**
- [ ] Python 3.12.10 used for development
- [ ] No version conditionals introduced
- [ ] No compatibility imports added
- [ ] All tests pass on Python 3.12
- [ ] Pre-commit hooks pass
- [ ] Validation script passes

**Reviewers must verify** Python 3.12 compliance before approval.

---

## 📚 Rationale

### Why Python 3.12 Only?

1. **Simplified Codebase**
   - No version conditionals → cleaner code
   - No compatibility layers → easier maintenance
   - Single test matrix → faster CI/CD

2. **Performance**
   - Python 3.12 is 5-10% faster than 3.11
   - Improved memory management
   - Better compilation optimizations

3. **Modern Features**
   - PEP 695: Type parameter syntax
   - PEP 701: F-string improvements
   - PEP 698: Override decorator
   - Improved error messages

4. **Cost Savings**
   - 50% reduction in CI/CD time (no matrix)
   - 50% reduction in GitHub Actions minutes
   - Estimated $648/year savings

5. **Industry Alignment**
   - Python 3.12 is widely adopted (Dec 2023 release)
   - Active security support
   - Long-term support (until Oct 2028)

---

## 🔄 Version Upgrade Process

### When to Upgrade

**Python 3.13 Upgrade:** When Python 3.13 is stable and:
- All dependencies support 3.13
- Team has tested compatibility
- Migration plan is approved
- Breaking changes documented

### Upgrade Steps

1. **Planning** (1 month before)
   - Review Python 3.13 release notes
   - Audit dependencies for 3.13 support
   - Create migration plan
   - Communicate to team

2. **Testing** (2 weeks)
   - Set up 3.13 test environment
   - Run full test suite on 3.13
   - Fix compatibility issues
   - Update dependencies

3. **Execution** (1 week)
   - Update configuration files
   - Update CI/CD workflows
   - Update documentation
   - Merge and deploy

4. **Validation** (1 week)
   - Monitor for issues
   - Fix any problems quickly
   - Update troubleshooting guide

---

## 🆘 Exception Process

### Requesting an Exception

**Rare cases only.** Must provide:
- **Business justification:** Why exception is needed
- **Technical impact:** What will break without exception
- **Mitigation plan:** How to minimize risk
- **Sunset date:** When exception will be removed

**Approval required from:** Repository owner (@mbaetiong)

### Example Valid Exceptions

- **Legacy Integration:** Critical third-party system only supports Python 3.11
  - **Mitigation:** Isolated adapter service with Python 3.11
  - **Sunset:** 6 months (when vendor upgrades)

### Example Invalid Exceptions

- ❌ "I don't want to upgrade my local Python"
- ❌ "Tests pass on Python 3.11"
- ❌ "It's easier to support both versions"

---

## 📊 Compliance Monitoring

### Metrics Tracked

1. **Version Violations**
   - Count of `sys.version_info` conditionals introduced
   - Count of compatibility imports added
   - PRs blocked by pre-commit hooks

2. **Adoption Rate**
   - % of developers using Python 3.12.10
   - % of CI jobs running on Python 3.12
   - % of production deployments on Python 3.12

3. **Performance Impact**
   - CI/CD duration (target: <6 min average)
   - GitHub Actions minutes used (target: <7,000/month)
   - Test execution time (target: <5 min)

### Quarterly Review

**Review schedule:** Last week of each quarter

**Review items:**
- Policy effectiveness
- Compliance rate
- Exception requests
- Version upgrade timeline
- Performance metrics

---

## 🔗 Related Documentation

- **Migration Guide:** `PYTHON_312_MIGRATION_GUIDE.md`
- **Phase 5 Complete:** `PHASE_5_COMPLETE.md`
- **Validation Script:** `scripts/validate_python_version.py`
- **Pre-Commit Config:** `.pre-commit-config.yaml`

---

## 📝 Change Log

### Version 1.0.0 (2026-01-25)
- Initial policy creation
- Python 3.12.10 minimum version established
- Enforcement mechanisms defined
- Exception process documented

---

## ✅ Policy Acceptance

By contributing to this repository, you agree to:
- Use Python 3.12.10 or later for all development
- Not introduce version conditionals or compatibility imports
- Follow pre-commit hook requirements
- Validate changes with validation script
- Comply with this policy in all contributions

---

**Questions?** Contact @mbaetiong or create an issue.

**Policy Review:** Quarterly (next review: 2026-04-30)
